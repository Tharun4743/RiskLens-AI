"""Tests for FastAPI HTTP Endpoints."""
import pytest
from fastapi.testclient import TestClient
from app import app
from src.database.seed_data import seed_database_if_empty

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    """Ensure database has demo seed data."""
    seed_database_if_empty()


def test_api_health():
    """Verify health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_api_customers_list():
    """Verify customer list returns 5 seeded customers."""
    response = client.get("/api/customers")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    customers = data["data"]
    assert len(customers) >= 5
    cust_ids = [c["customer_id"] for c in customers]
    assert "CUST-001" in cust_ids
    assert "CUST-005" in cust_ids


def test_api_customer_transactions():
    """Verify transaction querying and filtering."""
    response = client.get("/api/customers/CUST-001/transactions?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    txns = data["data"]["transactions"]
    assert len(txns) <= 10
    assert len(txns) > 0


def test_api_investigation_lifecycle():
    """Verify end-to-end investigation creation, retrieval, explanation, and PDF."""
    # 1. Create investigation for CUST-005
    create_resp = client.post("/api/investigations", json={"customer_id": "CUST-005"})
    assert create_resp.status_code == 200
    inv_data = create_resp.json()
    assert inv_data["success"] is True
    inv_id = inv_data["data"]["id"]
    assert inv_data["data"]["badge_text"] == "High Attention Required"
    assert len(inv_data["data"]["findings"]) >= 3

    # 2. Get investigation
    get_resp = client.get(f"/api/investigations/{inv_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["customer_id"] == "CUST-005"

    # 3. Explain investigation (fallback mode if key missing)
    explain_resp = client.post(f"/api/investigations/{inv_id}/explain")
    assert explain_resp.status_code == 200
    exp_data = explain_resp.json()
    assert exp_data["success"] is True
    assert "summary" in exp_data["data"]
    assert "key_findings" in exp_data["data"]

    # 4. Get evidence
    ev_resp = client.get(f"/api/investigations/{inv_id}/evidence")
    assert ev_resp.status_code == 200
    ev_data = ev_resp.json()
    assert ev_data["data"]["evidence_count"] > 0

    # 5. Export PDF
    pdf_resp = client.get(f"/api/investigations/{inv_id}/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000  # Non-trivial PDF binary content


def test_api_customer_details_and_not_found():
    """Verify customer details lookup and clean not-found error handling."""
    # Valid customer
    resp = client.get("/api/customers/CUST-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["customer_id"] == "CUST-001"
    assert data["data"]["name"] == "Priya Sharma"
    assert data["data"]["transaction_count"] > 0

    # Invalid customer (should return clean error, not 500)
    resp_invalid = client.get("/api/customers/CUST-DOES-NOT-EXIST")
    assert resp_invalid.status_code == 200
    inv_data = resp_invalid.json()
    assert inv_data["success"] is False
    assert inv_data["error"]["code"] == "CUSTOMER_NOT_FOUND"


def test_api_global_transactions_and_lookup():
    """Verify /api/transactions filtering, pagination, and single transaction lookup."""
    # 1. Global list
    resp = client.get("/api/transactions?limit=20")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert len(data["data"]["transactions"]) <= 20
    assert data["data"]["total_count"] >= 1000

    sample_txn = data["data"]["transactions"][0]
    sample_tid = sample_txn["transaction_id"]

    # 2. Lookup single transaction
    resp_single = client.get(f"/api/transactions/{sample_tid}")
    assert resp_single.status_code == 200
    s_data = resp_single.json()
    assert s_data["success"] is True
    assert s_data["data"]["transaction_id"] == sample_tid
    assert s_data["data"]["amount"] > 0
    assert len(s_data["data"]["channel"]) > 0

    # 3. Lookup invalid transaction ID
    resp_fake = client.get("/api/transactions/TXN-NON-EXISTENT-999")
    assert resp_fake.status_code == 200
    fake_data = resp_fake.json()
    assert fake_data["success"] is False
    assert fake_data["error"]["code"] == "TRANSACTION_NOT_FOUND"

    # 4. Filter by channel and amount
    resp_filter = client.get("/api/transactions?channel=UPI&min_amount=100&max_amount=5000&limit=10")
    assert resp_filter.status_code == 200
    f_data = resp_filter.json()
    assert f_data["success"] is True
    for t in f_data["data"]["transactions"]:
        assert t["channel"].upper() == "UPI"
        assert 100 <= t["amount"] <= 5000


def test_api_csv_upload_workflow():
    """Verify CSV upload ingestion and invalid CSV rejection."""
    valid_csv_content = (
        "transaction_id,date,description,payee,amount,channel\n"
        "TXN-UP-TEST-1,2026-02-01 10:00:00,Consulting Fee,Acme Corp,75000,NEFT\n"
        "TXN-UP-TEST-2,2026-02-02 11:30:00,Office Supplies,Stationery World,3200,CARD\n"
    )

    resp = client.post(
        "/api/upload",
        files={"file": ("upload.csv", valid_csv_content.encode("utf-8"), "text/csv")},
        data={"customer_id": "CUST-TEST-UPLOAD", "customer_name": "Test Upload Profile"}
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["success"] is True
    assert res_data["data"]["transactions_count"] == 2
    assert res_data["data"]["customer_id"] == "CUST-TEST-UPLOAD"

    # Ingested transactions should now be queryable
    t_resp = client.get("/api/customers/CUST-TEST-UPLOAD/transactions")
    assert t_resp.status_code == 200
    assert t_resp.json()["data"]["total_count"] == 2


def test_api_sql_injection_resilience():
    """Verify parameterized queries prevent SQL injection."""
    malicious_inputs = [
        "' OR '1'='1",
        "'; DROP TABLE transactions; --",
        "1 UNION SELECT * FROM customers --",
        "<script>alert(1)</script>"
    ]
    for injection in malicious_inputs:
        resp = client.get(f"/api/transactions?search={injection}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert isinstance(data["data"]["transactions"], list)

