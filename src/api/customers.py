"""Customer API endpoints supporting PostgreSQL and SQLite via SQLAlchemy 2.0."""
from fastapi import APIRouter
from typing import Dict, Any
from sqlalchemy import text
from src.database.database import get_db_session

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
def list_customers() -> Dict[str, Any]:
    """Retrieve all available customers with aggregate statistics."""
    with get_db_session() as session:
        result = session.execute(text("""
            SELECT c.id, c.customer_id, c.name, c.profile, c.expected_result, c.created_at,
                   COUNT(t.id) as transaction_count,
                   COALESCE(SUM(t.amount), 0) as total_volume
            FROM customers c
            LEFT JOIN transactions t ON c.customer_id = t.customer_id
            GROUP BY c.id, c.customer_id, c.name, c.profile, c.expected_result, c.created_at
            ORDER BY c.customer_id ASC
        """))
        rows = result.mappings().all()

        customers = []
        for r in rows:
            customers.append({
                "id": r["id"],
                "customer_id": r["customer_id"],
                "name": r["name"],
                "profile": r["profile"],
                "expected_result": r["expected_result"],
                "created_at": r["created_at"],
                "transaction_count": r["transaction_count"],
                "total_volume": round(float(r["total_volume"]), 2)
            })

        return {
            "success": True,
            "data": customers
        }


@router.get("/{customer_id}")
def get_customer(customer_id: str) -> Dict[str, Any]:
    """Retrieve a single customer profile by ID."""
    with get_db_session() as session:
        cust_res = session.execute(
            text("SELECT id, customer_id, name, profile, expected_result, created_at FROM customers WHERE customer_id = :customer_id"),
            {"customer_id": customer_id}
        )
        row = cust_res.mappings().first()

        if not row:
            return {
                "success": False,
                "error": {
                    "code": "CUSTOMER_NOT_FOUND",
                    "message": f"Customer with ID '{customer_id}' does not exist."
                }
            }

        stats_res = session.execute(
            text("SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM transactions WHERE customer_id = :customer_id"),
            {"customer_id": customer_id}
        )
        t_info = stats_res.mappings().first()

        return {
            "success": True,
            "data": {
                "id": row["id"],
                "customer_id": row["customer_id"],
                "name": row["name"],
                "profile": row["profile"],
                "expected_result": row["expected_result"],
                "created_at": row["created_at"],
                "transaction_count": t_info["count"] if t_info else 0,
                "total_volume": round(float(t_info["total"]), 2) if t_info else 0.0
            }
        }

