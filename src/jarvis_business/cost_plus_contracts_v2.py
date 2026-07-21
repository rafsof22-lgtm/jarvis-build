from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Mapping
from uuid import NAMESPACE_URL, uuid5

from .runtime import BUSINESS_COST_PLUS_ONE, BUSINESS_JENOK

SCHEMA_VERSION = "2.0.0"
SECRET_KEY_PATTERN = re.compile(r"(?:^|_)(?:password|passwd|access_token|refresh_token|api_key|private_key|seed_phrase|recovery_code|secret_value)(?:$|_)", re.IGNORECASE)

WORKFLOW_CONTRACTS: dict[str, dict[str, Any]] = {
    "WF-ORDER": {"event_type": "cost.order.created.v2", "business_id": BUSINESS_COST_PLUS_ONE, "required": ["customer_id", "vehicle_id", "lines", "zone", "delivery_run", "requested_channel"], "purpose": "Create a customer order before supplier splitting."},
    "WF-PICKUP": {"event_type": "cost.supplier_pickup.received.v2", "business_id": BUSINESS_COST_PLUS_ONE, "required": ["purchase_order_id", "supplier_id", "received_lines", "verification_method", "condition_check"], "purpose": "Record supplier pickup and verification evidence."},
    "WF-DELIVERY": {"event_type": "cost.delivery_assignment.created.v2", "business_id": BUSINESS_COST_PLUS_ONE, "required": ["customer_id", "delivery_run", "zone", "allocation_type", "allocation_number", "order_ids"], "purpose": "Assign a run-scoped side locker or centre-trolley slot."},
    "WF-LEAD": {"event_type": "cost.workshop_lead.created.v2", "business_id": BUSINESS_COST_PLUS_ONE, "required": ["customer_id", "vehicle_id", "workshop_id", "quote_request_id", "billable_rule_version", "consent_state"], "purpose": "Route a repair lead with consent and billing evidence."},
    "WF-BILL": {"event_type": "cost.monthly_statement.calculated.v2", "business_id": BUSINESS_COST_PLUS_ONE, "required": ["account_id", "period", "policy_id", "base_amount_aud", "fee_amount_aud", "delivery_count", "evidence_ref"], "purpose": "Record a monthly fee under an approved policy."},
    "WF-WARRANTY": {"event_type": "cost.warranty_claim.opened.v2", "business_id": BUSINESS_COST_PLUS_ONE, "required": ["order_id", "item_id", "claim_reason", "evidence_refs", "requested_resolution"], "purpose": "Open a warranty claim with lineage and evidence."},
    "WF-JENOK": {"event_type": "jenok.catalogue_item.upserted.v2", "business_id": BUSINESS_JENOK, "required": ["sku", "brand", "part_number", "fitment", "source_pointer", "source_rights_state"], "purpose": "Upsert a Jenok item under a separate namespace and rights gate."},
}
EVENT_TYPE_TO_WORKFLOW = {v["event_type"]: k for k, v in WORKFLOW_CONTRACTS.items()}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_id(namespace: str, *parts: object) -> str:
    material = "|".join(str(p).strip().lower() for p in parts)
    return str(uuid5(NAMESPACE_URL, f"jarvis:{namespace}:{material}"))


