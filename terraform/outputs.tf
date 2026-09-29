output "dynamodb_table_name" {
  description = "DynamoDB Claims Ledger Table Name"
  value       = aws_dynamodb_table.claims_ledger.name
}

output "dynamodb_table_arn" {
  description = "DynamoDB Claims Ledger Table ARN"
  value       = aws_dynamodb_table.claims_ledger.arn
}

output "eventbridge_bus_name" {
  description = "Custom EventBridge Event Bus Name"
  value       = aws_cloudwatch_event_bus.claims_bus.name
}

output "sqs_ingestion_queue_url" {
  description = "Claims Ingestion SQS Queue URL"
  value       = aws_sqs_queue.claims_ingestion_queue.url
}

output "sns_notifications_topic_arn" {
  description = "SNS Status Alerts Topic ARN"
  value       = aws_sns_topic.claims_notifications.arn
}

output "step_functions_state_machine_arn" {
  description = "Step Functions State Machine ARN"
  value       = aws_sfn_state_machine.claims_pipeline.arn
}

output "s3_documents_bucket_name" {
  description = "S3 Claims Documents Bucket Name"
  value       = aws_s3_bucket.claims_documents.id
}
