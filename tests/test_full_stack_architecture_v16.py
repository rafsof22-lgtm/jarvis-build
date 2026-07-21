from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_full_stack_architecture_v16 import verify


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class FullStackArchitectureV16Tests(unittest.TestCase):
    def setUp(self):
        self.architecture = load("registry/architecture/jarvis_full_stack_18_layer_reference_v1.json")
        self.aliases = load("registry/sources/health_split_upload_aliases_v16.json")
        self.access = load("registry/source-accounting/project_chat_access_reconciliation_v1.json")
        self.tracker = load("registry/trackers/all_progress_tracker_reconciliation_v16.json")

    def test_verifier_passes(self):
        self.assertTrue(verify()["verified"])

    def test_at_least_thirteen_layers(self):
        self.assertGreaterEqual(len(self.architecture["layers"]), 13)

    def test_declares_eighteen_layers(self):
        self.assertEqual(len(self.architecture["layers"]), 18)

    def test_layer_ids_are_unique(self):
        ids = [row["layer_id"] for row in self.architecture["layers"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_layer_order_is_contiguous(self):
        self.assertEqual([row["order"] for row in self.architecture["layers"]], list(range(1, 19)))

    def test_every_layer_has_evidence_and_gaps(self):
        for row in self.architecture["layers"]:
            self.assertTrue(row["existing_evidence"])
            self.assertTrue(row["open_gaps"])

    def test_new_uploads_are_exact_aliases(self):
        self.assertEqual(self.aliases["novel_source_bytes"], 0)
        self.assertTrue(all(row["state"] == "DUPLICATE_WITH_LINEAGE" for row in self.aliases["records"]))

    def test_chat_access_does_not_overclaim(self):
        self.assertFalse(self.access["all_live_project_chats_accessible"])

    def test_post_export_delta_remains_pending(self):
        rows = {row["source_class"]: row for row in self.access["sources"]}
        self.assertEqual(rows["POST_EXPORT_PROJECT_CHAT_DELTA"]["state"], "PENDING_INGEST")

    def test_live_project_ui_is_blocked_by_access(self):
        rows = {row["source_class"]: row for row in self.access["sources"]}
        self.assertEqual(rows["LIVE_PROJECT_UI_CHAT_ENUMERATION"]["state"], "BLOCKED_BY_ACCESS")

    def test_tracker_does_not_claim_completion(self):
        self.assertEqual(self.tracker["program_state"], "ACTIVE_PROGRAM_NOT_100_PERCENT")
        self.assertEqual(self.tracker["full_stack_state"]["end_to_end_connected_runtime"], "NOT_VERIFIED")

    def test_continuity_is_current_and_truthful(self):
        text = (ROOT / "PROJECT_CONTINUITY.md").read_text(encoding="utf-8")
        self.assertIn("all_progress_tracker_reconciliation_v16.json", text)
        self.assertIn("18-layer", text)
        self.assertIn("Never claim all project chats are current", text)
        self.assertIn("ACTIVE_PROGRAM_NOT_100_PERCENT", text)


if __name__ == "__main__":
    unittest.main()
