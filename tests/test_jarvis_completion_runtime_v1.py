import tempfile
import unittest
from pathlib import Path

from src.jarvis_completion import (
    CapabilityQuarantine,
    DomainStagingFactory,
    EvidenceRanker,
    KnowledgeFabric,
    Message,
    ModelRouter,
    PolicyEngine,
    ProviderProfile,
    TaskContract,
    sign_envelope,
    verify_envelope,
)


class KnowledgeFabricTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "fabric.db"
        self.fabric = KnowledgeFabric(self.path)

    def tearDown(self):
        self.fabric.close()
        self.tmp.cleanup()

    def test_ingestion_is_idempotent_and_preserves_exact_text(self):
        raw = b"**user**:\nhello\n**cloud-model**:\nanswer\n**cloud-model**:\nanswer\n"
        messages = [
            Message(1, "user", "hello\n", 1, 2),
            Message(2, "assistant", "answer\n", 3, 4, "model"),
            Message(3, "assistant", "answer\n", 5, 6, "model"),
        ]
        first = self.fabric.ingest_source(pointer="upload:x", title="x", raw=raw, messages=messages)
        second = self.fabric.ingest_source(pointer="upload:x", title="x", raw=raw, messages=messages)
        self.assertEqual(first["source"]["source_id"], second["source"]["source_id"])
        self.assertEqual(first["message_count"], 3)
        self.assertEqual(first["duplicate_count"], 1)
        self.assertEqual(first["messages"][0]["exact_text"], "hello\n")
        self.assertEqual(len(self.fabric.reproduction(first["source"]["source_id"])), 2)
        self.assertEqual(len(self.fabric.reproduction(first["source"]["source_id"], include_duplicates=True)), 3)

    def test_invalid_coordinates_roll_back_transaction(self):
        with self.assertRaises(ValueError):
            self.fabric.ingest_source(pointer="bad", title="bad", raw=b"x", messages=[Message(1, "user", "x", 0, 1)])
        count = self.fabric.db.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        self.assertEqual(count, 0)

    def test_requirement_evidence_and_no_gaps(self):
        self.fabric.upsert_requirement("R1", "exact", "normalized", "control_plane",
                                       implementation_path="src/a.py", status="IMPLEMENTED_NOT_INTEGRATED")
        self.assertFalse(self.fabric.no_gaps_report()["passed"])
        self.fabric.add_evidence("R1", "src/a.py", "tests/test_a.py", "DONE_VERIFIED")
        self.assertTrue(self.fabric.no_gaps_report()["passed"])

    def test_synthesis_requires_every_message_or_reasoned_exclusion(self):
        manifest = self.fabric.ingest_source(pointer="p", title="t", raw=b"a",
            messages=[Message(1, "user", "a", 1, 1), Message(2, "assistant", "b", 2, 2)])
        source_id = manifest["source"]["source_id"]
        ids = [m["message_id"] for m in manifest["messages"]]
        self.assertFalse(self.fabric.synthesis_coverage(source_id, [ids[0]], {})["passed"])
        self.assertTrue(self.fabric.synthesis_coverage(source_id, [ids[0]], {ids[1]: "duplicate summary"})["passed"])

    def test_idempotent_operation_and_alert_deduplication(self):
        calls = []
        def op():
            calls.append(1)
            return {"ok": True}
        self.assertEqual(self.fabric.idempotent_execute("k", op), {"ok": True})
        self.assertEqual(self.fabric.idempotent_execute("k", op), {"ok": True})
        self.assertEqual(len(calls), 1)
        self.fabric.create_alert("same", "high", "one")
        self.fabric.create_alert("same", "high", "one")
        self.assertEqual(len(self.fabric.status_dashboard()["active_alerts"]), 1)


