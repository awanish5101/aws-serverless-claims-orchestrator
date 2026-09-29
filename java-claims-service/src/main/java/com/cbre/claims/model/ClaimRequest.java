package com.cbre.claims.model;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.math.BigDecimal;

@Schema(description = "First Notice of Loss (FNOL) Claim Intake Payload")
public class ClaimRequest {

    @NotBlank(message = "Policy number is required")
    @Schema(description = "Active insurance policy identifier", example = "POL-STATEFARM-78901")
    private String policyNumber;

    @NotBlank(message = "Insured name is required")
    @Schema(description = "Primary policyholder full legal name", example = "Marcus Vance")
    private String insuredName;

    @NotBlank(message = "Claim type is required")
    @Schema(description = "Type of insurance claim (AUTO, PROPERTY, CASUALTY)", example = "AUTO")
    private String claimType;

    @NotNull(message = "Estimated damage amount is required")
    @DecimalMin(value = "0.01", message = "Estimated damage must be greater than zero")
    @Schema(description = "Initial estimated damage in USD", example = "4250.00")
    private BigDecimal estimatedDamageAmount;

    @NotBlank(message = "Incident description is required")
    @Schema(description = "Detailed statement of how the loss occurred", example = "Rear-ended at signal on Main Street during light precipitation")
    private String incidentDescription;

    public ClaimRequest() {}

    public ClaimRequest(String policyNumber, String insuredName, String claimType, BigDecimal estimatedDamageAmount, String incidentDescription) {
        this.policyNumber = policyNumber;
        this.insuredName = insuredName;
        this.claimType = claimType;
        this.estimatedDamageAmount = estimatedDamageAmount;
        this.incidentDescription = incidentDescription;
    }

    public String getPolicyNumber() { return policyNumber; }
    public void setPolicyNumber(String policyNumber) { this.policyNumber = policyNumber; }

    public String getInsuredName() { return insuredName; }
    public void setInsuredName(String insuredName) { this.insuredName = insuredName; }

    public String getClaimType() { return claimType; }
    public void setClaimType(String claimType) { this.claimType = claimType; }

    public BigDecimal getEstimatedDamageAmount() { return estimatedDamageAmount; }
    public void setEstimatedDamageAmount(BigDecimal estimatedDamageAmount) { this.estimatedDamageAmount = estimatedDamageAmount; }

    public String getIncidentDescription() { return incidentDescription; }
    public void setIncidentDescription(String incidentDescription) { this.incidentDescription = incidentDescription; }
}
