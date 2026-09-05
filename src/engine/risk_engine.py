"""Deterministic Risk Engine Orchestrator.
Coordinates baseline computation, deterministic rule execution, correlation, and scoring.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

from src.engine.baseline import calculate_baseline
from src.engine.rules import (
    evaluate_r001_large_transfer,
    evaluate_r002_new_payee_burst,
    evaluate_r003_odd_hours,
    evaluate_r004_behavioural_break
)
from src.engine.correlation import correlate_findings
from src.engine.scoring import calculate_priority_score

logger = logging.getLogger("risklens.engine")


class RiskEngine:
    """Orchestrates deterministic transaction risk investigation."""

    def __init__(self, rules_config_path: Optional[str] = None):
        self.rules_config_path = rules_config_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "rules.json"
        )
        self.rules_config = self._load_rules_config()

    def _load_rules_config(self) -> Dict[str, Any]:
        cfg = {}
        if os.path.exists(self.rules_config_path):
            try:
                with open(self.rules_config_path, "r", encoding="utf-8") as f:
                    rules_list = json.load(f)
                    for r in rules_list:
                        cfg[r["rule_id"]] = r.get("configuration", {})
            except Exception as e:
                logger.warning("Could not load rules.json: %s. Using default configs.", e)
        return cfg

    def run_investigation(
        self,
        customer_id: str,
        customer_name: str,
        transactions_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Run complete deterministic risk analysis for a customer.
        Returns full investigation payload with baseline, findings, correlation, and score.
        """
        logger.info("Investigation started customer=%s, transactions=%d", customer_id, len(transactions_df))

        # 1. Calculate behavioral baseline
        baseline = calculate_baseline(transactions_df)
        logger.info("Baseline generated transactions=%d, is_reliable=%s", baseline.get("transaction_count", 0), baseline.get("is_reliable", False))

        # Check for insufficient baseline
        if not baseline.get("is_reliable", False):
            return {
                "customer_id": customer_id,
                "customer_name": customer_name,
                "investigation_status": "REVIEW_REQUIRED",
                "risk_level": "UNKNOWN",
                "priority_score": 0,
                "badge_text": "Insufficient Evidence",
                "summary": "The available transaction history is not sufficient to establish a reliable customer behaviour profile. Human review recommended.",
                "baseline": baseline,
                "rule_evaluations": [],
                "findings": [],
                "correlated_events": [],
                "scoring": {
                    "priority_score": 0,
                    "risk_level": "UNKNOWN",
                    "investigation_status": "REVIEW_REQUIRED",
                    "badge_text": "Insufficient Evidence",
                    "contributing_rules": []
                },
                "unknowns": [
                    "Transaction purpose and business justification are unavailable.",
                    "Insufficient historical timeline to establish normal transaction patterns.",
                    "Customer confirmation of recent transactions is not present."
                ],
                "recommended_actions": [
                    "Request additional transaction history (minimum 3 months recommended).",
                    "Contact customer via verified secondary channel to verify account status."
                ]
            }

        # 2. Evaluate deterministic rules
        r001_res = evaluate_r001_large_transfer(transactions_df, baseline, self.rules_config.get("R001"))
        r002_res = evaluate_r002_new_payee_burst(transactions_df, baseline, self.rules_config.get("R002"))
        r003_res = evaluate_r003_odd_hours(transactions_df, baseline, self.rules_config.get("R003"))
        r004_res = evaluate_r004_behavioural_break(transactions_df, baseline, self.rules_config.get("R004"))

        rule_evaluations = [r001_res, r002_res, r003_res, r004_res]

        # 3. Aggregate all findings
        all_findings = []
        triggered_rule_ids = []
        for r_eval in rule_evaluations:
            if r_eval["status"] == "TRIGGERED":
                triggered_rule_ids.append(r_eval["rule_id"])
                for f in r_eval["findings"]:
                    all_findings.append(f)
                    logger.info("Rule %s triggered for finding=%s", r_eval["rule_id"], f["finding_id"])

        # 4. Correlation of triggered events
        correlated_events = correlate_findings(all_findings, transactions_df)

        # 5. Prioritization scoring
        scoring = calculate_priority_score(triggered_rule_ids)

        # 6. Overall result & summary
        if not all_findings:
            investigation_status = "NO_ATTENTION"
            summary_text = "No configured risk rule was triggered by the customer's transaction history. Behaviour conforms to established historical patterns."
        else:
            investigation_status = "ATTENTION_REQUIRED"
            summary_text = f"Identified {len(all_findings)} findings across rules {', '.join(triggered_rule_ids)}. Compounding anomalies warrant analyst review."

        # 7. Recommended investigator actions (evidence grounded)
        recommended_actions = []
        if "R001" in triggered_rule_ids:
            recommended_actions.append("Review source of funds and business justification for unusually large transfer.")
            recommended_actions.append("Confirm whether the customer initiated the high-value transfer directly.")
        if "R002" in triggered_rule_ids:
            recommended_actions.append("Verify the newly added payee and examine authentication logs for payee registration.")
            recommended_actions.append("Review rapid successive payments within the short execution window.")
        if "R003" in triggered_rule_ids:
            recommended_actions.append("Check device fingerprint, IP geolocation, and login timestamps for odd-hours transactions (00:00–05:00).")
        if "R004" in triggered_rule_ids:
            recommended_actions.append("Verify whether the recent sudden shift in payment channel distribution was planned or expected.")

        if not recommended_actions:
            recommended_actions.append("No immediate investigator action required. Maintain standard account monitoring.")

        # 8. Standard Unknown Information
        unknowns = [
            "Transaction commercial purpose and underlying contracts/invoices are unavailable.",
            "Customer authorization and subjective intent have not been confirmed directly.",
            "Counterparty beneficial ownership and merchant registry status are unknown."
        ]

        result = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "investigation_status": investigation_status,
            "risk_level": scoring["risk_level"],
            "priority_score": scoring["priority_score"],
            "badge_text": scoring["badge_text"],
            "summary": summary_text,
            "baseline": baseline,
            "rule_evaluations": rule_evaluations,
            "findings": all_findings,
            "correlated_events": correlated_events,
            "scoring": scoring,
            "recommended_actions": recommended_actions,
            "unknowns": unknowns,
            "created_at": datetime.utcnow().isoformat()
        }

        return result
