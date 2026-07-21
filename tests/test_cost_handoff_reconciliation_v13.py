from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CostHandoffReconciliationV13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = load("registry/sources/cost_auto_parts_source_reconciliation_v1.json")
        cls.health = load("registry/sources/health_spooky2_psychology_split_handover_v1.json")
        cls.requirements = load("registry/requirements/cost_auto_parts_requirements_reconciliation_v1.json")
        cls.tracker = load("registry/trackers/all_progress_tracker_reconciliation_v13.json")
        cls.contracts = load("registry/business/cost-plus-one-domain-contracts-v2.json")

    def test_project_denominator_preserves_mixed_lineage(self):
        exact = self.source["exact_project_export"]
        self.assertEqual(exact["conversation_envelope_count"], 15)
        self.assertEqual(exact["top_level_project_conversation_count"], 14)
        self.assertEqual(exact["mixed_lineage_conversation_count"], 1)
        self.assertEqual(exact["conversation_envelope_message_count"], 14654)
        self.assertEqual(exact["top_level_project_conversation_message_count"], 14602)
        self.assertEqual(exact["message_metadata_tagged_count"], 3804)

    def test_source_pack_and_docx_relationships(self):
        sources = {x["name"]: x for x in self.source["uploaded_sources"]}
        self.assertEqual(sources["JARVIS_COST_AUTO_PARTS_MODULE_HANDOFF_v2_NO_CHATGPT_EXPORT.zip"]["members"], 50)
        self.assertEqual(sources["COST AUTO PARTS FINAL.docx"]["relationship"], "EXACT_DUPLICATE_OF_HANDOFF_MEMBER")
        self.assertEqual(sources["COST AUTO PARTS FINAL1.docx"]["relationship"], "EXACT_DUPLICATE_OF_HANDOFF_MEMBER")
        self.assertEqual(self.source["document_version_relationship"]["decision"], "PRESERVE_BOTH_AS_DISTINCT_VERSIONS")

    def test_reuploaded_chathub_files_are_aliases(self):
        aliases = [x for x in self.source["uploaded_sources"] if x.get("state") == "DUPLICATE_WITH_LINEAGE"]
        self.assertEqual(len(aliases), 3)

    def test_prompt_template_is_not_automatically_activated(self):
        item = next(x for x in self.source["uploaded_sources"] if x["name"] == "ChatHubINstrPrompt.sql")
        self.assertEqual(item["source_type"], "PROMPT_TEMPLATE_NOT_SQL")
        self.assertEqual(item["activation"], "DENIED_AUTOMATIC")

    def test_84_chat_claim_is_preserved_as_conflict(self):
        conflict = next(x for x in self.source["internal_conflicts"] if x["conflict_id"] == "COST-HANDOFF-CF-001")
        self.assertEqual(conflict["state"], "CONFLICT_REVIEW")
        self.assertIn("zero", conflict["claim_b"].lower())

    def test_all_18_requirements_have_current_mapping(self):
        rows = self.requirements["requirements"]
        self.assertEqual(len(rows), 18)
        self.assertEqual(len({r["requirement_id"] for r in rows}), 18)
        for row in rows:
            self.assertTrue(row["current_artifacts"])
            self.assertTrue(row["current_implementation_state"])
            self.assertTrue(row["reason"])
            self.assertTrue(row["rollback"])

    def test_health_split_archive_integrity_boundary(self):
        self.assertEqual(len(self.health["parts"]), 5)
        self.assertEqual(self.health["combined_zip"]["members"], 642)
        self.assertEqual(self.health["combined_zip"]["zip_integrity"], "PASS")
        self.assertFalse(self.health["raw_content_committed"])
        self.assertFalse(self.health["safety"]["medical_claims_executable"])

    def test_domain_contracts_cover_seven_workflows(self):
        self.assertEqual(len(self.contracts["workflows"]), 7)
        self.assertEqual({x["workflow_id"] for x in self.contracts["workflows"]}, {"WF-ORDER", "WF-PICKUP", "WF-DELIVERY", "WF-LEAD", "WF-BILL", "WF-WARRANTY", "WF-JENOK"})
        self.assertEqual(self.contracts["status"], "IMPLEMENTED_NOT_INTEGRATED")

    def test_tracker_remains_not_100_percent(self):
        self.assertEqual(self.tracker["program_state"], "ACTIVE_PROGRAM_NOT_100_PERCENT")
        self.assertNotIn("END_TO_END_VERIFIED", json.dumps(self.tracker))
        self.assertEqual(self.tracker["cost_plus_one_current_states"]["domain_event_contracts"], "DONE_VERIFIED_LOCAL")
        self.assertEqual(self.tracker["cost_plus_one_current_states"]["production"], "NOT_AUTHORISED")

    def test_raw_sensitive_content_not_committed_in_registries(self):
        text = json.dumps([self.source, self.health, self.requirements, self.tracker, self.contracts]).lower()
        self.assertNotIn("seed_phrase", text)
        self.assertNotIn("private_key_value", text)
        self.assertNotIn("raw_chat_body", text)


if __name__ == "__main__":
    unittest.main()
