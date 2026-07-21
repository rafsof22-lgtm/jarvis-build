from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable
from uuid import NAMESPACE_URL, uuid5

BUSINESS_JENOK = "BUSINESS-JENOK"
BUSINESS_COST_PLUS_ONE = "BUSINESS-COST-PLUS-ONE-AUTO-PARTS"
ALLOWED_BUSINESSES = {BUSINESS_JENOK, BUSINESS_COST_PLUS_ONE}
SOURCE_STATES = ("NEW", "QUEUED", "PROC", "EXTRACT", "INDEX", "LINK", "READY")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(namespace: str, *parts: object) -> str:
    canonical = "|".join(str(p).strip().lower() for p in parts)
    return str(uuid5(NAMESPACE_URL, f"jarvis:{namespace}:{canonical}"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    title: str
    source_type: str
    origin: str
    raw_pointer: str
    status: str
    sha256: str | None
    bytes: int | None
    received_at: str
    reason_unavailable: str | None = None


class SourceReconstructor:
    """Builds a measured source manifest without inventing inaccessible sources."""

    def inventory(self, paths: Iterable[str | Path]) -> list[SourceRecord]:
        records: list[SourceRecord] = []
        for supplied in paths:
            path = Path(supplied)
            source_id = stable_id("source", str(path.resolve() if path.exists() else path))
            if not path.exists():
                records.append(SourceRecord(source_id, path.name or str(path), "unknown", "owner_declared", str(path), "PENDING_INGEST", None, None, utc_now(), "path_not_accessible"))
                continue
            if path.is_dir():
                for child in sorted(p for p in path.rglob("*") if p.is_file()):
                    records.append(self._file_record(child))
            else:
                records.append(self._file_record(path))
        return records

    def _file_record(self, path: Path) -> SourceRecord:
        suffix = path.suffix.lower().lstrip(".") or "file"
        return SourceRecord(stable_id("source", str(path.resolve()), sha256_file(path)), path.name, suffix, "mounted_or_owner_provided", str(path), "READY", sha256_file(path), path.stat().st_size, utc_now())

    def write_manifest(self, records: Iterable[SourceRecord], output: str | Path) -> dict[str, Any]:
        rows = [asdict(r) for r in records]
        result = {
            "schema_version": "1.0.0",
            "generated_at": utc_now(),
            "source_count": len(rows),
            "ready_count": sum(r["status"] == "READY" for r in rows),
            "pending_ingest_count": sum(r["status"] == "PENDING_INGEST" for r in rows),
            "records": rows,
            "truth_boundary": "Only supplied accessible paths are hashed. Missing sources remain PENDING_INGEST.",
        }
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        return result


@dataclass(frozen=True)
class CatalogueItem:
    business_id: str
    product_id: str
    sku: str
    brand: str
    part_number: str
    title: str
    category: str
    vehicle_make: str = ""
    vehicle_model: str = ""
    series: str = ""
    year_from: int | None = None
    year_to: int | None = None
    engine: str = ""
    body: str = ""
    position: str = ""
    oem_reference: str = ""
    cross_reference: str = ""
    source_pointer: str = ""
    source_hash: str = ""
    currency: str = "AUD"
    availability: str = "UNKNOWN"


class CatalogueStore:
    REQUIRED = ("business_id", "sku", "brand", "part_number", "title", "category", "source_pointer")

    @staticmethod
    def _clean(value: object) -> str:
        return re.sub(r"\s+", " ", str(value or "")).strip()

    def normalize(self, row: dict[str, Any]) -> CatalogueItem:
        data = {k: self._clean(v) for k, v in row.items()}
        missing = [name for name in self.REQUIRED if not data.get(name)]
        if missing:
            raise ValueError(f"missing catalogue fields: {', '.join(missing)}")
        business_id = data["business_id"]
        if business_id not in ALLOWED_BUSINESSES:
            raise ValueError("unknown or cross-business catalogue namespace")
        year_from = int(data["year_from"]) if data.get("year_from") else None
        year_to = int(data["year_to"]) if data.get("year_to") else None
        if year_from and year_to and year_from > year_to:
            raise ValueError("year_from cannot exceed year_to")
        identity = stable_id("catalogue", business_id, data["brand"], data["part_number"], data["sku"])
        return CatalogueItem(
            business_id=business_id,
            product_id=identity,
            sku=data["sku"].upper(),
            brand=data["brand"],
            part_number=data["part_number"].upper(),
            title=data["title"],
            category=data["category"],
            vehicle_make=data.get("vehicle_make", ""), vehicle_model=data.get("vehicle_model", ""), series=data.get("series", ""),
            year_from=year_from, year_to=year_to, engine=data.get("engine", ""), body=data.get("body", ""), position=data.get("position", ""),
            oem_reference=data.get("oem_reference", ""), cross_reference=data.get("cross_reference", ""), source_pointer=data["source_pointer"],
            source_hash=data.get("source_hash", ""), currency=data.get("currency", "AUD") or "AUD", availability=data.get("availability", "UNKNOWN") or "UNKNOWN",
        )

    def import_rows(self, rows: Iterable[dict[str, Any]]) -> tuple[list[CatalogueItem], list[dict[str, Any]]]:
        unique: dict[str, CatalogueItem] = {}
        exceptions: list[dict[str, Any]] = []
        for index, row in enumerate(rows, 1):
            try:
                item = self.normalize(row)
                unique[item.product_id] = item
            except (ValueError, TypeError) as exc:
                exceptions.append({"row": index, "error": str(exc), "record": row})
        return list(unique.values()), exceptions

    def import_file(self, path: str | Path) -> tuple[list[CatalogueItem], list[dict[str, Any]]]:
        file_path = Path(path)
        if file_path.suffix.lower() == ".csv":
            with file_path.open(newline="", encoding="utf-8-sig") as handle:
                return self.import_rows(csv.DictReader(handle))
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        rows = payload if isinstance(payload, list) else payload.get("records", [])
        return self.import_rows(rows)


@dataclass(frozen=True)
class CostInput:
    supplier_or_base_cost: Decimal
    freight_and_landed_cost: Decimal
    card_and_fx_fees: Decimal
    platform_or_marketplace_fees: Decimal
    taxes_and_duties: Decimal
    handling_and_packaging: Decimal
    returns_and_warranty_reserve: Decimal
    per_unit_operating_and_storage_allocation: Decimal
    currency: str
    source_pointer: str
    observed_at: datetime


class PricingEngine:
    COMPONENTS = (
        "supplier_or_base_cost", "freight_and_landed_cost", "card_and_fx_fees", "platform_or_marketplace_fees",
        "taxes_and_duties", "handling_and_packaging", "returns_and_warranty_reserve", "per_unit_operating_and_storage_allocation",
    )

    def quote(self, costs: CostInput, *, max_age_hours: int = 72, now: datetime | None = None) -> dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        observed = costs.observed_at if costs.observed_at.tzinfo else costs.observed_at.replace(tzinfo=timezone.utc)
        age_hours = (now - observed).total_seconds() / 3600
        if not costs.source_pointer:
            raise ValueError("pricing source evidence is required")
        if costs.currency != "AUD":
            raise ValueError("AUD-normalized inputs are required; provide evidenced FX conversion first")
        if age_hours < 0 or age_hours > max_age_hours:
            raise ValueError("cost evidence is stale or future-dated")
        values = {name: getattr(costs, name) for name in self.COMPONENTS}
        if any(value is None or value < 0 for value in values.values()):
            raise ValueError("all non-negative cost components are required")
        subtotal = sum(values.values(), Decimal("0"))
        customer_price = (subtotal + Decimal("1.00")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "quote_id": stable_id("quote", costs.source_pointer, observed.isoformat(), customer_price),
            "formula_version": "COST_PLUS_1_AUD_V1",
            "currency": "AUD",
            "components": {k: str(v.quantize(Decimal('0.01'))) for k, v in values.items()},
            "cost_subtotal": str(subtotal.quantize(Decimal("0.01"))),
            "fixed_markup": "1.00",
            "customer_price": str(customer_price),
            "source_pointer": costs.source_pointer,
            "observed_at": observed.isoformat(),
            "generated_at": now.isoformat(),
        }


@dataclass
class PurchaseOrder:
    po_id: str
    business_id: str
    supplier_id: str
    lines: list[dict[str, Any]]
    total_aud: Decimal
    status: str
    evidence: dict[str, Any] = field(default_factory=dict)


class ProcurementService:
    def create_po(self, business_id: str, supplier_id: str, lines: list[dict[str, Any]], *, approved_spend_limit_aud: Decimal) -> PurchaseOrder:
        if business_id not in ALLOWED_BUSINESSES:
            raise ValueError("invalid business namespace")
        if not supplier_id or not lines:
            raise ValueError("supplier and line items are required")
        total = Decimal("0")
        for line in lines:
            quantity = int(line.get("quantity", 0))
            unit_price = Decimal(str(line.get("unit_price_aud", "-1")))
            if quantity <= 0 or unit_price < 0 or not line.get("sku"):
                raise ValueError("each PO line requires sku, positive quantity and non-negative unit price")
            total += unit_price * quantity
        status = "APPROVED_FOR_ISSUE" if total <= approved_spend_limit_aud else "BLOCKED_OWNER_APPROVAL"
        po_id = stable_id("po", business_id, supplier_id, json.dumps(lines, sort_keys=True), total)
        return PurchaseOrder(po_id, business_id, supplier_id, lines, total.quantize(Decimal("0.01")), status, {"created_at": utc_now(), "approved_spend_limit_aud": str(approved_spend_limit_aud)})

    def transition(self, po: PurchaseOrder, new_status: str, evidence: dict[str, Any]) -> PurchaseOrder:
        allowed = {
            "APPROVED_FOR_ISSUE": {"ISSUED"}, "ISSUED": {"ACKNOWLEDGED", "CANCELLED"}, "ACKNOWLEDGED": {"PICKED", "EXCEPTION"},
            "PICKED": {"DISPATCHED", "EXCEPTION"}, "DISPATCHED": {"DELIVERED", "EXCEPTION"}, "DELIVERED": {"RECONCILED", "EXCEPTION"},
        }
        if new_status not in allowed.get(po.status, set()):
            raise ValueError(f"invalid PO transition {po.status} -> {new_status}")
        if not evidence:
            raise ValueError("transition evidence is required")
        po.status = new_status
        po.evidence.setdefault("transitions", []).append({"status": new_status, "at": utc_now(), "evidence": evidence})
        return po


class OrderVerifier:
    def reconcile(self, expected_lines: list[dict[str, Any]], received_lines: list[dict[str, Any]], evidence: dict[str, Any]) -> dict[str, Any]:
        expected = {str(x["sku"]).upper(): int(x["quantity"]) for x in expected_lines}
        received = {str(x["sku"]).upper(): int(x["quantity"]) for x in received_lines}
        exceptions: list[dict[str, Any]] = []
        for sku in sorted(set(expected) | set(received)):
            if expected.get(sku, 0) != received.get(sku, 0):
                exceptions.append({"type": "QUANTITY_MISMATCH", "sku": sku, "expected": expected.get(sku, 0), "received": received.get(sku, 0)})
        required_evidence = ("supplier_acknowledgement", "dispatch_reference", "delivery_proof", "condition_check")
        for key in required_evidence:
            if not evidence.get(key):
                exceptions.append({"type": "MISSING_EVIDENCE", "field": key})
        if not (evidence.get("barcode_or_qr") or (evidence.get("photo") and evidence.get("manual_count"))):
            exceptions.append({"type": "MISSING_SCAN_OR_MANUAL_FALLBACK"})
        return {
            "verification_id": stable_id("verification", json.dumps(expected, sort_keys=True), json.dumps(received, sort_keys=True), json.dumps(evidence, sort_keys=True)),
            "status": "RECONCILED" if not exceptions else "EXCEPTION",
            "exceptions": exceptions,
            "verified_at": utc_now(),
        }


class DeploymentController:
    def plan(self, business_id: str, environment: str, *, owner_approved: bool = False, required_env: Iterable[str] = ()) -> dict[str, Any]:
        if business_id not in ALLOWED_BUSINESSES:
            raise ValueError("invalid business namespace")
        if environment not in {"local", "staging", "production"}:
            raise ValueError("environment must be local, staging or production")
        if environment == "production" and not owner_approved:
            status = "BLOCKED_OWNER_APPROVAL"
        else:
            status = "READY_FOR_CONFIGURATION"
        return {
            "deployment_id": stable_id("deployment", business_id, environment, utc_now()),
            "business_id": business_id,
            "environment": environment,
            "status": status,
            "required_environment_variables": sorted(set(required_env)),
            "secret_policy": "Values must be stored in the platform secret manager and never committed or logged.",
            "health_checks": ["service_liveness", "database_connectivity", "catalogue_read", "pricing_determinism", "order_verification", "audit_write"],
            "release_sequence": ["build", "unit_test", "security_scan", "staging_deploy", "smoke_test", "rollback_test", "owner_gate", "production_canary", "monitor"],
            "rollback": {"strategy": "redeploy_previous_verified_image_and_restore_compatible_snapshot", "required": True},
            "generated_at": utc_now(),
        }
