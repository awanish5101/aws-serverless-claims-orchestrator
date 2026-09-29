from src.handlers.validation_handler import lambda_handler as validation_handler
from src.handlers.document_handler import lambda_handler as document_handler
from src.handlers.triage_handler import lambda_handler as triage_handler
from src.handlers.settlement_handler import lambda_handler as settlement_handler
from src.services.dynamodb_service import DynamoDBService
from src.models.claim import ClaimRecord, ClaimType, ClaimStatus

def test_step_functions_pipeline_happy_path(mocked_aws):
    # Setup initial claim in DynamoDB
    db_service = DynamoDBService(dynamodb_resource=mocked_aws["dynamodb"])
    claim = ClaimRecord(
        claim_id="CLM-PIPE-001",
        policy_number="POL-44556677",
        insured_name="Clark Kent",
        claim_type=ClaimType.PROPERTY,
        estimated_damage_amount=8500.0,
        incident_date="2026-09-24",
        incident_location="Metropolis, IL",
        incident_description="Storm wind damaged exterior siding"
    )
    db_service.save_claim(claim)

    initial_input = {
        "claim_id": "CLM-PIPE-001",
        "policy_number": "POL-44556677",
        "estimated_damage_amount": 8500.0,
        "claim_type": "PROPERTY",
        "incident_description": "Storm wind damaged exterior siding",
        "documents": [
            {
                "document_id": "DOC-99",
                "s3_bucket": "claims-evidence-bucket",
                "s3_key": "photos/damage.png",
                "file_type": "image/png",
                "file_size_bytes": 204800,
                "uploaded_at": "2026-09-24T12:00:00Z"
            }
        ]
    }

    # Step 1: Validation
    step1_out = validation_handler(initial_input, None)
    assert step1_out["validation_passed"] is True
    assert step1_out["policy_status"] == "ACTIVE_IN_FORCE"

    # Step 2: Document Processing
    step2_out = document_handler(step1_out, None)
    assert step2_out["document_count"] == 1

    # Step 3: Bedrock AI Triage
    step3_out = triage_handler(step2_out, None)
    assert "ai_triage" in step3_out
    assert step3_out["ai_triage"]["severity"] in ["MEDIUM", "HIGH"]

    # Step 4: Settlement & Status Finalization
    final_out = settlement_handler(step3_out, None)
    assert final_out["claim_id"] == "CLM-PIPE-001"
    assert final_out["final_status"] == ClaimStatus.AI_TRIAGED.value

    # Verify updated state in DynamoDB
    record = db_service.get_claim("CLM-PIPE-001")
    assert record["status"] == "AI_TRIAGED"

def test_step_functions_pipeline_validation_rejection(mocked_aws):
    invalid_input = {
        "claim_id": "CLM-REJECT-001",
        "policy_number": "BAD",
        "estimated_damage_amount": 1000.0
    }
    step1_out = validation_handler(invalid_input, None)
    assert step1_out["validation_passed"] is False
    assert "Invalid Policy Identifier" in step1_out["rejection_reason"]
