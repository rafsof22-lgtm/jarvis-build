#!/usr/bin/env python3
"""Verify evidence-backed Jarvis completion tracker and continuity reconciliation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "registry" / "full_completion_priority_plan_v1.json"
CONTINUITY = ROOT / "PROJECT_CONTINUITY.md"
EVIDENCE = ROOT / "evidence" / "progress-reconciliation-v2-verification.json"

ALLOWED_STATES = {
    "PENDING_INGEST",
    "SPEC_ONLY",
    "BACKLOGGED",
    "SCAFFOLDED",
    "IMPLEMENTED_NOT_INTEGRATED",
    "INTEGRATED_STAGING",
    "DEPLOYED_UNVERIFIED",
    "DONE_VERIFIED",
    "WAIVED",
    "BLOCKED",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    tracker = json.loads(TRACKER.read_text(encoding="utf-8"))
    continuity = CONTINUITY.read_text(encoding="utf-8")
    tasks = tracker.get("tasks")

    require(tracker.get("version") == "1.1.0", "tracker version must be 1.1.0")
    require(tracker.get("state") == "ACTIVE_PROGRAM_NOT_100_PERCENT", "program must not claim total completion")
    require(tracker.get("refresh_required_before_execution") is False, "tracker should be reconciled")
    require(isinstance(tasks, list) and len(tasks) >= 28, "expected complete P0-P6 task queue")

    ids = [task.get("task_id") for task in tasks]
    require(len(ids) == len(set(ids)), "duplicate task_id")
    require(all(task.get("state") in ALLOWED_STATES for task in tasks), "invalid runtime status vocabulary")

    by_id = {task["task_id"]: task for task in tasks}
    require(by_id["P2-3"]["state"] == "DONE_VERIFIED", "bounded XRP/HBAR batch 002 must be reconciled")
    require(by_id["P2-3"].get("completion_scope") == "BOUNDED_BATCH_002_ONLY", "bounded completion scope missing")
    require(by_id["P2-4"]["state"] == "IMPLEMENTED_NOT_INTEGRATED", "Health must retain open claim/runtime work")
    require(by_id["P1-3"]["state"] == "IMPLEMENTED_NOT_INTEGRATED", "Hub intake repository implementation not reconciled")
    require(by_id["P0-3"]["state"] == "BLOCKED", "Health live runtime must remain externally blocked")
    require(by_id["P5-1"]["state"] == "BLOCKED", "production promotion must remain approval-gated")

    require("ACTIVE_PROGRAM_NOT_100_PERCENT" in continuity, "continuity completion boundary missing")
    require("Visible Health handover denominator v2" in continuity, "Health denominator completion missing")
    require("Runtime auto-resume controller" in continuity, "runtime auto-resume completion missing")
    require("Four images remain without OCR" in continuity, "Health image gap missing")
    require("three opaque archives" in continuity, "Health opaque-archive gap missing")
    require("END_TO_END_VERIFIED" in continuity, "final completion declaration gate missing")

    done = [task["task_id"] for task in tasks if task["state"] == "DONE_VERIFIED"]
    blocked = [task["task_id"] for task in tasks if task["state"] == "BLOCKED"]
    report = {
        "verification_id": "JARVIS-PROGRESS-RECONCILIATION-V2",
        "status": "PASSED",
        "tracker_version": tracker["version"],
        "task_count": len(tasks),
        "done_verified_task_ids": done,
        "blocked_task_ids": blocked,
        "program_state": tracker["state"],
        "values_exposed": False,
        "proof_boundary": "Validates tracker/continuity consistency and bounded repository evidence only; it does not prove live providers or whole-program completion.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
