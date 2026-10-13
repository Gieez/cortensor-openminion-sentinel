<p align="center">
  <h1 align="center">🛡️ Cortensor Web3 Sentinel</h1>
  <p align="center">
    <strong>Autonomous Smart Contract Security Auditor & PoUW Gas Rebate Triage Agent</strong><br>
    Built with the <strong>OpenMinion 0.1 Python SDK</strong> for <strong>Cortensor Mainnet Full Alpha</strong> (DoraHacks Round #2418)
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenMinion-0.1.4-blue.svg" alt="OpenMinion 0.1.4">
  <img src="https://img.shields.io/badge/Python-3.11+-brightgreen.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Network-Cortensor_Mainnet_Alpha-orange.svg" alt="Cortensor Alpha">
  <img src="https://img.shields.io/badge/License-Apache--2.0-lightgrey.svg" alt="Apache 2.0">
</p>

---

## 📌 Executive Summary

**Cortensor Web3 Sentinel** is an autonomous security agent designed for the **Cortensor Mainnet Full Alpha** ecosystem. It bridges decentralized AI compute with Web3 security auditing and Proof-of-Useful-Work (PoUW) economic validation.

Using the **OpenMinion 0.1 Python SDK**, the Sentinel agent:
1. **Performs Automated Static Security Audits** on Solidity smart contracts (detecting reentrancy, dangerous `tx.origin` authorization, unchecked calls, and missing zero-address validation).
2. **Computes Cortensor PoUW Gas Rebates**, calculating ETH saved and equivalent **$COR token validator rewards** according to Cortensor node tier economics.
3. **Validates TaskRoot & SessionRoot** cryptographic integrity compliant with the **ERC-8004** decentralized execution fabric specification.
4. **Synthesizes Risk Verdicts** with durable SQLite session persistence, providing auditable on-chain readiness telemetry.

---

## ⚡ Quick Start (1-Line Execution)

### Prerequisites
- Python 3.11+
- Virtual environment (recommended: `uv` or `python -m venv`)

### 1-Line Run (Demo Mode)

```bash
git clone https://github.com/Gieez/cortensor-openminion-sentinel.git
cd cortensor-openminion-sentinel
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_sentinel.py --demo
```

### Run Custom Contract Audit

```bash
# Audit a vulnerable contract sample
python run_sentinel.py tests/sample_contracts/VulnerableBank.sol

# Audit a secure vault with custom gas and validator tier
python run_sentinel.py tests/sample_contracts/SecureVault.sol --gas 120000 --fee 35.0 --tier alpha-tier-2
```

### Run Automated Test & Benchmark Suite

```bash
# Run unit & integration tests
python -m unittest tests/test_sentinel.py

# Run latency & building blocks benchmark
python benchmark_run.py
```

---

## 🏗️ Architecture & Workflow

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CORTENSOR SENTINEL ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────────────────┘

       [ Developer / Protocol Operator ]
                       │
                       ▼
       ┌────────────────────────────────┐
       │     run_sentinel.py (CLI)      │
       └────────────────┬───────────────┘
                        │
                        ▼
   ┌───────────────────────────────────────────────┐
   │          OpenMinion 0.1 Python SDK            │
   │  ┌─────────────────────────────────────────┐  │
   │  │   Agent (openminion.api.agent)          │  │
   │  │   • Instructions & System Prompt        │  │
   │  │   • Tool Registry & Dynamic Dispatch    │  │
   │  │   • Session Lease & Memory Assembly     │  │
   │  └────────────────────┬────────────────────┘  │
   │                       │                       │
   │      ┌────────────────┴───────────────┐       │
   │      ▼                                ▼       │
   │ ┌───────────────┐             ┌─────────────┐ │
   │ │CortensorPortal│             │Local Router │ │
   │ │ (OpenAI Chat) │             │ (Completions)││
   │ └───────────────┘             └─────────────┘ │
   └───────────────────────┬───────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Tool 1:       │   │ Tool 2:       │   │ Tool 3:       │
│ contract_audit│   │ pouw_calc     │   │ session_valid │
│ AST & Regex   │   │ Gas Rebate &  │   │ ERC-8004 Root │
│ Vulnerabilities│  │ $COR Rewards  │   │ Cryptography  │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │       SentinelStorage (SQLite)        │
        │    • Audit Runs • PoUW • Hashes       │
        └───────────────────┬───────────────────┘
                            ▼
        ┌───────────────────────────────────────┐
        │      Rich Console UI & Report         │
        └───────────────────────────────────────┘
```

---

## 🧪 OpenMinion Building Blocks Tested

During the design and real execution of the Sentinel Agent, we comprehensively tested OpenMinion 0.1.4's core primitives across agent execution, tool contracts, configuration, storage, and networking adapters.

| Building Block | OpenMinion Module | Status | Observed Behavior & Findings |
| :--- | :--- | :---: | :--- |
| **Agent API** | `openminion.api.Agent` | ✅ **PASS** | Session context, instructions binding, and context-manager lifecycle (`with Agent(...)`) operate reliably. |
| **Tool Decorator** | `@tool` (`openminion.tools`) | ✅ **PASS** | Schema introspection correctly derives `args_model` and `ToolDecl` from Python type hints and docstrings. |
| **Cortensor Provider** | `CortensorProvider` | ⚠️ **PATCHED** | Native adapter supports `cortensor_completion` and `openai_chat` modes. Discovered SSE streaming hang when flag was omitted (see Bug Report #1). |
| **Storage Core** | `openminion-storage` | ✅ **PASS** | SQLite schema bootstrap with Alembic migrations v1-v11 completes cleanly. Bitemporal records and state persist correctly. |
| **Diagnostics** | `openminion doctor` | ⚠️ **ROUGH EDGE** | Normalizes 27 system probes. Flagged Windows NTFS file permissions as world-writable due to POSIX mode translation. |
| **Session Leases** | `SessionStore` | ✅ **PASS** | `acquire_session_turn_lease` prevents concurrent race conditions on SQLite session files with TTL expiration. |

---

## 🔍 Bug Reports & Rough Edges Discovered

As requested in the DoraHacks Hackathon #5 brief, here is our transparent report on what broke, the root cause, and our implemented fixes:

### Bug #1: Missing `stream: False` in `CortensorProvider._build_openai_chat_payload`
- **Location:** `openminion.modules.llm.providers.cortensor.adapter.py`, line 526.
- **Symptom:** When connecting to OpenAI-compatible routers or proxies that default to SSE streaming (like 9Router or custom proxy nodes), the client hung indefinitely at `urllib.request.urlopen` / `socket.recv_into`.
- **Root Cause:** In `_build_openai_chat_payload`, `payload["stream"] = False` was omitted, causing streaming-by-default endpoints to return chunked `data: {...}` lines which the non-streaming JSON reader could not parse.
- **Fix:** Injected `payload["stream"] = False` into `_build_openai_chat_payload`. Included in our `patch_openminion.py` script.

### Bug #2: Config Shadowing between `providers` and `system.providers`
- **Location:** `openminion.base.config.manager.ConfigManager` / `agents.json`.
- **Symptom:** Setting `providers.cortensor.base_url` or `model` in `agents.json` had no effect; the agent continued attempting connection to `127.0.0.1:8080`.
- **Root Cause:** `agents.json` contains duplicate dictionaries at both `cfg["providers"]` and `cfg["system"]["providers"]`. Internal loader prioritized `system.providers`, silently ignoring user modifications in root `providers`.
- **Recommendation:** Deprecate or unify `system.providers` so that single-point edits in `providers` take immediate effect.

### Bug #3: Tool Call Response Misclassified as `EMPTY_PAYLOAD`
- **Location:** `openminion.modules.llm.providers.cortensor.adapter._parse_response_payload`.
- **Symptom:** When an LLM model returned valid `tool_calls` but `message.content` was `null` (standard OpenAI function-calling format), the adapter triggered `_raise_empty_cortensor_response` and entered a retry loop up to 420 seconds.
- **Root Cause:** `_response_has_text_or_tool_calls` checked for text before verifying whether tool definitions matched allowed tools. If tool names weren't pre-resolved in request metadata, `tool_calls` was treated as empty.
- **Recommendation:** Inspect `message.tool_calls` array independently of `message.content` before asserting empty payload.

### Bug #4: False Positive World-Writable Warnings on Windows
- **Location:** `openminion.modules.policy.doctor.probes`.
- **Symptom:** `openminion doctor` issued 3 `WARN` severity alerts stating that `.openminion/agents.json` and storage directories were world-writable (`0o666` and `0o777`).
- **Root Cause:** On Windows, Python's `os.stat().st_mode` maps ACL permissions to standard POSIX octals, triggering Unix-style world-writable warnings on NTFS.
- **Recommendation:** Check `sys.platform == "win32"` and skip or adapt octal permission audits on Windows environments.

---

## 📊 Benchmark Telemetry

Reproduced using `python benchmark_run.py`:

| Component / Subsystem | Operation | Measured Latency | Verification Status |
| :--- | :--- | :---: | :---: |
| **Tool: contract_auditor** | AST & Regex Static Scan (40 lines Solidity) | **1.09 ms** | PASS (Detected 3 findings, Score: 35/100) |
| **Tool: pouw_calculator** | PoUW Gas Rebate (Tier-2 Multiplier) | **0.02 ms** | PASS (3.8307 $COR reward calculated) |
| **Tool: session_validator** | ERC-8004 TaskRoot + SessionRoot Hashing | **0.06 ms** | PASS (Deterministic 64-char hex root) |
| **Storage Engine** | SQLite Run Insert & History Retrieval | **2.88 ms** | PASS (Verified run record persistence) |
| **End-to-End Orchestrator** | Complete Sentinel Audit & Synthesis Turn | **21.69 ms** | PASS (Full structured report generated) |

---

## 💡 What We Learned & Feedback for Cortensor Core

1. **Local-First Architecture is Exceptional for Web3:** OpenMinion's approach of keeping session logs, SQLite history, and tool policies on the local machine provides a strong privacy and audit boundary for security-sensitive Web3 smart contract analysis.
2. **First-Class Support for Cortensor ERC-8004:** Cortensor's TaskRoot and SessionRoot model allows autonomous agents to submit provable execution receipts. We encourage adding a dedicated `cortensor.erc8004` helper module into the core OpenMinion Python SDK to make hashing and validation trivial for all builders.
3. **Streamlined Provider Configuration:** Consolidating `agents.json` into a single declarative YAML or JSON format without `system.` nesting will significantly reduce developer onboarding friction.
4. **Transport Timeout Granularity:** Allowing per-request transport timeout overrides (`agent.run(..., timeout_seconds=15)`) to propagate directly to HTTP socket connection timeouts prevents hanging runs when remote endpoints degrade.

---

## 📁 Repository Structure

```text
cortensor-openminion-sentinel/
├── README.md                          # Comprehensive Documentation & Audit Report
├── requirements.txt                   # Dependency specifications
├── pyproject.toml                     # Python package metadata
├── patch_openminion.py                # Automatic fix for OpenMinion 0.1.4 SSE hang
├── run_sentinel.py                    # 1-Line CLI entrypoint & interactive demo
├── benchmark_run.py                   # Automated benchmark metrics generator
├── config/
│   ├── agents.json                    # OpenMinion agents and provider configurations
│   └── sentinel.yaml                  # Sentinel domain thresholds & PoUW parameters
├── sentinel/
│   ├── __init__.py
│   ├── agent.py                       # OpenMinion runtime orchestrator & fallback
│   ├── models.py                      # Pydantic schemas (AuditReport, PoUW, ERC-8004)
│   ├── tools/
│   │   ├── __init__.py                # Exported @tool decorated functions
│   │   ├── contract_auditor.py        # Static EVM vulnerability scanner
│   │   ├── pouw_calculator.py         # PoUW gas rebate calculator
│   │   └── session_validator.py       # ERC-8004 TaskRoot & SessionRoot validator
│   ├── storage/
│   │   └── history.py                 # SQLite persistence for runs and history
│   └── ui/
│       └── console.py                 # Rich terminal tables and dashboard UI
└── tests/
    ├── sample_contracts/
    │   ├── VulnerableBank.sol         # Test sample with reentrancy & tx.origin
    │   └── SecureVault.sol            # Test sample with ReentrancyGuard & CEI
    └── test_sentinel.py               # Automated unittest test suite
```

---

## 📄 License

Apache License 2.0. Built by **Gieez** for the Cortensor OpenMinion Builder Round (DoraHacks #2418).
