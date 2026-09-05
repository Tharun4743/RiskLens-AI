"""Tests for customer behavioral baseline engine."""
import pytest
import pandas as pd
from src.engine.baseline import calculate_baseline


def test_baseline_calculation_basic():
    """Verify median, percentiles, normal hours, known payees, channel breakdown."""
    rows = []
    # 30 transactions
    for i in range(30):
        rows.append({
            "transaction_id": f"TXN-{100+i}",
            "timestamp": f"2026-02-{(i%28)+1:02d} 11:30:00",
            "payee": "Merchant A" if i % 2 == 0 else "Merchant B",
            "amount": 1000.0 + (i * 100.0),
            "channel": "UPI" if i % 2 == 0 else "CARD"
        })
    df = pd.DataFrame(rows)
    baseline = calculate_baseline(df)

    assert baseline["is_reliable"] is True
    assert baseline["transaction_count"] == 30
    assert baseline["median_amount"] == pytest.approx(2450.0, 1.0)
    assert baseline["percentiles"]["p95"] > baseline["median_amount"]
    assert "UPI" in baseline["channel_distribution_count_pct"]
    assert "Merchant A" in baseline["known_payees"]
    assert baseline["odd_hours"]["count"] == 0


def test_insufficient_baseline():
    """Verify that insufficient history returns is_reliable=False."""
    df = pd.DataFrame([
        {"transaction_id": "TXN-1", "timestamp": "2026-01-01 10:00:00", "amount": 100.0, "payee": "Shop", "channel": "UPI"}
    ])
    baseline = calculate_baseline(df)
    assert baseline["is_reliable"] is False
    assert "Insufficient" in baseline["reason"]
