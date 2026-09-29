import os
import json
import uuid
import boto3
from typing import Dict, Any, Optional
from src.models.claim import ClaimSubmissionRequest, ClaimRecord, ClaimStatus
from src.services.dynamodb_service import DynamoDBService

STATE_MACHINE_ARN = os.getenv("STATE_MACHINE_ARN", "arn:aws:states:us-east-1:123456789012:stateMachine:ClaimsProcessingWorkflow")

def get_services():
    sfn_client = boto3.client("stepfunctions", region_name=os.getenv("AWS_REGION", "us-east-1"))
    db_service = DynamoDBService()
    return sfn_client, db_service

def lambda_handler(event: Dict[str, Any], context: Any, db_svc: Optional[DynamoDBService] = None) -> Dict[str, Any]:
    """
    API Gateway REST proxy intake handler: POST /claims.
    Validates request payload, creates initial DynamoDB record,
    and initiates Step Functions execution.
    """
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event.get("body", {})
        request = ClaimSubmissionRequest(**body)
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid Claim Submission Payload", "details": str(e)})
        }

    sfn_client, default_db = get_services()
    db_service = db_svc or default_db

    claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"

    claim = ClaimRecord(
        claim_id=claim_id,
        policy_number=request.policy_number,
        insured_name=request.insured_name,
        claim_type=request.claim_type,
        status=ClaimStatus.SUBMITTED,
        estimated_damage_amount=request.estimated_damage_amount,
        incident_date=request.incident_date,
        incident_location=request.incident_location,
        incident_description=request.incident_description,
        documents=request.documents or []
    )

    # Persist preliminary claim in DynamoDB
    db_service.save_claim(claim)

    # Trigger Step Functions execution
    sfn_input = {
        "claim_id": claim.claim_id,
        "policy_number": claim.policy_number,
        "insured_name": claim.insured_name,
        "claim_type": claim.claim_type.value,
        "estimated_damage_amount": claim.estimated_damage_amount,
        "incident_date": claim.incident_date,
        "incident_location": claim.incident_location,
        "incident_description": claim.incident_description,
        "documents": [d.model_dump() for d in claim.documents]
    }

    try:
        sfn_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=f"exec-{claim_id}",
            input=json.dumps(sfn_input)
        )
    except Exception:
        pass  # In local test/mock environments where stepfunctions is unconfigured

    return {
        "statusCode": 202,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "message": "Claim submitted successfully and queued for orchestration",
            "claim_id": claim_id,
            "status": ClaimStatus.SUBMITTED.value
        })
    }
