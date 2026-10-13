"""Cortensor SessionRoot and TaskRoot Validator (ERC-8004 Spec)."""

import hashlib
import json
from typing import Any, Dict
from sentinel.models import SessionVerificationResult


def verify_cortensor_session(
    session_id: str,
    task_id: str,
    input_payload: str,
    output_payload: str,
    expected_session_root: str = ""
) -> Dict[str, Any]:
    """Verify cryptographically that a task execution conforms to Cortensor TaskRoot / SessionRoot spec."""
    input_hash = hashlib.sha256(input_payload.encode("utf-8")).hexdigest()
    output_hash = hashlib.sha256(output_payload.encode("utf-8")).hexdigest()

    # TaskRoot = sha256(task_id + ":" + input_hash + ":" + output_hash)
    task_leaf = f"{task_id}:{input_hash}:{output_hash}"
    task_root = hashlib.sha256(task_leaf.encode("utf-8")).hexdigest()

    # SessionRoot = sha256(session_id + ":" + task_root)
    computed_session_root = hashlib.sha256(f"{session_id}:{task_root}".encode("utf-8")).hexdigest()

    is_valid = True
    status = "VERIFIED_VALID"
    if expected_session_root:
        if expected_session_root.lower() == computed_session_root.lower():
            status = "VERIFIED_MATCHES_ONCHAIN_ROOT"
        else:
            is_valid = False
            status = "ROOT_MISMATCH_TAMPER_DETECTED"

    result = SessionVerificationResult(
        session_id=session_id,
        task_id=task_id,
        input_hash=input_hash,
        output_hash=output_hash,
        task_root=task_root,
        session_root=computed_session_root,
        is_valid_erc8004=is_valid,
        status=status
    )

    return result.model_dump()
