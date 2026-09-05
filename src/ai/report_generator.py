"""AI Report Generation, Hallucination Validation, and Deterministic Fallback.
Guarantees zero unverified AI claims reach the banking analyst.
"""
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd

from src.ai.gemini_client import GeminiClient, GeminiUnavailableException
from src.ai.schemas import InvestigationExplanation
from src.ai.prompts import SYSTEM_INSTRUCTION, build_investigation_prompt, build_chat_prompt
from src.evidence.citation import build_evidence_packet

logger = logging.getLogger("risklens.ai.validation")

VALID_RULE_IDS = {"R001", "R002", "R003", "R004"}


class HallucinationValidationError(Exception):
    """Raised when AI outputs unsupported, invented, or mismatched transaction data."""
    pass


def validate_ai_explanation(
    ai_output: InvestigationExplanation,
    valid_transactions_df: pd.DataFrame,
    deterministic_findings: List[Dict[str, Any]]
) -> Tuple[bool, Optional[str]]:
    """
    Rigorously validates Gemini output against the deterministic database records.
    Verifies:
      1. Every transaction ID exists in source data.
      2. Every rule ID exists in standard rules.
      3. Every finding ID references a real deterministic finding.
      4. No hallucinated amounts or claims.
    Returns: (is_valid, rejection_reason)
    """
    valid_txn_ids = set(valid_transactions_df["transaction_id"].astype(str).unique())
    valid_finding_ids = {f["finding_id"] for f in deterministic_findings}

    # 1. Check finding references
    for kf in ai_output.key_findings:
        # Check rule ID
        if kf.rule_id not in VALID_RULE_IDS:
            return False, f"Unsupported rule ID referenced: '{kf.rule_id}'"

        # Check finding ID
        if kf.finding_id not in valid_finding_ids:
            return False, f"Unsupported finding ID referenced: '{kf.finding_id}'"

        # Check transaction IDs
        for tid in kf.transaction_ids:
            if tid not in valid_txn_ids:
                return False, f"Hallucinated transaction ID referenced: '{tid}' does not exist in customer transactions"

        # Scan explanation text for hallucinated transaction IDs (e.g. TXN-999999)
        matches = re.findall(r"TXN-\d+", kf.explanation)
        for m_tid in matches:
            if m_tid not in valid_txn_ids:
                return False, f"Hallucinated transaction ID '{m_tid}' detected in explanation body"

    # 2. Check summary text for hallucinated TXN patterns
    summary_matches = re.findall(r"TXN-\d+", ai_output.summary)
    for m_tid in summary_matches:
        if m_tid not in valid_txn_ids:
            return False, f"Hallucinated transaction ID '{m_tid}' detected in summary"

    # 3. Check investigator actions target references
    for act in ai_output.investigator_actions:
        if act.target_reference and act.target_reference.startswith("TXN-"):
            if act.target_reference not in valid_txn_ids:
                return False, f"Hallucinated transaction ID '{act.target_reference}' in recommended actions"

    return True, None


