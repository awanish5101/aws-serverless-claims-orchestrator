from src.services.eventbridge_service import EventBridgeService

def test_publish_claim_event(mocked_aws):
    eb_service = EventBridgeService(
        eventbridge_client=mocked_aws["events"],
        sns_client=mocked_aws["sns"]
    )
    response = eb_service.publish_claim_event(
        detail_type="ClaimSubmitted",
        detail={"claim_id": "CLM-100", "policy_number": "POL-123", "amount": 2500.0}
    )
    assert response["FailedEntryCount"] == 0
    assert len(response["Entries"]) == 1

def test_notify_claim_status_sns(mocked_aws):
    eb_service = EventBridgeService(
        eventbridge_client=mocked_aws["events"],
        sns_client=mocked_aws["sns"]
    )
    response = eb_service.notify_claim_status(
        claim_id="CLM-100",
        status="AI_TRIAGED",
        message="Claim triaged successfully"
    )
    assert "MessageId" in response
