"""Unit and Integration Tests for Cortensor Sentinel."""

import unittest
from pathlib import Path
from sentinel.tools.contract_auditor import analyze_solidity_code
from sentinel.tools.pouw_calculator import calculate_cortensor_rebate
from sentinel.tools.session_validator import verify_cortensor_session
from sentinel.agent import SentinelAgent


class TestSentinel(unittest.TestCase):
    def test_vulnerable_bank_audit(self):
        contract_file = Path("tests/sample_contracts/VulnerableBank.sol")
        code = contract_file.read_text(encoding="utf-8")
        result = analyze_solidity_code(code, "VulnerableBank")

        self.assertGreaterEqual(result["total_findings"], 3)
        self.assertGreaterEqual(result["critical_count"], 1)
        self.assertLess(result["audit_score"], 50)
        self.assertTrue(any(f["vulnerability_id"] == "VULN-001" for f in result["findings"]))
        self.assertTrue(any(f["vulnerability_id"] == "VULN-002" for f in result["findings"]))

    def test_secure_vault_audit(self):
        contract_file = Path("tests/sample_contracts/SecureVault.sol")
        code = contract_file.read_text(encoding="utf-8")
        result = analyze_solidity_code(code, "SecureVault")

        self.assertEqual(result["critical_count"], 1) # Contains CEI transfer flagged for review
        self.assertEqual(result["high_count"], 0)
        self.assertGreaterEqual(result["audit_score"], 60)

    def test_pouw_calculation(self):
        res = calculate_cortensor_rebate(
            gas_consumed=50000,
            base_fee_gwei=30.0,
            validator_node_tier="alpha-tier-1",
            cor_price_usd=0.15,
            eth_price_usd=2600.0
        )

        self.assertEqual(res["total_rebate_eth"], 0.000075)
        self.assertEqual(res["cor_reward_estimate"], 1.3)
        self.assertEqual(res["rebate_percentage"], 5.0)

    def test_session_hash_verification(self):
        res = verify_cortensor_session(
            session_id="ses-100",
            task_id="task-200",
            input_payload="hello",
            output_payload="world"
        )

        self.assertTrue(res["is_valid_erc8004"])
        self.assertEqual(len(res["task_root"]), 64)
        self.assertEqual(len(res["session_root"]), 64)
        self.assertEqual(res["status"], "VERIFIED_VALID")

    def test_sentinel_agent_workflow(self):
        agent = SentinelAgent(db_path=":memory:")
        code = Path("tests/sample_contracts/SecureVault.sol").read_text(encoding="utf-8")
        report = agent.run_security_workflow(
            contract_code=code,
            contract_name="SecureVault",
            gas_used=40000,
            base_fee_gwei=20.0
        )

        self.assertTrue(report.report_id.startswith("sentinel-"))
        self.assertIsNotNone(report.audit_results)
        self.assertIsNotNone(report.pouw_results)
        self.assertIsNotNone(report.session_results)
        self.assertGreater(report.execution_time_ms, 0)
        self.assertGreater(len(report.summary_text), 20)


if __name__ == "__main__":
    unittest.main()
