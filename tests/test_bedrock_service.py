from src.services.bedrock_service import BedrockTriageService
from src.models.claim import PriorityTier

def test_bedrock_triage_low_severity():
    service = BedrockTriageService()
    result = service.triage_claim(
        claim_type="AUTO",
        incident_description="Minor scratch on parking door while shopping at grocery store",
        estimated_amount=850.0
    )
    assert result.severity == PriorityTier.LOW
    assert result.fraud_risk_score < 40.0
    assert "SIU" not in result.recommendation

def test_bedrock_triage_high_risk_fraud_flag():
    service = BedrockTriageService()
    result = service.triage_claim(
        claim_type="PROPERTY",
        incident_description="Unwitnessed total loss fire occurring overnight with cash demand",
        estimated_amount=65000.0
    )
    assert result.severity == PriorityTier.EXPEDITED
    assert result.fraud_risk_score > 60.0
    assert "Special Investigation Unit (SIU)" in result.recommendation
