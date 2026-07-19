"""Offline-first Jarvis cost governor and telemetry.

This module never calls a provider. It authorizes or blocks a proposed route before
an adapter may execute it, estimates spend from the provider registry, and records
append-only JSONL telemetry without storing prompts or secrets.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class BudgetPolicy:
    warning_usd: float = 20.0
    soft_limit_usd: float = 35.0
    hard_limit_usd: float = 50.0
    paid_enabled: bool = False
    owner_approval: bool = False


@dataclass(frozen=True)
class UsageEstimate:
    route_id: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    estimated_usd: float
    batch: bool


@dataclass(frozen=True)
class Authorization:
    allowed: bool
    level: str
    reason: str
    estimate: UsageEstimate
    projected_monthly_usd: float


def load_provider_registry(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("routes"), list):
        raise ValueError("provider registry must contain routes")
    return data


def find_route(registry: dict[str, Any], route_id: str) -> dict[str, Any]:
    for route in registry["routes"]:
        if route.get("route_id") == route_id:
            return route
    raise KeyError(f"unknown route_id: {route_id}")


def estimate_usage(route: dict[str, Any], *, input_tokens: int, output_tokens: int,
                   cached_input_tokens: int = 0, batch: bool = False) -> UsageEstimate:
    if min(input_tokens, output_tokens, cached_input_tokens) < 0:
        raise ValueError("token counts cannot be negative")
    cached = min(cached_input_tokens, input_tokens)
    uncached = input_tokens - cached
    if batch and route.get("batch_input_usd_per_million") is not None:
        in_rate = float(route["batch_input_usd_per_million"])
        out_rate = float(route["batch_output_usd_per_million"])
    else:
        discount = float(route.get("batch_discount_percent", 0)) / 100 if batch else 0
        in_rate = float(route.get("input_usd_per_million", 0)) * (1 - discount)
        out_rate = float(route.get("output_usd_per_million", 0)) * (1 - discount)
    cache_rate = float(route.get("cached_input_usd_per_million", in_rate))
    cost = (uncached * in_rate + cached * cache_rate + output_tokens * out_rate) / 1_000_000
    return UsageEstimate(route["route_id"], input_tokens, cached, output_tokens, round(cost, 8), batch)


def authorize(estimate: UsageEstimate, *, current_monthly_usd: float, policy: BudgetPolicy,
              route_tier: str) -> Authorization:
    projected = round(current_monthly_usd + estimate.estimated_usd, 8)
    is_paid = estimate.estimated_usd > 0 or route_tier not in {"local", "free_cloud"}
    if is_paid and not policy.paid_enabled:
        return Authorization(False, "blocked", "paid routes are disabled", estimate, projected)
    if is_paid and not policy.owner_approval:
        return Authorization(False, "blocked", "owner approval is required", estimate, projected)
    if projected > policy.hard_limit_usd:
        return Authorization(False, "hard_stop", "hard monthly budget would be exceeded", estimate, projected)
    if projected > policy.soft_limit_usd:
        return Authorization(True, "soft_limit", "soft limit exceeded; restrict to approved critical work", estimate, projected)
    if projected > policy.warning_usd:
        return Authorization(True, "warning", "monthly warning threshold exceeded", estimate, projected)
    return Authorization(True, "ok", "within approved budget", estimate, projected)


def append_usage_event(path: Path, *, task_id: str, task_type: str, authorization: Authorization,
                       latency_ms: int, retries: int, cache_hit: bool, success: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "task_type": task_type,
        "authorization": asdict(authorization),
        "latency_ms": latency_ms,
        "retries": retries,
        "cache_hit": cache_hit,
        "success": success,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def summarize_events(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(events)
    return {
        "runs": len(rows),
        "successful": sum(bool(x.get("success")) for x in rows),
        "retries": sum(int(x.get("retries", 0)) for x in rows),
        "cache_hits": sum(bool(x.get("cache_hit")) for x in rows),
        "estimated_usd": round(sum(float(x["authorization"]["estimate"]["estimated_usd"]) for x in rows), 8),
        "latency_ms": sum(int(x.get("latency_ms", 0)) for x in rows),
    }
