from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def main() -> None:
    registry = json.loads((ROOT / "registry/integrations/read_only_database_inspector_v1.json").read_text())
    matrix = json.loads((ROOT / "registry/requirements/folder0_capability_traceability_v1.json").read_text())
    tracker = json.loads((ROOT / "registry/trackers/all_progress_tracker_reconciliation_v7.json").read_text())
    runtime = (ROOT / "src/jarvis_integrations/read_only_db_inspector_v1.py").read_text()
    tests = (ROOT / "tests/test_read_only_db_inspector_v1.py").read_text()
    require(registry["runtime_state"] == "IMPLEMENTED_NOT_INTEGRATED", "database inspector false integration")
    require(registry["policy_bounds"]["database_mutation_allowed"] is False, "mutation must remain disabled")
    require(registry["live_integration_gate"]["state"] == "BLOCKED", "live database gate weakened")
    item = next(entry for entry in matrix["capabilities"] if entry["candidate_id"] == "F0-CAP-006")
    require(item["runtime_state"] == "IMPLEMENTED_NOT_INTEGRATED", "F0-CAP-006 not reconciled")
    for artifact in item["artifacts"]:
        require((ROOT / artifact).exists(), f"missing database inspector artifact: {artifact}")
    require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "tracker false completion")
    require(len(tracker["still_blocked"]) == 11, "external blocker set drifted")
    for control in ("mode=ro", "query_only=ON", "only SELECT or WITH", "parameters not allowed"):
        require(control in runtime, f"missing read-only control: {control}")
    require(tests.count("    def test_") == 6, "expected six database inspector tests")
    combined = json.dumps(registry) + json.dumps(matrix) + json.dumps(tracker) + runtime + tests
    for forbidden in ("DATABASE_URL=", "POSTGRES_PASSWORD=", "SUPABASE_SERVICE_ROLE_KEY="):
        require(forbidden not in combined, f"possible credential assignment: {forbidden}")
    print(json.dumps({"status":"DONE_VERIFIED","scope":"LOCAL_READ_ONLY_DATABASE_INSPECTOR_V1","live_database_proven":False,"whole_program_complete":False}, indent=2))


if __name__ == "__main__":
    main()
