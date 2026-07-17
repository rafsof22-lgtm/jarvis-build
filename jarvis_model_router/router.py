"""Deterministic task routing for Jarvis worker-model selection.

This module decides which configured route should handle a task class. It does not
send prompts or call model providers; provider clients belong behind a later
approval-gated implementation layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import ModelRoute, RouterConfig


@dataclass(frozen=True)
class RouteDecision:
    task_type: str
    route_name: str
    provider: str
    reason: str
    cloud_enabled: bool


TASK_ROUTE_PREFERENCES: dict[str, tuple[str, ...]] = {
    "planning": ("openai", "openrouter", "local"),
    "safety": ("openai", "openrouter", "local"),
    "coding": ("deepseek", "qwen", "openrouter", "local"),
    "long_context": ("kimi", "qwen", "openrouter", "local"),
    "classification": ("qwen", "deepseek", "local"),
    "extraction": ("qwen", "deepseek", "local"),
    "embedding": ("local", "openrouter"),
    "ocr": ("local", "qwen", "openrouter"),
    "repetitive_worker": ("local", "llamacpp", "qwen"),
    "final_synthesis": ("openai", "openrouter", "local"),
}


def route_task(task_type: str, config: RouterConfig | None = None) -> RouteDecision:
    """Return the safest available route for a task type."""

    active_config = config or RouterConfig.from_env()
    available = {route.name: route for route in active_config.available_routes()}
    normalized_task = task_type.strip().lower() or "repetitive_worker"

    preferred_names = TASK_ROUTE_PREFERENCES.get(
        normalized_task,
        (active_config.default_route, "local", "llamacpp"),
    )
    selected = _first_available(preferred_names, available.values())
    if selected is None:
        raise RuntimeError("No configured Jarvis model routes are available.")

    return RouteDecision(
        task_type=normalized_task,
        route_name=selected.name,
        provider=selected.provider,
        reason=_decision_reason(normalized_task, selected, active_config.allow_cloud),
        cloud_enabled=active_config.allow_cloud,
    )


def _first_available(names: Iterable[str], routes: Iterable[ModelRoute]) -> ModelRoute | None:
    route_map = {route.name: route for route in routes}
    for name in names:
        if name in route_map:
            return route_map[name]
    return next(iter(route_map.values()), None)


def _decision_reason(task_type: str, route: ModelRoute, allow_cloud: bool) -> str:
    if route.local_first:
        return f"{task_type} routed to local/free-first provider {route.provider}."
    if allow_cloud:
        return f"{task_type} routed to configured cloud provider {route.provider}."
    return f"{task_type} fell back to {route.provider}; cloud routing is disabled."
