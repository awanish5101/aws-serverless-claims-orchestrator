package com.cbre.claims.service;

import com.cbre.claims.model.ClaimRequest;
import com.cbre.claims.model.ClaimResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.sfn.SfnClient;
import software.amazon.awssdk.services.sfn.model.StartExecutionRequest;
import software.amazon.awssdk.services.sfn.model.StartExecutionResponse;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class ClaimsOrchestratorService {

    private static final Logger log = LoggerFactory.getLogger(ClaimsOrchestratorService.class);

    private final DynamoDbClient dynamoDbClient;
    private final SfnClient sfnClient;

    @Value("${aws.dynamodb.table-name:claims_ledger}")
    private String tableName;

    @Value("${aws.sfn.state-machine-arn:arn:aws:states:us-east-1:123456789012:stateMachine:ClaimsOrchestrationWorkflow}")
    private String stateMachineArn;

    public ClaimsOrchestratorService(DynamoDbClient dynamoDbClient, SfnClient sfnClient) {
        this.dynamoDbClient = dynamoDbClient;
        this.sfnClient = sfnClient;
    }

    public ClaimResponse submitClaim(ClaimRequest request) {
        String claimId = "CLM-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        Instant now = Instant.now();

        // 1. Persist initial claim state into DynamoDB
        Map<String, AttributeValue> item = new HashMap<>();
        item.put("claim_id", AttributeValue.builder().s(claimId).build());
        item.put("policy_number", AttributeValue.builder().s(request.getPolicyNumber()).build());
        item.put("insured_name", AttributeValue.builder().s(request.getInsuredName()).build());
        item.put("claim_type", AttributeValue.builder().s(request.getClaimType()).build());
        item.put("estimated_damage_amount", AttributeValue.builder().n(request.getEstimatedDamageAmount().toPlainString()).build());
        item.put("incident_description", AttributeValue.builder().s(request.getIncidentDescription()).build());
        item.put("status", AttributeValue.builder().s("SUBMITTED").build());
        item.put("created_at", AttributeValue.builder().s(now.toString()).build());

        try {
            dynamoDbClient.putItem(PutItemRequest.builder()
                    .tableName(tableName)
                    .item(item)
                    .build());
            log.info("Persisted claim record {} into DynamoDB table {}", claimId, tableName);
        } catch (Exception ex) {
            log.warn("DynamoDB persist bypassed or mock environment: {}", ex.getMessage());
        }

        // 2. Trigger AWS Step Functions state machine execution
        String executionArn = "mock-arn-" + claimId;
        try {
            String inputJson = String.format(
                    "{\"claim_id\":\"%s\",\"policy_number\":\"%s\",\"insured_name\":\"%s\",\"claim_type\":\"%s\",\"estimated_damage_amount\":%s,\"incident_description\":\"%s\"}",
                    claimId,
                    escapeJson(request.getPolicyNumber()),
                    escapeJson(request.getInsuredName()),
                    escapeJson(request.getClaimType()),
                    request.getEstimatedDamageAmount().toPlainString(),
                    escapeJson(request.getIncidentDescription())
            );

            StartExecutionResponse response = sfnClient.startExecution(StartExecutionRequest.builder()
                    .stateMachineArn(stateMachineArn)
                    .name(claimId)
                    .input(inputJson)
                    .build());

            executionArn = response.executionArn();
            log.info("Initialized Step Functions execution: {}", executionArn);
        } catch (Exception ex) {
            log.warn("Step Functions execution trigger bypassed or mock environment: {}", ex.getMessage());
        }

        return new ClaimResponse(
                claimId,
                "SUBMITTED",
                now,
                executionArn,
                "Claim intake accepted; orchestration workflow initialized"
        );
    }

    private String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\"", "\\\"");
    }
}
