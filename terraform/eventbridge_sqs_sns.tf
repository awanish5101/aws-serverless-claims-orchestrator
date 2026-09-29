# Custom EventBridge Event Bus for Claims Domain
resource "aws_cloudwatch_event_bus" "claims_bus" {
  name = "${var.project_name}-events-${var.environment}"
}

# Dead Letter Queue (DLQ) for Failed Claims Ingestion
resource "aws_sqs_queue" "claims_dlq" {
  name                      = "${var.project_name}-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days
}

# Ingestion SQS Queue with Redrive Policy
resource "aws_sqs_queue" "claims_ingestion_queue" {
  name                       = "${var.project_name}-ingestion-${var.environment}"
  visibility_timeout_seconds = 60
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.claims_dlq.arn
    maxReceiveCount     = 3
  })
}

# SNS Topic for Real-Time Status Notifications
resource "aws_sns_topic" "claims_notifications" {
  name = "${var.project_name}-status-alerts-${var.environment}"
}

# EventBridge Rule to capture all Claims Triage completed events
resource "aws_cloudwatch_event_rule" "triage_completed_rule" {
  name           = "${var.project_name}-triage-completed"
  event_bus_name = aws_cloudwatch_event_bus.claims_bus.name

  event_pattern = jsonencode({
    source      = ["insurance.claims.orchestrator"]
    detail-type = ["ClaimTriageCompleted"]
  })
}

# Send EventBridge notifications to SNS topic
resource "aws_cloudwatch_event_target" "sns_target" {
  rule           = aws_cloudwatch_event_rule.triage_completed_rule.name
  event_bus_name = aws_cloudwatch_event_bus.claims_bus.name
  target_id      = "SendToSNS"
  arn            = aws_sns_topic.claims_notifications.arn
}
