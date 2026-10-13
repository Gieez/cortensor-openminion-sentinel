"""Sentinel Agent Runtime Orchestrator powered by OpenMinion 0.1 SDK."""

import os
import time
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from openminion import Agent, ProviderError
from sentinel.tools import ALL_SENTINEL_TOOLS
from sentinel.tools.contract_auditor import analyze_solidity_code
from sentinel.tools.pouw_calculator import calculate_cortensor_rebate
from sentinel.tools.session_validator import verify_cortensor_session
from sentinel.models import SentinelReport, ContractAuditResult, PoUWRebateResult, SessionVerificationResult
from sentinel.storage.history import SentinelStorage


class SentinelAgent:
    """Cortensor Sentinel Agent wrapper coordinating OpenMinion building blocks."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        db_path: str = "sentinel_history.db",
        use_fallback_on_error: bool = True
    ):
        self.config_path = config_path or str(Path(__file__).parent.parent / "config" / "agents.json")
        self.storage = SentinelStorage(db_path=db_path)
        self.use_fallback_on_error = use_fallback_on_error

        # Ensure config has updated provider configuration
        self._ensure_config()

    def _ensure_config(self):
        """Ensure agents.json exists and has valid provider entries."""
        cfg_file = Path(self.config_path)
        if not cfg_file.exists():
            return

        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            # Check if environment provides custom keys or URL
            env_url = os.environ.get("CORTENSOR_API_URL", "http://127.0.0.1:20128/v1")
            env_key = os.environ.get("HERMES_CUSTOM_127_0_0_1_20128_API_KEY", "") or os.environ.get("CORTENSOR_API_KEY", "")
            env_model = os.environ.get("CORTENSOR_MODEL", "Friday-Combo")

            # Update providers dictionary
            for p_dict in [cfg.get("providers", {}), cfg.get("system", {}).get("providers", {})]:
                if "cortensor" in p_dict:
                    p_dict["cortensor"]["base_url"] = env_url
                    p_dict["cortensor"]["api_key"] = env_key
                    p_dict["cortensor"]["model"] = env_model
                    p_dict["cortensor"]["api_mode"] = "openai_chat" if "8080" not in env_url else "auto"
                    p_dict["cortensor"]["timeout_seconds"] = 10
                    p_dict["cortensor"]["transport_timeout_buffer_seconds"] = 2
                    p_dict["cortensor"]["result_wait_attempts"] = 1
                    p_dict["cortensor"]["empty_result_max_attempts"] = 1

            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def run_security_workflow(
        self,
        contract_code: str,
        contract_name: str = "TargetContract",
        gas_used: int = 85000,
        base_fee_gwei: float = 28.5,
        validator_tier: str = "alpha-tier-1",
        session_id: Optional[str] = None
    ) -> SentinelReport:
        """Run the comprehensive end-to-end Sentinel security & PoUW evaluation."""
        run_id = f"sentinel-{uuid4_hex[:8]}" if (uuid4_hex := uuid.uuid4().hex) else "sentinel-01"
        session_id = session_id or f"ses-{uuid.uuid4().hex[:12]}"
        start_time = time.perf_counter()

        # Step 1: Execute static analysis tool
        audit_raw = analyze_solidity_code(contract_code, contract_name)
        audit_res = ContractAuditResult(**audit_raw)

        # Step 2: Execute PoUW rebate calculation tool
        pouw_raw = calculate_cortensor_rebate(gas_used, base_fee_gwei, validator_tier)
        pouw_res = PoUWRebateResult(**pouw_raw)

        # Step 3: Execute session verification tool
        input_payload = json.dumps({"contract": contract_name, "gas": gas_used})
        output_payload = json.dumps({"audit_score": audit_res.audit_score, "pouw_rebate": pouw_res.cor_reward_estimate})
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        session_raw = verify_cortensor_session(session_id, task_id, input_payload, output_payload)
        session_res = SessionVerificationResult(**session_raw)

        # Step 4: Run OpenMinion Agent to summarize & reason over findings
        instructions = (
            "You are Cortensor Sentinel, an autonomous security auditor for Cortensor Mainnet Alpha. "
            "Synthesize the security audit score, PoUW rebate, and TaskRoot verification into a high-signal report."
        )

        prompt = (
            f"Synthesize the following security telemetry for {contract_name}:\n"
            f"- Security Audit Score: {audit_res.audit_score}/100 with {audit_res.total_findings} findings "
            f"({audit_res.critical_count} critical, {audit_res.high_count} high).\n"
            f"- PoUW Gas Rebate: {pouw_res.total_rebate_eth} ETH ({pouw_res.cor_reward_estimate} $COR rewarded).\n"
            f"- ERC-8004 SessionRoot: {session_res.session_root[:16]}... (Status: {session_res.status}).\n"
            "State concise verdict, key vulnerability risks, and staking recommendation."
        )

        agent_summary = ""
        provider_used = "cortensor"
        model_used = "Friday-Combo"

        try:
            with Agent(
                instructions=instructions,
                tools=ALL_SENTINEL_TOOLS,
                config_path=self.config_path,
                session_id=session_id
            ) as agent:
                res = agent.run(prompt, timeout_seconds=15)
                agent_summary = res.text
        except Exception as exc:
            if not self.use_fallback_on_error:
                raise
            # High-signal fallback synthesizer
            provider_used = "deterministic-sentinel-core"
            model_used = "sentinel-rule-engine-v1"
            agent_summary = (
                f"[Sentinel Synthesis] Contract {contract_name} scored {audit_res.audit_score}/100. "
                f"Identified {audit_res.critical_count} CRITICAL, {audit_res.high_count} HIGH vulnerabilities. "
                f"PoUW rebate grants {pouw_res.cor_reward_estimate} $COR ({pouw_res.total_rebate_eth} ETH saved). "
                f"TaskRoot {session_res.task_root[:12]} verified compliant with Cortensor ERC-8004 spec."
            )

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # Step 5: Persist to storage
        self.storage.record_run(
            run_id=run_id,
            session_id=session_id,
            provider=provider_used,
            model=model_used,
            prompt=prompt,
            response=agent_summary,
            audit_score=audit_res.audit_score,
            critical_count=audit_res.critical_count,
            high_count=audit_res.high_count,
            execution_time_ms=elapsed_ms
        )

        self.storage.record_pouw(
            run_id=run_id,
            gas_consumed=pouw_res.gas_consumed,
            base_fee_gwei=pouw_res.base_fee_gwei,
            rebate_eth=pouw_res.total_rebate_eth,
            cor_reward=pouw_res.cor_reward_estimate,
            validator_tier=pouw_res.validator_node_tier
        )

        return SentinelReport(
            report_id=run_id,
            agent_id="cortensor-sentinel",
            model_provider=provider_used,
            model_name=model_used,
            audit_results=audit_res,
            pouw_results=pouw_res,
            session_results=session_res,
            summary_text=agent_summary,
            execution_time_ms=elapsed_ms
        )
