"""Tests for deterministic risk rules R001 to R004."""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.engine.baseline import calculate_baseline
from src.engine.rules import (
    evaluate_r001_large_transfer,
    evaluate_r002_new_payee_burst,
    evaluate_r003_odd_hours,
    evaluate_r004_behavioural_break
)


@pytest.fixture
def normal_dataset():
    """Generates 50 normal transactions."""
    rows = []
    base_time = datetime(2026, 1, 1, 10, 0, 0)
    for i in range(50):
        t = base_time + timedelta(days=i, hours=2)
        rows.append({
            "transaction_id": f"TXN-{1000+i}",
            "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
            "payee": "Fresh Mart" if i % 2 == 0 else "Swiggy Orders",
            "amount": 1500.0 + (i % 5) * 200.0,
            "channel": "UPI" if i % 2 == 0 else "CARD",
            "description": "Standard expense"
        })
    return pd.DataFrame(rows)


def test_tc01_normal_customer_no_findings(normal_dataset):
    """TC01 & TC07: Normal customer with no anomalies triggers zero rules."""
    baseline = calculate_baseline(normal_dataset)
    r1 = evaluate_r001_large_transfer(normal_dataset, baseline)
    r2 = evaluate_r002_new_payee_burst(normal_dataset, baseline)
    r3 = evaluate_r003_odd_hours(normal_dataset, baseline)
    r4 = evaluate_r004_behavioural_break(normal_dataset, baseline)

    assert r1["status"] == "NOT_TRIGGERED"
    assert r2["status"] == "NOT_TRIGGERED"
    assert r3["status"] == "NOT_TRIGGERED"
    assert r4["status"] == "NOT_TRIGGERED"
    assert len(r1["findings"]) == 0


def test_tc02_large_transfer(normal_dataset):
    """TC02: R001 triggers on unusually large transfer."""
    baseline = calculate_baseline(normal_dataset)
    df = normal_dataset.copy()
    # Add large transfer
    df = pd.concat([df, pd.DataFrame([{
        "transaction_id": "TXN-LARGE",
        "timestamp": "2026-03-01 14:00:00",
        "payee": "Apex Ventures",
        "amount": 480000.0,
        "channel": "NEFT",
        "description": "Property Purchase"
    }])], ignore_index=True)

    r1 = evaluate_r001_large_transfer(df, baseline)
    assert r1["status"] == "TRIGGERED"
    assert len(r1["findings"]) == 1
    f = r1["findings"][0]
    assert f["rule_id"] == "R001"
    assert "TXN-LARGE" in f["transaction_ids"]
    assert f["multiplier"] > 50


def test_tc03_new_payee_burst(normal_dataset):
    """TC03: R002 triggers on new payee rapid burst."""
    baseline = calculate_baseline(normal_dataset)
    df = normal_dataset.copy()
    # Add rapid burst to newly seen payee
    burst_time = datetime(2026, 3, 15, 11, 0, 0)
    burst_txns = [
        {"transaction_id": f"TXN-BURST-{i}", "timestamp": (burst_time + timedelta(minutes=i*10)).strftime("%Y-%m-%d %H:%M:%S"),
         "payee": "XYZ Services", "amount": 50000.0, "channel": "IMPS", "description": "Rapid Burst"}
        for i in range(4)
    ]
    df = pd.concat([df, pd.DataFrame(burst_txns)], ignore_index=True)

    r2 = evaluate_r002_new_payee_burst(df, baseline)
    assert r2["status"] == "TRIGGERED"
    f = r2["findings"][0]
    assert f["rule_id"] == "R002"
    assert f["payee"] == "XYZ Services"
    assert len(f["transaction_ids"]) == 4


def test_tc04_odd_hours_transaction(normal_dataset):
    """TC04: R003 triggers on unexpected late-night transaction."""
    baseline = calculate_baseline(normal_dataset)
    df = normal_dataset.copy()
    # Add transactions at 02:14 and 03:20
    odd_txns = [
        {"transaction_id": "TXN-ODD-1", "timestamp": "2026-03-16 02:14:00", "payee": "FastPay Card", "amount": 15000.0, "channel": "NETBANKING", "description": "Wallet Load"},
        {"transaction_id": "TXN-ODD-2", "timestamp": "2026-03-16 03:20:00", "payee": "FastPay Card", "amount": 18000.0, "channel": "NETBANKING", "description": "Wallet Load"}
    ]
    df = pd.concat([df, pd.DataFrame(odd_txns)], ignore_index=True)

    r3 = evaluate_r003_odd_hours(df, baseline)
    assert r3["status"] == "TRIGGERED"
    f = r3["findings"][0]
    assert f["rule_id"] == "R003"
    assert "TXN-ODD-1" in f["transaction_ids"]


def test_tc05_behaviour_break(normal_dataset):
    """TC05: R004 triggers on channel shift."""
    baseline = calculate_baseline(normal_dataset)
    df = normal_dataset.copy()
    # Normal dataset is primarily UPI and CARD.
    # Add recent surge of NEFT transactions in last 5 days
    recent_time = datetime(2026, 3, 20, 10, 0, 0)
    neft_txns = [
        {"transaction_id": f"TXN-NEFT-{i}", "timestamp": (recent_time + timedelta(hours=i*4)).strftime("%Y-%m-%d %H:%M:%S"),
         "payee": f"Vendor {i}", "amount": 80000.0, "channel": "NEFT", "description": "Commercial Equipment"}
        for i in range(5)
    ]
    df = pd.concat([df, pd.DataFrame(neft_txns)], ignore_index=True)

    r4 = evaluate_r004_behavioural_break(df, baseline)
    assert r4["status"] == "TRIGGERED"
    f = r4["findings"][0]
    assert f["rule_id"] == "R004"
    assert f["primary_divergent_channel"] == "NEFT"
