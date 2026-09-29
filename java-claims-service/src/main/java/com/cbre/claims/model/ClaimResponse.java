package com.cbre.claims.model;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.Instant;

@Schema(description = "Synchronous response returned upon claim submission")
public class ClaimResponse {

    @Schema(description = "Globally unique claims tracking identifier", example = "CLM-8F3A29B1")
    private String claimId;

    @Schema(description = "Lifecycle processing status", example = "SUBMITTED")
    private String status;

    @Schema(description = "Timestamp when the record was received", example = "2026-09-29T06:30:00Z")
    private Instant receivedAt;

    @Schema(description = "AWS Step Functions execution ARN", example = "arn:aws:states:us-east-1:123456789012:execution:ClaimsOrchestrationWorkflow:CLM-8F3A29B1")
    private String executionArn;

    @Schema(description = "Human-readable status summary message", example = "Claim intake accepted; orchestration workflow initialized")
    private String message;

    public ClaimResponse() {}

    public ClaimResponse(String claimId, String status, Instant receivedAt, String executionArn, String message) {
        this.claimId = claimId;
        this.status = status;
        this.receivedAt = receivedAt;
        this.executionArn = executionArn;
        this.message = message;
    }

    public String getClaimId() { return claimId; }
    public void setClaimId(String claimId) { this.claimId = claimId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public Instant getReceivedAt() { return receivedAt; }
    public void setReceivedAt(Instant receivedAt) { this.receivedAt = receivedAt; }

    public String getExecutionArn() { return executionArn; }
    public void setExecutionArn(String executionArn) { this.executionArn = executionArn; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
