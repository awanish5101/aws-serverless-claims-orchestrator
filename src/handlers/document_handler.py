import boto3
import os
from typing import Dict, Any

s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION", "us-east-1"))

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Step Functions Task: Verifies evidence attachments in S3 bucket.
    """
    documents = event.get("documents", [])
    verified_docs = []

    for doc in documents:
        bucket = doc.get("s3_bucket")
        key = doc.get("s3_key")
        is_accessible = True

        if bucket and key:
            try:
                s3_client.head_object(Bucket=bucket, Key=key)
            except Exception:
                is_accessible = False

        verified_docs.append({
            **doc,
            "verified": is_accessible
        })

    return {
        **event,
        "processed_documents": verified_docs,
        "document_count": len(verified_docs)
    }