def _walk_keys(value: Any, path: str = "payload") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            current = f"{path}.{key}"
            yield current, child
            yield from _walk_keys(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def _require_nonempty(payload: Mapping[str, Any], fields: Iterable[str]) -> None:
    missing = [field for field in fields if field not in payload or payload[field] in (None, "", [], {})]
    if missing:
        raise ValueError(f"missing required payload fields: {', '.join(missing)}")


def _decimal(value: Any, field: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except Exception as exc:
        raise ValueError(f"{field} must be decimal-compatible") from exc
    if parsed < 0:
        raise ValueError(f"{field} cannot be negative")
    return parsed


@dataclass(frozen=True)
class EventEnvelope:
    event_id: str
    workflow_id: str
    event_type: str
    schema_version: str
    business_id: str
    aggregate_id: str
    correlation_id: str
    causation_id: str | None
    idempotency_key: str
    occurred_at: str
    source_pointer: str
    data_classification: str
    payload_sha256: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CostPlusContractEngine:
    """Validate seven bounded Cost + $1/Jenok domain contracts."""

    def __init__(self, *, approved_billing_policy_ids: Iterable[str] = ()) -> None:
        self.approved_billing_policy_ids = frozenset(str(x) for x in approved_billing_policy_ids)

    def build_event(self, *, event_type: str, business_id: str, aggregate_id: str, correlation_id: str, idempotency_key: str, payload: Mapping[str, Any], source_pointer: str, data_classification: str = "CONFIDENTIAL_BUSINESS", causation_id: str | None = None, occurred_at: str | None = None) -> EventEnvelope:
        workflow_id = EVENT_TYPE_TO_WORKFLOW.get(event_type)
        if not workflow_id:
            raise ValueError("unknown event_type")
        contract = WORKFLOW_CONTRACTS[workflow_id]
        if business_id != contract["business_id"]:
            raise ValueError("event_type cannot cross business namespace")
        for label, value in {"aggregate_id": aggregate_id, "correlation_id": correlation_id, "idempotency_key": idempotency_key, "source_pointer": source_pointer, "data_classification": data_classification}.items():
            if not str(value or "").strip():
                raise ValueError(f"{label} is required")
        clean_payload = dict(payload)
        self._validate_no_secrets(clean_payload)
        _require_nonempty(clean_payload, contract["required"])
        self._validate_payload(workflow_id, clean_payload)
        payload_json = canonical_json(clean_payload)
        payload_sha = sha256_text(payload_json)
        event_id = stable_id("cost-event", business_id, event_type, aggregate_id, idempotency_key, payload_sha)
        return EventEnvelope(event_id, workflow_id, event_type, SCHEMA_VERSION, business_id, aggregate_id, correlation_id, causation_id, idempotency_key, occurred_at or utc_now(), source_pointer, data_classification, payload_sha, clean_payload)

    def _validate_no_secrets(self, payload: Mapping[str, Any]) -> None:
        for path, _value in _walk_keys(payload):
            key = path.rsplit(".", 1)[-1]
            if SECRET_KEY_PATTERN.search(key):
                raise ValueError(f"secret-like payload field prohibited: {path}")

    def _validate_payload(self, workflow_id: str, payload: dict[str, Any]) -> None:
        if workflow_id == "WF-ORDER":
            if not isinstance(payload["lines"], list) or not payload["lines"]:
                raise ValueError("order lines must be a non-empty list")
            for line in payload["lines"]:
                if not isinstance(line, Mapping) or not line.get("sku") or int(line.get("quantity", 0)) <= 0:
                    raise ValueError("each order line requires sku and positive quantity")
            if payload["requested_channel"] not in {"retail_member", "trade", "sales_rep", "staff"}:
                raise ValueError("unsupported requested_channel")
        elif workflow_id == "WF-PICKUP":
            if payload["verification_method"] not in {"barcode", "qr", "photo_manual"}:
                raise ValueError("verification_method must be barcode, qr or photo_manual")
            if payload["verification_method"] == "photo_manual":
                _require_nonempty(payload, ["photo_ref", "manual_count"])
            if not isinstance(payload["received_lines"], list) or not payload["received_lines"]:
                raise ValueError("received_lines must be a non-empty list")
        elif workflow_id == "WF-DELIVERY":
            allocation_type = payload["allocation_type"]
            allocation_number = int(payload["allocation_number"])
            if allocation_type == "side_locker":
                if not 1 <= allocation_number <= 40:
                    raise ValueError("side_locker allocation_number must be 1..40")
            elif allocation_type == "centre_trolley":
                if allocation_number <= 0:
                    raise ValueError("centre_trolley allocation_number must be positive")
            else:
                raise ValueError("allocation_type must be side_locker or centre_trolley")
            if not isinstance(payload["order_ids"], list) or not payload["order_ids"]:
                raise ValueError("order_ids must be a non-empty list")
        elif workflow_id == "WF-LEAD":
            if payload["consent_state"] not in {"captured", "not_required_with_reason", "withdrawn"}:
                raise ValueError("invalid consent_state")
            if payload["consent_state"] == "withdrawn":
                raise ValueError("withdrawn consent cannot create a lead")
        elif workflow_id == "WF-BILL":
            if str(payload["policy_id"]) not in self.approved_billing_policy_ids:
                raise ValueError("billing policy is not approved")
            base = _decimal(payload["base_amount_aud"], "base_amount_aud")
            fee = _decimal(payload["fee_amount_aud"], "fee_amount_aud")
            if fee > base * Decimal("2"):
                raise ValueError("fee_amount_aud exceeds bounded sanity threshold")
            if int(payload["delivery_count"]) < 0:
                raise ValueError("delivery_count cannot be negative")
        elif workflow_id == "WF-WARRANTY":
            if not isinstance(payload["evidence_refs"], list) or not payload["evidence_refs"]:
                raise ValueError("warranty evidence_refs must be a non-empty list")
            if payload["requested_resolution"] not in {"inspect", "replace", "refund", "repair", "supplier_review"}:
                raise ValueError("unsupported requested_resolution")
        elif workflow_id == "WF-JENOK":
            if payload["source_rights_state"] not in {"approved", "public_permitted", "owner_supplied", "pending_review"}:
                raise ValueError("invalid source_rights_state")
            if payload["source_rights_state"] == "pending_review":
                raise ValueError("pending source rights cannot publish a catalogue item")
            if not isinstance(payload["fitment"], Mapping) or not payload["fitment"]:
                raise ValueError("fitment must be a non-empty object")


class BillingPolicyRegistry:
    """Versioned policies; no 20%, 25% or Cost+A$1 default is assumed."""

    def __init__(self) -> None:
        self._policies: dict[str, dict[str, Any]] = {}

    def register_percentage(self, *, policy_id: str, percentage: Decimal, channel: str, approved: bool) -> dict[str, Any]:
        if not policy_id or not channel:
            raise ValueError("policy_id and channel are required")
        percentage = _decimal(percentage, "percentage")
        if percentage > Decimal("100"):
            raise ValueError("percentage cannot exceed 100")
        policy = {"policy_id": policy_id, "kind": "percentage", "percentage": str(percentage), "channel": channel, "approved": bool(approved), "version_hash": sha256_text(canonical_json([policy_id, str(percentage), channel, bool(approved)]))}
        self._policies[policy_id] = policy
        return dict(policy)

    def calculate(self, policy_id: str, base_amount_aud: Decimal) -> Decimal:
        policy = self._policies.get(policy_id)
        if not policy or not policy["approved"]:
            raise ValueError("approved billing policy required")
        base = _decimal(base_amount_aud, "base_amount_aud")
        return (base * Decimal(policy["percentage"]) / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def approved_ids(self) -> set[str]:
        return {pid for pid, policy in self._policies.items() if policy["approved"]}


class SQLiteEventLedger:
    """Local append-only ledger with idempotency collision detection."""

    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS cost_events (event_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, workflow_id TEXT NOT NULL, event_type TEXT NOT NULL, aggregate_id TEXT NOT NULL, correlation_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, occurred_at TEXT NOT NULL, source_pointer TEXT NOT NULL, data_classification TEXT NOT NULL, payload_sha256 TEXT NOT NULL, payload_json TEXT NOT NULL, envelope_json TEXT NOT NULL, recorded_at TEXT NOT NULL, UNIQUE (business_id, idempotency_key))""")
        self.connection.commit()

    def append(self, event: EventEnvelope) -> dict[str, Any]:
        existing = self.connection.execute("SELECT event_id, payload_sha256 FROM cost_events WHERE business_id=? AND idempotency_key=?", (event.business_id, event.idempotency_key)).fetchone()
        if existing:
            if existing["payload_sha256"] != event.payload_sha256:
                raise ValueError("idempotency collision with different payload")
            return {"state": "DUPLICATE_REPLAY", "event_id": existing["event_id"]}
        payload_json = canonical_json(event.payload)
        envelope_json = canonical_json(event.to_dict())
        self.connection.execute("INSERT INTO cost_events (event_id,business_id,workflow_id,event_type,aggregate_id,correlation_id,idempotency_key,occurred_at,source_pointer,data_classification,payload_sha256,payload_json,envelope_json,recorded_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (event.event_id, event.business_id, event.workflow_id, event.event_type, event.aggregate_id, event.correlation_id, event.idempotency_key, event.occurred_at, event.source_pointer, event.data_classification, event.payload_sha256, payload_json, envelope_json, utc_now()))
        self.connection.commit()
        return {"state": "APPENDED", "event_id": event.event_id}

    def events_for_correlation(self, correlation_id: str) -> list[dict[str, Any]]:
        rows = self.connection.execute("SELECT envelope_json FROM cost_events WHERE correlation_id=? ORDER BY rowid", (correlation_id,)).fetchall()
        return [json.loads(row["envelope_json"]) for row in rows]

    def count(self) -> int:
        return int(self.connection.execute("SELECT COUNT(*) FROM cost_events").fetchone()[0])

    def close(self) -> None:
        self.connection.close()


@dataclass(frozen=True)
class Allocation:
    run_id: str
    zone: str
    customer_id: str
    allocation_type: str
    allocation_number: int
    order_ids: tuple[str, ...]


class LockerAllocator:
    """Reference allocator for the latest 40-side-locker vehicle rule."""

    def __init__(self, *, side_locker_capacity: int = 40, centre_trolley_capacity: int = 0) -> None:
        if side_locker_capacity != 40:
            raise ValueError("latest approved source rule requires exactly 40 side lockers")
        if centre_trolley_capacity < 0:
            raise ValueError("centre_trolley_capacity cannot be negative")
        self.side_locker_capacity = side_locker_capacity
        self.centre_trolley_capacity = centre_trolley_capacity
        self._allocations: dict[tuple[str, str, str], Allocation] = {}

    def allocate(self, *, run_id: str, zone: str, customer_id: str, order_ids: Iterable[str]) -> Allocation:
        key = (run_id, zone, customer_id)
        order_tuple = tuple(sorted({str(x) for x in order_ids if str(x)}))
        if not all(key) or not order_tuple:
            raise ValueError("run_id, zone, customer_id and order_ids are required")
        existing = self._allocations.get(key)
        if existing:
            updated = Allocation(existing.run_id, existing.zone, existing.customer_id, existing.allocation_type, existing.allocation_number, tuple(sorted(set(existing.order_ids) | set(order_tuple))))
            self._allocations[key] = updated
            return updated
        run_zone = [a for a in self._allocations.values() if a.run_id == run_id and a.zone == zone]
        used_side = {a.allocation_number for a in run_zone if a.allocation_type == "side_locker"}
        for number in range(1, self.side_locker_capacity + 1):
            if number not in used_side:
                allocation = Allocation(run_id, zone, customer_id, "side_locker", number, order_tuple)
                self._allocations[key] = allocation
                return allocation
        used_centre = {a.allocation_number for a in run_zone if a.allocation_type == "centre_trolley"}
        for number in range(1, self.centre_trolley_capacity + 1):
            if number not in used_centre:
                allocation = Allocation(run_id, zone, customer_id, "centre_trolley", number, order_tuple)
                self._allocations[key] = allocation
                return allocation
        raise RuntimeError("allocation capacity exhausted; engineering-approved overflow route required")

    def snapshot(self) -> list[dict[str, Any]]:
        return [asdict(a) for a in sorted(self._allocations.values(), key=lambda x: (x.run_id, x.zone, x.allocation_type, x.allocation_number))]


def architecture_decision() -> dict[str, Any]:
    return {"decision_id": "COST-ARCH-CORE-001", "canonical_operational_core": "Jarvis-owned custom automotive domain core", "odoo_role": "optional adapter for commodity ERP capabilities after sandbox comparison", "xero_role": "accounting ledger and approved export boundary only; not operational source of truth", "reason": "Preserves business-rule ownership, reversible adapters, testability and vendor independence.", "production_state": "NOT_AUTHORISED"}
