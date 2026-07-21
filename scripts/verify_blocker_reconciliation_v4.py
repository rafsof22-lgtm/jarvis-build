#!/usr/bin/env python3
"""Verify the blocker reconciliation v4 truth and safety contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "registry/trackers/all_progress_tracker_reconciliation_v4.json"


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    assert data["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    assert data["completion_assertion"].startswith("No whole-program completion claim")

    resolved = {item["blocker_id"]: item for item in data["resolved_this_pass"]}
    blocked = {item["blocker_id"]: item for item in data["still_blocked"]}

    assert resolved["VTI-AUDIT-SCHEMA-CONTRACT"]["state"] == "DONE_VERIFIED"
    assert resolved["DIGITALOCEAN-CONTROL-PLANE-AND-ROLLBACK"]["state"] == "CONTROL_PLANE_AND_ROLLBACK_VERIFIED"
    assert "remaining_gate" in resolved["DIGITALOCEAN-CONTROL-PLANE-AND-ROLLBACK"]
    assert resolved["SOURCE-FOLDER0-ACCESS"]["state"] == "ACCESSIBLE_BOUNDED_SOURCE"

    required = {
        "P0-1-RECOVERY-CONSOLE",
        "P0-2-TOKEN-ROTATION",
        "P0-3-RAILWAY-HEALTH",
        "P0-4-SHEETS-WEBHOOK",
        "P0-5-FRESH-WORKFLOW-DISPATCH",
        "P0-6-COBALT-HOST",
        "P0-7-VTI-HUB-FEDERATION",
        "LIVE-PROVIDER-PANEL",
        "AUTHENTICATED-COMMAND-CENTRE-STAGING",
        "MISSING-SOURCE-BYTES",
        "PRODUCTION-PROMOTION-AND-OWNER-ACCEPTANCE",
    }
    assert required.issubset(blocked)

    for item in data["still_blocked"]:
        assert item["class"]
        assert item["exact_action"]
        text = json.dumps(item).lower()
        assert "paste the token" not in text or "never paste the token" in text

    serialised = json.dumps(data).lower()
    forbidden = [
        '"program_state": "done"',
        '"program_state": "complete"',
        '"program_state": "production_ready"',
        'all blockers complete',
    ]
    for marker in forbidden:
        assert marker not in serialised

    print("blocker reconciliation v4 verified")


if __name__ == "__main__":
    main()
