"""Investigation Report and PDF export endpoints supporting PostgreSQL & SQLite."""
from fastapi import APIRouter, Response
from typing import Dict, Any
import pandas as pd
from sqlalchemy import text

from src.database.database import get_db_session
from src.engine.risk_engine import RiskEngine
from src.ai.report_generator import explain_investigation
from src.utils.pdf_generator import generate_investigation_pdf

router = APIRouter(tags=["reports"])


@router.post("/api/investigations/{investigation_id}/report")
def generate_report(investigation_id: int) -> Dict[str, Any]:
    """Generate comprehensive structured report data for an investigation."""
    risk_engine = RiskEngine()
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
    inv_result = risk_engine.run_investigation(customer_id, customer_name, df)
    inv_result["id"] = investigation_id

    # Attach explanation
    explanation = explain_investigation(inv_result, df)

    report_data = {
        "report_id": f"REP-INV-{investigation_id:04d}",
        "customer_id": customer_id,
        "customer_name": customer_name,
        "investigation_status": inv_result["investigation_status"],
        "risk_level": inv_result["risk_level"],
        "priority_score": inv_result["priority_score"],
        "badge_text": inv_result["badge_text"],
        "summary": explanation.get("summary", inv_result["summary"]),
        "explanation": explanation,
        "baseline": inv_result["baseline"],
        "findings": inv_result["findings"],
        "correlated_events": inv_result["correlated_events"],
        "recommended_actions": explanation.get("investigator_actions", inv_result["recommended_actions"]),
        "unknowns": explanation.get("unknowns", inv_result["unknowns"]),
        "human_review_disclaimer": "Human investigator review required. RiskLens AI identifies unusual activity and provides supporting evidence. It does not determine whether fraud occurred."
    }

    return {
        "success": True,
        "data": report_data
    }


@router.get("/api/investigations/{investigation_id}/pdf")
def export_investigation_pdf(investigation_id: int):
    """Export the formal investigation report as a clean downloadable PDF."""
    with get_db_session() as session:
        inv_row = session.execute(
            text("SELECT customer_id FROM investigations WHERE id = :inv_id"),
            {"inv_id": investigation_id}
        ).mappings().first()

        if not inv_row:
            return Response(status_code=404, content="Investigation not found.")

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

    pdf_buffer = generate_investigation_pdf(inv_result)

    filename = f"RiskLens_Investigation_{customer_id}_{investigation_id}.pdf"
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
