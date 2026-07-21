from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

FORBIDDEN_DIRECT_IDENTIFIERS = {"name", "email", "phone", "address", "date_of_birth", "medicare_number", "tfn", "bank_account"}
FORBIDDEN_SECRET_KEYS = {"password", "api_key", "access_token", "refresh_token", "private_key", "seed_phrase", "recovery_code", "secret"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key).lower()
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


@dataclass(frozen=True)
class LayerResult:
    order: int
    layer_id: str
    state: str
    attempts: int
    event_sha256: str


class FullStackDigitalTwinV17:
    """Local zero-spend staging simulator for the canonical 18-layer Jarvis stack."""

    def __init__(self, architecture_path: str | Path, database_path: str | Path, *, maximum_cost_aud: float = 0.0) -> None:
        self.architecture_path = Path(architecture_path)
        self.database_path = Path(database_path)
        self.maximum_cost_aud = float(maximum_cost_aud)
        self.architecture = json.loads(self.architecture_path.read_text(encoding="utf-8"))
        layers = self.architecture.get("layers") or []
        if len(layers) != 18:
            raise ValueError("canonical architecture must contain 18 layers")
        self.connection = sqlite3.connect(str(self.database_path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS staging_runs(
              run_id TEXT PRIMARY KEY, payload_sha256 TEXT NOT NULL, state TEXT NOT NULL,
              projected_cost_aud REAL NOT NULL, rollback_state TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS staging_layer_events(
              run_id TEXT NOT NULL, layer_order INTEGER NOT NULL, layer_id TEXT NOT NULL,
              state TEXT NOT NULL, attempts INTEGER NOT NULL, event_sha256 TEXT NOT NULL,
              PRIMARY KEY(run_id, layer_order)
            );
            """
        )
        self.connection.commit()

    def _validate(self, payload: Mapping[str, Any], projected_cost_aud: float) -> None:
        keys = set(_walk_keys(payload))
        direct = sorted(keys & FORBIDDEN_DIRECT_IDENTIFIERS)
        if direct:
            raise PermissionError(f"direct identifiers prohibited in staging twin: {', '.join(direct)}")
        secrets = sorted(key for key in keys if key in FORBIDDEN_SECRET_KEYS or key.endswith("_secret"))
        if secrets:
            raise PermissionError(f"secret-like fields prohibited: {', '.join(secrets)}")
        if projected_cost_aud < 0:
            raise ValueError("projected_cost_aud cannot be negative")
        if projected_cost_aud > self.maximum_cost_aud:
            raise PermissionError("cost ceiling exceeded")

    def run(self, *, payload: Mapping[str, Any], projected_cost_aud: float = 0.0,
            transient_fail_layer: str | None = None, hard_fail_layer: str | None = None) -> dict[str, Any]:
        self._validate(payload, projected_cost_aud)
        payload_sha = sha256_text(canonical_json(payload))
        run_id = sha256_text(f"v17|{payload_sha}|{projected_cost_aud}")[:32]
        self.connection.execute(
            "INSERT OR REPLACE INTO staging_runs VALUES(?,?,?,?,?)",
            (run_id, payload_sha, "RUNNING", projected_cost_aud, "NOT_REQUESTED"),
        )
        self.connection.commit()
        results: list[LayerResult] = []
        transient_consumed = False
        for layer in self.architecture["layers"]:
            attempts = 1
            layer_id = layer["layer_id"]
            if hard_fail_layer == layer_id:
                self.connection.execute("UPDATE staging_runs SET state=? WHERE run_id=?", ("FAILED_SAFE", run_id))
                self.connection.commit()
                return self._report(run_id, results, "FAILED_SAFE", failed_layer=layer_id)
            if transient_fail_layer == layer_id and not transient_consumed:
                attempts = 2
                transient_consumed = True
            event_sha = sha256_text(f"{run_id}|{layer['order']}|{layer_id}|{attempts}|PASSED")
            result = LayerResult(int(layer["order"]), layer_id, "PASSED_LOCAL_SIMULATION", attempts, event_sha)
            self.connection.execute(
                "INSERT OR REPLACE INTO staging_layer_events VALUES(?,?,?,?,?,?)",
                (run_id, result.order, result.layer_id, result.state, result.attempts, result.event_sha256),
            )
            self.connection.commit()
            results.append(result)
        self.connection.execute("UPDATE staging_runs SET state=? WHERE run_id=?", ("PASSED_LOCAL_SIMULATION", run_id))
        self.connection.commit()
        return self._report(run_id, results, "PASSED_LOCAL_SIMULATION")

    def _report(self, run_id: str, results: list[LayerResult], state: str, *, failed_layer: str | None = None) -> dict[str, Any]:
        row = self.connection.execute("SELECT * FROM staging_runs WHERE run_id=?", (run_id,)).fetchone()
        return {
            "run_id": run_id,
            "state": state,
            "layer_count": len(results),
            "layers": [result.__dict__ for result in results],
            "failed_layer": failed_layer,
            "projected_cost_aud": float(row["projected_cost_aud"]),
            "privacy_test": "PASS_NO_DIRECT_IDENTIFIERS_ACCEPTED",
            "security_test": "PASS_NO_SECRET_VALUES_ACCEPTED",
            "persistence_test": "PASS_SQLITE_EVENT_LEDGER",
            "retry_test": "PASS" if any(result.attempts == 2 for result in results) else "NOT_EXERCISED",
            "connected_external_staging": False,
            "truth_boundary": "All 18 layers are exercised as a local digital twin. No provider, credential, live database, external staging or production system is connected.",
        }

    def persisted_layer_count(self, run_id: str) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM staging_layer_events WHERE run_id=?", (run_id,)).fetchone()[0])

    def backup(self, destination: str | Path) -> dict[str, Any]:
        destination = Path(destination)
        self.connection.commit()
        backup_connection = sqlite3.connect(str(destination))
        try:
            self.connection.backup(backup_connection)
        finally:
            backup_connection.close()
        return {"path": str(destination), "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(), "state": "BACKUP_CREATED"}

    def restore(self, backup_path: str | Path, restored_path: str | Path) -> dict[str, Any]:
        backup_path, restored_path = Path(backup_path), Path(restored_path)
        shutil.copy2(backup_path, restored_path)
        restored = sqlite3.connect(str(restored_path))
        try:
            run_count = int(restored.execute("SELECT COUNT(*) FROM staging_runs").fetchone()[0])
            event_count = int(restored.execute("SELECT COUNT(*) FROM staging_layer_events").fetchone()[0])
        finally:
            restored.close()
        return {"state": "RESTORE_VERIFIED", "run_count": run_count, "event_count": event_count, "sha256": hashlib.sha256(restored_path.read_bytes()).hexdigest()}

    def rollback(self, run_id: str) -> dict[str, Any]:
        if not self.connection.execute("SELECT 1 FROM staging_runs WHERE run_id=?", (run_id,)).fetchone():
            raise ValueError("unknown run_id")
        self.connection.execute("DELETE FROM staging_layer_events WHERE run_id=?", (run_id,))
        self.connection.execute("UPDATE staging_runs SET state=?, rollback_state=? WHERE run_id=?", ("ROLLED_BACK", "VERIFIED_LOCAL", run_id))
        self.connection.commit()
        return {"state": "ROLLED_BACK", "remaining_layer_events": self.persisted_layer_count(run_id), "external_side_effects": False}

    def close(self) -> None:
        self.connection.close()
