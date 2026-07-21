from __future__ import annotations

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from jarvis_business.cost_plus_contracts_v2 import BillingPolicyRegistry, CostPlusContractEngine, LockerAllocator, SQLiteEventLedger, WORKFLOW_CONTRACTS, architecture_decision
from jarvis_business.runtime import BUSINESS_COST_PLUS_ONE, BUSINESS_JENOK


class CostPlusContractsV2Tests(unittest.TestCase):
    def order_payload(self):
        return {"customer_id":"cust-1","vehicle_id":"veh-1","lines":[{"sku":"BRK-1","quantity":2}],"zone":"Clayton","delivery_run":"run-1","requested_channel":"trade"}

    def event(self, engine, *, key="idem-1", payload=None):
        return engine.build_event(event_type="cost.order.created.v2", business_id=BUSINESS_COST_PLUS_ONE, aggregate_id="order-1", correlation_id="corr-1", idempotency_key=key, payload=payload or self.order_payload(), source_pointer="source://test/order-1")

    def test_exactly_seven_workflow_contracts(self):
        self.assertEqual(set(WORKFLOW_CONTRACTS), {"WF-ORDER","WF-PICKUP","WF-DELIVERY","WF-LEAD","WF-BILL","WF-WARRANTY","WF-JENOK"})

    def test_order_event_is_deterministic(self):
        engine = CostPlusContractEngine()
        first, second = self.event(engine), self.event(engine)
        self.assertEqual(first.event_id, second.event_id)
        self.assertEqual(first.payload_sha256, second.payload_sha256)

    def test_missing_required_field_is_rejected(self):
        payload = self.order_payload(); del payload["vehicle_id"]
        with self.assertRaisesRegex(ValueError, "missing required"):
            self.event(CostPlusContractEngine(), payload=payload)

    def test_secret_like_payload_field_is_rejected(self):
        payload = self.order_payload(); payload["api_key"] = "not-allowed"
        with self.assertRaisesRegex(ValueError, "secret-like"):
            self.event(CostPlusContractEngine(), payload=payload)

    def test_cross_business_namespace_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cross business namespace"):
            CostPlusContractEngine().build_event(event_type="cost.order.created.v2", business_id=BUSINESS_JENOK, aggregate_id="order-1", correlation_id="corr-1", idempotency_key="idem-x", payload=self.order_payload(), source_pointer="source://test")

    def test_sqlite_ledger_is_idempotent(self):
        event = self.event(CostPlusContractEngine())
        with tempfile.TemporaryDirectory() as td:
            ledger = SQLiteEventLedger(Path(td) / "events.sqlite")
            self.assertEqual(ledger.append(event)["state"], "APPENDED")
            self.assertEqual(ledger.append(event)["state"], "DUPLICATE_REPLAY")
            self.assertEqual(ledger.count(), 1)
            self.assertEqual(len(ledger.events_for_correlation("corr-1")), 1)
            ledger.close()

    def test_sqlite_ledger_rejects_idempotency_collision(self):
        engine = CostPlusContractEngine(); first = self.event(engine, key="same")
        changed = self.order_payload(); changed["lines"] = [{"sku":"BRK-2","quantity":1}]
        second = self.event(engine, key="same", payload=changed)
        with tempfile.TemporaryDirectory() as td:
            ledger = SQLiteEventLedger(Path(td) / "events.sqlite"); ledger.append(first)
            with self.assertRaisesRegex(ValueError, "collision"): ledger.append(second)
            ledger.close()

    def test_locker_allocator_reuses_customer_locker_within_run(self):
        allocator = LockerAllocator()
        first = allocator.allocate(run_id="run-1", zone="Clayton", customer_id="cust-1", order_ids=["order-1"])
        second = allocator.allocate(run_id="run-1", zone="Clayton", customer_id="cust-1", order_ids=["order-2"])
        self.assertEqual(first.allocation_number, second.allocation_number)
        self.assertEqual(second.order_ids, ("order-1", "order-2"))

    def test_locker_allocator_enforces_40_side_lockers_and_explicit_centre_capacity(self):
        allocator = LockerAllocator(centre_trolley_capacity=1)
        for i in range(1, 41):
            self.assertEqual(allocator.allocate(run_id="run-1", zone="Clayton", customer_id=f"c{i}", order_ids=[f"o{i}"]).allocation_type, "side_locker")
        overflow = allocator.allocate(run_id="run-1", zone="Clayton", customer_id="c41", order_ids=["o41"])
        self.assertEqual((overflow.allocation_type, overflow.allocation_number), ("centre_trolley", 1))
        with self.assertRaisesRegex(RuntimeError, "capacity exhausted"):
            allocator.allocate(run_id="run-1", zone="Clayton", customer_id="c42", order_ids=["o42"])

    def test_billing_requires_explicit_approved_policy(self):
        policies = BillingPolicyRegistry()
        policies.register_percentage(policy_id="trade-20-v1", percentage=Decimal("20"), channel="trade", approved=False)
        with self.assertRaisesRegex(ValueError, "approved"): policies.calculate("trade-20-v1", Decimal("1000"))
        policies.register_percentage(policy_id="trade-20-v2", percentage=Decimal("20"), channel="trade", approved=True)
        self.assertEqual(policies.calculate("trade-20-v2", Decimal("1000")), Decimal("200.00"))

    def test_billing_event_rejects_unapproved_policy(self):
        with self.assertRaisesRegex(ValueError, "not approved"):
            CostPlusContractEngine().build_event(event_type="cost.monthly_statement.calculated.v2", business_id=BUSINESS_COST_PLUS_ONE, aggregate_id="statement-1", correlation_id="corr-bill", idempotency_key="bill-1", source_pointer="source://test/billing", payload={"account_id":"acct-1","period":"2026-07","policy_id":"trade-20-v2","base_amount_aud":"1000","fee_amount_aud":"200","delivery_count":10,"evidence_ref":"evidence://calc-1"})

    def test_jenok_event_requires_source_rights(self):
        with self.assertRaisesRegex(ValueError, "pending source rights"):
            CostPlusContractEngine().build_event(event_type="jenok.catalogue_item.upserted.v2", business_id=BUSINESS_JENOK, aggregate_id="item-1", correlation_id="corr-j", idempotency_key="j-1", source_pointer="source://jenok/item", payload={"sku":"WIP-1","brand":"Jenok","part_number":"W1","fitment":{"make":"Toyota","model":"Corolla"},"source_pointer":"source://catalogue","source_rights_state":"pending_review"})

    def test_architecture_decision_keeps_xero_out_of_operational_core(self):
        decision = architecture_decision()
        self.assertIn("custom automotive domain core", decision["canonical_operational_core"])
        self.assertIn("not operational source of truth", decision["xero_role"])
        self.assertEqual(decision["production_state"], "NOT_AUTHORISED")


if __name__ == "__main__":
    unittest.main()
