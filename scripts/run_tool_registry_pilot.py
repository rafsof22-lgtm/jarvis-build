#!/usr/bin/env python3
"""Run the zero-provider-call Tool Registry routing pilot."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_model_router.cost_governor import BudgetPolicy, make_batches, run_measured_pilot


def main() -> int:
    tools = json.loads((ROOT / "registry" / "tools.json").read_text(encoding="utf-8"))["tools"]
    batches = make_batches(tools, 2)
    tasks = []
    for index, batch in enumerate(batches, start=1):
        tasks.append({
            "task_id": f"tool-batch-{index}",
            "task_type": "classification",
            "payload": [{"tool_id": item["tool_id"], "category": item["category"]} for item in batch],
            "usage": {"input_tokens": 1200, "cached_input_tokens": 0, "output_tokens": 250, "batch": True},
            "minimum_quality": 40,
            "sensitive": False,
        })
    tasks.append({**tasks[0], "task_id": "tool-batch-cache-repeat"})
    report = run_measured_pilot(
        ROOT / "registry" / "providers.json",
        ROOT / "evidence" / "tool-registry-pilot.json",
        tasks,
        BudgetPolicy(soft_limit_usd=20.0, hard_limit_usd=50.0),
    )
    if report["provider_calls"] != 0 or report["actual_cost_usd"] != 0:
        raise SystemExit("Pilot must not call providers or incur actual spend")
    if report["cache_hits"] < 1:
        raise SystemExit("Pilot expected at least one cache hit")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
