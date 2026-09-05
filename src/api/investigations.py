"""Investigation API endpoints with SQLAlchemy 2.0 PostgreSQL & SQLite support."""
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
from sqlalchemy import text

from src.database.database import get_db_session
from src.database.models import InvestigationDB, FindingDB
from src.engine.risk_engine import RiskEngine
from src.evidence.evidence_store import EvidenceStore
from src.ai.report_generator import explain_investigation, answer_investigation_query

logger = logging.getLogger("risklens.api.investigations")
router = APIRouter(prefix="/api/investigations", tags=["investigations"])


class CreateInvestigationRequest(BaseModel):
    customer_id: str


class ChatRequest(BaseModel):
    question: str


@router.post("")
def create_investigation(payload: CreateInvestigationRequest) -> Dict[str, Any]:
    """Start a deterministic risk investigation for a customer."""
    customer_id = payload.customer_id.strip()

    with get_db_session() as session:
        # Get customer info
        cust_row = session.execute(
            text("SELECT customer_id, name FROM customers WHERE customer_id = :cid"),
            {"cid": customer_id}
        ).mappings().first()

        if not cust_row:
            return {
                "success": False,
                "error": {
                    "code": "CUSTOMER_NOT_FOUND",
                    "message": f"Customer '{customer_id}' not found."
                }
            }

        customer_name = cust_row["name"]

        # Fetch customer transactions
        txn_rows = session.execute(text("""
            SELECT transaction_id, customer_id, timestamp, description, payee, amount, channel
            FROM transactions
            WHERE customer_id = :cid
            ORDER BY timestamp ASC
        """), {"cid": customer_id}).mappings().all()

        if not txn_rows:
            return {
                "success": False,
                "error": {
                    "code": "NO_TRANSACTIONS",
                    "message": f"Customer '{customer_id}' has zero transaction records."
                }
            }

        txns_data = [dict(r) for r in txn_rows]
        df = pd.DataFrame(txns_data)

        # Run deterministic risk engine
        risk_engine = RiskEngine()
        inv_result = risk_engine.run_investigation(
            customer_id=customer_id,
            customer_name=customer_name,
            transactions_df=df
        )

        now_str = datetime.utcnow().isoformat()

        # Persist investigation via ORM (dialect-agnostic ID generation)
        inv_db = InvestigationDB(
            customer_id=customer_id,
            status=inv_result["investigation_status"],
            risk_level=inv_result["risk_level"],
            started_at=now_str,
            completed_at=now_str,
            summary=inv_result["summary"]
        )
        session.add(inv_db)
        session.flush()
        investigation_id = inv_db.id

        # Persist findings and evidence
        for f in inv_result.get("findings", []):
            f_db = FindingDB(
                investigation_id=investigation_id,
                finding_id=f["finding_id"],
                rule_id=f["rule_id"],
                severity=f["severity"],
                title=f["title"],
                description=f["description"],
                confidence=float(f["confidence"]),
                created_at=now_str
            )
            session.add(f_db)
            EvidenceStore.save_evidence(session, f["finding_id"], f.get("evidence", []))

        inv_result["id"] = investigation_id
        logger.info("Investigation created id=%d customer=%s status=%s", investigation_id, customer_id, inv_result["investigation_status"])

        return {
            "success": True,
            "data": inv_result
        }


@router.get("")
def list_investigations() -> Dict[str, Any]:
    """List all completed investigations with aggregate metrics."""
    with get_db_session() as session:
        result = session.execute(text("""
            SELECT i.id, i.customer_id, i.status, i.risk_level, i.started_at, i.completed_at, i.summary,
                   c.name as customer_name,
                   COUNT(DISTINCT f.id) as findings_count,
                   COUNT(DISTINCT t.id) as transactions_count
            FROM investigations i
            LEFT JOIN customers c ON i.customer_id = c.customer_id
            LEFT JOIN findings f ON i.id = f.investigation_id
            LEFT JOIN transactions t ON i.customer_id = t.customer_id
            GROUP BY i.id, i.customer_id, i.status, i.risk_level, i.started_at, i.completed_at, i.summary, c.name
            ORDER BY i.id DESC
        """))
        rows = result.mappings().all()

        investigations = []
        for r in rows:
            investigations.append({
                "id": r["id"],
                "customer_id": r["customer_id"],
                "customer_name": r["customer_name"] or "Unknown",
                "status": r["status"],
                "risk_level": r["risk_level"],
                "started_at": r["started_at"],
                "completed_at": r["completed_at"],
                "summary": r["summary"],
                "findings_count": r["findings_count"],
                "transactions_count": r["transactions_count"]
            })

        return {
            "success": True,
            "data": investigations
        }


