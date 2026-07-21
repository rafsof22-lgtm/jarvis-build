from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from .runtime_v1 import KnowledgeFabric, PolicyEngine, TaskContract, canonical_json


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


def digest_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class BackupManifest:
    backup_id: str
    source_path: str
    backup_path: str
    sha256: str
    byte_count: int
    schema_version: int
    created_at: int


class KnowledgeFabricResilience:
    """Atomic SQLite backup, integrity, restore and retention controls."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        if str(self.database_path) == ":memory:":
            raise ValueError("resilience requires a file-backed database")

    def integrity(self, path: str | Path | None = None) -> dict[str, Any]:
        target = Path(path) if path is not None else self.database_path
        connection = sqlite3.connect(target)
        try:
            rows = [row[0] for row in connection.execute("PRAGMA integrity_check").fetchall()]
            version = int(connection.execute("PRAGMA user_version").fetchone()[0])
            tables = sorted(row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ))
        finally:
            connection.close()
        return {"passed": rows == ["ok"], "results": rows, "schema_version": version, "tables": tables}

    def create_backup(self, directory: str | Path) -> BackupManifest:
        if not self.database_path.exists():
            raise FileNotFoundError(self.database_path)
        before = self.integrity()
        if not before["passed"]:
            raise ValueError("source database failed integrity check")
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        backup_id = f"backup-{int(time.time())}-{uuid.uuid4().hex[:10]}"
        final_path = directory / f"{backup_id}.sqlite3"
        temp_path = directory / f".{backup_id}.tmp"
        source = sqlite3.connect(self.database_path)
        destination = sqlite3.connect(temp_path)
        try:
            source.backup(destination)
            destination.commit()
        finally:
            destination.close()
            source.close()
        os.replace(temp_path, final_path)
        check = self.integrity(final_path)
        if not check["passed"]:
            final_path.unlink(missing_ok=True)
            raise ValueError("backup failed integrity check")
        return BackupManifest(
            backup_id=backup_id,
            source_path=str(self.database_path),
            backup_path=str(final_path),
            sha256=digest_file(final_path),
            byte_count=final_path.stat().st_size,
            schema_version=check["schema_version"],
            created_at=int(time.time()),
        )

    def restore(self, manifest: BackupManifest, destination: str | Path, *, expected_schema_version: int | None = None) -> dict[str, Any]:
        backup_path = Path(manifest.backup_path)
        if digest_file(backup_path) != manifest.sha256:
            raise ValueError("backup digest mismatch")
        check = self.integrity(backup_path)
        if not check["passed"]:
            raise ValueError("backup integrity failure")
        if expected_schema_version is not None and check["schema_version"] != expected_schema_version:
            raise ValueError("schema version mismatch")
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
        shutil.copy2(backup_path, temp)
        restored = self.integrity(temp)
        if not restored["passed"]:
            temp.unlink(missing_ok=True)
            raise ValueError("restored copy failed integrity check")
        os.replace(temp, destination)
        return {
            "restored": True,
            "destination": str(destination),
            "sha256": digest_file(destination),
            "schema_version": restored["schema_version"],
            "tables": restored["tables"],
        }

    @staticmethod
    def enforce_retention(directory: str | Path, keep: int) -> list[str]:
        if keep < 1:
            raise ValueError("keep must be at least one")
        files = sorted(Path(directory).glob("backup-*.sqlite3"), key=lambda p: (p.stat().st_mtime_ns, p.name), reverse=True)
        removed: list[str] = []
        for path in files[keep:]:
            removed.append(str(path))
            path.unlink()
        return removed


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
                "INSERT INTO queue_jobs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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
        rows = self.db.execute(
            "SELECT job_id FROM queue_jobs WHERE state='LEASED' AND lease_until < ?", (now,)
        ).fetchall()
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
                "SELECT job_id FROM queue_jobs WHERE state IN ('QUEUED','RETRY_WAIT') AND available_at <= ? "
                "ORDER BY created_at, job_id LIMIT 1", (now,)
            ).fetchone()
            if row is None:
                return None
            job_id = row[0]
            changed = self.db.execute(
                "UPDATE queue_jobs SET state='LEASED', lease_owner=?, lease_until=?, attempts=attempts+1, updated_at=? "
                "WHERE job_id=? AND state IN ('QUEUED','RETRY_WAIT')",
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
                "UPDATE queue_jobs SET state='SUCCEEDED', result_json=?, lease_owner=NULL, lease_until=NULL, updated_at=? "
                "WHERE job_id=? AND state='LEASED' AND lease_owner=?",
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
                state = "DEAD_LETTER"
                self.db.execute(
                    "UPDATE queue_jobs SET state=?, last_error=?, lease_owner=NULL, lease_until=NULL, updated_at=? WHERE job_id=?",
                    (state, error, now, job_id),
                )
                self.db.execute(
                    "INSERT OR REPLACE INTO dead_letters(job_id,reason,quarantined_at,replay_count) VALUES(?,?,?,COALESCE((SELECT replay_count FROM dead_letters WHERE job_id=?),0))",
                    (job_id, error, now, job_id),
                )
                self._event(job_id, "DEAD_LETTERED", {"error": error})
            else:
                state = "RETRY_WAIT"
                delay = base_delay * (2 ** max(0, attempts - 1))
                self.db.execute(
                    "UPDATE queue_jobs SET state=?, last_error=?, available_at=?, lease_owner=NULL, lease_until=NULL, updated_at=? WHERE job_id=?",
                    (state, error, now + delay, now, job_id),
                )
                self._event(job_id, "RETRY_SCHEDULED", {"error": error, "available_at": now + delay})
        return self.get(job_id)

    def replay(self, job_id: str, *, approved: bool, now: int | None = None) -> dict[str, Any]:
        if not approved:
            raise PermissionError("controlled replay approval required")
        now = int(time.time()) if now is None else now
        row = self.db.execute("SELECT job_id FROM dead_letters WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
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


@dataclass(frozen=True)
class ExerciseResult:
    name: str
    passed: bool
    evidence: Mapping[str, Any]


class FederationExerciseRunner:
    """Deterministic source-to-evidence-to-domain simulation with failure exercises."""

    def __init__(self, fabric: KnowledgeFabric, queue: DurableQueue) -> None:
        self.fabric = fabric
        self.queue = queue

    def run_happy_path(self, contract: TaskContract, operation: Callable[[Mapping[str, Any]], Mapping[str, Any]]) -> ExerciseResult:
        allowed, reason = PolicyEngine().authorize(contract, action="research", tool=contract.allowed_tools[0])
        if not allowed:
            return ExerciseResult("happy_path", False, {"reason": reason})
        job = self.queue.enqueue("domain_operation", contract.inputs, f"exercise:{contract.task_id}")
        leased = self.queue.lease("exercise-worker")
        if leased is None or leased["job_id"] != job["job_id"]:
            return ExerciseResult("happy_path", False, {"reason": "lease_failed"})
        result = operation(json.loads(leased["payload_json"]))
        final = self.queue.succeed(job["job_id"], "exercise-worker", result)
        event_id = self.fabric.audit("exercise-runner", "federation_happy_path", "passed", result, contract.task_id)
        return ExerciseResult("happy_path", final["state"] == "SUCCEEDED", {"job": final["job_id"], "audit_event": event_id, "result": result})

    def run_failure_suite(self) -> list[ExerciseResult]:
        results: list[ExerciseResult] = []
        duplicate_a = self.queue.enqueue("duplicate", {"x": 1}, "duplicate-key")
        duplicate_b = self.queue.enqueue("duplicate", {"x": 2}, "duplicate-key")
        results.append(ExerciseResult("duplicate_suppression", duplicate_a["job_id"] == duplicate_b["job_id"], {"job_id": duplicate_a["job_id"]}))

        job = self.queue.enqueue("retry", {"x": 1}, "retry-key", max_attempts=2, available_at=10)
        lease1 = self.queue.lease("w", now=10)
        retry = self.queue.fail(job["job_id"], "w", "injected outage", now=10, base_delay=1)
        lease2 = self.queue.lease("w", now=11)
        dead = self.queue.fail(job["job_id"], "w", "injected outage", now=11, base_delay=1)
        results.append(ExerciseResult("retry_dead_letter", retry["state"] == "RETRY_WAIT" and lease2 is not None and dead["state"] == "DEAD_LETTER", {"state": dead["state"]}))

        replay = self.queue.replay(job["job_id"], approved=True, now=12)
        results.append(ExerciseResult("controlled_replay", replay["state"] == "QUEUED", {"state": replay["state"]}))

        results.append(ExerciseResult("approval_fail_closed", PolicyEngine().authorize(
            TaskContract("risk", "owner", "risk", {}, ["evidence"], ["local"], [], 2, ["production"], 10, 0, 5, 0, "rollback"),
            action="production", tool="local", approval=False,
        ) == (False, "owner_approval_required"), {}))
        return results


class OperatorPack:
    @staticmethod
    def build(fabric: KnowledgeFabric, queue: DurableQueue, exercises: Sequence[ExerciseResult], blockers: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        exercise_rows = [{"name": item.name, "passed": item.passed, "evidence": dict(item.evidence)} for item in exercises]
        return {
            "traffic_light": "GREEN" if all(item["passed"] for item in exercise_rows) else "RED",
            "knowledge_fabric": fabric.status_dashboard(),
            "queue": queue.dashboard(),
            "exercises": exercise_rows,
            "blocker_cards": [
                {
                    "title": item["title"],
                    "state": item.get("state", "BLOCKED"),
                    "owner_action": item["owner_action"],
                    "safe_retry": bool(item.get("safe_retry", False)),
                    "evidence_required": item.get("evidence_required", []),
                }
                for item in blockers
            ],
            "button_truth": {
                "retry_local": "ENABLED",
                "restore_local": "ENABLED",
                "production": "DISABLED_OWNER_APPROVAL_REQUIRED",
                "money_movement": "DISABLED",
                "live_trading": "DISABLED",
            },
        }


class ReleaseContinuityPack:
    @staticmethod
    def create(root: str | Path, *, release_id: str, artifacts: Sequence[str | Path], tests: Sequence[str], risks: Sequence[str], gaps: Sequence[str], rollback: str, resume: str) -> dict[str, Any]:
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        rows = []
        for artifact in artifacts:
            path = Path(artifact)
            rows.append({"path": str(path), "sha256": digest_file(path), "bytes": path.stat().st_size})
        manifest = {
            "release_id": release_id,
            "generated_at": int(time.time()),
            "artifacts": rows,
            "tests": list(tests),
            "risks": list(risks),
            "gaps": list(gaps),
            "rollback": rollback,
            "resume": resume,
            "truth_boundary": "Repository and deterministic local scope only; connected staging, production and owner acceptance remain separate.",
        }
        target = root / "release-continuity-manifest.json"
        target.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        manifest["manifest_path"] = str(target)
        manifest["manifest_sha256"] = digest_file(target)
        return manifest