class GovernanceTests(unittest.TestCase):
    def contract(self):
        return TaskContract(
            task_id="T1", owner="owner", purpose="test", inputs={}, outputs=["evidence"],
            allowed_tools=["local"], denied_tools=["live"], autonomy_level=2,
            approval_actions=["production", "live_trading"], token_limit=1000,
            cost_limit_aud=0, timeout_seconds=30, retry_limit=1, rollback="restore",
        )

    def test_policy_denies_unapproved_high_risk_and_denied_tools(self):
        policy = PolicyEngine()
        self.assertEqual(policy.authorize(self.contract(), action="production", tool="local"), (False, "owner_approval_required"))
        self.assertEqual(policy.authorize(self.contract(), action="research", tool="live"), (False, "tool_not_allowed"))
        self.assertEqual(policy.authorize(self.contract(), action="production", tool="local", approval=True), (True, "allowed"))

    def test_credential_readiness_never_requires_secret_values(self):
        result = PolicyEngine.credential_readiness(["DB_SECRET_REF"], {"DB_SECRET_REF": "vault://db/main"})
        self.assertTrue(result["ready"])
        bad = PolicyEngine.credential_readiness(["TOKEN"], {"TOKEN": "sk-example"})
        self.assertFalse(bad["ready"])
        self.assertEqual(bad["possible_raw_secret_values"], ["TOKEN"])


class RoutingAndIntegrationTests(unittest.TestCase):
    def test_free_first_deterministic_routing(self):
        profiles = [
            ProviderProfile("paid", "paid", frozenset({"text"}), 90, 99, 0.01),
            ProviderProfile("local", "local_model", frozenset({"text"}), 100, 80, 0),
            ProviderProfile("tool", "deterministic", frozenset({"text"}), 100, 100, 0),
        ]
        chosen = ModelRouter().choose(profiles, required={"text"}, max_cost=1, minimum_privacy=80)
        self.assertEqual(chosen.provider_id, "tool")

    def test_evidence_ranker_and_classification(self):
        self.assertEqual(EvidenceRanker.classify("verified_fact"), "verified_fact")
        self.assertGreater(EvidenceRanker.score(authority=100, freshness=100, corroboration=100, directness=100), 90)
        with self.assertRaises(ValueError):
            EvidenceRanker.classify("truth")

    def test_capability_quarantine_fails_closed(self):
        self.assertEqual(CapabilityQuarantine.verdict({}), "QUARANTINED_INCOMPLETE_REVIEW")
        review = {"licence":"compatible", "security":"pass", "maintenance":"active", "duplication":"none", "cost":"free", "data_access":"public"}
        self.assertEqual(CapabilityQuarantine.verdict(review), "APPROVED_FOR_STAGING_ADAPTER_ONLY")

    def test_signed_envelope_replay_age_and_tamper_controls(self):
        envelope = sign_envelope({"x": 1}, b"secret", idempotency_key="i", timestamp=1000)
        self.assertTrue(verify_envelope(envelope, b"secret", now=1001))
        self.assertFalse(verify_envelope(envelope, b"wrong", now=1001))
        self.assertFalse(verify_envelope(envelope, b"secret", now=2000))


class DomainStagingTests(unittest.TestCase):
    def test_cfo_crypto_paper_agency_and_saas_slices(self):
        self.assertEqual(DomainStagingFactory.cfo_scenario(100, 20, 10, -0.1)["stressed_net_worth"], 70.0)
        crypto = DomainStagingFactory.crypto_scenario({"XRP": 10}, {"XRP": 2}, 0.1)
        self.assertEqual(crypto["total_value"], 20.0)
        self.assertEqual(DomainStagingFactory.paper_trade(100, 10, 5, "buy", 100)["status"], "PAPER_FILLED")
        self.assertEqual(DomainStagingFactory.paper_trade(100, 10, 20, "buy", 100)["status"], "REJECTED_RISK_LIMIT")
        self.assertEqual(DomainStagingFactory.agency_unit_economics(100, 20, 10, 2)["contribution"], 70)
        self.assertEqual(DomainStagingFactory.saas_stage_gate(tests_pass=True, security_pass=True, billing_live=False, owner_publish_approval=False), "INTEGRATED_STAGING")
        self.assertEqual(DomainStagingFactory.saas_stage_gate(tests_pass=True, security_pass=True, billing_live=True, owner_publish_approval=False), "BLOCKED_PRODUCTION_APPROVAL_PATH")


if __name__ == "__main__":
    unittest.main()
