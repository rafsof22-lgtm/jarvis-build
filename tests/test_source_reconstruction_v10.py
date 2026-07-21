from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SourceReconstructionV10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chat = json.loads((ROOT / "registry/sources/chatgpt_export_2026_06_25_denominator_v1.json").read_text())
        cls.sources = json.loads((ROOT / "registry/sources/uploaded_source_universe_2026_07_21_v1.json").read_text())
        cls.tracker = json.loads((ROOT / "registry/trackers/all_progress_tracker_reconciliation_v10.json").read_text())

    def test_export_counts(self): self.assertEqual((self.chat["counts"]["conversations"], self.chat["counts"]["messages"]), (2610, 357835))
    def test_roles_reconcile(self): self.assertEqual(sum(self.chat["role_counts"].values()), 357835)
    def test_zero_parse_errors(self): self.assertEqual(self.chat["parse_errors"], 0)
    def test_project_denominator(self):
        p = self.chat["requested_project_denominator"]
        self.assertEqual((p["project_count"], p["conversation_count"], p["message_count"]), (10, 430, 123175))
    def test_project_ids_unique(self):
        items = self.chat["requested_project_denominator"]["projects"]
        self.assertEqual(len({item["project_id"] for item in items}), 10)
    def test_upload_denominator(self): self.assertEqual(self.sources["top_level_source_count"], 51)
    def test_archives_safe(self): self.assertTrue(all(item["unsafe_member_count"] == 0 for item in self.sources["archives"]))
    def test_no_false_completion(self): self.assertEqual(self.tracker["program_state"], "ACTIVE_PROGRAM_NOT_100_PERCENT")
    def test_next_openloop(self): self.assertIn("Cost + $1", self.tracker["next_safe_openloop"])
    def test_privacy_boundary(self): self.assertIn("not committed", self.chat["privacy_boundary"].lower())


if __name__ == "__main__":
    unittest.main()
