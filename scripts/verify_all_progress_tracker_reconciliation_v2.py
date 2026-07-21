from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS_REGISTRY = ROOT / "registry" / "jarvis_completion_pass_registry_v2.json"
RUNTIME_REGISTRY = ROOT / "registry" / "jarvis_unblocked_completion_runtime_v1.json"
RECONCILIATION = ROOT / "registry" / "trackers" / "all_progress_tracker_reconciliation_v2.json"

ALLOWED = {
    "PENDING_INGEST", "SPEC_ONLY", "BACKLOGGED", "SCAFFOLDED",
    "IMPLEMENTED_NOT_INTEGRATED", "INTEGRATED_STAGING",
    "DEPLOYED_UNVERIFIED", "DONE_VERIFIED", "WAIVED", "BLOCKED",
}


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    passes = load(PASS_REGISTRY)
    runtime = load(RUNTIME_REGISTRY)
    reconciliation = load(RECONCILIATION)

    assert passes["baseline_main_sha"] == runtime["merge_sha"]
    assert reconciliation["baseline_main_sha"] == runtime["merge_sha"]
    assert runtime["status"] == "DONE_VERIFIED"
    assert runtime["tests"]["result"] == "DONE_VERIFIED"
    assert runtime["tests"]["cases"] == 11
    assert runtime["tests"]["workflow_count"] == 7

    pass_rows = {row["pass_id"]: row for row in passes["passes"]}
    assert set(pass_rows) == set(range(1, 13))
    for pass_id in (1, 2, 3, 4, 5, 7):
        assert pass_rows[pass_id]["state"] == "DONE_VERIFIED"
        assert pass_rows[pass_id].get("completion_scope")
    for pass_id in (8, 10, 11):
        assert pass_rows[pass_id]["state"] == "BLOCKED"
        assert pass_rows[pass_id].get("blocker")

    phase_rows = runtime["phase_status"]
    assert len(phase_rows) == 17
    for row in phase_rows:
        assert row["status"] in ALLOWED
        assert row["proof"]

    corrections = reconciliation["task_state_corrections"]
    ids = [row["task_id"] for row in corrections]
    assert len(ids) == len(set(ids))
    expected = {"P1-6", "P2-5", "P2-6", "P3-2", "P3-3", "P3-4", "P3-5", "P3-6", "P2-3"}
    assert set(ids) == expected
    for row in corrections:
        assert row["current"] in ALLOWED
        assert row["scope"]

    now_work = reconciliation["additional_work_fully_executable_now"]
    assert len(now_work) >= 7
    assert all(row["deliverables"] and row["target_state"] for row in now_work)
    assert reconciliation["hard_blocks"]
    assert "Whole-program 100 percent remains impossible" in reconciliation["truth_boundary"]

    print(json.dumps({
        "verified": True,
        "baseline_main_sha": runtime["merge_sha"],
        "done_passes": [pid for pid, row in pass_rows.items() if row["state"] == "DONE_VERIFIED"],
        "task_corrections": len(corrections),
        "next_executable_work_items": len(now_work),
        "whole_program_state": passes["state"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
