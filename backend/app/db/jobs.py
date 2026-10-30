"""
AEGIS Persistent SQLite Job Store for HireCrew Seller API.
Provides thread-safe persistence, idempotency verification, and state transitions.
"""

import sqlite3
import json
import uuid
import datetime
import os
import threading
from typing import Dict, Any, Optional, List, Tuple
from app.config import config


class IdempotencyConflictError(Exception):
    """Raised when an existing idempotency key is reused with a different payload."""
    pass


class JobDatabase:
    """
    Thread-safe SQLite job repository with WAL mode and strict idempotency handling.
    """

    _local = threading.local()

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.database_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            self._local.conn = conn
        return self._local.conn

    def _init_schema(self):
        """Initializes jobs table and indexes."""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    brief TEXT NOT NULL,
                    status TEXT NOT NULL,
                    report TEXT,
                    sources TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_idempotency ON jobs(idempotency_key)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
        conn.close()

    def create_or_get_job(
        self,
        order_id: str,
        brief: str,
        idempotency_key: str
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Creates a new job or returns an existing job for the same idempotency key.
        Returns: (job_dict, is_new: bool)
        Raises IdempotencyConflictError if idempotency_key is reused with different brief or orderId.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check existing key
        cursor.execute("SELECT * FROM jobs WHERE idempotency_key = ?", (idempotency_key,))
        row = cursor.fetchone()
        if row:
            job_data = dict(row)
            # Idempotency check: must match the same order_id and brief
            if job_data["order_id"] != order_id or job_data["brief"] != brief:
                raise IdempotencyConflictError(
                    f"Idempotency-Key '{idempotency_key}' is already assigned to a different request."
                )
            return self._format_row(job_data), False

        # Create new job
        job_id = f"aegis-job-{uuid.uuid4().hex[:12]}"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with conn:
            conn.execute("""
                INSERT INTO jobs (job_id, order_id, idempotency_key, brief, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'queued', ?, ?)
            """, (job_id, order_id, idempotency_key, brief, now, now))

        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        new_row = cursor.fetchone()
        return self._format_row(dict(new_row)), True

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves job by jobId."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        return self._format_row(dict(row)) if row else None

    def update_status(
        self,
        job_id: str,
        status: str,
        report: Optional[str] = None,
        sources: Optional[List[Dict[str, str]]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Updates job status and outcomes."""
        conn = self._get_connection()
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        sources_json = json.dumps(sources) if sources is not None else None

        with conn:
            cursor = conn.execute("""
                UPDATE jobs
                SET status = ?,
                    report = COALESCE(?, report),
                    sources = COALESCE(?, sources),
                    error = COALESCE(?, error),
                    updated_at = ?
                WHERE job_id = ?
            """, (status, report, sources_json, error, now, job_id))
            return cursor.rowcount > 0

    def cleanup_old_jobs(self, retention_hours: int = 72) -> int:
        """Purges delivered and failed jobs older than the retention window."""
        conn = self._get_connection()
        threshold = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=retention_hours)).isoformat()
        with conn:
            cursor = conn.execute("""
                DELETE FROM jobs
                WHERE status IN ('delivered', 'failed') AND updated_at < ?
            """, (threshold,))
            return cursor.rowcount

    def _format_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes row dictionary with parsed JSON fields."""
        if row.get("sources"):
            try:
                row["sources"] = json.loads(row["sources"])
            except Exception:
                row["sources"] = []
        else:
            row["sources"] = []
        return row


job_db = JobDatabase()
