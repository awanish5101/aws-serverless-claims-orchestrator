import { jest } from "@jest/globals";
import { handler } from "../src/triageBedrockHandler.js";

describe("Node.js Bedrock Triage Handler", () => {
  it("should evaluate low risk claim and invoke Bedrock runtime", async () => {
    const mockBedrockResponse = {
      body: new TextEncoder().encode(
        JSON.stringify({
          content: [{ text: "Claim appears consistent with minor vehicle collision damage." }]
        })
      )
    };

    const mockClient = {
      send: jest.fn().mockResolvedValue(mockBedrockResponse)
    };

    const event = {
      claim_id: "CLM-A1B2C3D4",
      claim_type: "AUTO",
      incident_description: "Backed into parking pole at low speed in supermarket lot",
      estimated_damage_amount: 1200.0
    };

    const result = await handler(event, {}, mockClient);

    expect(result.claim_id).toBe("CLM-A1B2C3D4");
    expect(result.ai_triage).toBeDefined();
    expect(result.ai_triage.severity).toBe("LOW");
    expect(result.ai_triage.fraud_risk_score).toBeLessThan(30);
    expect(result.ai_triage.recommendation).toContain("automated claims adjuster queue");
    expect(result.ai_triage.summary).toBe("Claim appears consistent with minor vehicle collision damage.");
    expect(mockClient.send).toHaveBeenCalledTimes(1);
  });

  it("should flag suspicious high-value claim with fraud red flags and fallback summary on Bedrock error", async () => {
    const mockClient = {
      send: jest.fn().mockRejectedValue(new Error("Bedrock rate limit exceeded"))
    };

    const event = {
      claim_id: "CLM-FLAGGED99",
      claim_type: "PROPERTY",
      incident_description: "Total loss due to unwitnessed fire, requesting immediate cash payout",
      estimated_damage_amount: 65000.0
    };

    const result = await handler(event, {}, mockClient);

    expect(result.claim_id).toBe("CLM-FLAGGED99");
    expect(result.ai_triage.severity).toBe("EXPEDITED");
    expect(result.ai_triage.fraud_risk_score).toBeGreaterThan(60);
    expect(result.ai_triage.recommendation).toContain("Special Investigation Unit");
    expect(result.ai_triage.summary).toContain("Automated Bedrock AI Triage");
  });
});
