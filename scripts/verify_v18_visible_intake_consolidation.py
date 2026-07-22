#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    ROOT / "JARVIS_RAF213G_PROJECT_CONSTITUTION.md",
    ROOT / "PROJECT_CONTINUITY.md",
    ROOT / "registry/source-accounting/v18_chat_and_request_intake_20260722.json",
    ROOT / "registry/trackers/all_progress_tracker_reconciliation_v18.json",
    ROOT / "docs/trackers/JARVIS_MASTER_VISUAL_PROGRESS_TALLY_V18.md",
]


def main() -> None:
    checks: dict[str, bool] = {}
    checks["required_files"] = all(path.is_file() for path in REQUIRED)

    constitution = REQUIRED[0].read_text(encoding="utf-8")
    continuity = REQUIRED[1].read_text(encoding="utf-8")
    intake = json.loads(REQUIRED[2].read_text(encoding="utf-8"))
    tracker = json.loads(REQUIRED[3].read_text(encoding="utf-8"))
    visual = REQUIRED[4].read_text(encoding="utf-8")

    checks["constitution_version"] = "**Version:** 1.1.0" in constitution
    checks["automatic_intake"] = "## Automatic Jarvis relevance intake" in constitution
    checks["chronology_law"] = "## Chronology and consolidation law" in constitution
    checks["no_destructive_dedupe"] = "Do not delete repositories, branches, files, issues, PR history" in constitution
    checks["staging_gate"] = "## External staging and production gate" in constitution

    checks["eight_share_links"] = len(intake.get("share_links", [])) == 8
    checks["share_links_blocked_truthfully"] = intake.get("share_link_state", {}).get("state") == "BLOCKED_BY_ACCESS"
    checks["five_repositories"] = len(intake.get("connected_github_repositories", [])) == 5
    checks["zero_open_pr_snapshot"] = intake.get("github_pr_snapshot", {}).get("open_pull_requests_across_connected_repositories") == 0

    denominators = intake.get("direct_project_denominators", {})
    checks["xrp_denominator"] = denominators.get("XRP Tracking New", {}).get("conversations") == 83
    checks["longevity_denominator"] = denominators.get("Longevity Plan", {}).get("conversations") == 6
    checks["tax_trust_separate"] = "Tax" in denominators and "Active Trust" in denominators
    checks["finance_projects_separate"] = "Finance Planning" in denominators and "Financial New" in denominators

    checks["tracker_version"] = tracker.get("version") == "18.0.0"
    checks["truthful_program_state"] = tracker.get("program_state") == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    checks["priority_rows"] = len(tracker.get("priority_tally", [])) >= 15
    checks["all_rows_have_fields"] = all(
        {"priority", "workstream", "progress_percent", "state", "proven", "gap", "next_action"}.issubset(row)
        for row in tracker.get("priority_tally", [])
    )
    checks["percent_ranges"] = all(0 <= row.get("progress_percent", -1) <= 100 for row in tracker.get("priority_tally", []))
    truth_boundary = tracker.get("truth_boundary", "")
    checks["xrp_source_target_truth"] = "50-100-source" in truth_boundary and "live XRP/HBAR run" in truth_boundary
    checks["production_not_authorised"] = any(
        row.get("state") == "NOT_AUTHORISED" for row in tracker.get("priority_tally", [])
    )

    checks["visual_has_all_projects"] = all(
        name in visual for name in [
            "XRP Tracking New", "Longevity Plan", "Tax", "Active Trust", "Finance Planning", "Financial New"
        ]
    )
    checks["visual_has_xrp_contract"] = "## XRP/HBAR update-engine acceptance contract" in visual
    checks["visual_has_exact_blockers"] = "## Exact blocker queue" in visual
    checks["continuity_points_to_v18"] = "all_progress_tracker_reconciliation_v18.json" in continuity
    checks["continuity_preserves_v16_v17_lineage"] = all(
        name in continuity for name in [
            "all_progress_tracker_reconciliation_v16.json",
            "all_progress_tracker_reconciliation_v17.json",
        ]
    )
    checks["continuity_access_boundary"] = "BLOCKED_BY_ACCESS" in continuity
    checks["legacy_verifier_language_preserved"] = all(
        phrase in continuity for phrase in ["Four images remain without OCR", "three opaque archives"]
    )

    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "runtime_state": "REPOSITORY_GOVERNANCE_ONLY",
        "external_actions": "NOT_ATTEMPTED",
        "truth_boundary": "This verifier proves V18 repository artifacts and internal consistency only. It does not prove inaccessible chat extraction, live source refresh, external staging or production."
    }

    output = ROOT / "evidence/v18-visible-intake-consolidation-verification.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
