"""Evidence Citation and Source Traceability Utility.
Verifies citation integrity and builds structured citation breadcrumbs.
"""
from typing import Dict, List, Any


def build_evidence_packet(
    customer_id: str,
    customer_name: str,
    baseline: Dict[str, Any],
    findings: List[Dict[str, Any]],
    correlated_events: List[Dict[str, Any]],
    scoring: Dict[str, Any],
    unknowns: List[str]
) -> Dict[str, Any]:
    """
    Build a minimal, clean, structured evidence packet to feed into Gemini.
    Guarantees no extraneous raw noise is passed to the AI layer.
    """
    # Clean baseline for AI context
    clean_baseline = {
        "transaction_count": baseline.get("transaction_count", 0),
        "median_amount": baseline.get("median_amount", 0.0),
        "mean_amount": baseline.get("mean_amount", 0.0),
        "percentile_95": baseline.get("percentiles", {}).get("p95", 0.0),
        "typical_hours": baseline.get("typical_hours", {}).get("display", "08:00–22:00"),
        "known_payees_count": baseline.get("known_payees_count", 0),
        "channel_distribution": baseline.get("channel_distribution_count_pct", {}),
        "odd_hours_historical_rate": baseline.get("odd_hours", {}).get("ratio", 0.0)
    }

    # Clean findings
    clean_findings = []
    for f in findings:
        clean_findings.append({
            "finding_id": f["finding_id"],
            "rule_id": f["rule_id"],
            "title": f["title"],
            "severity": f["severity"],
            "transaction_ids": f.get("transaction_ids", []),
            "evidence": [
                {
                    "transaction_id": e.get("transaction_id"),
                    "observed": e.get("observed_value"),
                    "baseline": e.get("baseline_value"),
                    "deviation": e.get("deviation")
                }
                for e in f.get("evidence", [])
            ]
        })

    # Clean correlated clusters
    clean_events = []
    for evt in correlated_events:
        clean_events.append({
            "event_id": evt["event_id"],
            "transaction_ids": evt["transaction_ids"],
            "total_amount": evt["formatted_amount"],
            "payees": evt["payees"],
            "channels": evt["channels"],
            "duration_minutes": evt["time_window"]["duration_minutes"],
            "summary": evt["summary"]
        })

    return {
        "customer": {
            "customer_id": customer_id,
            "name": customer_name
        },
        "baseline": clean_baseline,
        "investigation_status": scoring.get("investigation_status", "ATTENTION_REQUIRED"),
        "priority_score": scoring.get("priority_score", 0),
        "triggered_rules": [f["rule_id"] for f in findings],
        "findings": clean_findings,
        "correlated_events": clean_events,
        "unknowns": unknowns
    }
