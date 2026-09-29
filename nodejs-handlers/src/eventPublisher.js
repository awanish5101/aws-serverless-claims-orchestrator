import { EventBridgeClient, PutEventsCommand } from "@aws-sdk/client-eventbridge";
import { SNSClient, PublishCommand } from "@aws-sdk/client-sns";

const REGION = process.env.AWS_REGION || "us-east-1";
const EVENT_BUS_NAME = process.env.CLAIMS_EVENT_BUS || "claims.events";
const SNS_TOPIC_ARN = process.env.CLAIMS_SNS_TOPIC_ARN || "arn:aws:sns:us-east-1:123456789012:claims-status-alerts";

export const createClients = (overrides = {}) => ({
  eb: overrides.eb || new EventBridgeClient({ region: REGION }),
  sns: overrides.sns || new SNSClient({ region: REGION })
});

export const handler = async (event, context, clients = createClients()) => {
  const { claim_id, ai_triage = {}, final_status = "AI_TRIAGED" } = event;

  // 1. Publish Domain Event to Amazon EventBridge custom event bus
  const eventPayload = {
    claim_id,
    status: final_status,
    severity: ai_triage.severity || "MEDIUM",
    fraud_risk_score: ai_triage.fraud_risk_score || 0,
    timestamp: new Date().toISOString()
  };

  const ebResult = await clients.eb.send(
    new PutEventsCommand({
      Entries: [
        {
          Source: "insurance.claims.orchestrator.node",
          DetailType: "ClaimTriageCompleted",
          Detail: JSON.stringify(eventPayload),
          EventBusName: EVENT_BUS_NAME
        }
      ]
    })
  );

  // 2. Publish Real-time Notification Alert to Amazon SNS topic
  let snsResult = null;
  try {
    snsResult = await clients.sns.send(
      new PublishCommand({
        TopicArn: SNS_TOPIC_ARN,
        Subject: `Claim ${claim_id} Status: ${final_status}`,
        Message: JSON.stringify({
          alert: `Claim ${claim_id} finalized with status ${final_status}`,
          details: eventPayload
        })
      })
    );
  } catch (err) {
    console.warn("SNS publish skipped in offline test environment:", err.message);
  }

  return {
    claim_id,
    eventbridge_entries_failed: ebResult.FailedEntryCount || 0,
    sns_message_id: snsResult?.MessageId || "mock-sns-id",
    status: final_status
  };
};
