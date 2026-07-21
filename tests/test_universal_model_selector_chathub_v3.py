import tempfile
import unittest
from pathlib import Path

from jarvis_model_router.selector import (
    ModelResponseRecord, build_model_catalogue, build_synthesis_packet,
    plan_parallel_panel, selector_surface_contract, verify_consolidated_response,
)
from src.jarvis_chathub.intake_v3 import (
    ChatHubTextParserV3, build_applicability_register, build_source_accounting,
)


class Route:
    def __init__(self, name, provider, default_model_env, local_first=False):
        self.name = name
        self.provider = provider
        self.default_model_env = default_model_env
        self.local_first = local_first
        self.cost_class = "owned" if local_first else "variable"
        self.privacy_class = "local" if local_first else "provider"


class Config:
    def __init__(self):
        self.routes = (
            Route("local", "ollama", "OLLAMA_DEFAULT_MODEL", True),
            Route("openai", "openai", "OPENAI_DEFAULT_MODEL"),
            Route("qwen", "qwen", "QWEN_DEFAULT_MODEL"),
        )

    def available_routes(self):
        return self.routes


class SelectorTests(unittest.TestCase):
    def env(self):
        return {
            "OLLAMA_DEFAULT_MODEL": "qwen3:32b",
            "JARVIS_LOCAL_MODELS": "qwen3:32b,llama3.3:70b",
            "OPENAI_DEFAULT_MODEL": "gpt-5.6",
            "JARVIS_OPENAI_MODELS": "gpt-5.6,gpt-5.6-mini",
            "QWEN_DEFAULT_MODEL": "qwen-max",
        }

    def test_catalogue_lists_every_unique_connected_model(self):
        cat = build_model_catalogue(Config(), environ=self.env())
        self.assertEqual(len(cat.models), 5)
        self.assertTrue(cat.parallel_enabled)

    def test_routes_without_inventory_are_visible(self):
        cat = build_model_catalogue(Config(), environ={"OLLAMA_DEFAULT_MODEL": "x"})
        self.assertEqual(set(cat.routes_without_model_inventory), {"openai", "qwen"})

    def test_panel_rejects_under_two_models(self):
        cat = build_model_catalogue(Config(), environ={"OLLAMA_DEFAULT_MODEL": "x"})
        with self.assertRaises(RuntimeError):
            plan_parallel_panel("p", "planning", cat, panel_size=2)

    def test_panel_accepts_up_to_eight_and_preserves_roles(self):
        cat = build_model_catalogue(Config(), environ=self.env())
        plan = plan_parallel_panel("p", "planning", cat, panel_size=5)
        self.assertEqual(len(plan.selected_models), 5)
        self.assertEqual(len(plan.roles), 5)
        self.assertTrue(plan.preserve_raw_outputs)

    def test_panel_rejects_more_than_eight(self):
        with self.assertRaises(ValueError):
            plan_parallel_panel("p", "planning", build_model_catalogue(Config(), environ=self.env()), panel_size=9)

    def test_synthesis_packet_preserves_all_raw_responses(self):
        cat = build_model_catalogue(Config(), environ=self.env())
        plan = plan_parallel_panel("p", "planning", cat, panel_size=3)
        responses = [ModelResponseRecord(m.selector_id, r, f"answer {i}") for i, (m, r) in enumerate(zip(plan.selected_models, plan.roles))]
        packet = build_synthesis_packet(plan, responses, required_sections=("answer", "risks"))
        self.assertTrue(packet["ready_for_synthesis"])
        self.assertEqual(packet["raw_response_count"], 3)

    def test_synthesis_verifier_detects_missing_response(self):
        cat = build_model_catalogue(Config(), environ=self.env())
        plan = plan_parallel_panel("p", "planning", cat, panel_size=2)
        responses = [ModelResponseRecord(m.selector_id, r, "answer") for m, r in zip(plan.selected_models, plan.roles)]
        packet = build_synthesis_packet(plan, responses, required_sections=("answer",))
        result = verify_consolidated_response(packet, {"included_response_refs": [f"{responses[0].selector_id}:{responses[0].sha256}"], "present_sections": ["answer"]})
        self.assertFalse(result["passed"])

    def test_surface_contract_propagates_selector(self):
        contract = selector_surface_contract(build_model_catalogue(Config(), environ=self.env()))
        self.assertIn("jarvis_pop", contract["surfaces"])
        self.assertIn("skill_editor", contract["surfaces"])
        self.assertEqual(contract["parallel_thinking"]["maximum_models"], 8)

    def test_high_risk_panel_requires_qualified_review(self):
        plan = plan_parallel_panel("p", "health", build_model_catalogue(Config(), environ=self.env()), panel_size=2, high_risk_domain=True)
        self.assertEqual(plan.approval_state, "QUALIFIED_REVIEW_REQUIRED")

    def test_identical_text_from_two_models_has_two_proof_refs(self):
        cat = build_model_catalogue(Config(), environ=self.env())
        plan = plan_parallel_panel("p", "planning", cat, panel_size=2)
        responses = [ModelResponseRecord(m.selector_id, r, "same") for m, r in zip(plan.selected_models, plan.roles)]
        packet = build_synthesis_packet(plan, responses)
        refs = [f"{x['selector_id']}:{x['sha256']}" for x in packet["raw_responses"]]
        self.assertEqual(len(set(refs)), 2)

    def test_manual_selected_ids_preserve_order(self):
        cat = build_model_catalogue(Config(), environ=self.env())
        ids = [cat.models[2].selector_id, cat.models[0].selector_id]
        plan = plan_parallel_panel("p", "coding", cat, selected_ids=ids, panel_size=2)
        self.assertEqual([m.selector_id for m in plan.selected_models], ids)

    def test_panel_packet_does_not_claim_universal_truth(self):
        cat = build_model_catalogue(Config(), environ=self.env())
        plan = plan_parallel_panel("p", "planning", cat, panel_size=2)
        responses = [ModelResponseRecord(m.selector_id, r, "answer") for m, r in zip(plan.selected_models, plan.roles)]
        packet = build_synthesis_packet(plan, responses)
        self.assertIn("not universal truth", packet["truth_boundary"])


