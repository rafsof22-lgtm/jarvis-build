from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .cost_plus_contracts_v2 import (
    BillingPolicyRegistry,
    CostPlusContractEngine,
    LockerAllocator,
    SQLiteEventLedger,
)
from .runtime import BUSINESS_COST_PLUS_ONE

ALLOWED_ACCOUNT_TYPES = {"retail_member", "trade", "workshop", "staff"}
ALLOWED_PROFILE_STATES = {"PENDING", "ACTIVE", "SUSPENDED", "CLOSED"}
ALLOWED_VETTING = {"PENDING", "APPROVED", "REJECTED", "EXPIRED"}
ALLOWED_SOURCE_RIGHTS = {"approved", "public_permitted", "owner_supplied", "pending_review"}
HASH_RE = re.compile(r"[0-9a-f]{64}")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def required(value: Any, label: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{label} is required")
    return result


def required_reference(value: Any, label: str) -> str:
    result = required(value, label)
    if not re.match(r"^(?:ref|hash|source|evidence|terms|policy)://", result):
        raise ValueError(f"{label} must be a pointer/reference, not a direct identifier")
    return result


@dataclass(frozen=True)
class CustomerProfile:
    customer_id: str
    account_type: str
    legal_name_ref: str
    contact_ref: str
    delivery_zone: str
    consent_state: str
    status: str = "PENDING"


@dataclass(frozen=True)
class WorkshopProfile:
    workshop_id: str
    business_name_ref: str
    abn_ref_sha256: str
    service_zones: tuple[str, ...]
    vetting_state: str
    lead_consent_policy_ref: str


@dataclass(frozen=True)
class VehicleProfile:
    vehicle_id: str
    customer_id: str
    vin_sha256: str
    registration_sha256: str
    make: str
    model: str
    year: int
    fitment_evidence_ref: str


@dataclass(frozen=True)
class SupplierProfile:
    supplier_id: str
    supplier_name_ref: str
    source_rights_state: str
    ordering_channel: str
    terms_ref: str
    active: bool = True


@dataclass(frozen=True)
class OrderProfile:
    order_id: str
    customer_id: str
    vehicle_id: str
    channel: str
    zone: str
    delivery_run: str
    lines: tuple[dict[str, Any], ...]
    status: str = "PENDING"


class CostProfileStore:
    """Local namespace-isolated profile store using pointers/hashes instead of direct contact values."""

    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers(
              customer_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, account_type TEXT NOT NULL,
              legal_name_ref TEXT NOT NULL, contact_ref TEXT NOT NULL, delivery_zone TEXT NOT NULL,
              consent_state TEXT NOT NULL, status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS workshops(
              workshop_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, business_name_ref TEXT NOT NULL,
              abn_ref_sha256 TEXT NOT NULL, service_zones_json TEXT NOT NULL, vetting_state TEXT NOT NULL,
              lead_consent_policy_ref TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS vehicles(
              vehicle_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, customer_id TEXT NOT NULL,
              vin_sha256 TEXT NOT NULL, registration_sha256 TEXT NOT NULL, make TEXT NOT NULL,
              model TEXT NOT NULL, year INTEGER NOT NULL, fitment_evidence_ref TEXT NOT NULL,
              FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
            );
            CREATE TABLE IF NOT EXISTS suppliers(
              supplier_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, supplier_name_ref TEXT NOT NULL,
              source_rights_state TEXT NOT NULL, ordering_channel TEXT NOT NULL, terms_ref TEXT NOT NULL,
              active INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS orders(
              order_id TEXT PRIMARY KEY, business_id TEXT NOT NULL, customer_id TEXT NOT NULL,
              vehicle_id TEXT NOT NULL, channel TEXT NOT NULL, zone TEXT NOT NULL, delivery_run TEXT NOT NULL,
              lines_json TEXT NOT NULL, status TEXT NOT NULL,
              FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
              FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id)
            );
            """
        )
        self.connection.commit()

    def upsert_customer(self, profile: CustomerProfile) -> str:
        if profile.account_type not in ALLOWED_ACCOUNT_TYPES:
            raise ValueError("unsupported account_type")
        if profile.status not in ALLOWED_PROFILE_STATES:
            raise ValueError("invalid customer status")
        if profile.consent_state not in {"captured", "not_required_with_reason", "withdrawn"}:
            raise ValueError("invalid consent_state")
        values = (
            required(profile.customer_id, "customer_id"), BUSINESS_COST_PLUS_ONE, profile.account_type,
            required_reference(profile.legal_name_ref, "legal_name_ref"), required_reference(profile.contact_ref, "contact_ref"),
            required(profile.delivery_zone, "delivery_zone"), profile.consent_state, profile.status,
        )
        self.connection.execute("INSERT OR REPLACE INTO customers VALUES(?,?,?,?,?,?,?,?)", values)
        self.connection.commit()
        return profile.customer_id

    def upsert_workshop(self, profile: WorkshopProfile) -> str:
        if profile.vetting_state not in ALLOWED_VETTING:
            raise ValueError("invalid vetting_state")
        if not HASH_RE.fullmatch(profile.abn_ref_sha256):
            raise ValueError("abn_ref_sha256 must be lowercase SHA-256")
        zones = tuple(sorted({required(zone, "service_zone") for zone in profile.service_zones}))
        if not zones:
            raise ValueError("service_zones required")
        self.connection.execute(
            "INSERT OR REPLACE INTO workshops VALUES(?,?,?,?,?,?,?)",
            (required(profile.workshop_id, "workshop_id"), BUSINESS_COST_PLUS_ONE,
             required_reference(profile.business_name_ref, "business_name_ref"), profile.abn_ref_sha256,
             canonical_json(zones), profile.vetting_state,
             required(profile.lead_consent_policy_ref, "lead_consent_policy_ref")),
        )
        self.connection.commit()
        return profile.workshop_id

    def upsert_vehicle(self, profile: VehicleProfile) -> str:
        if not HASH_RE.fullmatch(profile.vin_sha256) or not HASH_RE.fullmatch(profile.registration_sha256):
            raise ValueError("vehicle identifiers must be lowercase SHA-256")
        if not 1886 <= int(profile.year) <= 2100:
            raise ValueError("vehicle year outside supported bounds")
        self._require_customer(profile.customer_id)
        self.connection.execute(
            "INSERT OR REPLACE INTO vehicles VALUES(?,?,?,?,?,?,?,?,?)",
            (required(profile.vehicle_id, "vehicle_id"), BUSINESS_COST_PLUS_ONE, profile.customer_id,
             profile.vin_sha256, profile.registration_sha256, required(profile.make, "make"),
             required(profile.model, "model"), int(profile.year),
             required(profile.fitment_evidence_ref, "fitment_evidence_ref")),
        )
        self.connection.commit()
        return profile.vehicle_id

    def upsert_supplier(self, profile: SupplierProfile) -> str:
        if profile.source_rights_state not in ALLOWED_SOURCE_RIGHTS:
            raise ValueError("invalid source_rights_state")
        self.connection.execute(
            "INSERT OR REPLACE INTO suppliers VALUES(?,?,?,?,?,?,?)",
            (required(profile.supplier_id, "supplier_id"), BUSINESS_COST_PLUS_ONE,
             required_reference(profile.supplier_name_ref, "supplier_name_ref"), profile.source_rights_state,
             required(profile.ordering_channel, "ordering_channel"), required(profile.terms_ref, "terms_ref"),
             int(bool(profile.active))),
        )
        self.connection.commit()
        return profile.supplier_id

    def create_order(self, profile: OrderProfile) -> str:
        if profile.channel not in ALLOWED_ACCOUNT_TYPES:
            raise ValueError("unsupported order channel")
        if profile.status not in ALLOWED_PROFILE_STATES:
            raise ValueError("invalid order status")
        self._require_customer(profile.customer_id)
        self._require_vehicle(profile.vehicle_id)
        lines = [dict(line) for line in profile.lines]
        if not lines:
            raise ValueError("order lines required")
        for line in lines:
            required(line.get("sku"), "line.sku")
            required(line.get("supplier_id"), "line.supplier_id")
            if int(line.get("quantity", 0)) <= 0:
                raise ValueError("line quantity must be positive")
            if not self.connection.execute("SELECT 1 FROM suppliers WHERE supplier_id=? AND active=1", (line["supplier_id"],)).fetchone():
                raise ValueError("active supplier profile required")
        self.connection.execute(
            "INSERT INTO orders VALUES(?,?,?,?,?,?,?,?,?)",
            (required(profile.order_id, "order_id"), BUSINESS_COST_PLUS_ONE, profile.customer_id,
             profile.vehicle_id, profile.channel, required(profile.zone, "zone"),
             required(profile.delivery_run, "delivery_run"), canonical_json(lines), profile.status),
        )
        self.connection.commit()
        return profile.order_id

    def split_order_by_supplier(self, order_id: str) -> dict[str, list[dict[str, Any]]]:
        row = self.connection.execute("SELECT lines_json FROM orders WHERE order_id=?", (order_id,)).fetchone()
        if not row:
            raise ValueError("unknown order_id")
        grouped: dict[str, list[dict[str, Any]]] = {}
        for line in json.loads(row["lines_json"]):
            grouped.setdefault(line["supplier_id"], []).append(line)
        return grouped

    def counts(self) -> dict[str, int]:
        return {table: int(self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in ("customers", "workshops", "vehicles", "suppliers", "orders")}

    def _require_customer(self, customer_id: str) -> None:
        if not self.connection.execute("SELECT 1 FROM customers WHERE customer_id=?", (customer_id,)).fetchone():
            raise ValueError("customer profile required")

    def _require_vehicle(self, vehicle_id: str) -> None:
        if not self.connection.execute("SELECT 1 FROM vehicles WHERE vehicle_id=?", (vehicle_id,)).fetchone():
            raise ValueError("vehicle profile required")

    def close(self) -> None:
        self.connection.close()


def run_synthetic_order_to_billing(profile_db: str | Path, event_db: str | Path) -> dict[str, Any]:
    """Exercise the local Cost order-to-billing route with synthetic data and no provider calls."""
    profiles = CostProfileStore(profile_db)
    ledger = SQLiteEventLedger(event_db)
    policies = BillingPolicyRegistry()
    policies.register_percentage(policy_id="synthetic-trade-20-v1", percentage="20", channel="trade", approved=True)
    engine = CostPlusContractEngine(approved_billing_policy_ids=policies.approved_ids())
    allocator = LockerAllocator()
    try:
        customer = CustomerProfile("cust-synth-1", "trade", "ref://synthetic/customer-name", "ref://synthetic/contact", "Clayton", "captured", "ACTIVE")
        workshop = WorkshopProfile("workshop-synth-1", "ref://synthetic/workshop", sha256_text("synthetic-abn"), ("Clayton",), "APPROVED", "policy://lead-consent-v1")
        vehicle = VehicleProfile("vehicle-synth-1", customer.customer_id, sha256_text("synthetic-vin"), sha256_text("synthetic-rego"), "Synthetic", "TestVehicle", 2026, "evidence://synthetic/fitment")
        supplier_a = SupplierProfile("supplier-synth-a", "ref://supplier/a", "owner_supplied", "API_SIMULATION", "terms://synthetic/a")
        supplier_b = SupplierProfile("supplier-synth-b", "ref://supplier/b", "owner_supplied", "API_SIMULATION", "terms://synthetic/b")
        for record, method in ((customer, profiles.upsert_customer), (workshop, profiles.upsert_workshop), (supplier_a, profiles.upsert_supplier), (supplier_b, profiles.upsert_supplier)):
            method(record)
        profiles.upsert_vehicle(vehicle)
        order = OrderProfile(
            "order-synth-1", customer.customer_id, vehicle.vehicle_id, "trade", "Clayton", "run-synth-1",
            (
                {"sku": "BRK-SYNTH-1", "quantity": 2, "supplier_id": supplier_a.supplier_id},
                {"sku": "FLT-SYNTH-1", "quantity": 1, "supplier_id": supplier_b.supplier_id},
            ),
            "ACTIVE",
        )
        profiles.create_order(order)
        splits = profiles.split_order_by_supplier(order.order_id)
        correlation_id = "corr-synth-order-1"
        order_event = engine.build_event(
            event_type="cost.order.created.v2", business_id=BUSINESS_COST_PLUS_ONE,
            aggregate_id=order.order_id, correlation_id=correlation_id, idempotency_key="idem-order-synth-1",
            source_pointer="source://synthetic/order", payload={
                "customer_id": order.customer_id, "vehicle_id": order.vehicle_id,
                "lines": [{"sku": line["sku"], "quantity": line["quantity"]} for line in order.lines],
                "zone": order.zone, "delivery_run": order.delivery_run, "requested_channel": order.channel,
            },
        )
        ledger.append(order_event)
        allocation = allocator.allocate(run_id=order.delivery_run, zone=order.zone, customer_id=order.customer_id, order_ids=[order.order_id])
        delivery_event = engine.build_event(
            event_type="cost.delivery_assignment.created.v2", business_id=BUSINESS_COST_PLUS_ONE,
            aggregate_id="delivery-synth-1", correlation_id=correlation_id, causation_id=order_event.event_id,
            idempotency_key="idem-delivery-synth-1", source_pointer="source://synthetic/delivery",
            payload={"customer_id": order.customer_id, "delivery_run": order.delivery_run, "zone": order.zone,
                     "allocation_type": allocation.allocation_type, "allocation_number": allocation.allocation_number,
                     "order_ids": list(allocation.order_ids)},
        )
        ledger.append(delivery_event)
        fee = policies.calculate("synthetic-trade-20-v1", "100.00")
        bill_event = engine.build_event(
            event_type="cost.monthly_statement.calculated.v2", business_id=BUSINESS_COST_PLUS_ONE,
            aggregate_id="statement-synth-1", correlation_id=correlation_id, causation_id=delivery_event.event_id,
            idempotency_key="idem-bill-synth-1", source_pointer="source://synthetic/billing",
            payload={"account_id": customer.customer_id, "period": "2026-07", "policy_id": "synthetic-trade-20-v1",
                     "base_amount_aud": "100.00", "fee_amount_aud": str(fee), "delivery_count": 1,
                     "evidence_ref": "evidence://synthetic/billing-calculation"},
        )
        ledger.append(bill_event)
        events = ledger.events_for_correlation(correlation_id)
        return {
            "journey_id": "COST-ORDER-TO-BILLING-SYNTHETIC-V17",
            "synthetic_only": True,
            "provider_calls_executed": False,
            "payment_or_xero_actions_executed": False,
            "profile_counts": profiles.counts(),
            "supplier_split_count": len(splits),
            "supplier_ids": sorted(splits),
            "allocation": asdict(allocation),
            "event_types": [event["event_type"] for event in events],
            "event_count": len(events),
            "billing_fee_aud": str(fee),
            "passed": len(splits) == 2 and len(events) == 3 and allocation.allocation_type == "side_locker",
            "truth_boundary": "Local synthetic workflow only; no supplier, payment, Xero, driver, scanner, staging or production system was called.",
        }
    finally:
        profiles.close()
        ledger.close()
