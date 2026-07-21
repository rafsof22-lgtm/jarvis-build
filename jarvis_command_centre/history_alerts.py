from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Alert:
    alert_id: str
    repository_id: str
    kind: str
    severity: str
    summary: str
    evidence_pointer: str
    created_at: str


def _stable_id(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:20]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialise_history(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id TEXT PRIMARY KEY,
                generated_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                repository_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                severity TEXT NOT NULL,
                summary TEXT NOT NULL,
                evidence_pointer TEXT NOT NULL,
                created_at TEXT NOT NULL,
                resolved_at TEXT
            );
            """
        )


def record_snapshot(db_path: Path, snapshot: dict[str, Any]) -> dict[str, str]:
    initialise_history(db_path)
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    snapshot_id = _stable_id(snapshot.get("generated_at", "unknown"), digest)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO snapshots(snapshot_id, generated_at, payload_json, payload_sha256) VALUES (?, ?, ?, ?)",
            (snapshot_id, snapshot.get("generated_at", _now()), canonical, digest),
        )
    return {"snapshot_id": snapshot_id, "payload_sha256": digest}


def derive_alerts(snapshot: dict[str, Any]) -> list[Alert]:
    created_at = snapshot.get("generated_at") or _now()
    alerts: list[Alert] = []
    for repo in snapshot.get("repositories", []):
        repo_id = repo.get("repository_id", "unknown")
        status = str(repo.get("status", "unknown"))
        health = str(repo.get("health", "unknown"))
        if status in {"BLOCKED", "failed", "rotation_required"}:
            summary = f"{repo_id} is {status}"
            alerts.append(Alert(_stable_id(repo_id, "status", summary), repo_id, "status", "high", summary, f"repository:{repo_id}", created_at))
        if health in {"unknown", "failed", "not-deployed"}:
            severity = "medium" if health == "unknown" else "high"
            summary = f"{repo_id} health is {health}"
            alerts.append(Alert(_stable_id(repo_id, "health", summary), repo_id, "health", severity, summary, f"repository:{repo_id}", created_at))
        for blocker in repo.get("blockers", []):
            summary = str(blocker)
            if not summary:
                continue
            alerts.append(Alert(_stable_id(repo_id, "blocker", summary), repo_id, "blocker", "medium", summary, f"repository:{repo_id}", created_at))
    readiness = snapshot.get("configuration_readiness", {})
    if readiness.get("status") in {"failed", "not_generated"}:
        summary = "Configuration readiness evidence is unavailable"
        alerts.append(Alert(_stable_id("jarvis-build", "configuration", summary), "jarvis-build", "configuration", "medium", summary, "evidence:federated-config-readiness.json", created_at))
    return alerts


def record_alerts(db_path: Path, alerts: list[Alert]) -> int:
    initialise_history(db_path)
    inserted = 0
    with sqlite3.connect(db_path) as conn:
        for alert in alerts:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO alerts(alert_id, repository_id, kind, severity, summary, evidence_pointer, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (alert.alert_id, alert.repository_id, alert.kind, alert.severity, alert.summary, alert.evidence_pointer, alert.created_at),
            )
            inserted += cursor.rowcount
    return inserted


def list_recent_snapshots(db_path: Path, limit: int = 20) -> list[dict[str, Any]]:
    initialise_history(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT snapshot_id, generated_at, payload_sha256 FROM snapshots ORDER BY generated_at DESC LIMIT ?",
            (max(1, min(limit, 100)),),
        ).fetchall()
    return [{"snapshot_id": row[0], "generated_at": row[1], "payload_sha256": row[2]} for row in rows]


def list_open_alerts(db_path: Path, limit: int = 100) -> list[dict[str, Any]]:
    initialise_history(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT alert_id, repository_id, kind, severity, summary, evidence_pointer, created_at FROM alerts WHERE resolved_at IS NULL ORDER BY created_at DESC LIMIT ?",
            (max(1, min(limit, 500)),),
        ).fetchall()
    return [asdict(Alert(*row)) for row in rows]


def persist_snapshot_and_alerts(db_path: Path, snapshot: dict[str, Any]) -> dict[str, Any]:
    snapshot_result = record_snapshot(db_path, snapshot)
    alerts = derive_alerts(snapshot)
    inserted = record_alerts(db_path, alerts)
    return {
        **snapshot_result,
        "derived_alerts": len(alerts),
        "new_alerts": inserted,
        "open_alerts": len(list_open_alerts(db_path)),
        "secret_values_stored": False,
    }
