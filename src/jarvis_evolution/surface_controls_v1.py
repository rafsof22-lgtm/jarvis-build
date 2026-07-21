from __future__ import annotations
from typing import Any, Mapping
from jarvis_model_router.selector import ModelCatalogue, SHARED_SELECTOR_SURFACES, selector_surface_contract

PROTECTED_BY_SURFACE={
 "framework_editor":["owner_authority","security_baseline","production_gate"],
 "spec_editor":["evidence_requirements","acceptance_gate"],
 "workflow_builder":["credential_values","approval_bypass","destructive_actions"],
 "stack_and_architecture_editor":["network_trust_boundary","secret_store"],
 "orchestrator_editor":["self_elevation","recursive_spawning","policy_override"],
 "skill_editor":["frontmatter_name","safety_controls","release_gate"],
 "agent_editor":["allowed_tools","credential_scope","autonomy_ceiling"],
 "prompt_library":["system_policy","secret_values"],
 "source_analyst":["raw_source_integrity","provenance"],
 "test_and_evaluation_console":["test_evidence","waiver_authority"],
 "deployment_wizard":["production_promotion","billing","public_exposure"],
 "jarvis_pop":["owner_authority","approval_policy"],
 "command_centre":["owner_authority","release_gate"],
}

def build_surface_payload(surface:str,catalogue:ModelCatalogue,*,metrics:Mapping[str,Any]|None=None)->dict[str,Any]:
    if surface not in SHARED_SELECTOR_SURFACES:raise ValueError("unsupported selector surface")
    return {"component":"JARVIS_SHARED_MODEL_CONTROL_V1","surface":surface,"state":"INTEGRATED_STAGING","selector":selector_surface_contract(catalogue),"capabilities":{"view_all_connected_models":True,"manual_selection":True,"automatic_best_fit":True,"parallel_thinking_up_to_8":True,"view_raw_responses":True,"view_consolidated_response":True,"view_claim_evidence_matrix":True,"view_contradictions_and_omissions":True,"cancel_or_stop":True,"retry_failed_models":"POLICY_GATED","manual_override":"OWNER_GATED"},"protected_fields":PROTECTED_BY_SURFACE[surface],"panel_metrics":dict(metrics or {}),"provider_execution":"POLICY_BUDGET_PRIVACY_GATED","production_changes":"RELEASE_GATE_REQUIRED","truth_boundary":"The control is integrated as a local UI/runtime contract. Live providers and production remain separately evidenced."}

def build_all_surface_payloads(catalogue:ModelCatalogue,*,metrics:Mapping[str,Any]|None=None)->dict[str,dict[str,Any]]:
    return {surface:build_surface_payload(surface,catalogue,metrics=metrics) for surface in SHARED_SELECTOR_SURFACES}
