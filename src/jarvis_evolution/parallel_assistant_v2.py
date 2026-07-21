from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping, Sequence

from jarvis_model_router.selector import (
    ModelCatalogue,
    ModelResponseRecord,
    build_synthesis_packet,
    plan_parallel_panel,
    selector_surface_contract,
    verify_consolidated_response,
)
from .control_plane_v1 import EvolutionStore, UnifiedJarvisAssistant


class ParallelJarvisAssistantV2(UnifiedJarvisAssistant):
    """Jarvis Pop V2 with concrete model selectors and panel evidence controls."""

    def __init__(self, store: EvolutionStore, catalogue: ModelCatalogue) -> None:
        super().__init__(store, model_routes=tuple(model.selector_id for model in catalogue.models) or ("deterministic",))
        self.catalogue = catalogue

    def popup_payload(self, session_id: str, *, active_object_id: str | None = None) -> dict[str, Any]:
        payload = super().popup_payload(session_id, active_object_id=active_object_id)
        payload["component"] = "JARVIS_POP_UNIFIED_ASSISTANT_V2"
        payload["universal_model_selector"] = selector_surface_contract(self.catalogue)
        payload["controls"].update({
            "parallel_thinking": "ENABLED" if self.catalogue.parallel_enabled else "BLOCKED_NEEDS_TWO_CONNECTED_MODELS",
            "parallel_model_limit": 8,
            "view_each_raw_response": "ENABLED",
            "view_consolidated_response": "ENABLED_AFTER_PANEL_CAPTURE",
            "claim_matrix": "REQUIRED",
            "contradiction_register": "REQUIRED",
            "omission_register": "REQUIRED",
        })
        payload["suggestions"].extend([
            "Run Parallel Thinking with selected models",
            "Compare all model responses",
            "Show agreements, disagreements and unsupported claims",
            "Verify no selected response was omitted",
        ])
        return payload

    def parallel_preview(
        self,
        prompt: str,
        task_type: str,
        *,
        selected_ids: Sequence[str] | None = None,
        panel_size: int = 8,
        high_risk_domain: bool = False,
    ) -> dict[str, Any]:
        plan = plan_parallel_panel(
            prompt,
            task_type,
            self.catalogue,
            selected_ids=selected_ids,
            panel_size=panel_size,
            high_risk_domain=high_risk_domain,
        )
        return {
            "plan": asdict(plan),
            "provider_calls_executed": False,
            "next_step": "Run approved provider adapters, preserve each raw response, then build the synthesis packet.",
        }

    @staticmethod
    def synthesis_packet(plan: Any, responses: Sequence[ModelResponseRecord], *, required_sections: Sequence[str] = ()) -> dict[str, Any]:
        return build_synthesis_packet(plan, responses, required_sections=required_sections)

    @staticmethod
    def verify_synthesis(packet: Mapping[str, Any], consolidated: Mapping[str, Any]) -> dict[str, Any]:
        return verify_consolidated_response(packet, consolidated)
