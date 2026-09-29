package com.cbre.claims.controller;

import com.cbre.claims.model.ClaimRequest;
import com.cbre.claims.model.ClaimResponse;
import com.cbre.claims.service.ClaimsOrchestratorService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/claims")
@Tag(name = "Claims Intake & Orchestration API", description = "Endpoints for FNOL intake, policy ingestion, and serverless workflow triggering")
public class ClaimsController {

    private final ClaimsOrchestratorService claimsOrchestratorService;

    public ClaimsController(ClaimsOrchestratorService claimsOrchestratorService) {
        this.claimsOrchestratorService = claimsOrchestratorService;
    }

    @PostMapping("/intake")
    @Operation(
            summary = "Submit a First Notice of Loss (FNOL) insurance claim",
            description = "Validates incoming policy payload, writes initial immutable record to DynamoDB ledger, and asynchronously invokes AWS Step Functions state machine."
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "202",
                    description = "Claim accepted and orchestration workflow triggered",
                    content = @Content(mediaType = "application/json", schema = @Schema(implementation = ClaimResponse.class))
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "Invalid payload or validation failure"
            ),
            @ApiResponse(
                    responseCode = "500",
                    description = "Internal orchestration or cloud provider failure"
            )
    })
    public ResponseEntity<ClaimResponse> intakeClaim(@Valid @RequestBody ClaimRequest request) {
        ClaimResponse response = claimsOrchestratorService.submitClaim(request);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(response);
    }

    @GetMapping("/health")
    @Operation(summary = "Microservice Health & Readiness Probe")
    public ResponseEntity<Map<String, String>> healthCheck() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "java-claims-service",
                "runtime", "Java 21 OpenJDK",
                "framework", "Spring Boot 3.2"
        ));
    }
}