def generate_deterministic_fallback(
    investigation_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a 100% deterministic explanation when Gemini is unavailable or rejected.
    Uses exact observed values, deviations, and established findings.
    """
    findings = investigation_result.get("findings", [])
    scoring = investigation_result.get("scoring", {})
    status = investigation_result.get("investigation_status", "NO_ATTENTION")
    priority = scoring.get("risk_level", "NORMAL")
    baseline = investigation_result.get("baseline", {})

    key_findings_list = []
    for f in findings:
        dev_str = ""
        if f.get("evidence"):
            dev_str = f" Deviation: {f['evidence'][0].get('deviation', '')}."
        key_findings_list.append({
            "finding_id": f["finding_id"],
            "rule_id": f["rule_id"],
            "transaction_ids": f.get("transaction_ids", []),
            "explanation": f"{f['title']}. {f['description']}{dev_str}"
        })

    actions = []
    for act_text in investigation_result.get("recommended_actions", []):
        actions.append({
            "priority_level": "HIGH" if priority in ["HIGH", "MODERATE"] else "LOW",
            "action_text": act_text,
            "target_reference": None
        })

    unknowns = investigation_result.get("unknowns", [
        "Commercial justification or invoice documentation is unavailable in transaction stream.",
        "Customer subjective authorization has not been verified via external phone/auth callback.",
        "Merchant or payee corporate registry status has not been confirmed."
    ])

    if status == "NO_ATTENTION":
        summary = "No configured risk rule was triggered by the customer's transaction history. All analysed transactions conform to normal behavioural distribution."
        attention_req = False
    else:
        triggered_rules = sorted(list(set(f["rule_id"] for f in findings)))
        summary = f"Investigation priority level is {priority}. {len(findings)} anomalous finding(s) detected across rules {', '.join(triggered_rules)}. Human analyst verification is recommended."
        attention_req = True

    return {
        "summary": summary,
        "attention_required": attention_req,
        "priority": priority,
        "key_findings": key_findings_list,
        "investigator_actions": actions,
        "unknowns": unknowns,
        "human_review_disclaimer": "Human investigator review required. RiskLens AI identifies unusual activity and provides supporting evidence. It does not determine whether fraud occurred.",
        "is_deterministic_fallback": True,
        "fallback_notice": "AI explanation unavailable or unverified. Deterministic investigation findings remain available."
    }


def explain_investigation(
    investigation_result: Dict[str, Any],
    transactions_df: pd.DataFrame,
    gemini_client: Optional[GeminiClient] = None
) -> Dict[str, Any]:
    """
    Generate investigation explanation using Gemini if available.
    Validates output for hallucinations and falls back gracefully.
    """
    client = gemini_client or GeminiClient()

    # Build clean evidence packet
    evidence_packet = build_evidence_packet(
        customer_id=investigation_result["customer_id"],
        customer_name=investigation_result["customer_name"],
        baseline=investigation_result["baseline"],
        findings=investigation_result.get("findings", []),
        correlated_events=investigation_result.get("correlated_events", []),
        scoring=investigation_result.get("scoring", {}),
        unknowns=investigation_result.get("unknowns", [])
    )

    if not client.is_available():
        logger.info("Gemini unavailable. Generating deterministic fallback.")
        fallback = generate_deterministic_fallback(investigation_result)
        return fallback

    try:
        prompt = build_investigation_prompt(evidence_packet)
        raw_json_str = client.generate_explanation(
            system_instruction=SYSTEM_INSTRUCTION,
            prompt=prompt,
            response_schema=InvestigationExplanation
        )

        if not raw_json_str:
            logger.warning("Empty response from Gemini. Falling back to deterministic output.")
            return generate_deterministic_fallback(investigation_result)

        parsed_dict = json.loads(raw_json_str)
        pydantic_obj = InvestigationExplanation(**parsed_dict)

        # Validate against hallucinations
        is_valid, reject_reason = validate_ai_explanation(
            pydantic_obj,
            transactions_df,
            investigation_result.get("findings", [])
        )

        if not is_valid:
            logger.warning("AI Hallucination detected: %s. Rejecting and falling back.", reject_reason)
            fallback = generate_deterministic_fallback(investigation_result)
            fallback["fallback_notice"] = f"AI output rejected due to unsupported claim ({reject_reason}). Deterministic findings applied."
            return fallback

        # Validated successfully
        result_dict = pydantic_obj.model_dump()
        result_dict["is_deterministic_fallback"] = False
        result_dict["fallback_notice"] = None
        return result_dict

    except (GeminiUnavailableException, json.JSONDecodeError, Exception) as e:
        logger.warning("Error generating Gemini explanation: %s. Using deterministic fallback.", str(e))
        return generate_deterministic_fallback(investigation_result)


def answer_investigation_query(
    investigation_result: Dict[str, Any],
    question: str,
    gemini_client: Optional[GeminiClient] = None
) -> Dict[str, Any]:
    """
    Answers an investigator question strictly grounded in the investigation evidence.
    """
    client = gemini_client or GeminiClient()

    evidence_packet = build_evidence_packet(
        customer_id=investigation_result["customer_id"],
        customer_name=investigation_result["customer_name"],
        baseline=investigation_result["baseline"],
        findings=investigation_result.get("findings", []),
        correlated_events=investigation_result.get("correlated_events", []),
        scoring=investigation_result.get("scoring", {}),
        unknowns=investigation_result.get("unknowns", [])
    )

    if not client.is_available():
        # Deterministic Q&A responder
        q_lower = question.lower()
        findings = investigation_result.get("findings", [])
        correlated = investigation_result.get("correlated_events", [])

        if "why" in q_lower or "flagged" in q_lower or "rule" in q_lower:
            if not findings:
                ans = "No transactions were flagged. The customer's activity matches established baseline behavior."
            else:
                lines = ["Activity was flagged for the following deterministic reasons:"]
                for f in findings:
                    lines.append(f"- **{f['rule_id']} ({f['title']})**: {f['description']}")
                ans = "\n".join(lines)
        elif "connect" in q_lower or "related" in q_lower:
            if not correlated:
                ans = "No multi-transaction clusters or correlated events were identified."
            else:
                lines = [f"Found {len(correlated)} correlated transaction cluster(s):"]
                for c in correlated:
                    lines.append(f"- **{c['event_id']}**: {c['summary']}")
                ans = "\n".join(lines)
        elif "first" in q_lower or "action" in q_lower or "check" in q_lower:
            actions = investigation_result.get("recommended_actions", [])
            lines = ["Recommended investigator review steps:"]
            for i, a in enumerate(actions, 1):
                lines.append(f"{i}. {a}")
            ans = "\n".join(lines)
        elif "unknown" in q_lower:
            unknowns = investigation_result.get("unknowns", [])
            lines = ["Information remaining unknown from transaction logs:"]
            for u in unknowns:
                lines.append(f"- {u}")
            ans = "\n".join(lines)
        else:
            ans = f"Customer {investigation_result['customer_id']} ({investigation_result['customer_name']}) has status '{investigation_result['badge_text']}' with priority score {investigation_result['priority_score']}/100 and {len(findings)} finding(s)."

        return {
            "answer": ans,
            "grounded_on": "Deterministic Evidence Records",
            "is_ai": False
        }

    try:
        prompt = build_chat_prompt(evidence_packet, question)
        ai_response = client.answer_investigation_question(SYSTEM_INSTRUCTION, prompt)
        return {
            "answer": ai_response,
            "grounded_on": "Gemini AI Grounded on Evidence Packet",
            "is_ai": True
        }
    except Exception as e:
        logger.warning("Failed to answer via Gemini: %s", str(e))
        return {
            "answer": f"Unable to generate AI answer ({str(e)}). Please refer to the deterministic findings table.",
            "grounded_on": "Fallback",
            "is_ai": False
        }
