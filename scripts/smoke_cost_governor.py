#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_model_router.cost_governor import (
    BudgetPolicy, UsageEstimate, cache_key, estimate_cost,
    load_provider_registry, make_batches, quote_routes, select_route,
)


def main() -> int:
    registry = load_provider_registry(ROOT / "registry" / "providers.json")
    usage = UsageEstimate(input_tokens=10_000, cached_input_tokens=5_000, output_tokens=1_000, batch=True)
    quotes = quote_routes(registry["routes"], usage, 50, BudgetPolicy(20, 50), sensitive=False)
    selected = select_route(quotes)
    if selected.blocked:
        raise SystemExit("Selected route must not be blocked")
    if selected.estimated_cost_usd < 0:
        raise SystemExit("Estimated cost cannot be negative")
    sensitive_quotes = quote_routes(registry["routes"], usage, 40, BudgetPolicy(20, 50), sensitive=True)
    if any(item.route_id == "openrouter-free" for item in sensitive_quotes):
        raise SystemExit("Sensitive tasks must exclude non-sensitive-only routes")
    expensive = quote_routes(
        registry["routes"], UsageEstimate(100_000_000, 0, 100_000_000),
        90, BudgetPolicy(1, 2), sensitive=False,
    )
    if expensive and not all(item.blocked for item in expensive):
        raise SystemExit("Hard budget should block excessive projected spend")
    if cache_key("x", {"a": 1}) != cache_key("x", {"a": 1}):
        raise SystemExit("Cache keys must be deterministic")
    if make_batches([1, 2, 3, 4, 5], 2) != [[1, 2], [3, 4], [5]]:
        raise SystemExit("Batching failed")
    nano = next(item for item in registry["routes"] if item["route_id"] == "openai-gpt-5-nano")
    if estimate_cost(nano, UsageEstimate(1_000_000, 0, 0)) != 0.05:
        raise SystemExit("Token cost estimate failed")
    print(f"Cost governor smoke passed; cheapest qualified route: {selected.route_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
