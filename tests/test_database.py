"""Tests for database layer, schema constraints, connection pooling, and Supabase integration."""
from sqlalchemy import select, func
from dotenv import load_dotenv
load_dotenv()
from src.database.database import get_db_session, init_db, check_db_connection
from src.database.models import CustomerDB, TransactionDB
from src.database.supabase_client import get_supabase_client


def test_database_connection_and_schema():
    """Verify database connection and schema initialization."""
    conn_info = check_db_connection()
    assert conn_info["status"] == "connected"
    assert "dialect" in conn_info

    # Run schema verification
    init_db()


def test_customer_and_transaction_orm_persistence():
    """Verify ORM model persistence, relationships, and queries."""
    with get_db_session() as session:
        # Check that demo customers exist
        cust_count = session.scalar(select(func.count()).select_from(CustomerDB))
        assert cust_count >= 5

        # Query CUST-001
        c1 = session.scalar(select(CustomerDB).where(CustomerDB.customer_id == "CUST-001"))
        assert c1 is not None
        assert c1.name == "Priya Sharma"

        # Check transactions for CUST-001
        txns = session.scalars(select(TransactionDB).where(TransactionDB.customer_id == "CUST-001")).all()
        assert len(txns) > 100
        for t in txns[:5]:
            assert t.amount > 0
            assert len(t.payee) > 0
            assert len(t.channel) > 0


def test_foreign_key_and_cascading():
    """Verify customer foreign key relationship with transactions."""
    with get_db_session() as session:
        # Query CUST-005 complex scenario
        c5 = session.scalar(select(CustomerDB).where(CustomerDB.customer_id == "CUST-005"))
        assert c5 is not None

        c5_txns = session.scalars(select(TransactionDB).where(TransactionDB.customer_id == "CUST-005")).all()
        assert len(c5_txns) > 100


def test_supabase_client_initialization():
    """Verify Supabase client initializes cleanly with provided credentials."""
    client = get_supabase_client()
    assert client is not None
