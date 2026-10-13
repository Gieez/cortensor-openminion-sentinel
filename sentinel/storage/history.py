"""SQLite Storage for Cortensor Sentinel Runs and Audit History."""

import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SentinelStorage:
    def __init__(self, db_path: str = "sentinel_history.db"):
        self.db_path = str(db_path)
        self._conn = None
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:")
        self._init_db()

    def _get_connection(self):
        if self._conn is not None:
            return self._conn
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE,
                session_id TEXT,
                provider TEXT,
                model TEXT,
                prompt TEXT,
                response TEXT,
                audit_score INTEGER,
                critical_count INTEGER,
                high_count INTEGER,
                execution_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pouw_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                gas_consumed INTEGER,
                base_fee_gwei REAL,
                rebate_eth REAL,
                cor_reward REAL,
                validator_tier TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        if self._conn is None:
            conn.close()

    def record_run(
        self,
        run_id: str,
        session_id: str,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        audit_score: Optional[int] = None,
        critical_count: int = 0,
        high_count: int = 0,
        execution_time_ms: int = 0
    ):
        conn = self._get_connection()
        conn.execute("""
            INSERT OR REPLACE INTO audit_runs 
            (run_id, session_id, provider, model, prompt, response, audit_score, critical_count, high_count, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, session_id, provider, model, prompt, response, 
            audit_score, critical_count, high_count, execution_time_ms
        ))
        conn.commit()
        if self._conn is None:
            conn.close()

    def record_pouw(
        self,
        run_id: str,
        gas_consumed: int,
        base_fee_gwei: float,
        rebate_eth: float,
        cor_reward: float,
        validator_tier: str
    ):
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO pouw_records
            (run_id, gas_consumed, base_fee_gwei, rebate_eth, cor_reward, validator_tier)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (run_id, gas_consumed, base_fee_gwei, rebate_eth, cor_reward, validator_tier))
        conn.commit()
        if self._conn is None:
            conn.close()

    def list_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM audit_runs ORDER BY id DESC LIMIT ?", (limit,))
        results = [dict(row) for row in cursor.fetchall()]
        if self._conn is None:
            conn.close()
        return results
