from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

OBJECT_TYPES = {
    "framework", "spec", "workflow", "stack", "architecture", "orchestrator",
    "skill", "agent", "prompt", "instruction", "policy", "schema", "model_route",
    "tool", "integration", "connector", "ui", "test", "deployment_profile",
    "memory_policy", "source", "module", "service", "sop", "ojt",
}
AUTOMATION_MODES = {"MANUAL_ONLY", "RECOMMEND", "AUTO_REVERSIBLE", "GATED_EXECUTION"}
CHANGE_STATES = {
    "PROPOSED", "SIMULATED", "AWAITING_APPROVAL", "APPROVED", "APPLIED_STAGING",
    "VERIFIED", "REJECTED", "ROLLED_BACK", "BLOCKED",
}
HIGH_RISK_TYPES = {"policy", "deployment_profile", "memory_policy", "connector"}
HIGH_RISK_ACTIONS = {"production", "publish", "money_movement", "live_trading", "credential", "destructive"}
SOURCE_STATES = {
    "AVAILABLE", "PENDING_INGEST", "FAILED_WITH_REASON", "DUPLICATE_WITH_LINEAGE",
    "EXCLUDED_WITH_REASON", "BLOCKED_BY_ACCESS",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EditableObjectSpec:
    object_id: str
    object_type: str
    name: str
    version: str
    location: str
    scope: str
    owner: str
    automation_mode: str
    content: str
    editable_fields: tuple[str, ...] = ("content",)
    dependencies: tuple[str, ...] = ()
    validators: tuple[str, ...] = ()
    rollback_ref: str = "previous-version"
    status: str = "IMPLEMENTED_NOT_INTEGRATED"

    def validate(self) -> None:
        if self.object_type not in OBJECT_TYPES:
            raise ValueError("invalid object type")
        if self.automation_mode not in AUTOMATION_MODES:
            raise ValueError("invalid automation mode")
        if not all((self.object_id, self.name, self.version, self.location, self.scope, self.owner)):
            raise ValueError("missing object identity")
        if not self.editable_fields:
            raise ValueError("editable fields required")


@dataclass(frozen=True)
class ChangeRequest:
    request_id: str
    actor: str
    source_pointer: str
    objective: str
    target_ids: tuple[str, ...]
    operations: tuple[Mapping[str, Any], ...]
    requested_mode: str = "RECOMMEND"
    manual_override: bool = False
    requested_action: str = "staging"

    def validate(self) -> None:
        if not self.actor or not self.source_pointer or not self.objective or not self.target_ids:
            raise ValueError("incomplete change request")
        if self.requested_mode not in AUTOMATION_MODES:
            raise ValueError("invalid requested mode")
        if self.requested_action not in ({"staging"} | HIGH_RISK_ACTIONS):
            raise ValueError("invalid requested action")
        for operation in self.operations:
            if operation.get("op") not in {"replace", "append", "set"}:
                raise ValueError("invalid operation")


@dataclass(frozen=True)
class ChangePlan:
    plan_id: str
    request_id: str
    target_ids: tuple[str, ...]
    state: str
    blast_radius: tuple[str, ...]
    required_approvals: tuple[str, ...]
    tests: tuple[str, ...]
    rollback_points: tuple[str, ...]
    diffs: Mapping[str, Mapping[str, str]]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class SourceCoverageRecord:
    source_id: str
    title: str
    state: str
    pointer: str
    reason: str = ""

    def validate(self) -> None:
        if self.state not in SOURCE_STATES:
            raise ValueError("invalid source state")
        if not self.source_id or not self.title or not self.pointer:
            raise ValueError("source identity required")
        if self.state in {"FAILED_WITH_REASON", "EXCLUDED_WITH_REASON", "BLOCKED_BY_ACCESS"} and not self.reason:
            raise ValueError("reason required for non-available source")


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS editable_objects(
 object_id TEXT PRIMARY KEY, object_type TEXT NOT NULL, name TEXT NOT NULL,
 version TEXT NOT NULL, location TEXT NOT NULL, scope TEXT NOT NULL, owner TEXT NOT NULL,
 automation_mode TEXT NOT NULL, content TEXT NOT NULL, content_digest TEXT NOT NULL,
 editable_fields_json TEXT NOT NULL, dependencies_json TEXT NOT NULL, validators_json TEXT NOT NULL,
 rollback_ref TEXT NOT NULL, status TEXT NOT NULL, updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS object_versions(
 version_id TEXT PRIMARY KEY, object_id TEXT NOT NULL REFERENCES editable_objects(object_id),
 version TEXT NOT NULL, content TEXT NOT NULL, content_digest TEXT NOT NULL,
 reason TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS change_requests(
 request_id TEXT PRIMARY KEY, actor TEXT NOT NULL, source_pointer TEXT NOT NULL,
 objective TEXT NOT NULL, target_ids_json TEXT NOT NULL, operations_json TEXT NOT NULL,
 requested_mode TEXT NOT NULL, manual_override INTEGER NOT NULL, requested_action TEXT NOT NULL,
 state TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS change_plans(
 plan_id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES change_requests(request_id),
 plan_json TEXT NOT NULL, state TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals(
 approval_id TEXT PRIMARY KEY, plan_id TEXT NOT NULL REFERENCES change_plans(plan_id),
 authority TEXT NOT NULL, decision TEXT NOT NULL, reason TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events(
 event_id TEXT PRIMARY KEY, correlation_id TEXT NOT NULL, actor TEXT NOT NULL,
 action TEXT NOT NULL, outcome TEXT NOT NULL, payload_json TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS source_coverage(
 source_id TEXT PRIMARY KEY, title TEXT NOT NULL, state TEXT NOT NULL,
 pointer TEXT NOT NULL, reason TEXT NOT NULL, updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS assistant_sessions(
 session_id TEXT PRIMARY KEY, channel TEXT NOT NULL, model_route TEXT NOT NULL,
 context_json TEXT NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS assistant_messages(
 message_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES assistant_sessions(session_id),
 role TEXT NOT NULL, content TEXT NOT NULL, redacted INTEGER NOT NULL, created_at INTEGER NOT NULL
);
"""


class EvolutionStore:
    """Versioned editable-object and change-governance store."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def audit(self, actor: str, action: str, outcome: str, payload: Mapping[str, Any], correlation_id: str | None = None) -> str:
        event_id = f"evt-{uuid.uuid4().hex}"
        with self.db:
            self.db.execute(
                "INSERT INTO audit_events VALUES(?,?,?,?,?,?,?)",
                (event_id, correlation_id or uuid.uuid4().hex, actor, action, outcome, canonical_json(payload), int(time.time())),
            )
        return event_id

    def register_object(self, spec: EditableObjectSpec, *, reason: str = "initial registration") -> dict[str, Any]:
        spec.validate()
        now = int(time.time())
        content_digest = digest_text(spec.content)
        current = self.db.execute("SELECT * FROM editable_objects WHERE object_id=?", (spec.object_id,)).fetchone()
        with self.db:
            if current and current["content_digest"] != content_digest:
                self.db.execute(
                    "INSERT INTO object_versions VALUES(?,?,?,?,?,?,?)",
                    (f"ver-{uuid.uuid4().hex}", spec.object_id, current["version"], current["content"], current["content_digest"], reason, now),
                )
            self.db.execute(
                "INSERT INTO editable_objects VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(object_id) DO UPDATE SET object_type=excluded.object_type,name=excluded.name,version=excluded.version,"
                "location=excluded.location,scope=excluded.scope,owner=excluded.owner,automation_mode=excluded.automation_mode,"
                "content=excluded.content,content_digest=excluded.content_digest,editable_fields_json=excluded.editable_fields_json,"
                "dependencies_json=excluded.dependencies_json,validators_json=excluded.validators_json,rollback_ref=excluded.rollback_ref,"
                "status=excluded.status,updated_at=excluded.updated_at",
                (
                    spec.object_id, spec.object_type, spec.name, spec.version, spec.location, spec.scope, spec.owner,
                    spec.automation_mode, spec.content, content_digest, canonical_json(spec.editable_fields),
                    canonical_json(spec.dependencies), canonical_json(spec.validators), spec.rollback_ref, spec.status, now,
                ),
            )
        self.audit(spec.owner, "register_object", "registered", {"object_id": spec.object_id, "digest": content_digest})
        return self.get_object(spec.object_id)

    def get_object(self, object_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM editable_objects WHERE object_id=?", (object_id,)).fetchone()
        if row is None:
            raise KeyError(object_id)
        result = dict(row)
        for field in ("editable_fields_json", "dependencies_json", "validators_json"):
            result[field.removesuffix("_json")] = json.loads(result.pop(field))
        return result

    def list_objects(self, object_type: str | None = None) -> list[dict[str, Any]]:
        if object_type is not None and object_type not in OBJECT_TYPES:
            raise ValueError("invalid object type")
        sql = "SELECT object_id FROM editable_objects"
        args: tuple[Any, ...] = ()
        if object_type:
            sql += " WHERE object_type=?"
            args = (object_type,)
        sql += " ORDER BY object_type,name"
        return [self.get_object(row[0]) for row in self.db.execute(sql, args)]

    def register_source(self, record: SourceCoverageRecord) -> None:
        record.validate()
        with self.db:
            self.db.execute(
                "INSERT INTO source_coverage VALUES(?,?,?,?,?,?) ON CONFLICT(source_id) DO UPDATE SET "
                "title=excluded.title,state=excluded.state,pointer=excluded.pointer,reason=excluded.reason,updated_at=excluded.updated_at",
                (record.source_id, record.title, record.state, record.pointer, record.reason, int(time.time())),
            )

    def source_coverage_report(self) -> dict[str, Any]:
        rows = [dict(r) for r in self.db.execute("SELECT * FROM source_coverage ORDER BY source_id")]
        counts = {state: 0 for state in SOURCE_STATES}
        for row in rows:
            counts[row["state"]] += 1
        unresolved = [r for r in rows if r["state"] in {"PENDING_INGEST", "FAILED_WITH_REASON", "BLOCKED_BY_ACCESS"}]
        accounted = len(rows)
        resolved = accounted - len(unresolved)
        return {
            "denominator": accounted,
            "resolved": resolved,
            "counts": counts,
            "unresolved": unresolved,
            "coverage_percent": round((resolved / accounted * 100), 2) if accounted else 0.0,
            "universal_100_percent_allowed": bool(accounted) and not unresolved,
            "truth_boundary": "100 percent is allowed only when every known source is available, duplicated with lineage, or excluded with a reason; implementation proof remains separate.",
        }

    @staticmethod
    def _apply_operations(content: str, operations: Sequence[Mapping[str, Any]]) -> str:
        result = content
        for operation in operations:
            op = operation["op"]
            if op == "replace":
                old = str(operation.get("old", ""))
                new = str(operation.get("new", ""))
                if old not in result:
                    raise ValueError("replace target not found")
                result = result.replace(old, new)
            elif op == "append":
                result += str(operation.get("value", ""))
            elif op == "set":
                result = str(operation.get("value", ""))
        return result

    def propose_change(self, request: ChangeRequest, *, tests: Sequence[str] = ()) -> ChangePlan:
        request.validate()
        targets = [self.get_object(target_id) for target_id in request.target_ids]
        required: set[str] = set()
        reasons: list[str] = []
        if request.manual_override:
            required.add("OWNER")
            reasons.append("manual override requires an explicit owner decision and pauses autonomous promotion")
        if request.requested_action in HIGH_RISK_ACTIONS:
            required.update({"OWNER", "RISK_AUTHORITY", "RELEASE_GATEKEEPER"})
            reasons.append("high-risk action")
        for target in targets:
            if target["automation_mode"] in {"MANUAL_ONLY", "GATED_EXECUTION"} or target["object_type"] in HIGH_RISK_TYPES:
                required.add("OWNER")
                reasons.append(f"{target['object_id']} is protected")
        diffs: dict[str, Mapping[str, str]] = {}
        rollback_points: list[str] = []
        for target in targets:
            next_content = self._apply_operations(target["content"], request.operations)
            diffs[target["object_id"]] = {
                "before_digest": target["content_digest"],
                "after_digest": digest_text(next_content),
                "before": target["content"],
                "after": next_content,
            }
            rollback_points.append(f"{target['object_id']}@{target['version']}")
        state = "AWAITING_APPROVAL" if required else "SIMULATED"
        plan = ChangePlan(
            plan_id=f"plan-{uuid.uuid4().hex}", request_id=request.request_id,
            target_ids=request.target_ids, state=state,
            blast_radius=tuple(sorted(set(request.target_ids) | {dep for target in targets for dep in target["dependencies"]})),
            required_approvals=tuple(sorted(required)), tests=tuple(tests),
            rollback_points=tuple(rollback_points), diffs=diffs,
            reasons=tuple(dict.fromkeys(reasons)),
        )
        now = int(time.time())
        with self.db:
            self.db.execute(
                "INSERT INTO change_requests VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (request.request_id, request.actor, request.source_pointer, request.objective,
                 canonical_json(request.target_ids), canonical_json(request.operations), request.requested_mode,
                 int(request.manual_override), request.requested_action, state, now),
            )
            self.db.execute(
                "INSERT INTO change_plans VALUES(?,?,?,?,?)",
                (plan.plan_id, plan.request_id, canonical_json(asdict(plan)), state, now),
            )
        self.audit(request.actor, "propose_change", state, {"plan_id": plan.plan_id, "targets": request.target_ids})
        return plan

    def decide(self, plan_id: str, authority: str, decision: str, reason: str) -> str:
        if decision not in {"APPROVE", "REJECT"} or not authority or not reason:
            raise ValueError("invalid approval decision")
        plan_row = self.db.execute("SELECT * FROM change_plans WHERE plan_id=?", (plan_id,)).fetchone()
        if plan_row is None:
            raise KeyError(plan_id)
        plan = json.loads(plan_row["plan_json"])
        with self.db:
            self.db.execute(
                "INSERT INTO approvals VALUES(?,?,?,?,?,?)",
                (f"approval-{uuid.uuid4().hex}", plan_id, authority, decision, reason, int(time.time())),
            )
            if decision == "REJECT":
                self.db.execute("UPDATE change_plans SET state='REJECTED' WHERE plan_id=?", (plan_id,))
                self.db.execute("UPDATE change_requests SET state='REJECTED' WHERE request_id=?", (plan["request_id"],))
                return "REJECTED"
        required = set(plan["required_approvals"])
        approvals = {row[0] for row in self.db.execute(
            "SELECT authority FROM approvals WHERE plan_id=? AND decision='APPROVE'", (plan_id,)
        )}
        state = "APPROVED" if required <= approvals else "AWAITING_APPROVAL"
        with self.db:
            self.db.execute("UPDATE change_plans SET state=? WHERE plan_id=?", (state, plan_id))
            self.db.execute("UPDATE change_requests SET state=? WHERE request_id=?", (state, plan["request_id"]))
        return state

    def apply_staging(self, plan_id: str, *, verifier: Callable[[str, str], bool] | None = None) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM change_plans WHERE plan_id=?", (plan_id,)).fetchone()
        if row is None:
            raise KeyError(plan_id)
        plan = json.loads(row["plan_json"])
        if row["state"] == "AWAITING_APPROVAL":
            raise PermissionError("required approvals missing")
        request = self.db.execute("SELECT * FROM change_requests WHERE request_id=?", (plan["request_id"],)).fetchone()
        if request["requested_action"] != "staging":
            raise PermissionError("direct high-risk or production self-modification is prohibited")
        applied: list[str] = []
        try:
            with self.db:
                for target_id, change in plan["diffs"].items():
                    current = self.get_object(target_id)
                    if current["content_digest"] != change["before_digest"]:
                        raise RuntimeError("target changed after simulation")
                    if verifier is not None and not verifier(target_id, change["after"]):
                        raise ValueError("verification failed")
                    self.db.execute(
                        "INSERT INTO object_versions VALUES(?,?,?,?,?,?,?)",
                        (f"ver-{uuid.uuid4().hex}", target_id, current["version"], current["content"],
                         current["content_digest"], f"before plan {plan_id}", int(time.time())),
                    )
                    self.db.execute(
                        "UPDATE editable_objects SET content=?,content_digest=?,version=?,status='INTEGRATED_STAGING',updated_at=? WHERE object_id=?",
                        (change["after"], change["after_digest"], self._next_version(current["version"]), int(time.time()), target_id),
                    )
                    applied.append(target_id)
                self.db.execute("UPDATE change_plans SET state='VERIFIED' WHERE plan_id=?", (plan_id,))
                self.db.execute("UPDATE change_requests SET state='VERIFIED' WHERE request_id=?", (plan["request_id"],))
        except Exception:
            self.db.rollback()
            raise
        self.audit("evolution-engine", "apply_staging", "VERIFIED", {"plan_id": plan_id, "applied": applied})
        return {"state": "VERIFIED", "applied": applied, "rollback_points": plan["rollback_points"]}

    @staticmethod
    def _next_version(version: str) -> str:
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
        if not match:
            return f"{version}+1"
        major, minor, patch = map(int, match.groups())
        return f"{major}.{minor}.{patch + 1}"

    def rollback(self, object_id: str, *, authority: str, reason: str) -> dict[str, Any]:
        if authority != "OWNER" or not reason:
            raise PermissionError("owner authority required")
        prior = self.db.execute(
            "SELECT * FROM object_versions WHERE object_id=? ORDER BY created_at DESC, version_id DESC LIMIT 1", (object_id,)
        ).fetchone()
        if prior is None:
            raise LookupError("no rollback point")
        with self.db:
            current = self.get_object(object_id)
            self.db.execute(
                "INSERT INTO object_versions VALUES(?,?,?,?,?,?,?)",
                (f"ver-{uuid.uuid4().hex}", object_id, current["version"], current["content"],
                 current["content_digest"], f"rollback displaced version: {reason}", int(time.time())),
            )
            self.db.execute(
                "UPDATE editable_objects SET version=?,content=?,content_digest=?,status='INTEGRATED_STAGING',updated_at=? WHERE object_id=?",
                (prior["version"], prior["content"], prior["content_digest"], int(time.time()), object_id),
            )
        self.audit(authority, "rollback", "ROLLED_BACK", {"object_id": object_id, "reason": reason})
        return self.get_object(object_id)


class SelfRepairEngine:
    """Safe repair loop for reversible staging objects only."""

    def __init__(self, store: EvolutionStore) -> None:
        self.store = store

    def repair(self, object_id: str, validators: Sequence[Callable[[str], tuple[bool, str]]],
               repairer: Callable[[str, Sequence[str]], str], *, source_pointer: str = "runtime:self-repair") -> dict[str, Any]:
        target = self.store.get_object(object_id)
        if target["automation_mode"] != "AUTO_REVERSIBLE":
            return {"state": "BLOCKED", "reason": "object is not approved for reversible automatic repair"}
        failures = [message for passed, message in (validator(target["content"]) for validator in validators) if not passed]
        if not failures:
            return {"state": "NO_CHANGE", "failures": []}
        repaired = repairer(target["content"], failures)
        request = ChangeRequest(
            request_id=f"repair-{uuid.uuid4().hex}", actor="self-repair-engine", source_pointer=source_pointer,
            objective="repair validator failures", target_ids=(object_id,),
            operations=({"op": "set", "value": repaired},), requested_mode="AUTO_REVERSIBLE", requested_action="staging",
        )
        plan = self.store.propose_change(request, tests=tuple(target["validators"]))
        result = self.store.apply_staging(
            plan.plan_id, verifier=lambda _target_id, content: all(validator(content)[0] for validator in validators),
        )
        return {"state": result["state"], "failures": failures, "plan_id": plan.plan_id,
                "object": self.store.get_object(object_id)}


class UnifiedJarvisAssistant:
    """Text/voice-parity assistant session and popup control contract."""

    REDACTION_PATTERNS = (
        re.compile(r"(?i)(password|secret|token|api[_ -]?key)\s*[:=]\s*\S+"),
        re.compile(r"\b\d{6}\b"),
    )

    def __init__(self, store: EvolutionStore,
                 model_routes: Sequence[str] = ("deterministic", "local", "free-first", "manual")) -> None:
        self.store = store
        self.model_routes = tuple(dict.fromkeys(model_routes))

    @classmethod
    def redact(cls, text: str) -> tuple[str, bool]:
        result = text
        for pattern in cls.REDACTION_PATTERNS:
            result = pattern.sub("[REDACTED]", result)
        return result, result != text

    def start_session(self, *, channel: str, model_route: str = "free-first",
                      context: Mapping[str, Any] | None = None) -> str:
        if channel not in {"text", "voice", "multimodal"}:
            raise ValueError("invalid assistant channel")
        if model_route not in self.model_routes:
            raise ValueError("unsupported model route")
        session_id = f"session-{uuid.uuid4().hex}"
        with self.store.db:
            self.store.db.execute(
                "INSERT INTO assistant_sessions VALUES(?,?,?,?,?)",
                (session_id, channel, model_route, canonical_json(context or {}), int(time.time())),
            )
        return session_id

    def add_message(self, session_id: str, role: str, content: str) -> dict[str, Any]:
        if role not in {"user", "assistant", "system", "tool"}:
            raise ValueError("invalid message role")
        safe_content, redacted = self.redact(content)
        message_id = f"message-{uuid.uuid4().hex}"
        with self.store.db:
            self.store.db.execute(
                "INSERT INTO assistant_messages VALUES(?,?,?,?,?,?)",
                (message_id, session_id, role, safe_content, int(redacted), int(time.time())),
            )
        return {"message_id": message_id, "content": safe_content, "redacted": redacted}

    def command_preview(self, command: str) -> dict[str, Any]:
        normalized = command.strip().lower()
        action = "explain"
        risk = "read_only"
        if any(word in normalized for word in ("edit", "update", "change", "repair", "fix")):
            action = "propose_change"
            risk = "reversible_staging"
        if "rollback" in normalized:
            action = "rollback_request"
            risk = "owner_gated"
        if any(word in normalized for word in ("production", "publish", "trade", "payment", "secret")):
            action = "prepare_only"
            risk = "high_risk_owner_gated"
        return {
            "command": command, "action": action, "risk": risk,
            "automatic_execution": risk in {"read_only", "reversible_staging"},
            "approval_required": risk in {"owner_gated", "high_risk_owner_gated"},
            "voice_and_text_same_policy": True,
        }

    def popup_payload(self, session_id: str, *, active_object_id: str | None = None) -> dict[str, Any]:
        session = self.store.db.execute("SELECT * FROM assistant_sessions WHERE session_id=?", (session_id,)).fetchone()
        if session is None:
            raise KeyError(session_id)
        messages = [dict(row) for row in self.store.db.execute(
            "SELECT role,content,redacted,created_at FROM assistant_messages WHERE session_id=? ORDER BY created_at,message_id",
            (session_id,),
        )]
        active = self.store.get_object(active_object_id) if active_object_id else None
        return {
            "component": "JARVIS_POP_UNIFIED_ASSISTANT_V1",
            "channel": session["channel"], "model_route": session["model_route"],
            "model_options": list(self.model_routes), "messages": messages, "active_object": active,
            "panels": {
                "chat": True, "voice_transcript": True, "llm_selector": True, "object_browser": True,
                "context_and_evidence": True, "diff_preview": True, "approval_queue": True,
                "activity_timeline": True, "tests_and_health": True, "rollback_history": True,
            },
            "controls": {
                "send": "ENABLED", "push_to_talk": "AVAILABLE_NOT_CONNECTED",
                "stop_mute_cancel": "ALWAYS_AVAILABLE", "preview_change": "ENABLED",
                "apply_safe_staging": "POLICY_GATED", "manual_override": "OWNER_GATED",
                "rollback": "OWNER_GATED", "production": "DISABLED_UNTIL_RELEASE_GATE",
                "money_movement": "DISABLED", "live_trading": "DISABLED",
            },
            "suggestions": [
                "Explain this object in simple English", "Show dependencies and blast radius",
                "Propose a safe update", "Run checks and suggest repairs", "Show versions, evidence and rollback",
            ],
            "accessibility": {
                "keyboard_navigation": True, "screen_reader_labels": True, "reduced_motion": True,
                "high_contrast": True, "captions_and_transcript": True, "mobile_responsive": True,
            },
        }


def default_editable_object_catalog() -> list[EditableObjectSpec]:
    return [
        EditableObjectSpec(
            object_id=f"jarvis-{object_type}-root", object_type=object_type,
            name=f"Jarvis {object_type.replace('_', ' ').title()} Root", version="1.0.0",
            location=f"registry/editable/{object_type}.json",
            scope="GLOBAL_CONTROL_PLANE" if object_type in {"framework", "architecture", "orchestrator", "policy"} else "MODULE_SPECIFIC",
            owner="JARVIS_OWNER",
            automation_mode="GATED_EXECUTION" if object_type in HIGH_RISK_TYPES else "AUTO_REVERSIBLE",
            content=canonical_json({"object_type": object_type, "enabled": True, "status": "registered"}),
            validators=("schema", "security", "regression"),
        )
        for object_type in sorted(OBJECT_TYPES)
    ]
