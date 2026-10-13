"""Smart Contract Static Security Audit Engine for EVM Bytecode/Solidity."""

import json
import re
from typing import Any, Dict, List
from sentinel.models import Finding, Severity, ContractAuditResult


def analyze_solidity_code(contract_code: str, contract_name: str = "TargetContract") -> Dict[str, Any]:
    """Analyze Solidity source code for critical vulnerabilities."""
    findings: List[Finding] = []
    lines = contract_code.splitlines()

    # 1. Check for Reentrancy (call.value or call{value:} followed by state update or without nonReentrant)
    for idx, line in enumerate(lines, start=1):
        if re.search(r'\.(call\.value|call\{value:)', line):
            # Check surrounding lines for state updates after call
            has_state_update_after = False
            for forward_idx in range(idx, min(idx + 10, len(lines))):
                forward_line = lines[forward_idx]
                if re.search(r'balances\[.*?\]\s*(-=|=|\+=)', forward_line) or re.search(r'\b(owner|totalBalance)\s*=', forward_line):
                    has_state_update_after = True
                    break

            findings.append(Finding(
                vulnerability_id="VULN-001",
                title="Potential Reentrancy Vulnerability (External Value Transfer)",
                severity=Severity.CRITICAL if has_state_update_after else Severity.HIGH,
                line_number=idx,
                snippet=line.strip(),
                description="Low-level call transferring ETH detected. If state updates occur after the external call or without reentrancy guard, attackers can drain contract funds.",
                remediation="Follow Checks-Effects-Interactions (CEI) pattern: update internal state before external calls. Use OpenZeppelin ReentrancyGuard nonReentrant modifier."
            ))

    # 2. Check for tx.origin authentication
    for idx, line in enumerate(lines, start=1):
        if re.search(r'tx\.origin\s*==', line) or re.search(r'require\(.*tx\.origin', line):
            findings.append(Finding(
                vulnerability_id="VULN-002",
                title="Dangerous Use of tx.origin for Authentication",
                severity=Severity.HIGH,
                line_number=idx,
                snippet=line.strip(),
                description="Using tx.origin for authorization makes the contract vulnerable to phishing attacks where an attacker tricks an authorized account into calling a malicious contract.",
                remediation="Replace tx.origin with msg.sender for sender authorization."
            ))

    # 3. Check for Unchecked Call Return Value
    for idx, line in enumerate(lines, start=1):
        if re.search(r'address\(.*?\)\.call\{', line) or re.search(r'\.call\(', line):
            if not re.search(r'(bool\s+\w+\s*,\s*|success\s*=|require\(|if\s*\()', line):
                findings.append(Finding(
                    vulnerability_id="VULN-003",
                    title="Unchecked Return Value of Low-Level Call",
                    severity=Severity.MEDIUM,
                    line_number=idx,
                    snippet=line.strip(),
                    description="Low-level call return value is not captured or verified. If the called contract fails or reverts, execution continues silently.",
                    remediation="Capture return value tuple `(bool success, bytes memory data) = ...` and assert `require(success, 'call failed')`."
                ))

    # 4. Check for Selfdestruct / Suicide
    for idx, line in enumerate(lines, start=1):
        if re.search(r'\b(selfdestruct|suicide)\s*\(', line):
            findings.append(Finding(
                vulnerability_id="VULN-004",
                title="Use of selfdestruct / suicide Instruction",
                severity=Severity.HIGH,
                line_number=idx,
                snippet=line.strip(),
                description="selfdestruct is deprecated in recent EVM forks (EIP-6780 / Dencun) and allows contract destruction if access control is flawed.",
                remediation="Remove selfdestruct. Design contracts with pausable or upgradeable patterns if deprecation is needed."
            ))

    # 5. Check for Missing Zero Address Validation
    for idx, line in enumerate(lines, start=1):
        if re.search(r'function\s+(setOwner|transferOwnership|initialize|setAdmin)\s*\(.*address\s+(\w+)', line):
            param_match = re.search(r'address\s+(\w+)', line)
            param_name = param_match.group(1) if param_match else "newOwner"
            # verify next 5 lines for zero check
            has_zero_check = False
            for forward_idx in range(idx, min(idx + 6, len(lines))):
                if re.search(rf'{param_name}\s*!=\s*address\(0\)', lines[forward_idx]) or re.search(rf'{param_name}\s*==\s*address\(0\)', lines[forward_idx]):
                    has_zero_check = True
                    break
            if not has_zero_check:
                findings.append(Finding(
                    vulnerability_id="VULN-005",
                    title="Missing Zero Address Validation on Privileged Setter",
                    severity=Severity.LOW,
                    line_number=idx,
                    snippet=line.strip(),
                    description=f"Privileged setter `{param_name}` lacks zero-address check. Accidental address(0) transfer leads to permanent loss of administrative privileges.",
                    remediation=f"Add `require({param_name} != address(0), 'zero address');` check."
                ))

    # Calculate audit score
    penalty = 0
    crit_count = 0
    high_count = 0
    med_count = 0
    low_count = 0

    for f in findings:
        if f.severity == Severity.CRITICAL:
            penalty += 40
            crit_count += 1
        elif f.severity == Severity.HIGH:
            penalty += 20
            high_count += 1
        elif f.severity == Severity.MEDIUM:
            penalty += 10
            med_count += 1
        elif f.severity == Severity.LOW:
            penalty += 5
            low_count += 1

    score = max(0, 100 - penalty)

    audit_result = ContractAuditResult(
        contract_name=contract_name,
        total_findings=len(findings),
        critical_count=crit_count,
        high_count=high_count,
        medium_count=med_count,
        low_count=low_count,
        findings=findings,
        audit_score=score
    )

    return audit_result.model_dump()
