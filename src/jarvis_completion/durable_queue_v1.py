from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Mapping

from .runtime_v1 import canonical_json

QUEUE_SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS queue_jobs(
 job_id TEXT PRIMARY KEY,
 idempotency_key TEXT UNIQUE NOT NULL,
 kind TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 state TEXT NOT NULL,
 attempts INTEGER NOT NULL DEFAULT 0,
 max_attempts INTEGER NOT NULL,
 available_at INTEGER NOT NULL,
 lease_owner TEXT,
 lease_until INTEGER,
 last_error TEXT,
 result_json TEXT,
 created_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS queue_events(
 event_id TEXT PRIMARY KEY,
 job_id TEXT NOT NULL REFERENCES queue_jobs(job_id),
 event_type TEXT NOT NULL,
 detail_json TEXT NOT NULL,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS dead_letters(
 job_id TEXT PRIMARY KEY REFERENCES queue_jobs(job_id),
 reason TEXT NOT NULL,
 quarantined_at INTEGER NOT NULL,
 replay_count INTEGER NOT NULL DEFAULT 0
);
"""

ALLOWED_QUEUE_STATES = {"QUEUED", "LEASED", "SUCCEEDED", "RETRY_WAIT", "DEAD_LETTER", "CANCELLED"}


class DurableQueue:
    """Persistent local queue with leases, retries, dead letters and controlled replay."""

    def __init__(self, database_path: str | Path) -> None:
        self.path = str(database_path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(QUEUE_SCHEMA)

    def close(self) -> None:
        self.db.close()

    def _event(self, job_id: str, event_type: str, detail: Mapping[str, Any]) -> None:
        self.db.execute(
            "INSERT INTO queue_events VALUES(?,?,?,?,?)",
            (f"qe-{uuid.uuid4().hex}", job_id, event_type, canonical_json(detail), int(time.time())),
        )

    def enqueue(self, kind: str, payload: Mapping[str, Any], idempotency_key: str, *, max_attempts: int = 3, available_at: int | None = None) -> dict[str, Any]:
        if not kind or not idempotency_key or max_attempts < 1:
            raise ValueError("invalid queue request")
        existing = self.db.execute("SELECT * FROM queue_jobs WHERE idempotency_key=?", (idempotency_key,)).fetchone()
        if existing:
            return dict(existing)
        now = int(time.time())
        job_id = f"job-{uuid.uuid4().hex}"
        with self.db:
            self.db.execute(
                "INSERT INTO queue_jobs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (job_id, idempotency_key, kind, canonical_json(payload), "QUEUED", 0, max_attempts,
                 now if available_at is None else available_at, None, None, None, None, now, now),
            )
            self._event(job_id, "ENQUEUED", {"kind": kind})
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM queue_jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return dict(row)

    def recover_stale_leases(self, *, now: int | None = None) -> list[str]:
        now = int(time.time()) if now is None else now
        rows = self.db.execute("SELECT job_id FROM queue_jobs WHERE state='LEASED' AND lease_until < ?", (now,)).fetchall()
        recovered = [row[0] for row in rows]
        with self.db:
            for job_id in recovered:
                self.db.execute(
                    "UPDATE queue_jobs SET state='QUEUED', lease_owner=NULL, lease_until=NULL, updated_at=? WHERE job_id=?",
                    (now, job_id),
                )
                self._event(job_id, "STALE_LEASE_RECOVERED", {})
        return recovered

    def lease(self, worker: str, *, now: int | None = None, lease_seconds: int = 30) -> dict[str, Any] | None:
        if not worker or lease_seconds < 1:
            raise ValueError("invalid lease")
        now = int(time.time()) if now is None else now
        self.recover_stale_leases(now=now)
        with self.db:
            row = self.db.execute(
                "SELECT job_id FROM queue_jobs WHERE state IN ('QUEUED','RETRY_WAIT') AND available_at <= ? ORDER BY created_at, job_id LIMIT 1",
                (now,),
            ).fetchone()
            if row is None:
                return None
            job_id = row[0]
            changed = self.db.execute(
                "UPDATE queue_jobs SET state='LEASED', lease_owner=?, lease_until=?, attempts=attempts+1, updated_at=? WHERE job_id=? AND state IN ('QUEUED','RETRY_WAIT')",
                (worker, now + lease_seconds, now, job_id),
            ).rowcount
            if changed != 1:
                return None
            self._event(job_id, "LEASED", {"worker": worker, "lease_until": now + lease_seconds})
        return self.get(job_id)

    def succeed(self, job_id: str, worker: str, result: Mapping[str, Any]) -> dict[str, Any]:
        now = int(time.time())
        with self.db:
            changed = self.db.execute(
                "UPDATE queue_jobs SET state='SUCCEEDED', result_json=?, lease_owner=NULL, lease_until=NULL, updated_at=? WHERE job_id=? AND state='LEASED' AND lease_owner=?",
                (canonical_json(result), now, job_id, worker),
            ).rowcount
            if changed != 1:
                raise ValueError("job is not leased by worker")
            self._event(job_id, "SUCCEEDED", result)
        return self.get(job_id)

    def fail(self, job_id: str, worker: str, error: str, *, now: int | None = None, base_delay: int = 2) -> dict[str, Any]:
        now = int(time.time()) if now is None else now
        row = self.db.execute(
            "SELECT attempts,max_attempts FROM queue_jobs WHERE job_id=? AND state='LEASED' AND lease_owner=?",
            (job_id, worker),
        ).fetchone()
        if row is None:
            raise ValueError("job is not leased by worker")
        attempts, max_attempts = int(row[0]), int(row[1])
        with self.db:
            if attempts >= max_attempts:
                self.db.execute(
                    "UPDATE queue_jobs SET state='DEAD_LETTER', last_error=?, lease_owner=NULL, lease_until=NULL, updated_at=? WHERE job_id=?",
                    (error, now, job_id),
                )
                self.db.execute(
                    "INSERT OR REPLACE INTO dead_letters(job_id,reason,quarantined_at,replay_count) VALUES(?,?,?,COALESCE((SELECT replay_count FROM dead_letters WHERE job_id=?),0))",
                    (job_id, error, now, job_id),
                )
                self._event(job_id, "DEAD_LETTERED", {"error": error})
            else:
                delay = base_delay * (2 ** max(0, attempts - 1))
                self.db.execute(
                    "UPDATE queue_jobs SET state='RETRY_WAIT', last_error=?, available_at=?, lease_owner=NULL, lease_until=NULL, updated_at=? WHERE job_id=?",
                    (error, now + delay, now, job_id),
                )
                self._event(job_id, "RETRY_SCHEDULED", {"error": error, "available_at": now + delay})
        return self.get(job_id)

    def replay(self, job_id: str, *, approved: bool, now: int | None = None) -> dict[str, Any]:
        if not approved:
            raise PermissionError("controlled replay approval required")
        now = int(time.time()) if now is None else now
        if self.db.execute("SELECT 1 FROM dead_letters WHERE job_id=?", (job_id,)).fetchone() is None:
            raise ValueError("job is not in dead letter quarantine")
        with self.db:
            self.db.execute(
                "UPDATE queue_jobs SET state='QUEUED', attempts=0, available_at=?, lease_owner=NULL, lease_until=NULL, last_error=NULL, updated_at=? WHERE job_id=?",
                (now, now, job_id),
            )
            self.db.execute("UPDATE dead_letters SET replay_count=replay_count+1 WHERE job_id=?", (job_id,))
            self._event(job_id, "CONTROLLED_REPLAY", {})
        return self.get(job_id)

    def dashboard(self) -> dict[str, Any]:
        counts = {state: 0 for state in ALLOWED_QUEUE_STATES}
        for row in self.db.execute("SELECT state,COUNT(*) FROM queue_jobs GROUP BY state"):
            counts[row[0]] = row[1]
        dead = [dict(row) for row in self.db.execute("SELECT * FROM dead_letters ORDER BY quarantined_at")]
        return {"counts": counts, "dead_letters": dead, "passed_state_validation": not (set(counts) - ALLOWED_QUEUE_STATES)}
