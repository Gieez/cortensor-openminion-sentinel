"""Rich Terminal Interface for Cortensor Sentinel."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Any, Dict, List

console = Console()


def print_banner():
    banner = """[bold cyan]
   ______           __                                 _____            __  _            __
  / ____/___  _____/ /____  ____  _________  _____    / ___/___  ____  / /_(_)___  ___  / /
 / /   / __ \/ ___/ __/ _ \/ __ \/ ___/ __ \/ ___/    \__ \/ _ \/ __ \/ __/ / __ \/ _ \/ / 
/ /___/ /_/ / /  / /_/  __/ / / (__  ) /_/ / /        ___/ /  __/ / / / /_/ / / / /  __/ /  
\____/\____/_/   \__/\___/_/ /_/____/\____/_/        /____/\___/_/ /_/\__/_/_/ /_/\___/_/   
[/bold cyan]
[bold white]Autonomous Web3 Security Sentinel & PoUW Triage Agent[/bold white]
[green]Powered by OpenMinion 0.1 Python SDK | Cortensor Mainnet Full Alpha[/green]
"""
    console.print(Panel(banner, border_style="cyan"))


def print_audit_table(audit_data: Dict[str, Any]):
    score = audit_data.get("audit_score", 100)
    score_color = "green" if score >= 80 else ("yellow" if score >= 50 else "red")
    
    table = Table(title=f"Smart Contract Security Audit Findings (Score: [{score_color}]{score}/100[/{score_color}])", border_style="cyan")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Severity", width=12)
    table.add_column("Line", width=6)
    table.add_column("Vulnerability", style="bold")
    table.add_column("Remediation", style="green")

    for f in audit_data.get("findings", []):
        sev = f.get("severity", "INFO")
        sev_style = {
            "CRITICAL": "[bold red]CRITICAL[/bold red]",
            "HIGH": "[red]HIGH[/red]",
            "MEDIUM": "[yellow]MEDIUM[/yellow]",
            "LOW": "[blue]LOW[/blue]",
            "INFO": "[dim]INFO[/dim]"
        }.get(sev, sev)

        table.add_row(
            f.get("vulnerability_id", "-"),
            sev_style,
            str(f.get("line_number", "-")),
            f.get("title", ""),
            f.get("remediation", "")
        )

    console.print(table)


def print_pouw_table(pouw_data: Dict[str, Any]):
    table = Table(title="Cortensor PoUW Gas Rebate & Incentive Estimation", border_style="magenta")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="cyan")

    table.add_row("Gas Consumed", f"{pouw_data.get('gas_consumed', 0):,} units")
    table.add_row("Base Fee", f"{pouw_data.get('base_fee_gwei', 0.0)} Gwei")
    table.add_row("Rebate Tier", f"{pouw_data.get('validator_node_tier', '-')} ({pouw_data.get('rebate_percentage', 0.0)}%)")
    table.add_row("Total ETH Rebate", f"{pouw_data.get('total_rebate_eth', 0.0):.8f} ETH")
    table.add_row("$COR Token Price", f"${pouw_data.get('cor_exchange_rate_usd', 0.15):.2f} USD")
    table.add_row("Estimated $COR Reward", f"[bold green]{pouw_data.get('cor_reward_estimate', 0.0):.4f} $COR[/bold green]")

    console.print(table)


def print_session_table(session_data: Dict[str, Any]):
    table = Table(title="Cortensor ERC-8004 Session & TaskRoot Verification", border_style="green")
    table.add_column("Property", style="bold")
    table.add_column("Hash / Value", style="white")

    table.add_row("Session ID", session_data.get("session_id", "-"))
    table.add_row("Task ID", session_data.get("task_id", "-"))
    table.add_row("Input Hash", session_data.get("input_hash", "-"))
    table.add_row("Output Hash", session_data.get("output_hash", "-"))
    table.add_row("Computed TaskRoot", f"[cyan]{session_data.get('task_root', '-')}[/cyan]")
    table.add_row("Computed SessionRoot", f"[yellow]{session_data.get('session_root', '-')}[/yellow]")
    
    status = session_data.get("status", "")
    status_text = f"[bold green]{status}[/bold green]" if session_data.get("is_valid_erc8004") else f"[bold red]{status}[/bold red]"
    table.add_row("Integrity Status", status_text)

    console.print(table)
