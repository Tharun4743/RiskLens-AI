"""Tests for Correlation Engine and Multi-Rule Synergy (TC06)."""
import pandas as pd
from datetime import datetime, timedelta
from src.engine.correlation import correlate_findings
from src.engine.scoring import calculate_priority_score


def test_tc06_multi_rule_correlation():
    """Verify multiple triggered rules are correlated and priority score correctly calculated."""
    findings = [
        {
            "finding_id": "F-001-01",
            "rule_id": "R001",
            "transaction_ids": ["TXN-101"]
        },
        {
            "finding_id": "F-002-01",
            "rule_id": "R002",
            "transaction_ids": ["TXN-101", "TXN-102", "TXN-103"]
        },
        {
            "finding_id": "F-003-01",
            "rule_id": "R003",
            "transaction_ids": ["TXN-101"]
        }
    ]

    base_time = datetime(2026, 6, 18, 2, 14, 0)
    txns = [
        {"transaction_id": "TXN-101", "timestamp": base_time.strftime("%Y-%m-%d %H:%M:%S"), "amount": 480000.0, "payee": "XYZ Services", "channel": "NEFT", "description": "Settlement"},
        {"transaction_id": "TXN-102", "timestamp": (base_time + timedelta(minutes=12)).strftime("%Y-%m-%d %H:%M:%S"), "amount": 60000.0, "payee": "XYZ Services", "channel": "NEFT", "description": "Tranche 1"},
        {"transaction_id": "TXN-103", "timestamp": (base_time + timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M:%S"), "amount": 70000.0, "payee": "XYZ Services", "channel": "NEFT", "description": "Tranche 2"}
    ]
    df = pd.DataFrame(txns)

    events = correlate_findings(findings, df)
    assert len(events) >= 1
    primary_event = events[0]
    assert "XYZ Services" in primary_event["payees"]
    assert len(primary_event["transaction_ids"]) == 3
    assert set(primary_event["rules_involved"]) == {"R001", "R002", "R003"}

    # Test scoring with multi-rule synergy
    score_res = calculate_priority_score(["R001", "R002", "R003"])
    assert score_res["priority_score"] >= 75
    assert score_res["risk_level"] == "HIGH"
    assert score_res["badge_text"] == "High Attention Required"
