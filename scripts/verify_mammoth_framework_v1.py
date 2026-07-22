#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK = ROOT / "docs/spec/JARVIS_MAMMOTH_CONSOLIDATED_FRAMEWORK_V1.md"
PLAN = ROOT / "registry/plans/jarvis_full_completion_execution_plan_v1.json"
BLOCKERS = ROOT / "registry/gaps/jarvis_blocker_resolution_register_v1.json"
TRACKER = ROOT / "registry/trackers/all_progress_tracker_reconciliation_v18.json"
CONTINUITY = ROOT / "PROJECT_CONTINUITY.md"

REQUIRED_FRAMEWORK_HEADINGS = [
    "## 1. Executive objective",
    "## 2. Scope and boundaries",
    "## 3. Source universe and denominator",
    "## 4. Requirement extraction and traceability",
    "## 5. Stakeholders and authority",
    "## 6. Governance and policies",
    "## 7. System architecture",
    "## 8. Module registry",
    "## 9. Agent hierarchy",
    "## 10. Skill routing",
    "## 11. Tools, APIs and integrations",
    "## 12. Data architecture",
    "## 13. Memory architecture",
    "## 14. Knowledge ingestion",
    "## 15. Intelligence gathering",
    "## 16. Model routing",
    "## 17. Workflow engine",
    "## 18. Security and identity",
    "## 19. Human approval gates",
    "## 20. Command Centre UX",
    "## 21. SOP and OJT",
    "## 22. Testing",
    "## 23. Observability and operations",
    "## 24. Deployment architecture",
    "## 25. Reliability and continuity",
    "## 26. Cost model",
    "## 27. Implementation roadmap",
    "## 28. Release and maintenance",
    "## 29. Evidence matrix",
    "## 30. Open loops and exact blockers",
]

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


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    checks: dict[str, bool] = {}
    required = [FRAMEWORK, PLAN, BLOCKERS, TRACKER, CONTINUITY]
    checks["required_files"] = all(path.is_file() for path in required)

    framework = FRAMEWORK.read_text(encoding="utf-8")
    plan = load(PLAN)
    blockers = load(BLOCKERS)
    tracker = load(TRACKER)
    continuity = CONTINUITY.read_text(encoding="utf-8")

    checks["thirty_framework_sections"] = all(heading in framework for heading in REQUIRED_FRAMEWORK_HEADINGS)
    checks["completion_chain"] = "Source -> Request -> Requirement -> Module -> Artifact -> Test/Waiver -> Evidence -> Runtime State -> Rollback -> Owner Acceptance" in framework
    checks["truth_boundary"] = "not a claim that inaccessible chats, external staging or production are complete" in framework
    checks["xrp_source_contract"] = "50-100-source target" in framework
    checks["five_repo_scope"] = all(name in framework for name in ["jarvis-build", "hub", "videotranscribe", "Jarvis-Health", "property-agent-mcp"])

    phase_ids = [phase["phase_id"] for phase in plan.get("phases", [])]
    checks["eight_phases"] = len(phase_ids) == 8 and len(phase_ids) == len(set(phase_ids))
    checks["phase_order_matches"] = phase_ids == plan.get("phase_order")
    checks["program_open_truthfully"] = plan.get("program_state") == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    checks["status_vocabulary"] = set(plan.get("status_vocabulary", [])) == ALLOWED_STATES
    tasks = [task for phase in plan.get("phases", []) for task in phase.get("tasks", [])]
    checks["sufficient_task_depth"] = len(tasks) >= 35
    checks["task_ids_unique"] = len({task["task_id"] for task in tasks}) == len(tasks)
    checks["all_task_states_allowed"] = all(task.get("state") in ALLOWED_STATES for task in tasks)
    checks["all_phases_have_exit_criteria"] = all(phase.get("exit_criteria") for phase in plan.get("phases", []))

    blocker_rows = blockers.get("blockers", [])
    blocker_ids = {row["blocker_id"] for row in blocker_rows}
    referenced_blockers = {task["blocker_id"] for task in tasks if "blocker_id" in task}
    checks["blocker_depth"] = len(blocker_rows) >= 18
    checks["blocker_ids_unique"] = len(blocker_ids) == len(blocker_rows)
    checks["all_referenced_blockers_exist"] = referenced_blockers.issubset(blocker_ids)
    checks["blockers_have_unblock_and_proof"] = all(
        row.get("exact_unblock_input") and row.get("proof_required") and row.get("owner")
        for row in blocker_rows
    )
    checks["production_blocked"] = "BLK-PROD-001" in blocker_ids

    checks["tracker_stays_open"] = tracker.get("program_state") == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    checks["continuity_stays_open"] = "ACTIVE_PROGRAM_NOT_100_PERCENT" in continuity
    checks["continuity_has_v16_v17_v18"] = all(
        f"all_progress_tracker_reconciliation_v{version}.json" in continuity for version in (16, 17, 18)
    )

    report = {
        "verification_id": "JARVIS-MAMMOTH-FRAMEWORK-V1-VERIFY",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "phase_count": len(phase_ids),
        "task_count": len(tasks),
        "blocker_count": len(blocker_rows),
        "files": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in required
        },
        "runtime_state": "REPOSITORY_SPEC_AND_GOVERNANCE_ONLY",
        "truth_boundary": "This verifies framework structure, plan integrity, blocker routing and continuity truth. It does not prove inaccessible source ingestion, external staging or production."
    }

    destination = ROOT / "evidence/jarvis-mammoth-framework-v1-verification.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