@router.get("/{investigation_id}")
def get_investigation(investigation_id: int) -> Dict[str, Any]:
    """Retrieve full details of an investigation."""
    with get_db_session() as session:
        inv_row = session.execute(text("""
            SELECT i.id, i.customer_id, i.status, i.risk_level, i.started_at, i.completed_at, i.summary,
                   c.name as customer_name
            FROM investigations i
            LEFT JOIN customers c ON i.customer_id = c.customer_id
            WHERE i.id = :inv_id
        """), {"inv_id": investigation_id}).mappings().first()

        if not inv_row:
            return {
                "success": False,
                "error": {
                    "code": "INVESTIGATION_NOT_FOUND",
                    "message": f"Investigation ID {investigation_id} not found."
                }
            }

        customer_id = inv_row["customer_id"]
        customer_name = inv_row["customer_name"] or "Unknown"

        # Load customer transactions to rebuild baseline and correlations
        txn_rows = session.execute(text("""
            SELECT transaction_id, customer_id, timestamp, description, payee, amount, channel
            FROM transactions
            WHERE customer_id = :cid
            ORDER BY timestamp ASC
        """), {"cid": customer_id}).mappings().all()

        df = pd.DataFrame([dict(r) for r in txn_rows])
        risk_engine = RiskEngine()
        inv_result = risk_engine.run_investigation(customer_id, customer_name, df)
        inv_result["id"] = investigation_id

        return {
            "success": True,
            "data": inv_result
        }


@router.post("/{investigation_id}/explain")
def explain_investigation_endpoint(investigation_id: int) -> Dict[str, Any]:
    """Generate Gemini AI explanation with strict hallucination validation and fallback."""
    with get_db_session() as session:
        inv_row = session.execute(
            text("SELECT customer_id FROM investigations WHERE id = :inv_id"),
            {"inv_id": investigation_id}
        ).mappings().first()

        if not inv_row:
            return {
                "success": False,
                "error": {"code": "INVESTIGATION_NOT_FOUND", "message": "Investigation not found."}
            }

        customer_id = inv_row["customer_id"]
        c_row = session.execute(
            text("SELECT name FROM customers WHERE customer_id = :cid"),
            {"cid": customer_id}
        ).mappings().first()
        customer_name = c_row["name"] if c_row else "Unknown"

        txn_rows = session.execute(
            text("SELECT * FROM transactions WHERE customer_id = :cid ORDER BY timestamp ASC"),
            {"cid": customer_id}
        ).mappings().all()

        df = pd.DataFrame([dict(r) for r in txn_rows])
        risk_engine = RiskEngine()
        inv_result = risk_engine.run_investigation(customer_id, customer_name, df)
        inv_result["id"] = investigation_id

        explanation = explain_investigation(inv_result, df)

        return {
            "success": True,
            "data": explanation
        }


@router.get("/{investigation_id}/evidence")
def get_investigation_evidence(investigation_id: int) -> Dict[str, Any]:
    """Retrieve all evidence records linked to this investigation."""
    evidence_items = EvidenceStore.get_evidence_for_investigation(investigation_id)
    return {
        "success": True,
        "data": {
            "investigation_id": investigation_id,
            "evidence_count": len(evidence_items),
            "evidence": evidence_items
        }
    }


@router.post("/{investigation_id}/chat")
def chat_investigation_endpoint(investigation_id: int, payload: ChatRequest) -> Dict[str, Any]:
    """Ask an evidence-grounded query regarding the ongoing investigation."""
    with get_db_session() as session:
        inv_row = session.execute(
            text("SELECT customer_id FROM investigations WHERE id = :inv_id"),
            {"inv_id": investigation_id}
        ).mappings().first()

        if not inv_row:
            return {
                "success": False,
                "error": {"code": "INVESTIGATION_NOT_FOUND", "message": "Investigation not found."}
            }

        customer_id = inv_row["customer_id"]
        c_row = session.execute(
            text("SELECT name FROM customers WHERE customer_id = :cid"),
            {"cid": customer_id}
        ).mappings().first()
        customer_name = c_row["name"] if c_row else "Unknown"

        txn_rows = session.execute(
            text("SELECT * FROM transactions WHERE customer_id = :cid ORDER BY timestamp ASC"),
            {"cid": customer_id}
        ).mappings().all()

        df = pd.DataFrame([dict(r) for r in txn_rows])
        risk_engine = RiskEngine()
        inv_result = risk_engine.run_investigation(customer_id, customer_name, df)
        inv_result["id"] = investigation_id

        answer_data = answer_investigation_query(inv_result, payload.question)

        return {
            "success": True,
            "data": answer_data
        }
