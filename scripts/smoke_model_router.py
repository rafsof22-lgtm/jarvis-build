#!/usr/bin/env python3
"""Smoke-test the Jarvis model-router scaffold without external services."""

from __future__ import annotations

from jarvis_model_router import RouterConfig, route_task


def main() -> int:
    config = RouterConfig.from_env()
    available = config.available_routes()
    if not available:
        raise SystemExit("No free/local Jarvis model routes are available.")

    expected_local_tasks = [
        "coding",
        "long_context",
        "classification",
        "repetitive_worker",
        "unknown_task",
    ]
    for task_type in expected_local_tasks:
        decision = route_task(task_type, config)
        if decision.cloud_enabled:
            raise SystemExit("Smoke test expected cloud routing to be disabled by default.")
        if decision.route_name not in {route.name for route in available}:
            raise SystemExit(f"Task {task_type} selected unavailable route {decision.route_name}.")
        print(f"{task_type}: {decision.route_name} ({decision.provider})")

    print("Jarvis model-router smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
