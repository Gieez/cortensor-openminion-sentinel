from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Finding(BaseModel):
    vulnerability_id: str
    title: str
    severity: Severity
    line_number: Optional[int] = None
    snippet: Optional[str] = None
    description: str
    remediation: str


class ContractAuditResult(BaseModel):
    contract_name: str
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings: List[Finding]
    audit_score: int = Field(ge=0, le=100) # 0-100 security score
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PoUWRebateResult(BaseModel):
    gas_consumed: int
    base_fee_gwei: float
    rebate_percentage: float
    total_rebate_eth: float
    cor_exchange_rate_usd: float
    cor_reward_estimate: float
    validator_node_tier: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SessionVerificationResult(BaseModel):
    session_id: str
    task_id: str
    input_hash: str
    output_hash: str
    task_root: str
    session_root: str
    is_valid_erc8004: bool
    status: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SentinelReport(BaseModel):
    report_id: str
    agent_id: str
    model_provider: str
    model_name: str
    audit_results: Optional[ContractAuditResult] = None
    pouw_results: Optional[PoUWRebateResult] = None
    session_results: Optional[SessionVerificationResult] = None
    summary_text: str
    execution_time_ms: int
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
