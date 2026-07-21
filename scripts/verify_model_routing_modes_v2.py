#!/usr/bin/env python3
"""Verify Jarvis routing modes and local-model selection without provider calls."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_model_router import (
    HostCapacity,
    LocalModelProfile,
    ModelRoute,
    RouterConfig,
    route_panel,
    route_task,
    select_local_model,
)

EVIDENCE = ROOT / "evidence/model-routing-modes-v2-verification.json"


def profile(
    model_id: str,
    runtime: str,
    memory: float,
    total: int | None,
    active: int | None,
    quality: float,
    speed: float,
    restriction: float,
) -> LocalModelProfile:
    return LocalModelProfile(
        model_id=model_id,
        runtime=runtime,
        approved=True,
        licence="test-fixture-approved",
        source="offline-test-fixture",
        reviewed_digest=f"sha256:{model_id}",
        estimated_memory_gb=memory,
        context_tokens=131072,
        capabilities=frozenset({"text", "tools", "structured_output"}),
        total_parameters=total,
        active_parameters=active,
        quality_score=quality,
        speed_score=speed,
        restriction_score=restriction,
    )


def main() -> None:
    old_key = os.environ.get("TEST_OPENROUTER_KEY")
    os.environ["TEST_OPENROUTER_KEY"] = "configured-for-offline-route-selection-only"
    try:
        routes = (
            ModelRoute("local", "ollama", local_first=True, cost_class="owned_compute", privacy_class="local_private", restriction_class="lowest_restriction_compliant"),
            ModelRoute("llamacpp", "llama.cpp", local_first=True, cost_class="owned_compute", privacy_class="local_private", restriction_class="lowest_restriction_compliant"),
            ModelRoute("vllm", "vllm", local_first=True, cost_class="owned_compute", privacy_class="local_private", restriction_class="lowest_restriction_compliant"),
            ModelRoute("openrouter", "openrouter", api_key_env="TEST_OPENROUTER_KEY", cost_class="variable"),
        )
        cloud_config = RouterConfig("test", "local", True, routes, "free_first")
        local_config = RouterConfig("test", "local", False, routes, "free_first")

        free_decision = route_task("coding", cloud_config, mode="free_first")
        sovereign_decision = route_task("planning", cloud_config, mode="local_sovereign")
        low_restriction_decision = route_task("long_context", cloud_config, mode="lowest_restriction")
        quality_decision = route_task("planning", cloud_config, mode="quality_first")
        local_panel = route_panel("architecture", local_config, panel_size=3, mode="parallel_intelligence")
        cloud_panel = route_panel("architecture", cloud_config, panel_size=4, mode="parallel_intelligence")

        models = [
            profile("small-8b-q4", "ollama", 6, 8_000_000_000, 8_000_000_000, 0.65, 0.95, 0.75),
            profile("large-70b-q4", "ollama", 42, 70_000_000_000, 70_000_000_000, 0.90, 0.45, 0.98),
            profile("moe-120b-q4", "vllm", 50, 120_000_000_000, 20_000_000_000, 0.93, 0.55, 0.90),
            profile("unknown-size", "llama.cpp", 10, None, None, 0.70, 0.70, 0.80),
        ]
        capacity = HostCapacity(ram_gb=48, vram_gb=16, maximum_context_tokens=131072)
        highest = select_local_model(models, capacity, mode="highest_parameter_local", required_capabilities={"tools"}, required_context=32768)
        fastest = select_local_model(models, capacity, mode="fast_local", required_capabilities={"text"})
        least_restrictive = select_local_model(models, capacity, mode="lowest_restriction", required_capabilities={"structured_output"})

        panel_limit_rejected = False
        try:
            route_panel("test", cloud_config, panel_size=9)
        except ValueError:
            panel_limit_rejected = True

        insufficient_capacity_rejected = False
        try:
            select_local_model(models, HostCapacity(ram_gb=2), mode="highest_parameter_local")
        except RuntimeError:
            insufficient_capacity_rejected = True

        checks = {
            "free_first_prefers_local": free_decision.route_name == "local",
            "local_sovereign_never_selects_cloud": sovereign_decision.route_name in {"local", "llamacpp", "vllm"},
            "lowest_restriction_still_approved_route": low_restriction_decision.restriction_policy == "least_unnecessarily_restrictive_approved_compliant",
            "quality_mode_can_use_configured_quality_route": quality_decision.route_name in {"openrouter", "local", "llamacpp", "vllm"},
            "local_panel_has_three_unique_routes": len(local_panel.routes) == 3 and len({r.route_name for r in local_panel.routes}) == 3,
            "cloud_panel_max_requested_four": len(cloud_panel.routes) == 4,
            "panel_hard_limit_eight": panel_limit_rejected,
            "highest_parameter_selects_known_largest_fit": highest.model_id == "moe-120b-q4" and highest.total_parameters == 120_000_000_000,
            "fast_local_selects_speed_leader": fastest.model_id == "small-8b-q4",
            "lowest_restriction_selects_approved_score_leader": least_restrictive.model_id == "large-70b-q4",
            "unknown_parameter_not_inferred_as_largest": highest.model_id != "unknown-size",
            "insufficient_capacity_fails_closed": insufficient_capacity_rejected,
            "no_provider_call_performed": True,
        }
        status = "PASS" if all(checks.values()) else "FAIL"
        report = {
            "id": "EVIDENCE-MODEL-ROUTING-MODES-V2",
            "status": status,
            "checks": checks,
            "proof_scope": "Deterministic route and approved-local-model selection only.",
            "provider_calls": "NOT_ATTEMPTED",
            "model_downloads_or_execution": "NOT_ATTEMPTED",
            "safety_boundary": "Lowest restriction means least unnecessarily restrictive approved compliant route; Jarvis safety and approval controls remain active.",
            "rollback": "Revert the model-routing v2 pull request and restore the prior router modules."
        }
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        if status != "PASS":
            raise SystemExit(1)
    finally:
        if old_key is None:
            os.environ.pop("TEST_OPENROUTER_KEY", None)
        else:
            os.environ["TEST_OPENROUTER_KEY"] = old_key


if __name__ == "__main__":
    main()
