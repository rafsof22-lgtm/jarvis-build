from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .history_alerts import Alert, initialise_history


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_lifecycle_schema(db_path: Path) -> None:
    initialise_history(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS alert_suppressions(
                suppression_key TEXT PRIMARY KEY,
                reason TEXT NOT NULL,
                expires_at TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS alert_events(
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def suppress(db_path: Path, suppression_key: str, reason: str, *, expires_at: str | None = None) -> None:
    if not suppression_key or not reason.strip():
        raise ValueError("suppression key and reason are required")
    ensure_lifecycle_schema(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO alert_suppressions VALUES(?,?,?,?)",
            (suppression_key, reason.strip(), expires_at, _now()),
        )


def _active_suppressions(db_path: Path, *, now: str | None = None) -> set[str]:
    ensure_lifecycle_schema(db_path)
    current = now or _now()
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT suppression_key FROM alert_suppressions WHERE expires_at IS NULL OR expires_at > ?",
            (current,),
        ).fetchall()
    return {row[0] for row in rows}


def filter_suppressed(db_path: Path, alerts: Iterable[Alert], *, now: str | None = None) -> list[Alert]:
    active = _active_suppressions(db_path, now=now)
    return [alert for alert in alerts if alert.alert_id not in active and f"{alert.repository_id}:{alert.kind}" not in active]


def resolve_alert(db_path: Path, alert_id: str, *, evidence_pointer: str) -> bool:
    if not evidence_pointer.strip():
        raise ValueError("resolution evidence is required")
    ensure_lifecycle_schema(db_path)
    resolved_at = _now()
    with sqlite3.connect(db_path) as conn:
        changed = conn.execute(
            "UPDATE alerts SET resolved_at=? WHERE alert_id=? AND resolved_at IS NULL",
            (resolved_at, alert_id),
        ).rowcount
        if changed:
            conn.execute(
                "INSERT INTO alert_events(alert_id,event_type,detail,created_at) VALUES(?,?,?,?)",
                (alert_id, "RESOLVED", evidence_pointer, resolved_at),
            )
    return changed == 1


def reconcile_resolved(db_path: Path, current_alert_ids: set[str], *, evidence_pointer: str) -> list[str]:
    ensure_lifecycle_schema(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT alert_id FROM alerts WHERE resolved_at IS NULL").fetchall()
    resolved: list[str] = []
    for (alert_id,) in rows:
        if alert_id not in current_alert_ids and resolve_alert(db_path, alert_id, evidence_pointer=evidence_pointer):
            resolved.append(alert_id)
    return resolved
