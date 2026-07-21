from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis_command_centre.alert_lifecycle_v1 import filter_suppressed, reconcile_resolved, resolve_alert, suppress
from jarvis_command_centre.history_alerts import Alert, list_open_alerts, record_alerts
from jarvis_command_centre.operational_controls_v1 import assess_provider_account, assess_provider_ledger, build_remediation_proposal
from src.jarvis_knowledge_fabric_benchmark_v2 import BenchmarkDocument, BenchmarkQuery, KnowledgeFabricBenchmarkV2


NOW = datetime(2026, 7, 21, 10, 0, tzinfo=timezone.utc)


class ProviderAssessmentTests(unittest.TestCase):
    def test_unverified_account_requires_evidence(self):
        result = assess_provider_account({"account_id": "x", "provider": "X", "balance_status": "unavailable", "usage": []}, now=NOW)
        self.assertEqual(result.alert_state, "EVIDENCE_REQUIRED")
        self.assertEqual(result.freshness_state, "UNKNOWN")

    def test_fresh_numeric_usage_within_allowance(self):
        result = assess_provider_account({
            "account_id": "x", "provider": "X", "balance_status": "verified",
            "last_verified_at": "2026-07-21T09:00:00Z", "alert_threshold_percent": 80,
            "usage": [{"value": 20, "limit": 100}],
        }, now=NOW)
        self.assertEqual(result.usage_percent, 20.0)
        self.assertEqual(result.exhaustion_forecast, "WITHIN_ALLOWANCE")
        self.assertEqual(result.alert_state, "OK")

    def test_threshold_usage_is_action_required(self):
        result = assess_provider_account({
            "account_id": "x", "provider": "X", "balance_status": "verified",
            "last_verified_at": "2026-07-21T09:00:00Z", "alert_threshold_percent": 80,
            "usage": [{"value": 85, "limit": 100}], "renewal_at": "2026-08-01T00:00:00Z",
        }, now=NOW)
        self.assertEqual(result.exhaustion_forecast, "AT_RISK_BEFORE_RENEWAL")
        self.assertEqual(result.alert_state, "ACTION_REQUIRED")

    def test_ledger_does_not_infer_balances(self):
        report = assess_provider_ledger([{"account_id": "x", "provider": "X", "balance_status": "unavailable"}], now=NOW)
        self.assertFalse(report["authoritative_balances_inferred"])
        self.assertEqual(report["summary"]["accounts"], 1)

    def test_remediation_is_proposal_only(self):
        proposal = build_remediation_proposal(target_id="repo", issue_kind="failed_health", evidence_pointer="evidence:1")
        self.assertEqual(proposal.action_mode, "PROPOSAL_ONLY")
        self.assertTrue(proposal.approval_required)
        self.assertIn("rollback_proof", proposal.evidence_required)


class AlertLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "alerts.db"
        self.alert = Alert("a1", "repo", "health", "high", "failed", "evidence:x", "2026-07-21T00:00:00Z")
        record_alerts(self.db, [self.alert])

    def tearDown(self):
        self.tmp.cleanup()

    def test_suppression_filters_by_alert_id(self):
        suppress(self.db, "a1", "maintenance window")
        self.assertEqual(filter_suppressed(self.db, [self.alert]), [])

    def test_suppression_filters_by_repo_kind(self):
        suppress(self.db, "repo:health", "known outage")
        self.assertEqual(filter_suppressed(self.db, [self.alert]), [])

    def test_resolution_requires_evidence(self):
        with self.assertRaises(ValueError):
            resolve_alert(self.db, "a1", evidence_pointer="")

    def test_resolution_closes_open_alert(self):
        self.assertTrue(resolve_alert(self.db, "a1", evidence_pointer="evidence:fixed"))
        self.assertEqual(list_open_alerts(self.db), [])

    def test_reconcile_resolves_disappeared_alerts(self):
        resolved = reconcile_resolved(self.db, set(), evidence_pointer="snapshot:new")
        self.assertEqual(resolved, ["a1"])


class KnowledgeFabricBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.documents = [
            BenchmarkDocument("gov-new", "governance", "Proof", "rollback evidence required", "public", 30, "proof", "supports"),
            BenchmarkDocument("gov-old", "governance", "Proof old", "rollback evidence required", "public", 10, "proof", "supports"),
            BenchmarkDocument("gov-dup", "governance", "Proof duplicate", "rollback evidence required", "public", 30, "proof", "supports", "gov-new"),
            BenchmarkDocument("health-private", "health", "Private", "device control disabled", "health-team", 40, "device", "supports"),
            BenchmarkDocument("health-public", "health", "Public", "device control disabled", "public", 20, "device", "supports"),
            BenchmarkDocument("claim-support", "research", "Supports", "claim alpha verified", "public", 30, "alpha", "supports"),
            BenchmarkDocument("claim-conflict", "research", "Conflicts", "claim alpha contradicted", "public", 29, "alpha", "contradicts"),
        ]
        self.benchmark = KnowledgeFabricBenchmarkV2(self.documents)

    def tearDown(self):
        self.benchmark.close()

    def test_permission_filter_hides_private_document(self):
        query = BenchmarkQuery("q", "device", "health", "public", ("health-public",))
        returned = self.benchmark.search(query)
        self.assertEqual([item["document_id"] for item in returned], ["health-public"])

    def test_authorized_permission_can_see_private_document(self):
        query = BenchmarkQuery("q", "device", "health", "health-team", ("health-private", "health-public"))
        ids = [item["document_id"] for item in self.benchmark.search(query)]
        self.assertIn("health-private", ids)

    def test_duplicate_is_suppressed(self):
        query = BenchmarkQuery("q", "rollback", "governance", "public", ("gov-new", "gov-old"))
        ids = [item["document_id"] for item in self.benchmark.search(query)]
        self.assertNotIn("gov-dup", ids)

    def test_fresh_document_wins_equal_lexical_match(self):
        query = BenchmarkQuery("q", "rollback evidence required", "governance", "public", ("gov-new", "gov-old"))
        ids = [item["document_id"] for item in self.benchmark.search(query)]
        self.assertEqual(ids[0], "gov-new")

    def test_contradiction_pair_is_found(self):
        pairs = self.benchmark.contradiction_pairs("alpha", permission="public")
        self.assertEqual(pairs, [("claim-support", "claim-conflict")])

    def test_report_has_explicit_unconnected_backends(self):
        query = BenchmarkQuery("q", "claim alpha", "research", "public", ("claim-support", "claim-conflict"), True)
        report = self.benchmark.run([query])
        self.assertEqual(report["postgres_backend"], "NOT_CONNECTED")
        self.assertEqual(report["vector_backend"], "NOT_EXECUTED_DEPENDENCY_NOT_SELECTED")
        self.assertEqual(report["permission_failures"], 0)


if __name__ == "__main__":
    unittest.main()
