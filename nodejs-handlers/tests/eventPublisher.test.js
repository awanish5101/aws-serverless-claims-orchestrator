import { jest } from "@jest/globals";
import { handler } from "../src/eventPublisher.js";

describe("Node.js Event Publisher Handler", () => {
  it("should publish triage completed event to EventBridge and notification to SNS", async () => {
    const mockEb = {
      send: jest.fn().mockResolvedValue({
        FailedEntryCount: 0,
        Entries: [{ EventId: "eb-event-999" }]
      })
    };

    const mockSns = {
      send: jest.fn().mockResolvedValue({
        MessageId: "sns-msg-12345"
      })
    };

    const event = {
      claim_id: "CLM-NODE1234",
      final_status: "AI_TRIAGED",
      ai_triage: {
        severity: "HIGH",
        fraud_risk_score: 34.5
      }
    };

    const result = await handler(event, {}, { eb: mockEb, sns: mockSns });

    expect(result.claim_id).toBe("CLM-NODE1234");
    expect(result.status).toBe("AI_TRIAGED");
    expect(result.eventbridge_entries_failed).toBe(0);
    expect(result.sns_message_id).toBe("sns-msg-12345");

    expect(mockEb.send).toHaveBeenCalledTimes(1);
    expect(mockSns.send).toHaveBeenCalledTimes(1);
  });

  it("should gracefully handle SNS offline or permission error and still complete event flow", async () => {
    const mockEb = {
      send: jest.fn().mockResolvedValue({
        FailedEntryCount: 0,
        Entries: [{ EventId: "eb-event-1000" }]
      })
    };

    const mockSns = {
      send: jest.fn().mockRejectedValue(new Error("SNS topic offline"))
    };

    const event = {
      claim_id: "CLM-NODE5678",
      final_status: "AUTO_APPROVED",
      ai_triage: {
        severity: "LOW",
        fraud_risk_score: 12.0
      }
    };

    const result = await handler(event, {}, { eb: mockEb, sns: mockSns });

    expect(result.claim_id).toBe("CLM-NODE5678");
    expect(result.status).toBe("AUTO_APPROVED");
    expect(result.sns_message_id).toBe("mock-sns-id");
    expect(mockEb.send).toHaveBeenCalledTimes(1);
  });
});
