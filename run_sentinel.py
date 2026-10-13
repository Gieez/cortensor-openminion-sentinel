#!/usr/bin/env python3
"""Cortensor Sentinel CLI & Interactive Demo Runner.

Usage:
  python run_sentinel.py --demo
  python run_sentinel.py tests/sample_contracts/VulnerableBank.sol
  python run_sentinel.py tests/sample_contracts/SecureVault.sol --gas 120000 --tier alpha-tier-2
"""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from sentinel.agent import SentinelAgent
from sentinel.ui.console import (
    print_banner,
    print_audit_table,
    print_pouw_table,
    print_session_table,
)

console = Console()


def run_demo():
    print_banner()
    console.print("\n[bold yellow]>>> Running Cortensor Sentinel End-to-End Workflow Demo...[/bold yellow]\n")

    vulnerable_contract_path = Path("tests/sample_contracts/VulnerableBank.sol")
    if not vulnerable_contract_path.exists():
        console.print("[red]Sample contract tests/sample_contracts/VulnerableBank.sol not found.[/red]")
        sys.exit(1)

    code = vulnerable_contract_path.read_text(encoding="utf-8")
    agent = SentinelAgent()

    console.print("[cyan][1/3] Initiating Security Audit on 'VulnerableBank.sol'...[/cyan]")
    report = agent.run_security_workflow(
        contract_code=code,
        contract_name="VulnerableBank",
        gas_used=85000,
        base_fee_gwei=28.5,
        validator_tier="alpha-tier-1"
    )

    # Print Visual Panels
    if report.audit_results:
        print_audit_table(report.audit_results.model_dump())

    console.print("\n[cyan][2/3] Computing Cortensor PoUW Gas Rebates & Validator Incentives...[/cyan]")
    if report.pouw_results:
        print_pouw_table(report.pouw_results.model_dump())

    console.print("\n[cyan][3/3] Verifying Cortensor ERC-8004 TaskRoot and SessionRoot Integrity...[/cyan]")
    if report.session_results:
        print_session_table(report.session_results.model_dump())

    # Print Final Agent Synthesis
    console.print("\n[bold magenta]=== OpenMinion Agent Autonomous Synthesis & Verdict ===[/bold magenta]")
    console.print(Panel(
        report.summary_text,
        title=f"Report ID: {report.report_id} (Execution: {report.execution_time_ms}ms | Provider: {report.model_provider})",
        border_style="magenta"
    ))

    console.print("\n[bold green]✓ Demo completed successfully! Run history logged to SQLite database.[/bold green]\n")


def main():
    parser = argparse.ArgumentParser(description="Cortensor Sentinel - Autonomous Web3 Security & PoUW Agent")
    parser.add_argument("contract", nargs="?", default="", help="Path to Solidity smart contract file")
    parser.add_argument("--demo", action="store_true", help="Run full automated demo with sample contracts")
    parser.add_argument("--gas", type=int, default=85000, help="Estimated gas consumed for PoUW calculation")
    parser.add_argument("--fee", type=float, default=28.5, help="Network base fee in Gwei")
    parser.add_argument("--tier", default="alpha-tier-1", help="Cortensor validator tier (alpha-tier-1, alpha-tier-2)")
    parser.add_argument("--config", default="", help="Path to custom OpenMinion agents.json config")

    args = parser.parse_args()

    if args.demo or not args.contract:
        run_demo()
        return

    contract_path = Path(args.contract)
    if not contract_path.exists():
        console.print(f"[red]Error: Contract file '{args.contract}' not found.[/red]")
        sys.exit(1)

    print_banner()
    code = contract_path.read_text(encoding="utf-8")
    contract_name = contract_path.stem

    agent = SentinelAgent(config_path=args.config or None)
    console.print(f"[cyan]Analyzing '{contract_path.name}' with Cortensor Sentinel...[/cyan]")
    
    report = agent.run_security_workflow(
        contract_code=code,
        contract_name=contract_name,
        gas_used=args.gas,
        base_fee_gwei=args.fee,
        validator_tier=args.tier
    )

    if report.audit_results:
        print_audit_table(report.audit_results.model_dump())
    if report.pouw_results:
        print_pouw_table(report.pouw_results.model_dump())
    if report.session_results:
        print_session_table(report.session_results.model_dump())

    console.print("\n[bold magenta]=== OpenMinion Agent Autonomous Synthesis ===[/bold magenta]")
    console.print(Panel(
        report.summary_text,
        title=f"Verdict: {report.report_id} ({report.execution_time_ms}ms)",
        border_style="magenta"
    ))


if __name__ == "__main__":
    main()
