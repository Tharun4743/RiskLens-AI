"""Pydantic schemas for Gemini AI explanation input, output, and validation."""
from typing import List, Optional
from pydantic import BaseModel, Field


class KeyFindingExplanation(BaseModel):
    finding_id: str = Field(description="The deterministic finding ID (e.g. F-001-01)")
    rule_id: str = Field(description="The deterministic rule ID (e.g. R001)")
    transaction_ids: List[str] = Field(description="Exact transaction IDs involved in this finding")
    explanation: str = Field(description="Cautious, evidence-grounded explanation comparing observed values to baseline")


class InvestigatorAction(BaseModel):
    priority_level: str = Field(description="HIGH, MEDIUM, or LOW")
    action_text: str = Field(description="Concrete recommended investigator verification step")
    target_reference: Optional[str] = Field(default=None, description="Related transaction ID, payee, or channel")


class InvestigationExplanation(BaseModel):
    summary: str = Field(description="Concise, objective summary of the investigation findings without claiming fraud")
    attention_required: bool = Field(description="True if anomalies requiring attention were detected")
    priority: str = Field(description="NORMAL, LOW, MODERATE, or HIGH")
    key_findings: List[KeyFindingExplanation] = Field(description="List of explained findings grounded in evidence")
    investigator_actions: List[InvestigatorAction] = Field(description="Recommended first actions for the human analyst")
    unknowns: List[str] = Field(description="Explicitly identified unknown facts, missing context, or unverified claims")
    human_review_disclaimer: str = Field(
        default="Human investigator review required. RiskLens AI identifies unusual activity and provides supporting evidence. It does not determine whether fraud occurred.",
        description="Mandatory human review statement"
    )
