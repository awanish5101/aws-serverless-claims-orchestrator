from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ClaimType(str, Enum):
    AUTO = "AUTO"
    PROPERTY = "PROPERTY"
    CASUALTY = "CASUALTY"
    LIFE = "LIFE"

class ClaimStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    AI_TRIAGED = "AI_TRIAGED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FLAGGED_FOR_FRAUD = "FLAGGED_FOR_FRAUD"

class PriorityTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXPEDITED = "EXPEDITED"

class DocumentAttachment(BaseModel):
    document_id: str
    s3_bucket: str
    s3_key: str
    file_type: str
    file_size_bytes: int
    uploaded_at: str

class ClaimSubmissionRequest(BaseModel):
    policy_number: str = Field(..., min_length=6, max_length=20)
    insured_name: str = Field(..., min_length=2)
    claim_type: ClaimType
    incident_date: str
    incident_location: str
    incident_description: str
    estimated_damage_amount: float = Field(..., ge=0.0)
    documents: Optional[List[DocumentAttachment]] = []

class AITriageResult(BaseModel):
    summary: str
    severity: PriorityTier
    fraud_risk_score: float = Field(..., ge=0.0, le=100.0)
    recommendation: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"

class ClaimRecord(BaseModel):
    claim_id: str
    policy_number: str
    insured_name: str
    claim_type: ClaimType
    status: ClaimStatus = ClaimStatus.SUBMITTED
    estimated_damage_amount: float
    incident_date: str
    incident_location: str
    incident_description: str
    documents: List[DocumentAttachment] = []
    triage_result: Optional[AITriageResult] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert into DynamoDB single-table item format."""
        item = {
            "PK": f"CLAIM#{self.claim_id}",
            "SK": "METADATA",
            "GSI1PK": f"POLICY#{self.policy_number}",
            "GSI1SK": f"STATUS#{self.status.value}",
            "claim_id": self.claim_id,
            "policy_number": self.policy_number,
            "insured_name": self.insured_name,
            "claim_type": self.claim_type.value,
            "status": self.status.value,
            "estimated_damage_amount": str(self.estimated_damage_amount),
            "incident_date": self.incident_date,
            "incident_location": self.incident_location,
            "incident_description": self.incident_description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.triage_result:
            item["triage_summary"] = self.triage_result.summary
            item["triage_severity"] = self.triage_result.severity.value
            item["fraud_risk_score"] = str(self.triage_result.fraud_risk_score)
            item["recommendation"] = self.triage_result.recommendation
        return item
