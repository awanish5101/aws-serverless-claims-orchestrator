from typing import Dict, Any
from src.services.bedrock_service import BedrockTriageService

bedrock_service = BedrockTriageService()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Step Functions Task: Invokes Amazon Bedrock for AI claims triage and fraud risk scoring.
    """
    claim_type = event.get("claim_type", "AUTO")
    description = event.get("incident_description", "")
    amount = float(event.get("estimated_damage_amount", 0.0))

    triage_result = bedrock_service.triage_claim(
        claim_type=claim_type,
        incident_description=description,
        estimated_amount=amount
    )

    return {
        **event,
        "ai_triage": triage_result.model_dump()
    }
