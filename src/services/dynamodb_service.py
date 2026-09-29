import os
import boto3
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from src.models.claim import ClaimRecord, ClaimStatus

TABLE_NAME = os.getenv("CLAIMS_DYNAMODB_TABLE", "claims-ledger-table")

class DynamoDBService:
    def __init__(self, dynamodb_resource=None):
        self.dynamodb = dynamodb_resource or boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.table = self.dynamodb.Table(TABLE_NAME)

    def save_claim(self, claim: ClaimRecord) -> Dict[str, Any]:
        """Save or update claim item in DynamoDB Single-Table Design."""
        item = claim.to_dynamodb_item()
        self.table.put_item(Item=item)
        return item

    def get_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve claim by partition key."""
        try:
            response = self.table.get_item(
                Key={
                    "PK": f"CLAIM#{claim_id}",
                    "SK": "METADATA"
                }
            )
            return response.get("Item")
        except ClientError:
            return None

    def update_claim_status(self, claim_id: str, new_status: ClaimStatus) -> Dict[str, Any]:
        """Update claim status and GSI2 status index."""
        response = self.table.update_item(
            Key={
                "PK": f"CLAIM#{claim_id}",
                "SK": "METADATA"
            },
            UpdateExpression="SET #status = :s, GSI1SK = :gsi_sk",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":s": new_status.value,
                ":gsi_sk": f"STATUS#{new_status.value}"
            },
            ReturnValues="ALL_NEW"
        )
        return response.get("Attributes", {})

    def query_claims_by_policy(self, policy_number: str) -> List[Dict[str, Any]]:
        """Query claims for a specific policy using Global Secondary Index (GSI1)."""
        response = self.table.query(
            IndexName="GSI1-PolicyClaimsIndex",
            KeyConditionExpression="GSI1PK = :policy_pk",
            ExpressionAttributeValues={
                ":policy_pk": f"POLICY#{policy_number}"
            }
        )
        return response.get("Items", [])
