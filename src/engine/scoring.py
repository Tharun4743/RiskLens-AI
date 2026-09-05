"""Investigation Priority Scoring Engine.
Calculates investigation-priority score (0-100).
CRITICAL: This is strictly an INVESTIGATION PRIORITY score, NOT a fraud probability.
Never describe the score as fraud probability or fraud percentage.
"""
from typing import List, Dict, Any

RULE_WEIGHTS = {
    "R001": 30,  # Unusually Large Transfer
    "R002": 30,  # New Payee Burst
    "R003": 15,  # Odd-Hours Activity
    "R004": 25   # Behavioural Pattern Break
}


def calculate_priority_score(triggered_rule_ids: List[str]) -> Dict[str, Any]:
    """
    Calculate the investigation priority score based on triggered rules.
    Categories:
      0–19    Normal
      20–49   Low Attention
      50–74   Moderate Attention
      75–100  High Attention
    """
    score = 0
    breakdown = []
    unique_rules = sorted(list(set(triggered_rule_ids)))

    for rid in unique_rules:
        pts = RULE_WEIGHTS.get(rid, 10)
        score += pts
        breakdown.append({
            "rule_id": rid,
            "points": pts,
            "rule_name": {
                "R001": "Unusually Large Transfer",
                "R002": "New Payee Burst",
                "R003": "Odd-Hours Activity",
                "R004": "Behavioural Pattern Break"
            }.get(rid, rid)
        })

    # Multi-rule synergy: if multiple high-impact rules triggered together, add correlation weight
    if len(unique_rules) >= 3:
        # Boost investigation priority for compounding anomalies
        extra_pts = min(15, (len(unique_rules) - 2) * 8)
        score += extra_pts
        breakdown.append({
            "rule_id": "COMPOUNDING_SYNERGY",
            "points": extra_pts,
            "rule_name": "Multi-Rule Compounding Anomaly Synergy"
        })

    score = min(100, score)

    # Determine status & priority category
    if score == 0:
        level = "NORMAL"
        status = "NO_ATTENTION"
        badge_text = "No Attention Required"
    elif score < 50:
        level = "LOW"
        status = "ATTENTION_REQUIRED"
        badge_text = "Low Attention Required"
    elif score < 75:
        level = "MODERATE"
        status = "ATTENTION_REQUIRED"
        badge_text = "Moderate Attention Required"
    else:
        level = "HIGH"
        status = "ATTENTION_REQUIRED"
        badge_text = "High Attention Required"

    return {
        "priority_score": score,
        "max_score": 100,
        "risk_level": level,
        "investigation_status": status,
        "badge_text": badge_text,
        "contributing_rules": breakdown,
        "disclaimer": "This score indicates investigator triaging priority only. It does NOT represent a fraud probability or determination."
    }
