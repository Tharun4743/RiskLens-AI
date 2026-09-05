"""Evidence Store.
Persists and retrieves traceable evidence records tying findings directly to source transactions.
Works seamlessly across PostgreSQL and SQLite via SQLAlchemy 2.0.
"""
from typing import List, Dict, Any
from sqlalchemy import text
from src.database.database import get_db_session


class EvidenceStore:
    """Manages persistent traceable evidence records."""

    @staticmethod
    def save_evidence(session, finding_id: str, evidence_items: List[Dict[str, Any]]):
        """Save evidence entries linked to a finding using an active session or connection."""
        for item in evidence_items:
            session.execute(text("""
                INSERT INTO evidence (
                    finding_id, transaction_id, evidence_type, observed_value,
                    baseline_value, deviation, explanation
                ) VALUES (
                    :finding_id, :transaction_id, :evidence_type, :observed_value,
                    :baseline_value, :deviation, :explanation
                )
            """), {
                "finding_id": finding_id,
                "transaction_id": item.get("transaction_id", "N/A"),
                "evidence_type": item.get("evidence_type", "GENERAL"),
                "observed_value": str(item.get("observed_value", "")),
                "baseline_value": str(item.get("baseline_value", "")),
                "deviation": str(item.get("deviation", "")),
                "explanation": str(item.get("explanation", ""))
            })

    @staticmethod
    def get_evidence_for_finding(finding_id: str) -> List[Dict[str, Any]]:
        """Retrieve all evidence for a finding with underlying transaction details."""
        with get_db_session() as session:
            result = session.execute(text("""
                SELECT e.id, e.finding_id, e.transaction_id, e.evidence_type,
                       e.observed_value, e.baseline_value, e.deviation, e.explanation,
                       t.timestamp, t.amount, t.payee, t.channel, t.description
                FROM evidence e
                LEFT JOIN transactions t ON e.transaction_id = t.transaction_id
                WHERE e.finding_id = :finding_id
                ORDER BY e.id ASC
            """), {"finding_id": finding_id})
            rows = result.mappings().all()

            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "finding_id": r["finding_id"],
                    "transaction_id": r["transaction_id"],
                    "evidence_type": r["evidence_type"],
                    "observed_value": r["observed_value"],
                    "baseline_value": r["baseline_value"],
                    "deviation": r["deviation"],
                    "explanation": r["explanation"],
                    "transaction_details": {
                        "transaction_id": r["transaction_id"],
                        "timestamp": r["timestamp"],
                        "amount": float(r["amount"]) if r["amount"] is not None else 0.0,
                        "payee": r["payee"],
                        "channel": r["channel"],
                        "description": r["description"]
                    } if r["transaction_id"] and r["timestamp"] else None
                })
            return results

    @staticmethod
    def get_evidence_for_investigation(investigation_id: int) -> List[Dict[str, Any]]:
        """Retrieve all evidence for an entire investigation."""
        with get_db_session() as session:
            result = session.execute(text("""
                SELECT e.id, e.finding_id, e.transaction_id, e.evidence_type,
                       e.observed_value, e.baseline_value, e.deviation, e.explanation,
                       f.rule_id, f.title as finding_title, f.severity,
                       t.timestamp, t.amount, t.payee, t.channel, t.description
                FROM evidence e
                JOIN findings f ON e.finding_id = f.finding_id
                LEFT JOIN transactions t ON e.transaction_id = t.transaction_id
                WHERE f.investigation_id = :investigation_id
                ORDER BY f.id ASC, e.id ASC
            """), {"investigation_id": investigation_id})
            rows = result.mappings().all()

            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "finding_id": r["finding_id"],
                    "finding_title": r["finding_title"],
                    "rule_id": r["rule_id"],
                    "severity": r["severity"],
                    "transaction_id": r["transaction_id"],
                    "evidence_type": r["evidence_type"],
                    "observed_value": r["observed_value"],
                    "baseline_value": r["baseline_value"],
                    "deviation": r["deviation"],
                    "explanation": r["explanation"],
                    "source": {
                        "source_table": "transactions",
                        "transaction_id": r["transaction_id"],
                        "timestamp": r["timestamp"],
                        "amount": float(r["amount"]) if r["amount"] is not None else 0.0,
                        "payee": r["payee"],
                        "channel": r["channel"],
                        "description": r["description"]
                    }
                })
            return results
