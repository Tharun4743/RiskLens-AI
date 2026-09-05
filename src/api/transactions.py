"""Transaction API endpoints and CSV Upload with SQLAlchemy 2.0 PostgreSQL & SQLite support."""
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, Query
from sqlalchemy import text
from src.database.database import get_db_session
from src.utils.validation import validate_and_parse_csv, ValidationError

router = APIRouter(tags=["transactions"])


@router.get("/api/transactions")
def list_transactions(
    customer_id: Optional[str] = None,
    channel: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = Query("timestamp", pattern="^(timestamp|amount|payee|transaction_id)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(100, ge=1, le=5000),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """Retrieve transactions across all or specific customers with filtering, sorting and pagination."""
    with get_db_session() as session:
        where_clauses = ["1=1"]
        params: Dict[str, Any] = {}

        if customer_id:
            where_clauses.append("customer_id = :customer_id")
            params["customer_id"] = customer_id.strip()

        if channel:
            where_clauses.append("UPPER(channel) = :channel")
            params["channel"] = channel.upper()

        if min_amount is not None:
            where_clauses.append("amount >= :min_amount")
            params["min_amount"] = min_amount

        if max_amount is not None:
            where_clauses.append("amount <= :max_amount")
            params["max_amount"] = max_amount

        if search:
            where_clauses.append("(LOWER(payee) LIKE :search OR LOWER(description) LIKE :search OR LOWER(transaction_id) LIKE :search)")
            params["search"] = f"%{search.lower()}%"

        where_str = " AND ".join(where_clauses)

        # Count total matching
        count_res = session.execute(
            text(f"SELECT COUNT(*) as cnt FROM transactions WHERE {where_str}"),
            params
        )
        total_count = count_res.scalar() or 0

        # Query data with sorting and paging
        params["limit"] = limit
        params["offset"] = offset
        query_sql = f"""
            SELECT id, transaction_id, customer_id, timestamp, description, payee, amount, channel, created_at
            FROM transactions
            WHERE {where_str}
            ORDER BY {sort_by} {sort_order.upper()}
            LIMIT :limit OFFSET :offset
        """
        rows = session.execute(text(query_sql), params).mappings().all()

        txns = []
        for r in rows:
            txns.append({
                "id": r["id"],
                "transaction_id": r["transaction_id"],
                "customer_id": r["customer_id"],
                "timestamp": r["timestamp"],
                "description": r["description"],
                "payee": r["payee"],
                "amount": float(r["amount"]),
                "channel": r["channel"],
                "created_at": r["created_at"]
            })

        return {
            "success": True,
            "data": {
                "transactions": txns,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
        }


@router.get("/api/transactions/{transaction_id}")
def get_transaction(transaction_id: str) -> Dict[str, Any]:
    """Retrieve a single transaction by ID."""
    with get_db_session() as session:
        t_row = session.execute(
            text("SELECT id, transaction_id, customer_id, timestamp, description, payee, amount, channel, created_at FROM transactions WHERE transaction_id = :tid"),
            {"tid": transaction_id.strip()}
        ).mappings().first()

        if not t_row:
            return {
                "success": False,
                "error": {
                    "code": "TRANSACTION_NOT_FOUND",
                    "message": f"Transaction with ID '{transaction_id}' not found."
                }
            }

        return {
            "success": True,
            "data": {
                "id": t_row["id"],
                "transaction_id": t_row["transaction_id"],
                "customer_id": t_row["customer_id"],
                "timestamp": t_row["timestamp"],
                "description": t_row["description"],
                "payee": t_row["payee"],
                "amount": float(t_row["amount"]),
                "channel": t_row["channel"],
                "created_at": t_row["created_at"]
            }
        }


@router.get("/api/customers/{customer_id}/transactions")
def get_customer_transactions(
    customer_id: str,
    channel: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: str = Query("timestamp", pattern="^(timestamp|amount|payee|transaction_id)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = 500,
    offset: int = 0
) -> Dict[str, Any]:
    """Retrieve transactions for a specific customer with filtering and sorting."""
    with get_db_session() as session:
        where_clauses = ["customer_id = :customer_id"]
        params: Dict[str, Any] = {"customer_id": customer_id}

        if channel:
            where_clauses.append("UPPER(channel) = :channel")
            params["channel"] = channel.upper()

        if min_amount is not None:
            where_clauses.append("amount >= :min_amount")
            params["min_amount"] = min_amount

        if max_amount is not None:
            where_clauses.append("amount <= :max_amount")
            params["max_amount"] = max_amount

        if search:
            where_clauses.append("(payee ILIKE :search OR description ILIKE :search OR transaction_id ILIKE :search)")
            # SQLite does not support ILIKE natively unless like is used, but for standard compatibility:
            # We can use LOWER(...) LIKE :search
            where_clauses.pop()
            where_clauses.append("(LOWER(payee) LIKE :search OR LOWER(description) LIKE :search OR LOWER(transaction_id) LIKE :search)")
            params["search"] = f"%{search.lower()}%"

        where_str = " AND ".join(where_clauses)

        # Count total matching
        count_res = session.execute(
            text(f"SELECT COUNT(*) as cnt FROM transactions WHERE {where_str}"),
            params
        )
        total_count = count_res.scalar() or 0

        # Query data with sorting and paging
        params["limit"] = limit
        params["offset"] = offset
        query_sql = f"""
            SELECT id, transaction_id, customer_id, timestamp, description, payee, amount, channel, created_at
            FROM transactions
            WHERE {where_str}
            ORDER BY {sort_by} {sort_order.upper()}
            LIMIT :limit OFFSET :offset
        """
        rows = session.execute(text(query_sql), params).mappings().all()

        txns = []
        for r in rows:
            txns.append({
                "id": r["id"],
                "transaction_id": r["transaction_id"],
                "customer_id": r["customer_id"],
                "timestamp": r["timestamp"],
                "description": r["description"],
                "payee": r["payee"],
                "amount": float(r["amount"]),
                "channel": r["channel"],
                "created_at": r["created_at"]
            })

        return {
            "success": True,
            "data": {
                "transactions": txns,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
        }


@router.post("/api/upload")
async def upload_transactions_csv(
    file: UploadFile = File(...),
    customer_id: Optional[str] = Form(None),
    customer_name: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Validate and ingest customer transaction CSV file.
    Rejects missing columns, invalid amounts, negative amounts, duplicate IDs, empty payees.
    Persists data in-memory directly to PostgreSQL without writing local files.
    """
    if not file.filename.lower().endswith(".csv"):
        return {
            "success": False,
            "error": {
                "code": "INVALID_FILE_TYPE",
                "message": "Only CSV files are supported for transaction history upload."
            }
        }

    try:
        content = await file.read()
        cleaned_df, metadata = validate_and_parse_csv(content)
    except ValidationError as ve:
        return {
            "success": False,
            "error": {
                "code": ve.code,
                "message": ve.message
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "UPLOAD_PARSE_FAILED",
                "message": f"Failed to process transaction file: {str(e)}"
            }
        }

    # Generate customer ID if not provided
    cid = customer_id.strip() if customer_id else f"CUST-UP-{int(datetime.utcnow().timestamp()) % 10000:04d}"
    cname = customer_name.strip() if customer_name else f"Uploaded Profile ({cid})"
    now_str = datetime.utcnow().isoformat()

    try:
        with get_db_session() as session:
            # Check or create customer
            cust = session.scalar(
                text("SELECT id FROM customers WHERE customer_id = :cid"),
                {"cid": cid}
            )
            if not cust:
                session.execute(
                    text("INSERT INTO customers (customer_id, name, created_at) VALUES (:cid, :cname, :created_at)"),
                    {"cid": cid, "cname": cname, "created_at": now_str}
                )
            else:
                session.execute(
                    text("UPDATE customers SET name = :cname WHERE customer_id = :cid"),
                    {"cid": cid, "cname": cname}
                )

            # Insert transactions
            inserted_count = 0
            for _, row in cleaned_df.iterrows():
                # Check if transaction exists
                t_exists = session.scalar(
                    text("SELECT id FROM transactions WHERE transaction_id = :tid"),
                    {"tid": row["transaction_id"]}
                )
                if not t_exists:
                    session.execute(text("""
                        INSERT INTO transactions (
                            transaction_id, customer_id, timestamp, description, payee, amount, channel, created_at
                        ) VALUES (
                            :tid, :cid, :timestamp, :description, :payee, :amount, :channel, :created_at
                        )
                    """), {
                        "tid": row["transaction_id"],
                        "cid": cid,
                        "timestamp": row["timestamp"],
                        "description": row["description"],
                        "payee": row["payee"],
                        "amount": float(row["amount"]),
                        "channel": row["channel"],
                        "created_at": now_str
                    })
                    inserted_count += 1
                else:
                    session.execute(text("""
                        UPDATE transactions SET
                            customer_id = :cid, timestamp = :timestamp, description = :description,
                            payee = :payee, amount = :amount, channel = :channel
                        WHERE transaction_id = :tid
                    """), {
                        "tid": row["transaction_id"],
                        "cid": cid,
                        "timestamp": row["timestamp"],
                        "description": row["description"],
                        "payee": row["payee"],
                        "amount": float(row["amount"]),
                        "channel": row["channel"]
                    })
                    inserted_count += 1

        return {
            "success": True,
            "data": {
                "customer_id": cid,
                "customer_name": cname,
                "transactions_count": inserted_count,
                "months_covered": metadata["months_covered"],
                "channels_detected": metadata["channels_count"],
                "payees_detected": metadata["payees_count"],
                "date_range": metadata["date_range"],
                "message": f"Successfully ingested {inserted_count} transactions across {metadata['months_covered']} months."
            }
        }
    except Exception as db_err:
        return {
            "success": False,
            "error": {
                "code": "DATABASE_INSERTION_ERROR",
                "message": f"Failed to persist validated transactions to database: {str(db_err)}"
            }
        }
