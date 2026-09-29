import json
from src.handlers.intake_handler import lambda_handler

def test_intake_handler_success(mocked_aws):
    payload = {
        "policy_number": "POL-99887766",
        "insured_name": "Michael Scott",
        "claim_type": "AUTO",
        "incident_date": "2026-09-28",
        "incident_location": "Scranton, PA",
        "incident_description": "Car struck a pole in office parking lot",
        "estimated_damage_amount": 3200.0,
        "documents": [
            {
                "document_id": "DOC-1",
                "s3_bucket": "claims-evidence-bucket",
                "s3_key": "evidence/photo1.jpg",
                "file_type": "image/jpeg",
                "file_size_bytes": 102400,
                "uploaded_at": "2026-09-28T10:00:00Z"
            }
        ]
    }

    event = {"body": json.dumps(payload)}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 202
    body = json.loads(response["body"])
    assert "claim_id" in body
    assert body["status"] == "SUBMITTED"

def test_intake_handler_invalid_payload(mocked_aws):
    # Missing policy_number and estimated_damage_amount
    event = {"body": json.dumps({"insured_name": "Bob"})}
    response = lambda_handler(event, None)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body
