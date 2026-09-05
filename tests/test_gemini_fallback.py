"""Tests for Gemini Fallback and Hallucination Validation (TC12, TC13, TC14, TC15)."""
import pytest
import pandas as pd
from src.ai.gemini_client import GeminiClient
from src.ai.schemas import InvestigationExplanation, KeyFindingExplanation, InvestigatorAction
from src.ai.report_generator import (
    validate_ai_explanation,
    explain_investigation
)


@pytest.fixture
def sample_investigation_result():
    return {
        "customer_id": "CUST-002",
        "customer_name": "Arjun Patel",
        "investigation_status": "ATTENTION_REQUIRED",
        "risk_level": "HIGH",
        "priority_score": 85,
        "badge_text": "High Attention Required",
        "summary": "Large transfer detected.",
        "baseline": {
            "is_reliable": True,
            "transaction_count": 120,
            "median_amount": 3250.0,
            "percentiles": {"p95": 12000.0},
            "typical_hours": {"display": "08:00–21:00"},
            "known_payees_count": 25,
            "channel_distribution_count_pct": {"UPI": 60, "CARD": 40},
            "odd_hours": {"ratio": 0.0}
        },
        "findings": [
            {
                "finding_id": "F-001-01",
                "rule_id": "R001",
                "severity": "HIGH",
                "title": "Unusually Large Transfer of ₹4,80,000",
                "description": "Transaction TXN-182 exceeds median by 147.7x.",
                "transaction_ids": ["TXN-182"],
                "evidence": [{
                    "transaction_id": "TXN-182",
                    "observed_value": "₹4,80,000",
                    "baseline_value": "₹3,250",
                    "deviation": "147.7x customer median",
                    "explanation": "Material surge."
                }]
            }
        ],
        "correlated_events": [],
        "scoring": {
            "priority_score": 85,
            "risk_level": "HIGH",
            "investigation_status": "ATTENTION_REQUIRED",
            "badge_text": "High Attention Required"
        },
        "recommended_actions": ["Review source of funds for TXN-182."],
        "unknowns": ["Commercial justification is unavailable."]
    }


@pytest.fixture
def valid_txns_df():
    return pd.DataFrame([
        {"transaction_id": "TXN-182", "amount": 480000.0, "payee": "Apex Ventures", "channel": "NEFT"}
    ])


def test_tc12_gemini_unavailable_fallback(sample_investigation_result, valid_txns_df):
    """TC12: When Gemini key is missing, fallback cleanly produces verified deterministic output."""
    dummy_client = GeminiClient(api_key="")
    assert not dummy_client.is_available()

    result = explain_investigation(sample_investigation_result, valid_txns_df, gemini_client=dummy_client)

    assert result["is_deterministic_fallback"] is True
    assert "Deterministic investigation findings remain available" in result["fallback_notice"]
    assert len(result["key_findings"]) == 1
    assert result["key_findings"][0]["finding_id"] == "F-001-01"
    assert "TXN-182" in result["key_findings"][0]["transaction_ids"]
    assert result["priority"] == "HIGH"


def test_tc13_gemini_malformed_response(sample_investigation_result, valid_txns_df, monkeypatch):
    """TC13: Malformed AI output triggers graceful fallback without crashing."""
    client = GeminiClient(api_key="test_key")
    # Mock client generate_explanation to return invalid JSON
    monkeypatch.setattr(client, "is_available", lambda: True)
    monkeypatch.setattr(client, "generate_explanation", lambda *args, **kwargs: "MALFORMED_NON_JSON_OUTPUT")

    result = explain_investigation(sample_investigation_result, valid_txns_df, gemini_client=client)
    assert result["is_deterministic_fallback"] is True
    assert result["priority"] == "HIGH"


def test_tc14_gemini_invents_transaction_rejected(sample_investigation_result, valid_txns_df):
    """TC14: Hallucination validator rejects AI response referencing non-existent transaction IDs."""
    fake_ai_output = InvestigationExplanation(
        summary="Customer conducted unauthorized activity on TXN-999999.",
        attention_required=True,
        priority="HIGH",
        key_findings=[
            KeyFindingExplanation(
                finding_id="F-001-01",
                rule_id="R001",
                transaction_ids=["TXN-999999"],  # Invented!
                explanation="Transaction TXN-999999 for ₹9999999 is abnormal."
            )
        ],
        investigator_actions=[
            InvestigatorAction(priority_level="HIGH", action_text="Check TXN-999999", target_reference="TXN-999999")
        ],
        unknowns=["Origin unknown"]
    )

    is_valid, reason = validate_ai_explanation(
        fake_ai_output,
        valid_txns_df,
        sample_investigation_result["findings"]
    )

    assert is_valid is False
    assert "Hallucinated transaction ID" in reason
    assert "TXN-999999" in reason


def test_tc15_evidence_references_valid_transaction(sample_investigation_result, valid_txns_df):
    """TC15: Valid AI claims referencing real transactions pass validation."""
    valid_ai_output = InvestigationExplanation(
        summary="Transaction TXN-182 deviates significantly from established baseline.",
        attention_required=True,
        priority="HIGH",
        key_findings=[
            KeyFindingExplanation(
                finding_id="F-001-01",
                rule_id="R001",
                transaction_ids=["TXN-182"],
                explanation="Transaction TXN-182 exceeds customer median."
            )
        ],
        investigator_actions=[
            InvestigatorAction(priority_level="HIGH", action_text="Verify TXN-182", target_reference="TXN-182")
        ],
        unknowns=["Underlying commercial invoice"]
    )

    is_valid, reason = validate_ai_explanation(
        valid_ai_output,
        valid_txns_df,
        sample_investigation_result["findings"]
    )

    assert is_valid is True
    assert reason is None
