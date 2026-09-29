from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Step Functions Task: Validates policy number eligibility and coverage limits.
    """
    policy_number = event.get("policy_number", "")
    claim_amount = float(event.get("estimated_damage_amount", 0.0))

    # Basic business rule validation
    is_valid_format = policy_number.startswith("POL-") or len(policy_number) >= 8
    is_within_limit = claim_amount <= 500000.0

    if not is_valid_format:
        return {
            **event,
            "validation_passed": False,
            "rejection_reason": "Invalid Policy Identifier Format"
        }

    if not is_within_limit:
        return {
            **event,
            "validation_passed": False,
            "rejection_reason": "Estimated claim amount exceeds automated policy ceiling"
        }

    return {
        **event,
        "validation_passed": True,
        "policy_status": "ACTIVE_IN_FORCE",
        "deductible_amount": 500.0
    }
