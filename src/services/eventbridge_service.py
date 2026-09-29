import os
import json
import boto3
from typing import Dict, Any

EVENT_BUS_NAME = os.getenv("CLAIMS_EVENT_BUS", "claims.events")
SNS_TOPIC_ARN = os.getenv("CLAIMS_SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:claim-notifications")

class EventBridgeService:
    def __init__(self, eventbridge_client=None, sns_client=None):
        self.eb_client = eventbridge_client or boto3.client("events", region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.sns_client = sns_client or boto3.client("sns", region_name=os.getenv("AWS_REGION", "us-east-1"))

    def publish_claim_event(self, detail_type: str, detail: Dict[str, Any]) -> Dict[str, Any]:
        """Publish structured event to Amazon EventBridge custom bus."""
        entry = {
            "Source": "insurance.claims.orchestrator",
            "DetailType": detail_type,
            "Detail": json.dumps(detail),
            "EventBusName": EVENT_BUS_NAME
        }
        response = self.eb_client.put_events(Entries=[entry])
        return response

    def notify_claim_status(self, claim_id: str, status: str, message: str) -> Dict[str, Any]:
        """Publish status alert to Amazon SNS topic."""
        payload = {
            "claim_id": claim_id,
            "status": status,
            "message": message
        }
        response = self.sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"Claim Status Update: {claim_id} [{status}]",
            Message=json.dumps(payload)
        )
        return response
