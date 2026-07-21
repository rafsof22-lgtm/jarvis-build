"""Deterministic task routing for Jarvis worker-model selection.

This module decides which configured route should handle a task class. It does not
send prompts or call model providers; provider clients belong behind a later
approval-gated implementation layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import ModelRoute, ROUTING_MODES, RouterConfig


@dataclass(frozen=True)
class RouteDecision:
    task_type: str
    route_name: str
    provider: str
    reason: str
    cloud_enabled: bool
    routing_mode: str = "free_first"
    restriction_policy: str = "approved_compliant_routes_only"


@dataclass(frozen=True)
class PanelDecision:
    task_type: str
    routing_mode: str
    routes: tuple[RouteDecision, ...]
    roles: tuple[str, ...]
    maximum_routes: int
    reason: str


TASK_ROUTE_PREFERENCES: dict[str, tuple[str, ...]] = {
    "planning": ("openai", "anthropic", "google", "openrouter", "local"),
    "safety": ("openai", "anthropic", "google", "openrouter", "local"),
    "coding": ("deepseek", "qwen", "anthropic", "openrouter", "local"),
    "long_context": ("kimi", "qwen", "google", "openrouter", "local"),
    "classification": ("qwen", "deepseek", "local"),
    "extraction": ("qwen", "deepseek", "local"),
    "embedding": ("local", "vllm", "llamacpp", "openrouter"),
    "ocr": ("local", "qwen", "google", "openrouter"),
    "repetitive_worker": ("local", "llamacpp", "vllm", "qwen"),
    "final_synthesis": ("openai", "anthropic", "google", "openrouter", "local"),
}

LOCAL_ONLY_MODES = {
    "local_sovereign",
    "offline_private",
    "highest_parameter_local",
    "fast_local",
}

MODE_ROUTE_PREFERENCES: dict[str, tuple[str, ...]] = {
    "lowest_restriction": ("local", "vllm", "llamacpp", "openrouter", "deepseek", "qwen", "kimi", "groq", "mistral", "google", "anthropic", "openai"),
    "local_sovereign": ("local", "vllm", "llamacpp"),
    "offline_private": ("local", "vllm", "llamacpp"),
    "highest_parameter_local": ("local", "vllm", "llamacpp"),
    "fast_local": ("local", "llamacpp", "vllm"),
    "free_first": ("local", "llamacpp", "vllm", "openrouter", "groq", "deepseek", "qwen", "kimi", "mistral", "google", "anthropic", "openai"),
    "cheapest_effective": ("local", "llamacpp", "vllm", "openrouter", "groq", "deepseek", "qwen", "kimi", "mistral", "google", "anthropic", "openai"),
    "quality_first": ("openai", "anthropic", "google", "mistral", "openrouter", "local", "vllm", "llamacpp"),
    "parallel_intelligence": ("local", "vllm", "llamacpp", "openrouter", "deepseek", "qwen", "kimi", "groq", "mistral", "google", "anthropic", "openai"),
}

PANEL_ROLES = (
    "primary",
    "researcher",
    "architect",
    "security_critic",
    "cost_critic",
    "domain_specialist",
    "independent_verifier",
    "synthesiser",
)


def route_task(
    task_type: str,
    config: RouterConfig | None = None,
    *,
    mode: str | None = None,
) -> RouteDecision:
    """Return the safest available route for a task type and routing mode."""

    active_config = config or RouterConfig.from_env()
    normalized_task = task_type.strip().lower() or "repetitive_worker"
    normalized_mode = (mode or active_config.routing_mode).strip().lower()
    if normalized_mode not in ROUTING_MODES:
        normalized_mode = "free_first"

    available_routes = active_config.available_routes()
    if normalized_mode in LOCAL_ONLY_MODES:
        available_routes = tuple(route for route in available_routes if route.local_first)
    available = {route.name: route for route in available_routes}

    if normalized_mode == "manual_model":
        if not active_config.manual_route:
            raise RuntimeError("Manual routing mode requires JARVIS_ROUTER_MANUAL_ROUTE.")
        selected = available.get(active_config.manual_route)
        if selected is None:
            raise RuntimeError("The requested manual route is not configured and approved.")
        preferred_names = (selected.name,)
    elif normalized_mode == "normal":
        preferred_names = TASK_ROUTE_PREFERENCES.get(
            normalized_task,
            (active_config.default_route, "local", "llamacpp", "vllm"),
        )
        selected = _first_available(preferred_names, available.values())
    else:
        mode_preferences = MODE_ROUTE_PREFERENCES.get(normalized_mode, MODE_ROUTE_PREFERENCES["free_first"])
        task_preferences = TASK_ROUTE_PREFERENCES.get(normalized_task, ())
        preferred_names = _merge_preferences(mode_preferences, task_preferences)
        selected = _first_available(preferred_names, available.values())

    if selected is None:
        raise RuntimeError("No configured Jarvis model routes are available for the selected policy.")

    return RouteDecision(
        task_type=normalized_task,
        route_name=selected.name,
        provider=selected.provider,
        reason=_decision_reason(normalized_task, normalized_mode, selected, active_config.allow_cloud),
        cloud_enabled=active_config.allow_cloud,
        routing_mode=normalized_mode,
        restriction_policy="least_unnecessarily_restrictive_approved_compliant" if normalized_mode == "lowest_restriction" else "approved_compliant_routes_only",
    )


def route_panel(
    task_type: str,
    config: RouterConfig | None = None,
    *,
    panel_size: int = 3,
    mode: str = "parallel_intelligence",
) -> PanelDecision:
    """Select one-to-eight unique configured routes without calling providers."""

    if not 1 <= int(panel_size) <= 8:
        raise ValueError("panel_size must be between 1 and 8")
    active_config = config or RouterConfig.from_env()
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"parallel_intelligence", "lowest_restriction", "local_sovereign", "offline_private", "free_first", "cheapest_effective", "quality_first"}:
        raise ValueError("Unsupported panel routing mode")

    routes = active_config.available_routes()
    if normalized_mode in {"local_sovereign", "offline_private"}:
        routes = tuple(route for route in routes if route.local_first)
    ordered_names = MODE_ROUTE_PREFERENCES.get(normalized_mode, MODE_ROUTE_PREFERENCES["parallel_intelligence"])
    route_map = {route.name: route for route in routes}
    selected_routes = [route_map[name] for name in ordered_names if name in route_map][: int(panel_size)]
    if not selected_routes:
        raise RuntimeError("No configured routes are available for the requested panel.")

    decisions = tuple(
        RouteDecision(
            task_type=task_type.strip().lower() or "repetitive_worker",
            route_name=route.name,
            provider=route.provider,
            reason=f"Selected as panel route {index + 1} under {normalized_mode} policy.",
            cloud_enabled=active_config.allow_cloud,
            routing_mode=normalized_mode,
            restriction_policy="approved_compliant_routes_only",
        )
        for index, route in enumerate(selected_routes)
    )
    roles = PANEL_ROLES[: len(decisions)]
    return PanelDecision(
        task_type=task_type.strip().lower() or "repetitive_worker",
        routing_mode=normalized_mode,
        routes=decisions,
        roles=roles,
        maximum_routes=8,
        reason="Independent routes are selected for comparison; provider calls, budgets, evidence checks and synthesis remain downstream approval-gated steps.",
    )


def _merge_preferences(primary: Iterable[str], secondary: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    for name in (*tuple(primary), *tuple(secondary)):
        if name not in result:
            result.append(name)
    return tuple(result)


def _first_available(names: Iterable[str], routes: Iterable[ModelRoute]) -> ModelRoute | None:
    route_map = {route.name: route for route in routes}
    for name in names:
        if name in route_map:
            return route_map[name]
    return next(iter(route_map.values()), None)


def _decision_reason(task_type: str, mode: str, route: ModelRoute, allow_cloud: bool) -> str:
    if route.local_first:
        return f"{task_type} routed to local/free-first provider {route.provider} under {mode} mode."
    if allow_cloud:
        return f"{task_type} routed to configured cloud provider {route.provider} under {mode} mode."
    return f"{task_type} fell back to {route.provider}; cloud routing is disabled."
