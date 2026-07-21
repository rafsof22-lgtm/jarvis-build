from __future__ import annotations

import hashlib
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.jarvis_completion.runtime_v1 import canonical_json

_MUTATION_PATTERN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|REPLACE|CREATE|ALTER|DROP|TRUNCATE|ATTACH|DETACH|VACUUM|REINDEX|ANALYZE|PRAGMA)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class QuerySpec:
    query_id: str
    sql: str
    allowed_parameters: frozenset[str] = frozenset()
    purpose: str = ""

    def validate(self) -> None:
        normalized = self.sql.strip()
        if not self.query_id or not normalized:
            raise ValueError("query_id and sql are required")
        if ";" in normalized:
            raise ValueError("multiple statements and semicolons are prohibited")
        if not normalized.upper().startswith(("SELECT ", "WITH ")):
            raise ValueError("only SELECT or WITH queries are allowed")
        if _MUTATION_PATTERN.search(normalized):
            raise ValueError("mutation or database-control keyword prohibited")


@dataclass(frozen=True)
class InspectorPolicy:
    maximum_rows: int = 100
    timeout_milliseconds: int = 500

    def validate(self) -> None:
        if not 1 <= self.maximum_rows <= 1000:
            raise ValueError("maximum_rows must be 1..1000")
        if not 10 <= self.timeout_milliseconds <= 5000:
            raise ValueError("timeout_milliseconds must be 10..5000")


class ReadOnlyDatabaseInspector:
    """Named-query SQLite inspector with immutable connection policy and redacted audit evidence."""

    def __init__(self, database_path: str | Path, queries: Mapping[str, QuerySpec]) -> None:
        self.path = Path(database_path).resolve()
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        self.queries = dict(queries)
        for query_id, spec in self.queries.items():
            if query_id != spec.query_id:
                raise ValueError("query registry key must equal query_id")
            spec.validate()
        self.audit_events: list[dict[str, Any]] = []

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        return connection

    def inspect_schema(self, policy: InspectorPolicy = InspectorPolicy()) -> dict[str, Any]:
        policy.validate()
        query = QuerySpec(
            "__schema__",
            "SELECT type,name,tbl_name FROM sqlite_master WHERE type IN ('table','view','index') ORDER BY type,name",
        )
        return self._execute_spec(query, {}, policy)

    def execute(self, query_id: str, parameters: Mapping[str, Any] | None = None, policy: InspectorPolicy = InspectorPolicy()) -> dict[str, Any]:
        if query_id not in self.queries:
            raise KeyError(query_id)
        return self._execute_spec(self.queries[query_id], dict(parameters or {}), policy)

    def _execute_spec(self, spec: QuerySpec, parameters: Mapping[str, Any], policy: InspectorPolicy) -> dict[str, Any]:
        policy.validate()
        supplied = set(parameters)
        if supplied - set(spec.allowed_parameters):
            raise ValueError(f"parameters not allowed: {sorted(supplied - set(spec.allowed_parameters))}")
        started = time.monotonic()
        deadline = started + policy.timeout_milliseconds / 1000
        connection = self._connect()
        connection.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 1000)
        try:
            cursor = connection.execute(spec.sql, parameters)
            rows = cursor.fetchmany(policy.maximum_rows + 1)
            truncated = len(rows) > policy.maximum_rows
            visible = rows[: policy.maximum_rows]
            columns = [item[0] for item in cursor.description or ()]
            result_rows = [dict(row) for row in visible]
            outcome = "SUCCEEDED"
        except sqlite3.OperationalError as exc:
            outcome = "TIMEOUT" if "interrupted" in str(exc).lower() else "QUERY_ERROR"
            self._record(spec, parameters, started, outcome, 0, False)
            raise RuntimeError(outcome) from exc
        finally:
            connection.close()
        event = self._record(spec, parameters, started, outcome, len(result_rows), truncated)
        return {
            "state": "DONE_VERIFIED_LOCAL_READ_ONLY",
            "query_id": spec.query_id,
            "columns": columns,
            "rows": result_rows,
            "row_count": len(result_rows),
            "truncated": truncated,
            "audit": event,
            "database_mutation_allowed": False,
        }

    def _record(
        self,
        spec: QuerySpec,
        parameters: Mapping[str, Any],
        started: float,
        outcome: str,
        row_count: int,
        truncated: bool,
    ) -> dict[str, Any]:
        body = {
            "query_id": spec.query_id,
            "sql_sha256": hashlib.sha256(spec.sql.encode()).hexdigest(),
            "parameter_names": sorted(parameters),
            "outcome": outcome,
            "row_count": row_count,
            "truncated": truncated,
            "duration_ms": round((time.monotonic() - started) * 1000, 3),
        }
        event = {**body, "event_sha256": hashlib.sha256(canonical_json(body).encode()).hexdigest()}
        self.audit_events.append(event)
        return event
