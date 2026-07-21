from __future__ import annotations

import hashlib
import os
import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

PANEL_ROLES = (
    "primary_reasoner",
    "source_researcher",
    "systems_architect",
    "domain_specialist",
    "security_and_safety_critic",
    "cost_and_efficiency_critic",
    "independent_verifier",
    "final_synthesiser",
)

SHARED_SELECTOR_SURFACES = (
    "jarvis_pop",
    "command_centre",
    "framework_editor",
    "spec_editor",
    "workflow_builder",
    "stack_and_architecture_editor",
    "orchestrator_editor",
    "skill_editor",
    "agent_editor",
    "prompt_library",
    "source_analyst",
    "test_and_evaluation_console",
    "deployment_wizard",
)


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _split_models(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    parts = re.split(r"[,\n;]", value)
    return tuple(dict.fromkeys(part.strip() for part in parts if part.strip()))


@dataclass(frozen=True)
class ConnectedModel:
    selector_id: str
    route_name: str
    provider: str
    model_id: str
    local_first: bool
    cost_class: str
    privacy_class: str
    source: str
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModelCatalogue:
    models: tuple[ConnectedModel, ...]
    routes_without_model_inventory: tuple[str, ...]
    maximum_parallel_models: int = 8

    @property
    def parallel_enabled(self) -> bool:
        return len(self.models) >= 2

    def selector_options(self) -> list[dict[str, Any]]:
        return [asdict(model) for model in self.models]

    def get(self, selector_id: str) -> ConnectedModel:
        for model in self.models:
            if model.selector_id == selector_id:
                return model
        raise KeyError(selector_id)


def build_model_catalogue(config: Any, *, environ: Mapping[str, str] | None = None) -> ModelCatalogue:
    """Enumerate every concrete model declared for each currently available route."""
    env = environ if environ is not None else os.environ
    models: list[ConnectedModel] = []
    unresolved: list[str] = []
    seen: set[str] = set()
    for route in config.available_routes():
        inventory_env = f"JARVIS_{route.name.upper().replace('-', '_')}_MODELS"
        candidates: list[tuple[str, str]] = []
        if route.default_model_env and env.get(route.default_model_env):
            candidates.append((env[route.default_model_env].strip(), f"env:{route.default_model_env}"))
        candidates.extend((model_id, f"env:{inventory_env}") for model_id in _split_models(env.get(inventory_env)))
        if not candidates:
            unresolved.append(route.name)
            continue
        for model_id, source in candidates:
            selector_id = f"{route.name}:{model_id}"
            if selector_id in seen:
                continue
            seen.add(selector_id)
            models.append(ConnectedModel(
                selector_id=selector_id,
                route_name=route.name,
                provider=route.provider,
                model_id=model_id,
                local_first=route.local_first,
                cost_class=route.cost_class,
                privacy_class=route.privacy_class,
                source=source,
                capabilities=("text",),
            ))
    return ModelCatalogue(tuple(models), tuple(unresolved))


@dataclass(frozen=True)
class ParallelPanelPlan:
    panel_id: str
    task_type: str
    prompt_sha256: str
    selected_models: tuple[ConnectedModel, ...]
    roles: tuple[str, ...]
    maximum_models: int
    preserve_raw_outputs: bool
    synthesis_contract: Mapping[str, Any]
    approval_state: str


def plan_parallel_panel(
    prompt: str,
    task_type: str,
    catalogue: ModelCatalogue,
    *,
    selected_ids: Sequence[str] | None = None,
    panel_size: int = 8,
    high_risk_domain: bool = False,
) -> ParallelPanelPlan:
    if not 2 <= int(panel_size) <= 8:
        raise ValueError("panel_size must be between 2 and 8")
    if selected_ids is not None:
        unique_ids = tuple(dict.fromkeys(selected_ids))
        if len(unique_ids) > 8:
            raise ValueError("no more than eight models may be selected")
        selected = [catalogue.get(model_id) for model_id in unique_ids]
    else:
        selected = list(catalogue.models)[: int(panel_size)]
    if len(selected) < 2:
        raise RuntimeError("Parallel Thinking requires at least two concrete connected models")
    selected = selected[: int(panel_size)]
    contract = {
        "raw_response_retention": "REQUIRED",
        "response_hashes": "REQUIRED",
        "claim_and_evidence_matrix": "REQUIRED",
        "contradiction_register": "REQUIRED",
        "omission_register": "REQUIRED",
        "all_selected_models_referenced_by_final": True,
        "unresolved_disagreement_must_be_visible": True,
        "source_citations_required_when_available": True,
        "universal_zero_error_claim_allowed": False,
        "completion_label": "NO_KNOWN_GAPS_WITHIN_VERIFIED_PANEL_SCOPE",
        "human_or_qualified_review_required": high_risk_domain,
    }
    return ParallelPanelPlan(
        panel_id=f"panel-{uuid.uuid4().hex}",
        task_type=task_type.strip().lower() or "general",
        prompt_sha256=_digest(prompt),
        selected_models=tuple(selected),
        roles=PANEL_ROLES[: len(selected)],
        maximum_models=8,
        preserve_raw_outputs=True,
        synthesis_contract=contract,
        approval_state="QUALIFIED_REVIEW_REQUIRED" if high_risk_domain else "POLICY_PREFLIGHT_REQUIRED",
    )


@dataclass(frozen=True)
class ModelResponseRecord:
    selector_id: str
    role: str
    raw_text: str
    citations: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()

    @property
    def sha256(self) -> str:
        return _digest(self.raw_text)


def build_synthesis_packet(
    plan: ParallelPanelPlan,
    responses: Sequence[ModelResponseRecord],
    *,
    required_sections: Sequence[str] = (),
) -> dict[str, Any]:
    expected = [model.selector_id for model in plan.selected_models]
    received = [response.selector_id for response in responses]
    if len(received) != len(set(received)):
        raise ValueError("duplicate model response")
    missing = sorted(set(expected) - set(received))
    unexpected = sorted(set(received) - set(expected))
    role_by_model = {model.selector_id: role for model, role in zip(plan.selected_models, plan.roles)}
    records = [{
        "selector_id": response.selector_id,
        "assigned_role": role_by_model.get(response.selector_id),
        "reported_role": response.role,
        "sha256": response.sha256,
        "word_count": len(re.findall(r"\S+", response.raw_text)),
        "citations": list(response.citations),
        "claim_ids": list(response.claim_ids),
        "raw_text": response.raw_text,
    } for response in responses]
    return {
        "schema_version": "1.0.0",
        "panel_id": plan.panel_id,
        "prompt_sha256": plan.prompt_sha256,
        "expected_models": expected,
        "received_models": received,
        "missing_models": missing,
        "unexpected_models": unexpected,
        "raw_response_count": len(records),
        "raw_responses": records,
        "required_sections": list(dict.fromkeys(required_sections)),
        "consolidation_instructions": [
            "Preserve every model response as an immutable source record.",
            "Extract claims, evidence, unique insights, agreements and disagreements.",
            "Do not use majority vote as proof.",
            "Prefer verified evidence, safety, compliance and current authoritative sources.",
            "Keep unresolved contradictions visible.",
            "List omitted or unsupported material with reasons.",
            "Produce a best-supported consolidated response, not a guaranteed perfect answer.",
        ],
        "ready_for_synthesis": not missing and not unexpected,
        "truth_boundary": "The packet can prove complete capture of selected panel outputs, not universal truth or universal source coverage.",
    }


def verify_consolidated_response(packet: Mapping[str, Any], consolidated: Mapping[str, Any]) -> dict[str, Any]:
    expected_refs = {f"{item['selector_id']}:{item['sha256']}" for item in packet["raw_responses"]}
    included_refs = set(consolidated.get("included_response_refs", ()))
    missing_refs = sorted(expected_refs - included_refs)
    required_sections = set(packet.get("required_sections", ()))
    present_sections = set(consolidated.get("present_sections", ()))
    missing_sections = sorted(required_sections - present_sections)
    unresolved = list(consolidated.get("unresolved_conflicts", ()))
    passed = bool(packet.get("ready_for_synthesis")) and not missing_refs and not missing_sections
    return {
        "passed": passed,
        "missing_response_refs": missing_refs,
        "missing_required_sections": missing_sections,
        "unresolved_conflicts": unresolved,
        "status": "NO_KNOWN_DATA_LOSS_WITHIN_VERIFIED_PANEL_SCOPE" if passed else "INCOMPLETE_SYNTHESIS",
        "universal_zero_error_or_zero_gap_claim": False,
    }


def selector_surface_contract(catalogue: ModelCatalogue) -> dict[str, Any]:
    return {
        "component": "JARVIS_UNIVERSAL_MODEL_SELECTOR_V1",
        "surfaces": list(SHARED_SELECTOR_SURFACES),
        "selector_options": catalogue.selector_options(),
        "routes_without_model_inventory": list(catalogue.routes_without_model_inventory),
        "parallel_thinking": {
            "button_label": "Parallel Thinking · Up to 8 LLMs",
            "enabled": catalogue.parallel_enabled,
            "minimum_models": 2,
            "maximum_models": 8,
            "raw_outputs_preserved": True,
            "consolidated_output_separate": True,
            "manual_model_selection": True,
            "automatic_best_fit_selection": True,
        },
        "truth_boundary": "Selectors show concrete configured model IDs only. A configured provider route without a model inventory is reported as unresolved, not silently invented.",
    }
