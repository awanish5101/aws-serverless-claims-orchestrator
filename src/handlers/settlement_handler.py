from typing import Dict, Any, Optional
from src.models.claim import ClaimStatus
from src.services.dynamodb_service import DynamoDBService
from src.services.eventbridge_service import EventBridgeService

def lambda_handler(
    event: Dict[str, Any],
    context: Any,
    db_svc: Optional[DynamoDBService] = None,
    eb_svc: Optional[EventBridgeService] = None
) -> Dict[str, Any]:
    """
    Step Functions Task: Finalizes triage, updates DynamoDB,
    and publishes events to EventBridge and SNS.
    """
    db_service = db_svc or DynamoDBService()
    eb_service = eb_svc or EventBridgeService()

    claim_id = event.get("claim_id")
    ai_triage = event.get("ai_triage", {})
    fraud_score = float(ai_triage.get("fraud_risk_score", 0.0))

    if fraud_score > 65.0:
        final_status = ClaimStatus.FLAGGED_FOR_FRAUD
    elif event.get("validation_passed") is False:
        final_status = ClaimStatus.REJECTED
    else:
        final_status = ClaimStatus.AI_TRIAGED

    # Update claim status in DynamoDB
    if claim_id:
        db_service.update_claim_status(claim_id, final_status)

    # Publish EventBridge event
    eb_service.publish_claim_event(
        detail_type="ClaimTriageCompleted",
        detail={
            "claim_id": claim_id,
            "status": final_status.value,
            "fraud_score": fraud_score,
            "priority": ai_triage.get("severity")
        }
    )

    # Publish SNS notification alert
    eb_service.notify_claim_status(
        claim_id=claim_id,
        status=final_status.value,
        message=f"Claim {claim_id} triage completed with status {final_status.value}. Priority: {ai_triage.get('severity')}"
    )

    return {
        "claim_id": claim_id,
        "final_status": final_status.value,
        "fraud_score": fraud_score,
        "processed_at": event.get("incident_date")
    }
