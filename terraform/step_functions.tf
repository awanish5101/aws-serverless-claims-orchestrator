# IAM Role for Step Functions State Machine
resource "aws_iam_role" "step_functions_role" {
  name = "${var.project_name}-sfn-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })
}

# Step Functions State Machine definition
resource "aws_sfn_state_machine" "claims_pipeline" {
  name     = "${var.project_name}-pipeline-${var.environment}"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = templatefile("${path.module}/../statemachine/claims_workflow.asl.json", {
    ValidateClaimLambdaArn     = "arn:aws:lambda:${var.aws_region}:123456789012:function:${var.project_name}-validate",
    DocumentProcessorLambdaArn = "arn:aws:lambda:${var.aws_region}:123456789012:function:${var.project_name}-doc-processor",
    BedrockTriageLambdaArn     = "arn:aws:lambda:${var.aws_region}:123456789012:function:${var.project_name}-bedrock-triage",
    SettlementLambdaArn        = "arn:aws:lambda:${var.aws_region}:123456789012:function:${var.project_name}-settlement"
  })

  logging_configuration {
    level                  = "ALL"
    include_execution_data = true
  }
}