class ChatHubV3Tests(unittest.TestCase):
    def test_roles_and_authority_are_separate(self):
        parsed = ChatHubTextParserV3().parse("**user**: build Jarvis\n**cloud-qwen-3.8-max**: proposal\n")
        self.assertEqual(parsed["messages"][0]["authority"], "USER_REQUIREMENT")
        self.assertEqual(parsed["messages"][1]["authority"], "ASSISTANT_PROPOSAL_NOT_APPROVED")

    def test_unsafe_medical_claim_is_quarantined(self):
        message = ChatHubTextParserV3().parse("**cloud-mistral-large**: cure is inevitable. Use CRISPR and ibogaine 10 mg.\n")["messages"][0]
        self.assertEqual(message["disposition"], "QUARANTINED_FOR_REVIEW")

    def test_duplicate_has_lineage(self):
        parsed = ChatHubTextParserV3().parse("**cloud-qwen-3.8-max**: same\n**cloud-qwen-3.8-max**: same\n")
        self.assertEqual(parsed["messages"][1]["exact_duplicate_of"], 1)

    def test_every_message_accounted_and_routed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.txt"
            path.write_text("**user**: Apollo CSV export\n**cloud-gpt-5-thinking**: use official API and audit\n", encoding="utf-8")
            accounting = build_source_accounting([path], pointer_prefix="upload:")
            register = build_applicability_register(accounting)
        self.assertTrue(accounting["all_messages_accounted"])
        self.assertTrue(any(route["module"] == "apollo_property" for route in register["routes"]))


if __name__ == "__main__":
    unittest.main()
