import tempfile
import unittest
from pathlib import Path

from src.jarvis_evolution import (
    OBJECT_TYPES,
    ChangeRequest,
    EditableObjectSpec,
    EvolutionStore,
    SelfRepairEngine,
    SourceCoverageRecord,
    UnifiedJarvisAssistant,
    default_editable_object_catalog,
)


class EvolutionStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = EvolutionStore(Path(self.temp.name) / "evolution.db")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_default_catalog_registers_every_editable_object_type(self):
        for item in default_editable_object_catalog():
            self.store.register_object(item)
        registered = {item["object_type"] for item in self.store.list_objects()}
        self.assertEqual(registered, OBJECT_TYPES)

    def test_safe_reversible_change_simulates_applies_and_versions(self):
        self.store.register_object(EditableObjectSpec(
            "workflow-a", "workflow", "Workflow A", "1.0.0", "workflows/a.json",
            "WORKFLOW_SPECIFIC", "JARVIS_OWNER", "AUTO_REVERSIBLE", "old value",
            validators=("unit", "regression"),
        ))
        request = ChangeRequest(
            "request-a", "user", "chat:current", "update workflow", ("workflow-a",),
            ({"op": "replace", "old": "old", "new": "new"},), "AUTO_REVERSIBLE",
        )
        plan = self.store.propose_change(request, tests=("unit", "regression"))
        self.assertEqual(plan.state, "SIMULATED")
        result = self.store.apply_staging(plan.plan_id, verifier=lambda _object_id, content: "new value" in content)
        self.assertEqual(result["state"], "VERIFIED")
        self.assertEqual(self.store.get_object("workflow-a")["content"], "new value")
        self.assertEqual(self.store.get_object("workflow-a")["version"], "1.0.1")

    def test_protected_objects_and_manual_override_require_owner(self):
        self.store.register_object(EditableObjectSpec(
            "policy-a", "policy", "Policy A", "1.0.0", "policies/a.json",
            "GLOBAL_CONTROL_PLANE", "JARVIS_OWNER", "GATED_EXECUTION", "deny by default",
        ))
        request = ChangeRequest(
            "request-policy", "user", "chat:current", "manual policy change", ("policy-a",),
            ({"op": "append", "value": "\nnew rule"},), "GATED_EXECUTION", True,
        )
        plan = self.store.propose_change(request)
        self.assertEqual(plan.state, "AWAITING_APPROVAL")
        self.assertIn("OWNER", plan.required_approvals)
        with self.assertRaises(PermissionError):
            self.store.apply_staging(plan.plan_id)
        self.assertEqual(self.store.decide(plan.plan_id, "OWNER", "APPROVE", "approved manual override"), "APPROVED")
        self.assertEqual(self.store.apply_staging(plan.plan_id)["state"], "VERIFIED")

    def test_direct_production_self_modification_is_denied(self):
        self.store.register_object(EditableObjectSpec(
            "module-a", "module", "Module A", "1.0.0", "modules/a.json",
            "MODULE_SPECIFIC", "JARVIS_OWNER", "AUTO_REVERSIBLE", "v1",
        ))
        request = ChangeRequest(
            "request-production", "system", "runtime:detector", "production edit", ("module-a",),
            ({"op": "set", "value": "v2"},), "GATED_EXECUTION", False, "production",
        )
        plan = self.store.propose_change(request)
        for authority in ("OWNER", "RISK_AUTHORITY", "RELEASE_GATEKEEPER"):
            self.store.decide(plan.plan_id, authority, "APPROVE", "test approval")
        with self.assertRaises(PermissionError):
            self.store.apply_staging(plan.plan_id)

    def test_owner_can_rollback_verified_staging_change(self):
        self.store.register_object(EditableObjectSpec(
            "agent-a", "agent", "Agent A", "1.0.0", "agents/a.json",
            "AGENT_SPECIFIC", "JARVIS_OWNER", "AUTO_REVERSIBLE", "before",
        ))
        plan = self.store.propose_change(ChangeRequest(
            "request-agent", "user", "chat:current", "change agent", ("agent-a",),
            ({"op": "set", "value": "after"},), "AUTO_REVERSIBLE",
        ))
        self.store.apply_staging(plan.plan_id)
        restored = self.store.rollback("agent-a", authority="OWNER", reason="user requested rollback")
        self.assertEqual(restored["content"], "before")

    def test_source_coverage_truth_gate_blocks_false_100_percent(self):
        self.store.register_source(SourceCoverageRecord("current", "Current chat", "AVAILABLE", "chat:current"))
        self.store.register_source(SourceCoverageRecord(
            "missing-export", "Missing ChatGPT export", "PENDING_INGEST", "file:missing-export"
        ))
        report = self.store.source_coverage_report()
        self.assertFalse(report["universal_100_percent_allowed"])
        self.assertEqual(report["denominator"], 2)
        self.store.register_source(SourceCoverageRecord(
            "missing-export", "Missing ChatGPT export", "EXCLUDED_WITH_REASON", "file:missing-export", "not supplied"
        ))
        self.assertTrue(self.store.source_coverage_report()["universal_100_percent_allowed"])


class RepairAndAssistantTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = EvolutionStore(Path(self.temp.name) / "evolution.db")

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_self_repair_only_changes_auto_reversible_objects(self):
        self.store.register_object(EditableObjectSpec(
            "spec-a", "spec", "Spec A", "1.0.0", "specs/a.md", "MODULE_SPECIFIC",
            "JARVIS_OWNER", "AUTO_REVERSIBLE", "missing section", validators=("required-heading",),
        ))
        validator = lambda content: ("## Safety" in content, "missing Safety heading")
        result = SelfRepairEngine(self.store).repair(
            "spec-a", [validator], lambda content, _failures: content + "\n## Safety\nDeny by default.\n"
        )
        self.assertEqual(result["state"], "VERIFIED")
        self.assertIn("## Safety", result["object"]["content"])

    def test_self_repair_fails_closed_for_gated_object(self):
        self.store.register_object(EditableObjectSpec(
            "architecture-a", "architecture", "Architecture A", "1.0.0", "architecture/a.md",
            "GLOBAL_CONTROL_PLANE", "JARVIS_OWNER", "GATED_EXECUTION", "architecture",
        ))
        result = SelfRepairEngine(self.store).repair(
            "architecture-a", [lambda _content: (False, "issue")], lambda content, _failures: content + "fixed"
        )
        self.assertEqual(result["state"], "BLOCKED")

    def test_voice_and_chat_use_same_policy_and_redact_sensitive_text(self):
        assistant = UnifiedJarvisAssistant(self.store)
        text_session = assistant.start_session(channel="text", model_route="free-first")
        voice_session = assistant.start_session(channel="voice", model_route="local")
        text_preview = assistant.command_preview("update the workflow")
        voice_preview = assistant.command_preview("update the workflow")
        self.assertEqual(text_preview, voice_preview)
        message = assistant.add_message(voice_session, "user", "token=hidden-value and code 123456")
        self.assertTrue(message["redacted"])
        self.assertNotIn("hidden-value", message["content"])
        self.assertNotIn("123456", message["content"])
        assistant.add_message(text_session, "assistant", "Ready")

    def test_popup_payload_exposes_controls_models_context_and_evidence(self):
        self.store.register_object(EditableObjectSpec(
            "skill-a", "skill", "Skill A", "1.0.0", "skills/a/SKILL.md", "MODULE_SPECIFIC",
            "JARVIS_OWNER", "GATED_EXECUTION", "skill instructions",
        ))
        assistant = UnifiedJarvisAssistant(self.store)
        session = assistant.start_session(channel="multimodal", model_route="manual", context={"module": "skill-a"})
        assistant.add_message(session, "user", "show me this skill")
        payload = assistant.popup_payload(session, active_object_id="skill-a")
        self.assertTrue(payload["panels"]["voice_transcript"])
        self.assertTrue(payload["panels"]["diff_preview"])
        self.assertTrue(payload["panels"]["approval_queue"])
        self.assertIn("manual", payload["model_options"])
        self.assertEqual(payload["active_object"]["object_id"], "skill-a")
        self.assertEqual(payload["controls"]["production"], "DISABLED_UNTIL_RELEASE_GATE")

    def test_high_risk_assistant_command_is_prepare_only(self):
        assistant = UnifiedJarvisAssistant(self.store)
        preview = assistant.command_preview("publish this to production and use the secret")
        self.assertEqual(preview["action"], "prepare_only")
        self.assertTrue(preview["approval_required"])
        self.assertFalse(preview["automatic_execution"])


if __name__ == "__main__":
    unittest.main()
