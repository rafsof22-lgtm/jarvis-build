from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    source = json.loads((ROOT / "registry/sources/folder0_partial_bounded_ingestion_v1.json").read_text())
    tracker = json.loads((ROOT / "registry/trackers/all_progress_tracker_reconciliation_v5.json").read_text())
    runtime = (ROOT / "jarvis_command_centre/integrated_v13.py").read_text()
    resolver = (ROOT / "jarvis_command_centre/progress_tracker.py").read_text()

    require(source["source_state"] == "EXTRACT_BOUNDED_NOT_DENOMINATOR_COMPLETE", "source truth boundary missing")
    require(source["sha256"] is None and source["sha256_unavailable_reason"], "unavailable hash must be explicit")
    require(source["extraction_coverage"]["denominator_complete"] is False, "false source denominator completion")
    require(len(source["quarantine"]) >= 5, "unsafe source assertions not quarantined")
    require(len(source["conflicts"]) >= 3, "source conflicts not preserved")
    require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "false program completion")
    require(len(tracker["still_blocked"]) == 11, "external blocker set drifted")
    require("read_latest_progress_tracker(legacy.REGISTRY)" in runtime, "Command Centre does not serve latest tracker")
    require("max(candidates" in resolver and "PENDING_TRACKER" in resolver, "latest tracker resolver incomplete")

    combined = json.dumps(source) + json.dumps(tracker) + runtime + resolver
    for forbidden in ("OPENAI_API_KEY=", "GITHUB_TOKEN=", "SUPABASE_SERVICE_ROLE_KEY=", "DATABASE_URL=postgres"):
        require(forbidden not in combined, f"possible secret assignment detected: {forbidden}")

    print(json.dumps({
        "status": "DONE_VERIFIED",
        "scope": "FOLDER0_BOUNDED_INGESTION_AND_LATEST_TRACKER_V5",
        "whole_program_complete": False
    }, indent=2))


if __name__ == "__main__":
    main()
