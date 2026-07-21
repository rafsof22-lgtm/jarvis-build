from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

RUNTIME_STATES = {
    "PENDING_INGEST", "SPEC_ONLY", "BACKLOGGED", "SCAFFOLDED",
    "IMPLEMENTED_NOT_INTEGRATED", "INTEGRATED_STAGING",
    "DEPLOYED_UNVERIFIED", "DONE_VERIFIED", "WAIVED", "BLOCKED",
}
HIGH_RISK_ACTIONS = {"production", "publish", "money_movement", "live_trading", "sensitive_health", "destructive"}

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sources(
 source_id TEXT PRIMARY KEY, pointer TEXT NOT NULL, sha256 TEXT NOT NULL,
 title TEXT NOT NULL, state TEXT NOT NULL, byte_count INTEGER NOT NULL,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS messages(
 message_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(source_id),
 ordinal INTEGER NOT NULL, role TEXT NOT NULL, model TEXT,
 exact_text TEXT NOT NULL, start_line INTEGER NOT NULL, end_line INTEGER NOT NULL,
 sha256 TEXT NOT NULL, duplicate_of TEXT REFERENCES messages(message_id),
 fragment_of TEXT REFERENCES messages(message_id),
 UNIQUE(source_id, ordinal)
);
CREATE TABLE IF NOT EXISTS requirements(
 requirement_id TEXT PRIMARY KEY, source_id TEXT REFERENCES sources(source_id),
 verbatim TEXT NOT NULL, normalized TEXT NOT NULL, module_id TEXT NOT NULL,
 implementation_path TEXT, status TEXT NOT NULL, updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence(
 evidence_id TEXT PRIMARY KEY, requirement_id TEXT REFERENCES requirements(requirement_id),
 artifact_ref TEXT NOT NULL, test_ref TEXT, status TEXT NOT NULL,
 digest TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions(
 decision_id TEXT PRIMARY KEY, kind TEXT NOT NULL, subject TEXT NOT NULL,
 detail TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events(
 event_id TEXT PRIMARY KEY, correlation_id TEXT NOT NULL, actor TEXT NOT NULL,
 action TEXT NOT NULL, outcome TEXT NOT NULL, payload_json TEXT NOT NULL,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS idempotency(
 key TEXT PRIMARY KEY, response_json TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS alerts(
 alert_id TEXT PRIMARY KEY, dedupe_key TEXT UNIQUE NOT NULL, severity TEXT NOT NULL,
 message TEXT NOT NULL, acknowledged INTEGER NOT NULL DEFAULT 0,
 created_at INTEGER NOT NULL
);
"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Message:
    ordinal: int
    role: str
    exact_text: str
    start_line: int
    end_line: int
    model: str | None = None
    duplicate_of: str | None = None
    fragment_of: str | None = None


@dataclass(frozen=True)
class TaskContract:
    task_id: str
    owner: str
    purpose: str
    inputs: Mapping[str, Any]
    outputs: Sequence[str]
    allowed_tools: Sequence[str]
    denied_tools: Sequence[str]
    autonomy_level: int
    approval_actions: Sequence[str]
    token_limit: int
    cost_limit_aud: float
    timeout_seconds: int
    retry_limit: int
    rollback: str

    def validate(self) -> None:
        if not self.task_id or not self.owner or not self.purpose:
            raise ValueError("task_id, owner and purpose are required")
        if not 0 <= self.autonomy_level <= 4:
            raise ValueError("autonomy_level must be 0..4")
        if self.token_limit < 0 or self.cost_limit_aud < 0 or self.timeout_seconds <= 0 or self.retry_limit < 0:
            raise ValueError("invalid quota")
        if set(self.allowed_tools) & set(self.denied_tools):
            raise ValueError("tool cannot be both allowed and denied")
        unknown = set(self.approval_actions) - HIGH_RISK_ACTIONS
        if unknown:
            raise ValueError(f"unknown approval actions: {sorted(unknown)}")


@dataclass(frozen=True)
class ProviderProfile:
    provider_id: str
    route_class: str
    capabilities: frozenset[str]
    privacy_score: int
    reliability_score: int
    estimated_cost: float
    enabled: bool = True


@dataclass(frozen=True)
class SignedEnvelope:
    message_id: str
    timestamp: int
    idempotency_key: str
    payload: Mapping[str, Any]
    signature: str


class KnowledgeFabric:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def ingest_source(self, *, pointer: str, title: str, raw: bytes, messages: Sequence[Message]) -> dict[str, Any]:
        source_hash = sha256_bytes(raw)
        source_id = f"src-{source_hash[:24]}"
        now = int(time.time())
        try:
            with self.db:
                self.db.execute(
                    "INSERT OR IGNORE INTO sources VALUES(?,?,?,?,?,?,?)",
                    (source_id, pointer, source_hash, title, "READY", len(raw), now),
                )
                seen: dict[tuple[str, str | None, str], str] = {}
                for item in messages:
                    if item.start_line < 1 or item.end_line < item.start_line:
                        raise ValueError("invalid source coordinates")
                    digest = sha256_bytes(item.exact_text.encode("utf-8"))
                    message_id = f"msg-{source_hash[:12]}-{item.ordinal:06d}"
                    key = (item.role, item.model, digest)
                    duplicate_of = item.duplicate_of or seen.get(key)
                    self.db.execute(
                        "INSERT OR IGNORE INTO messages VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (message_id, source_id, item.ordinal, item.role, item.model,
                         item.exact_text, item.start_line, item.end_line, digest,
                         duplicate_of, item.fragment_of),
                    )
                    seen.setdefault(key, message_id)
        except Exception:
            self.db.rollback()
            raise
        return self.source_manifest(source_id)

    def source_manifest(self, source_id: str) -> dict[str, Any]:
        source = self.db.execute("SELECT * FROM sources WHERE source_id=?", (source_id,)).fetchone()
        if source is None:
            raise KeyError(source_id)
        rows = self.db.execute("SELECT * FROM messages WHERE source_id=? ORDER BY ordinal", (source_id,)).fetchall()
        return {
            "source": dict(source),
            "message_count": len(rows),
            "messages": [dict(r) for r in rows],
            "duplicate_count": sum(1 for r in rows if r["duplicate_of"]),
            "fragment_count": sum(1 for r in rows if r["fragment_of"]),
        }

    def reproduction(self, source_id: str, *, include_duplicates: bool = False) -> list[dict[str, Any]]:
        sql = "SELECT * FROM messages WHERE source_id=?"
        args: list[Any] = [source_id]
        if not include_duplicates:
            sql += " AND duplicate_of IS NULL"
        sql += " ORDER BY ordinal"
        return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def upsert_requirement(self, requirement_id: str, verbatim: str, normalized: str, module_id: str,
                           *, source_id: str | None = None, implementation_path: str | None = None,
                           status: str = "BACKLOGGED") -> None:
        if status not in RUNTIME_STATES:
            raise ValueError("invalid runtime status")
        with self.db:
            self.db.execute(
                "INSERT INTO requirements VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(requirement_id) DO UPDATE SET "
                "verbatim=excluded.verbatim, normalized=excluded.normalized, module_id=excluded.module_id, "
                "implementation_path=excluded.implementation_path, status=excluded.status, updated_at=excluded.updated_at",
                (requirement_id, source_id, verbatim, normalized, module_id, implementation_path, status, int(time.time())),
            )

    def add_evidence(self, requirement_id: str, artifact_ref: str, test_ref: str | None, status: str) -> str:
        if status not in RUNTIME_STATES:
            raise ValueError("invalid runtime status")
        body = canonical_json({"requirement_id": requirement_id, "artifact_ref": artifact_ref, "test_ref": test_ref, "status": status})
        evidence_id = f"ev-{sha256_bytes(body.encode())[:24]}"
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO evidence VALUES(?,?,?,?,?,?,?)",
                            (evidence_id, requirement_id, artifact_ref, test_ref, status,
                             sha256_bytes(body.encode()), int(time.time())))
        return evidence_id

    def no_gaps_report(self) -> dict[str, Any]:
        orphan_sources = self.db.execute(
            "SELECT source_id FROM sources s WHERE NOT EXISTS(SELECT 1 FROM messages m WHERE m.source_id=s.source_id)"
        ).fetchall()
        invalid_coordinates = self.db.execute(
            "SELECT message_id FROM messages WHERE start_line < 1 OR end_line < start_line"
        ).fetchall()
        uncovered = self.db.execute(
            "SELECT requirement_id FROM requirements r WHERE status NOT IN ('WAIVED','BLOCKED') "
            "AND (implementation_path IS NULL OR NOT EXISTS(SELECT 1 FROM evidence e WHERE e.requirement_id=r.requirement_id))"
        ).fetchall()
        unresolved_fragments = self.db.execute(
            "SELECT message_id FROM messages WHERE fragment_of IS NOT NULL AND fragment_of NOT IN (SELECT message_id FROM messages)"
        ).fetchall()
        report = {
            "orphan_sources": [r[0] for r in orphan_sources],
            "invalid_coordinates": [r[0] for r in invalid_coordinates],
            "uncovered_requirements": [r[0] for r in uncovered],
            "unresolved_fragments": [r[0] for r in unresolved_fragments],
        }
        report["passed"] = not any(report.values())
        return report

    def synthesis_coverage(self, source_id: str, referenced: Iterable[str], excluded: Mapping[str, str]) -> dict[str, Any]:
        all_ids = {r[0] for r in self.db.execute("SELECT message_id FROM messages WHERE source_id=?", (source_id,))}
        covered = set(referenced) | set(excluded)
        missing = sorted(all_ids - covered)
        invalid_exclusions = sorted(k for k, v in excluded.items() if k not in all_ids or not v.strip())
        return {"passed": not missing and not invalid_exclusions, "missing": missing, "invalid_exclusions": invalid_exclusions}

    def audit(self, actor: str, action: str, outcome: str, payload: Mapping[str, Any], correlation_id: str | None = None) -> str:
        event_id = f"evt-{uuid.uuid4().hex}"
        with self.db:
            self.db.execute("INSERT INTO audit_events VALUES(?,?,?,?,?,?,?)",
                            (event_id, correlation_id or uuid.uuid4().hex, actor, action, outcome,
                             canonical_json(payload), int(time.time())))
        return event_id

    def create_alert(self, dedupe_key: str, severity: str, message: str) -> str:
        alert_id = f"alert-{sha256_bytes(dedupe_key.encode())[:20]}"
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO alerts VALUES(?,?,?,?,?,?)",
                            (alert_id, dedupe_key, severity, message, 0, int(time.time())))
        return alert_id

    def status_dashboard(self) -> dict[str, Any]:
        reqs = [dict(r) for r in self.db.execute("SELECT * FROM requirements ORDER BY requirement_id")]
        alerts = [dict(r) for r in self.db.execute("SELECT * FROM alerts WHERE acknowledged=0 ORDER BY created_at")]
        counts = {state: 0 for state in RUNTIME_STATES}
        for row in reqs:
            counts[row["status"]] += 1
        return {"runtime_counts": counts, "requirements": reqs, "active_alerts": alerts, "no_gaps": self.no_gaps_report()}

    def idempotent_execute(self, key: str, operation) -> Any:
        row = self.db.execute("SELECT response_json FROM idempotency WHERE key=?", (key,)).fetchone()
        if row:
            return json.loads(row[0])
        result = operation()
        with self.db:
            self.db.execute("INSERT INTO idempotency VALUES(?,?,?)", (key, canonical_json(result), int(time.time())))
        return result


class PolicyEngine:
    def authorize(self, contract: TaskContract, *, action: str, tool: str, approval: bool = False) -> tuple[bool, str]:
        contract.validate()
        if tool in contract.denied_tools or tool not in contract.allowed_tools:
            return False, "tool_not_allowed"
        if action in HIGH_RISK_ACTIONS and (action in contract.approval_actions or contract.autonomy_level < 4) and not approval:
            return False, "owner_approval_required"
        return True, "allowed"

    @staticmethod
    def credential_readiness(required_refs: Sequence[str], environment: Mapping[str, str]) -> dict[str, Any]:
        missing = [name for name in required_refs if not environment.get(name)]
        leaked = [name for name, value in environment.items() if value and any(token in name.upper() for token in ("PASSWORD", "TOKEN", "SECRET", "KEY")) and value.startswith(("sk-", "ghp_"))]
        return {"ready": not missing and not leaked, "missing_references": missing, "possible_raw_secret_values": leaked}


class ModelRouter:
    ORDER = {"cache": 0, "deterministic": 1, "internal_api": 2, "local_model": 3, "free_provider": 4, "paid": 5, "premium": 6}

    def choose(self, profiles: Sequence[ProviderProfile], *, required: set[str], max_cost: float,
               minimum_privacy: int = 0) -> ProviderProfile:
        candidates = [p for p in profiles if p.enabled and required <= p.capabilities and p.estimated_cost <= max_cost and p.privacy_score >= minimum_privacy]
        if not candidates:
            raise LookupError("no suitable provider")
        return min(candidates, key=lambda p: (self.ORDER.get(p.route_class, 99), p.estimated_cost, -p.reliability_score, p.provider_id))


class EvidenceRanker:
    @staticmethod
    def score(*, authority: int, freshness: int, corroboration: int, directness: int, conflict_penalty: int = 0) -> int:
        values = (authority, freshness, corroboration, directness)
        if any(not 0 <= x <= 100 for x in values) or not 0 <= conflict_penalty <= 100:
            raise ValueError("scores must be 0..100")
        return max(0, round(0.35 * authority + 0.25 * freshness + 0.2 * corroboration + 0.2 * directness - 0.3 * conflict_penalty))

    @staticmethod
    def classify(statement_type: str) -> str:
        allowed = {"verified_fact", "source_claim", "inference", "assumption", "risk", "action_hypothesis"}
        if statement_type not in allowed:
            raise ValueError("invalid statement type")
        return statement_type


class CapabilityQuarantine:
    REQUIRED = {"licence", "security", "maintenance", "duplication", "cost", "data_access"}

    @classmethod
    def verdict(cls, review: Mapping[str, str]) -> str:
        missing = cls.REQUIRED - set(review)
        if missing:
            return "QUARANTINED_INCOMPLETE_REVIEW"
        if review["security"] not in {"pass", "low"} or review["licence"] in {"unknown", "incompatible"}:
            return "QUARANTINED_REJECT"
        return "APPROVED_FOR_STAGING_ADAPTER_ONLY"


def sign_envelope(payload: Mapping[str, Any], secret: bytes, *, idempotency_key: str, timestamp: int | None = None) -> SignedEnvelope:
    ts = int(time.time()) if timestamp is None else timestamp
    message_id = uuid.uuid4().hex
    body = canonical_json({"message_id": message_id, "timestamp": ts, "idempotency_key": idempotency_key, "payload": payload})
    signature = hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
    return SignedEnvelope(message_id, ts, idempotency_key, payload, signature)


def verify_envelope(envelope: SignedEnvelope, secret: bytes, *, now: int | None = None, max_age: int = 300) -> bool:
    current = int(time.time()) if now is None else now
    if abs(current - envelope.timestamp) > max_age:
        return False
    body = canonical_json({"message_id": envelope.message_id, "timestamp": envelope.timestamp,
                           "idempotency_key": envelope.idempotency_key, "payload": envelope.payload})
    expected = hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, envelope.signature)


class DomainStagingFactory:
    """Bounded, deterministic staging implementations. No external side effects."""

    @staticmethod
    def cfo_scenario(assets: float, liabilities: float, annual_cashflow: float, shock_pct: float) -> dict[str, float]:
        if shock_pct < -1:
            raise ValueError("shock_pct below -100%")
        net_worth = assets - liabilities
        stressed_assets = assets * (1 + shock_pct)
        return {"net_worth": round(net_worth, 2), "stressed_net_worth": round(stressed_assets - liabilities, 2),
                "cashflow_coverage": round(annual_cashflow / liabilities, 4) if liabilities else float("inf")}

    @staticmethod
    def crypto_scenario(holdings: Mapping[str, float], prices: Mapping[str, float], annual_yield: float = 0.0) -> dict[str, float]:
        if not 0 <= annual_yield <= 1:
            raise ValueError("annual_yield must be 0..1")
        values = {asset: float(amount) * float(prices.get(asset, 0)) for asset, amount in holdings.items()}
        total = sum(values.values())
        return {**{f"{k}_value": round(v, 2) for k, v in values.items()}, "total_value": round(total, 2),
                "illustrative_annual_yield": round(total * annual_yield, 2)}

    @staticmethod
    def paper_trade(cash: float, price: float, quantity: float, side: str, max_position_value: float) -> dict[str, float | str]:
        if side not in {"buy", "sell"} or price <= 0 or quantity <= 0:
            raise ValueError("invalid paper order")
        notional = price * quantity
        if notional > max_position_value:
            return {"status": "REJECTED_RISK_LIMIT", "notional": round(notional, 2), "cash": round(cash, 2)}
        new_cash = cash - notional if side == "buy" else cash + notional
        if new_cash < 0:
            return {"status": "REJECTED_INSUFFICIENT_CASH", "notional": round(notional, 2), "cash": round(cash, 2)}
        return {"status": "PAPER_FILLED", "notional": round(notional, 2), "cash": round(new_cash, 2)}

    @staticmethod
    def agency_unit_economics(price: float, variable_cost: float, acquisition_cost: float, hours: float) -> dict[str, float]:
        if min(price, variable_cost, acquisition_cost, hours) < 0:
            raise ValueError("negative input")
        contribution = price - variable_cost - acquisition_cost
        return {"contribution": round(contribution, 2), "margin_pct": round((contribution / price * 100), 2) if price else 0.0,
                "contribution_per_hour": round(contribution / hours, 2) if hours else 0.0}

    @staticmethod
    def saas_stage_gate(*, tests_pass: bool, security_pass: bool, billing_live: bool, owner_publish_approval: bool) -> str:
        if not tests_pass or not security_pass:
            return "BLOCKED_TEST_OR_SECURITY"
        if billing_live or owner_publish_approval:
            return "BLOCKED_PRODUCTION_APPROVAL_PATH"
        return "INTEGRATED_STAGING"
