#!/usr/bin/env python3
"""Validate Jarvis workflow, UI, module-chat and secret-safety controls."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    workflows_path = ROOT / "registry" / "workflows.json"
    spec_path = ROOT / "docs" / "sovereign-command-centre-and-automation-spec.md"
    workflows = json.loads(workflows_path.read_text(encoding="utf-8"))
    rows = workflows.get("workflows")
    if not isinstance(rows, list) or len(rows) < 7:
        raise SystemExit("workflow registry must contain the initial canonical workflow set")
    required_fields = {"workflow_id", "repository", "type", "trigger", "owner", "status", "cost_route", "capabilities", "next_action"}
    for row in rows:
        missing = required_fields - set(row)
        if missing:
            raise SystemExit(f"workflow {row.get('workflow_id')} missing {sorted(missing)}")
    text = spec_path.read_text(encoding="utf-8")
    required_phrases = [
        "Sovereign Command Centre",
        "Credential Readiness",
        "Secret values remain in approved",
        "New project MODULE chat rule",
        "reuse -> configure -> extend -> compose -> create",
        "free/local, included, cheapest-qualified, best-value, scalable and premium",
        "manual override",
        "rollback",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            raise SystemExit(f"missing governance phrase: {phrase}")
    forbidden_paths = [ROOT / ".env", ROOT / ".env.local", ROOT / ".env.production"]
    if any(path.exists() for path in forbidden_paths):
        raise SystemExit("repository root must not contain committed runtime .env files")
    print("Sovereign controls smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
