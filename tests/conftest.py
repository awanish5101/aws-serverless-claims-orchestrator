import os

# Set dummy AWS credentials before any boto3 client initialization
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["CLAIMS_DYNAMODB_TABLE"] = "claims-ledger-table"
os.environ["CLAIMS_EVENT_BUS"] = "claims.events"
os.environ["CLAIMS_SNS_TOPIC_ARN"] = "arn:aws:sns:us-east-1:123456789012:claim-notifications"

import pytest
import boto3
from moto import mock_aws

@pytest.fixture(scope="function")
def mocked_aws():
    with mock_aws():
        # Setup mock DynamoDB table
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        dynamodb.create_table(
            TableName="claims-ledger-table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1-PolicyClaimsIndex",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        # Setup mock S3 bucket
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="claims-evidence-bucket")

        # Setup mock EventBridge bus
        events = boto3.client("events", region_name="us-east-1")
        events.create_event_bus(Name="claims.events")

        # Setup mock SNS topic
        sns = boto3.client("sns", region_name="us-east-1")
        topic = sns.create_topic(Name="claim-notifications")
        os.environ["CLAIMS_SNS_TOPIC_ARN"] = topic["TopicArn"]

        yield {
            "dynamodb": dynamodb,
            "s3": s3,
            "events": events,
            "sns": sns
        }
