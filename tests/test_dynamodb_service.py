from src.models.claim import ClaimRecord, ClaimType, ClaimStatus
from src.services.dynamodb_service import DynamoDBService

def test_dynamodb_save_and_retrieve_claim(mocked_aws):
    service = DynamoDBService(dynamodb_resource=mocked_aws["dynamodb"])
    claim = ClaimRecord(
        claim_id="CLM-TEST-001",
        policy_number="POL-98765432",
        insured_name="John Doe",
        claim_type=ClaimType.AUTO,
        status=ClaimStatus.SUBMITTED,
        estimated_damage_amount=4500.0,
        incident_date="2026-09-25",
        incident_location="Bloomington, IL",
        incident_description="Rear-end collision at red light"
    )

    # Save
    service.save_claim(claim)

    # Retrieve
    retrieved = service.get_claim("CLM-TEST-001")
    assert retrieved is not None
    assert retrieved["claim_id"] == "CLM-TEST-001"
    assert retrieved["policy_number"] == "POL-98765432"
    assert retrieved["status"] == "SUBMITTED"

def test_dynamodb_update_claim_status(mocked_aws):
    service = DynamoDBService(dynamodb_resource=mocked_aws["dynamodb"])
    claim = ClaimRecord(
        claim_id="CLM-TEST-002",
        policy_number="POL-98765432",
        insured_name="Jane Smith",
        claim_type=ClaimType.PROPERTY,
        estimated_damage_amount=12000.0,
        incident_date="2026-09-20",
        incident_location="Normal, IL",
        incident_description="Roof hail damage"
    )
    service.save_claim(claim)

    # Update status
    updated = service.update_claim_status("CLM-TEST-002", ClaimStatus.AI_TRIAGED)
    assert updated["status"] == "AI_TRIAGED"
    assert updated["GSI1SK"] == "STATUS#AI_TRIAGED"

def test_dynamodb_query_by_policy_gsi(mocked_aws):
    service = DynamoDBService(dynamodb_resource=mocked_aws["dynamodb"])
    claim1 = ClaimRecord(
        claim_id="CLM-TEST-003A",
        policy_number="POL-STATEFARM-100",
        insured_name="Alice Brown",
        claim_type=ClaimType.AUTO,
        estimated_damage_amount=1500.0,
        incident_date="2026-09-10",
        incident_location="Peoria, IL",
        incident_description="Minor bumper scratch"
    )
    claim2 = ClaimRecord(
        claim_id="CLM-TEST-003B",
        policy_number="POL-STATEFARM-100",
        insured_name="Alice Brown",
        claim_type=ClaimType.AUTO,
        estimated_damage_amount=2200.0,
        incident_date="2026-09-22",
        incident_location="Bloomington, IL",
        incident_description="Windshield rock crack"
    )
    service.save_claim(claim1)
    service.save_claim(claim2)

    # Query GSI
    results = service.query_claims_by_policy("POL-STATEFARM-100")
    assert len(results) == 2
    claim_ids = [r["claim_id"] for r in results]
    assert "CLM-TEST-003A" in claim_ids
    assert "CLM-TEST-003B" in claim_ids
