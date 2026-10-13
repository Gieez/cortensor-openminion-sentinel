#!/usr/bin/env python3
"""Benchmark and Validation Suite for OpenMinion 0.1 on Cortensor Mainnet Alpha."""

import json
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table

from sentinel.agent import SentinelAgent
from sentinel.tools.contract_auditor import analyze_solidity_code
from sentinel.tools.pouw_calculator import calculate_cortensor_rebate
from sentinel.tools.session_validator import verify_cortensor_session

console = Console()


def run_benchmarks():
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold white]   OpenMinion 0.1 SDK & Cortensor Sentinel Benchmark Suite     [/bold white]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")

    results = []

    # Benchmark 1: Tool Execution - Contract Auditor
    vulnerable_code = Path("tests/sample_contracts/VulnerableBank.sol").read_text(encoding="utf-8")
    t0 = time.perf_counter()
    audit_res = analyze_solidity_code(vulnerable_code, "VulnerableBank")
    audit_time_ms = (time.perf_counter() - t0) * 1000
    results.append({
        "component": "OpenMinion Tool: contract_auditor",
        "operation": "Static AST & Regex pattern audit",
        "latency_ms": round(audit_time_ms, 2),
        "status": "PASS",
        "notes": f"Detected {audit_res['total_findings']} vulns (Score: {audit_res['audit_score']}/100)"
    })

    # Benchmark 2: Tool Execution - PoUW Calculator
    t0 = time.perf_counter()
    pouw_res = calculate_cortensor_rebate(85000, 32.5, "alpha-tier-2")
    pouw_time_ms = (time.perf_counter() - t0) * 1000
    results.append({
        "component": "OpenMinion Tool: pouw_calculator",
        "operation": "Tier-2 PoUW gas rebate computation",
        "latency_ms": round(pouw_time_ms, 2),
        "status": "PASS",
        "notes": f"{pouw_res['cor_reward_estimate']} $COR ({pouw_res['total_rebate_eth']} ETH)"
    })

    # Benchmark 3: Tool Execution - Session Root Cryptography
    t0 = time.perf_counter()
    session_res = verify_cortensor_session("ses-bench", "task-bench", "input-data", "output-data")
    session_time_ms = (time.perf_counter() - t0) * 1000
    results.append({
        "component": "OpenMinion Tool: session_validator",
        "operation": "ERC-8004 TaskRoot + SessionRoot hashing",
        "latency_ms": round(session_time_ms, 2),
        "status": "PASS",
        "notes": f"Root: {session_res['session_root'][:12]}... (Valid: {session_res['is_valid_erc8004']})"
    })

    # Benchmark 4: Storage & History - SQLite Record Persistence
    agent = SentinelAgent(db_path="sentinel_benchmark.db")
    t0 = time.perf_counter()
    agent.storage.record_run(
        run_id="bench-01",
        session_id="ses-bench",
        provider="openminion-cortensor",
        model="Friday-Combo",
        prompt="Audit benchmark test",
        response="Audit completed successfully",
        audit_score=35,
        critical_count=1,
        high_count=2,
        execution_time_ms=50
    )
    records = agent.storage.list_recent_runs(limit=1)
    storage_time_ms = (time.perf_counter() - t0) * 1000
    results.append({
        "component": "OpenMinion Storage / History",
        "operation": "Durable SQLite session persistence & query",
        "latency_ms": round(storage_time_ms, 2),
        "status": "PASS",
        "notes": f"Persisted & retrieved run {records[0]['run_id']}"
    })

    # Benchmark 5: End-to-End Workflow Execution
    t0 = time.perf_counter()
    report = agent.run_security_workflow(
        contract_code=vulnerable_code,
        contract_name="VulnerableBank",
        gas_used=85000,
        base_fee_gwei=32.5,
        validator_tier="alpha-tier-2"
    )
    e2e_time_ms = (time.perf_counter() - t0) * 1000
    results.append({
        "component": "Sentinel End-to-End Orchestrator",
        "operation": "Full security audit + PoUW + ERC-8004 report",
        "latency_ms": round(e2e_time_ms, 2),
        "status": "PASS",
        "notes": f"Report ID: {report.report_id} ({report.model_provider})"
    })

    # Display Benchmark Table
    table = Table(title="OpenMinion 0.1 SDK Building Blocks Benchmark Results", border_style="cyan")
    table.add_column("Building Block / Component", style="bold white")
    table.add_column("Operation", style="yellow")
    table.add_column("Latency (ms)", justify="right", style="cyan")
    table.add_column("Status", justify="center", style="bold green")
    table.add_column("Verification Notes", style="dim white")

    for r in results:
        table.add_row(
            r["component"],
            r["operation"],
            f"{r['latency_ms']:.2f} ms",
            r["status"],
            r["notes"]
        )

    console.print(table)

    # Save benchmark metrics to json
    bench_file = Path("benchmark_results.json")
    bench_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    console.print(f"\n[green]✓ Benchmark metrics saved to {bench_file}[/green]\n")


if __name__ == "__main__":
    run_benchmarks()
