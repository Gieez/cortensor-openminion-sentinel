"""OpenMinion Tools for Cortensor Sentinel Agent."""

import json
from openminion import tool
from sentinel.tools.contract_auditor import analyze_solidity_code
from sentinel.tools.pouw_calculator import calculate_cortensor_rebate
from sentinel.tools.session_validator import verify_cortensor_session


@tool
def audit_smart_contract(contract_code: str, contract_name: str = "TargetContract") -> str:
    """Perform automated static security audit on Solidity smart contract code.
    
    Detects reentrancy, dangerous tx.origin authorization, unchecked calls, 
    deprecated selfdestruct, and missing zero-address validation.
    
    Returns structured JSON with vulnerability findings, line numbers, and security score.
    """
    result = analyze_solidity_code(contract_code, contract_name)
    return json.dumps(result, indent=2)


@tool
def calculate_gas_rebate(gas_consumed: int, base_fee_gwei: float, validator_tier: str = "alpha-tier-1") -> str:
    """Calculate the Cortensor PoUW (Proof of Useful Work) gas rebate in ETH and $COR token rewards.
    
    Returns structured JSON with gas cost, rebate percentage, ETH saved, and estimated $COR payout.
    """
    result = calculate_cortensor_rebate(gas_consumed, base_fee_gwei, validator_tier)
    return json.dumps(result, indent=2)


@tool
def verify_session_integrity(session_id: str, task_id: str, input_payload: str, output_payload: str) -> str:
    """Verify cryptographically that a task execution adheres to Cortensor TaskRoot and SessionRoot (ERC-8004 spec).
    
    Returns structured JSON with input/output hashes, computed TaskRoot, and SessionRoot verification status.
    """
    result = verify_cortensor_session(session_id, task_id, input_payload, output_payload)
    return json.dumps(result, indent=2)


ALL_SENTINEL_TOOLS = [
    audit_smart_contract,
    calculate_gas_rebate,
    verify_session_integrity,
]
