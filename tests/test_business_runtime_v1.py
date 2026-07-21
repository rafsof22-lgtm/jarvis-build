import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from src.jarvis_business.runtime import (
    BUSINESS_COST_PLUS_ONE,
    BUSINESS_JENOK,
    CatalogueStore,
    CostInput,
    DeploymentController,
    OrderVerifier,
    PricingEngine,
    ProcurementService,
    SourceReconstructor,
)


class BusinessRuntimeTests(unittest.TestCase):
    def test_source_reconstruction_hashes_accessible_and_preserves_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.txt"
            source.write_text("evidence", encoding="utf-8")
            records = SourceReconstructor().inventory([source, Path(tmp) / "missing.jsonl"])
            self.assertEqual(records[0].status, "READY")
            self.assertEqual(len(records[0].sha256), 64)
            self.assertEqual(records[1].status, "PENDING_INGEST")

    def test_catalogue_dedupes_inside_business_namespace(self):
        row = {"business_id": BUSINESS_JENOK, "sku": " j-1 ", "brand": "Jenok", "part_number": " abc ", "title": " Test Part ", "category": "Suspension", "source_pointer": "file:1"}
        records, exceptions = CatalogueStore().import_rows([row, dict(row)])
        self.assertEqual(len(records), 1)
        self.assertFalse(exceptions)
        self.assertEqual(records[0].sku, "J-1")

    def test_catalogue_rejects_cross_business_or_unknown_namespace(self):
        row = {"business_id": "UNKNOWN", "sku": "x", "brand": "x", "part_number": "x", "title": "x", "category": "x", "source_pointer": "x"}
        records, exceptions = CatalogueStore().import_rows([row])
        self.assertFalse(records)
        self.assertEqual(len(exceptions), 1)

    def _costs(self, observed_at=None):
        values = dict(
            supplier_or_base_cost=Decimal("100"), freight_and_landed_cost=Decimal("10"), card_and_fx_fees=Decimal("2"),
            platform_or_marketplace_fees=Decimal("3"), taxes_and_duties=Decimal("4"), handling_and_packaging=Decimal("5"),
            returns_and_warranty_reserve=Decimal("6"), per_unit_operating_and_storage_allocation=Decimal("7"),
            currency="AUD", source_pointer="supplier-feed:record-1", observed_at=observed_at or datetime.now(timezone.utc),
        )
        return CostInput(**values)

    def test_price_is_all_evidenced_costs_plus_exactly_one_aud(self):
        quote = PricingEngine().quote(self._costs())
        self.assertEqual(quote["cost_subtotal"], "137.00")
        self.assertEqual(quote["fixed_markup"], "1.00")
        self.assertEqual(quote["customer_price"], "138.00")

    def test_price_fails_closed_on_stale_costs(self):
        with self.assertRaises(ValueError):
            PricingEngine().quote(self._costs(datetime.now(timezone.utc) - timedelta(days=10)))

    def test_procurement_blocks_spend_above_limit(self):
        po = ProcurementService().create_po(BUSINESS_COST_PLUS_ONE, "supplier-1", [{"sku": "P1", "quantity": 2, "unit_price_aud": "60"}], approved_spend_limit_aud=Decimal("100"))
        self.assertEqual(po.status, "BLOCKED_OWNER_APPROVAL")

    def test_order_verification_requires_scan_or_manual_fallback(self):
        result = OrderVerifier().reconcile([{"sku": "P1", "quantity": 1}], [{"sku": "P1", "quantity": 1}], {
            "supplier_acknowledgement": "ack", "dispatch_reference": "d", "delivery_proof": "photo", "condition_check": "pass"
        })
        self.assertEqual(result["status"], "EXCEPTION")
        self.assertTrue(any(x["type"] == "MISSING_SCAN_OR_MANUAL_FALLBACK" for x in result["exceptions"]))

    def test_production_deployment_requires_owner_gate(self):
        blocked = DeploymentController().plan(BUSINESS_JENOK, "production")
        staging = DeploymentController().plan(BUSINESS_JENOK, "staging")
        self.assertEqual(blocked["status"], "BLOCKED_OWNER_APPROVAL")
        self.assertEqual(staging["status"], "READY_FOR_CONFIGURATION")


if __name__ == "__main__":
    unittest.main()
