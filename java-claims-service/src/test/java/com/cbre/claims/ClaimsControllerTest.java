package com.cbre.claims;

import com.cbre.claims.model.ClaimRequest;
import com.cbre.claims.service.ClaimsOrchestratorService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.eventbridge.EventBridgeClient;
import software.amazon.awssdk.services.sfn.SfnClient;
import software.amazon.awssdk.services.sfn.model.StartExecutionRequest;
import software.amazon.awssdk.services.sfn.model.StartExecutionResponse;

import java.math.BigDecimal;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class ClaimsControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @MockBean
    private DynamoDbClient dynamoDbClient;

    @MockBean
    private SfnClient sfnClient;

    @MockBean
    private EventBridgeClient eventBridgeClient;

    @Test
    @DisplayName("GET /api/v1/claims/health should return UP status")
    void testHealthEndpoint() throws Exception {
        mockMvc.perform(get("/api/v1/claims/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.service").value("java-claims-service"))
                .andExpect(jsonPath("$.framework").value("Spring Boot 3.2"));
    }

    @Test
    @DisplayName("POST /api/v1/claims/intake with valid claim should return 202 Accepted")
    void testIntakeSuccess() throws Exception {
        when(sfnClient.startExecution(any(StartExecutionRequest.class)))
                .thenReturn(StartExecutionResponse.builder()
                        .executionArn("arn:aws:states:us-east-1:123456789012:execution:ClaimsWorkflow:test-exec")
                        .build());

        ClaimRequest request = new ClaimRequest(
                "POL-STATEFARM-9901",
                "Bruce Wayne",
                "AUTO",
                new BigDecimal("6800.50"),
                "Vehicle collided with highway barrier during midnight patrol"
        );

        mockMvc.perform(post("/api/v1/claims/intake")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.claimId").exists())
                .andExpect(jsonPath("$.status").value("SUBMITTED"))
                .andExpect(jsonPath("$.message").value("Claim intake accepted; orchestration workflow initialized"));
    }

    @Test
    @DisplayName("POST /api/v1/claims/intake with invalid input should return 400 Bad Request")
    void testIntakeValidationFailure() throws Exception {
        ClaimRequest invalidRequest = new ClaimRequest();
        invalidRequest.setInsuredName("Bruce Wayne");
        // Missing policyNumber, claimType, estimatedDamageAmount, incidentDescription

        mockMvc.perform(post("/api/v1/claims/intake")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(invalidRequest)))
                .andExpect(status().isBadRequest());
    }
}
