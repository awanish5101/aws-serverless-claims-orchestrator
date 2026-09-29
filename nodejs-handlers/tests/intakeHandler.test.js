import { jest } from "@jest/globals";
import { handler } from "../src/intakeHandler.js";

describe("Node.js Intake Handler", () => {
  it("should validate and persist valid claim submission", async () => {
    const mockDynamo = { send: jest.fn().mockResolvedValue({}) };
    const mockSfn = { send: jest.fn().mockResolvedValue({ executionArn: "arn:aws:states:exec-123" }) };

    const event = {
      body: JSON.stringify({
        policy_number: "POL-STATEFARM-555",
        insured_name: "Tony Stark",
        claim_type: "AUTO",
        estimated_damage_amount: 5200.0,
        incident_description: "Fender bender on highway"
      })
    };

    const response = await handler(event, {}, { dynamo: mockDynamo, sfn: mockSfn });

    expect(response.statusCode).toBe(202);
    const body = JSON.parse(response.body);
    expect(body.claim_id).toMatch(/^CLM-[A-Z0-9]{8}$/);
    expect(body.status).toBe("SUBMITTED");
    expect(mockDynamo.send).toHaveBeenCalledTimes(1);
  });

  it("should reject payload with missing required fields", async () => {
    const event = {
      body: JSON.stringify({
        insured_name: "Bruce Wayne"
        // missing policy_number, claim_type, estimated_damage_amount
      })
    };

    const response = await handler(event, {}, { dynamo: { send: jest.fn() }, sfn: { send: jest.fn() } });
    expect(response.statusCode).toBe(400);
    const body = JSON.parse(response.body);
    expect(body.error).toContain("Missing required claim fields");
  });
});
