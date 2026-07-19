"""Offline-first Jarvis cost governor.

This module never calls a provider. It estimates cost, enforces soft/hard
limits, selects the cheapest qualified route, records telemetry, and plans
cache/batch use before an external client is allowed to run.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic
from typing import Any, Iterable


@dataclass(frozen=True)
class BudgetPolicy:
    soft_limit_usd: float = 20.0
    hard_limit_usd: float = 50.0
    require_approval_above_soft: bool = True


@dataclass(frozen=True)
class UsageEstimate:
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    batch: bool = False


@dataclass(frozen=True)
class RouteQuote:
    route_id: str
    tier: str
    estimated_cost_usd: float
    quality_score: int
    cache_supported: bool
    batch_supported: bool
    approval_required: bool
    blocked: bool
    reason: str


def load_provider_registry(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload.get("routes"), list):
        raise ValueError("provider registry must contain a routes list")
    return payload


def estimate_cost(route: dict[str, Any], usage: UsageEstimate) -> float:
    input_rate = float(route.get("input_usd_per_million", 0.0))
    cached_rate = float(route.get("cached_input_usd_per_million", input_rate))
    output_rate = float(route.get("output_usd_per_million", 0.0))
    normal_input = max(usage.input_tokens - usage.cached_input_tokens, 0)
    total = (
        normal_input * input_rate
        + usage.cached_input_tokens * cached_rate
        + usage.output_tokens * output_rate
    ) / 1_000_000
    if usage.batch:
        if "batch_input_usd_per_million" in route or "batch_output_usd_per_million" in route:
            total = (
                normal_input * float(route.get("batch_input_usd_per_million", input_rate))
                + usage.cached_input_tokens * cached_rate
                + usage.output_tokens * float(route.get("batch_output_usd_per_million", output_rate))
            ) / 1_000_000
        else:
            total *= 1 - float(route.get("batch_discount_percent", 0.0)) / 100
    return round(total, 8)


def quote_routes(
    routes: Iterable[dict[str, Any]],
    usage: UsageEstimate,
    minimum_quality: int,
    policy: BudgetPolicy,
    spent_usd: float = 0.0,
    sensitive: bool = False,
) -> list[RouteQuote]:
    quotes: list[RouteQuote] = []
    for route in routes:
        quality = int(route.get("quality_score", 0))
        if quality < minimum_quality:
            continue
        privacy = route.get("privacy_class", "unknown")
        status = route.get("status", "unknown")
        if sensitive and (privacy in {"provider_dependent", "free_training_tier"} or status == "non_sensitive_only"):
            continue
        cost = estimate_cost(route, usage)
        projected = spent_usd + cost
        blocked = projected > policy.hard_limit_usd
        approval = (
            status in {"approval_gated", "owner_approval_required"}
            or (policy.require_approval_above_soft and projected > policy.soft_limit_usd)
        )
        reason = "within budget"
        if blocked:
            reason = "hard budget limit exceeded"
        elif approval:
            reason = "approval required before billable execution"
        quotes.append(RouteQuote(
            route_id=str(route["route_id"]),
            tier=str(route.get("tier", "unknown")),
            estimated_cost_usd=cost,
            quality_score=quality,
            cache_supported=bool(route.get("supports_cache")),
            batch_supported=bool(route.get("supports_batch")),
            approval_required=approval,
            blocked=blocked,
            reason=reason,
        ))
    return sorted(quotes, key=lambda item: (item.blocked, item.estimated_cost_usd, -item.quality_score))


def select_route(quotes: Iterable[RouteQuote]) -> RouteQuote:
    for quote in quotes:
        if not quote.blocked:
            return quote
    raise RuntimeError("No qualified route is within the hard budget limit")


def cache_key(task_type: str, payload: Any, policy_version: str = "1.0.0") -> str:
    encoded = json.dumps(
        {"task_type": task_type, "payload": payload, "policy_version": policy_version},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def make_batches(items: list[Any], batch_size: int) -> list[list[Any]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    return [items[index:index + batch_size] for index in range(0, len(items), batch_size)]


def run_measured_pilot(
    registry_path: Path,
    telemetry_path: Path,
    tasks: list[dict[str, Any]],
    policy: BudgetPolicy | None = None,
) -> dict[str, Any]:
    active_policy = policy or BudgetPolicy()
    registry = load_provider_registry(registry_path)
    started = monotonic()
    spent = 0.0
    cache: dict[str, dict[str, Any]] = {}
    events: list[dict[str, Any]] = []
    retries = 0

    for task in tasks:
        key = cache_key(task["task_type"], task["payload"])
        if key in cache:
            events.append({"task_id": task["task_id"], "cache_hit": True, **cache[key]})
            continue
        usage = UsageEstimate(**task["usage"])
        quotes = quote_routes(
            registry["routes"], usage, int(task.get("minimum_quality", 0)),
            active_policy, spent_usd=spent, sensitive=bool(task.get("sensitive")),
        )
        chosen = select_route(quotes)
        spent += chosen.estimated_cost_usd
        event = {
            "task_id": task["task_id"], "cache_hit": False,
            "route": asdict(chosen), "simulated": True,
        }
        cache[key] = {"route": asdict(chosen), "simulated": True}
        events.append(event)

    report = {
        "pilot": "tool-registry-offline-routing",
        "provider_calls": 0,
        "actual_cost_usd": 0.0,
        "estimated_selected_cost_usd": round(spent, 8),
        "tasks": len(tasks),
        "cache_hits": sum(1 for event in events if event["cache_hit"]),
        "retries": retries,
        "duration_ms": round((monotonic() - started) * 1000, 3),
        "events": events,
    }
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)
    telemetry_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
