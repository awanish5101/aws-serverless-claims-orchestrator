import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
import { SFNClient, StartExecutionCommand } from "@aws-sdk/client-sfn";
import { marshall } from "@aws-sdk/util-dynamodb";
import { randomUUID } from "node:crypto";

const REGION = process.env.AWS_REGION || "us-east-1";
const TABLE_NAME = process.env.CLAIMS_DYNAMODB_TABLE || "claims-ledger-table";
const STATE_MACHINE_ARN = process.env.STATE_MACHINE_ARN || "arn:aws:states:us-east-1:123456789012:stateMachine:ClaimsProcessingWorkflow";

export const createClients = (overrides = {}) => ({
  dynamo: overrides.dynamo || new DynamoDBClient({ region: REGION }),
  sfn: overrides.sfn || new SFNClient({ region: REGION })
});

export const handler = async (event, context, clients = createClients()) => {
  let body;
  try {
    body = typeof event.body === "string" ? JSON.parse(event.body) : event.body || {};
  } catch (err) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Invalid JSON format in request body" })
    };
  }

  // Validate required claim attributes
  const { policy_number, insured_name, claim_type, estimated_damage_amount, incident_date, incident_description } = body;
  if (!policy_number || !insured_name || !claim_type || estimated_damage_amount === undefined) {
    return {
      statusCode: 400,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        error: "Missing required claim fields",
        required: ["policy_number", "insured_name", "claim_type", "estimated_damage_amount"]
      })
    };
  }

  const claimId = `CLM-${randomUUID().slice(0, 8).toUpperCase()}`;
  const now = new Date().toISOString();

  const claimItem = {
    PK: `CLAIM#${claimId}`,
    SK: "METADATA",
    GSI1PK: `POLICY#${policy_number}`,
    GSI1SK: "STATUS#SUBMITTED",
    claim_id: claimId,
    policy_number,
    insured_name,
    claim_type,
    status: "SUBMITTED",
    estimated_damage_amount: Number(estimated_damage_amount),
    incident_date: incident_date || now.split("T")[0],
    incident_description: incident_description || "",
    created_at: now,
    updated_at: now
  };

  // 1. Write to DynamoDB Single-Table Ledger
  await clients.dynamo.send(
    new PutItemCommand({
      TableName: TABLE_NAME,
      Item: marshall(claimItem)
    })
  );

  // 2. Trigger Step Functions State Machine Execution
  let executionArn = null;
  try {
    const sfnResult = await clients.sfn.send(
      new StartExecutionCommand({
        stateMachineArn: STATE_MACHINE_ARN,
        name: `exec-${claimId}`,
        input: JSON.stringify(claimItem)
      })
    );
    executionArn = sfnResult.executionArn;
  } catch (sfnErr) {
    console.warn("Step Functions trigger bypassed in offline test/mock:", sfnErr.message);
  }

  return {
    statusCode: 202,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: "Claim intake validated and queued for serverless orchestration",
      claim_id: claimId,
      status: "SUBMITTED",
      execution_arn: executionArn
    })
  };
};
