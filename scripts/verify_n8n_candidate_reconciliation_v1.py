from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    integration = json.loads((ROOT / "registry/integrations/n8n_adapter_v1.json").read_text())
    matrix = json.loads((ROOT / "registry/requirements/folder0_capability_traceability_v1.json").read_text())
    tracker = json.loads((ROOT / "registry/trackers/all_progress_tracker_reconciliation_v6.json").read_text())
    runtime = (ROOT / "src/jarvis_integrations/n8n_adapter_v1.py").read_text()
    tests = (ROOT / "tests/test_n8n_adapter_v1.py").read_text()

    require(integration["runtime_state"] == "IMPLEMENTED_NOT_INTEGRATED", "n8n integration truth boundary weakened")
    require(integration["execution_defaults"]["enabled"] is False, "n8n execution must default off")
    require(integration["live_integration_gate"]["state"] == "BLOCKED", "connected n8n gate must remain blocked")
    require(matrix["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "matrix false completion")
    require(len(matrix["capabilities"]) == 6, "all six folder0 candidates must be dispositioned")
    require({item["candidate_id"] for item in matrix["capabilities"]} == {f"F0-CAP-{index:03d}" for index in range(1, 7)}, "candidate set drifted")
    db_item = next(item for item in matrix["capabilities"] if item["candidate_id"] == "F0-CAP-006")
    require(db_item["runtime_state"] in {"BACKLOGGED", "IMPLEMENTED_NOT_INTEGRATED"}, "database inspector state invalid")
    if db_item["runtime_state"] == "IMPLEMENTED_NOT_INTEGRATED":
        require(len(db_item["artifacts"]) >= 3, "implemented database inspector lacks evidence")
    for item in matrix["capabilities"]:
        for artifact in item["artifacts"]:
            require((ROOT / artifact).exists(), f"missing traceability artifact: {artifact}")
    require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "tracker false completion")
    require(len(tracker["still_blocked"]) == 11, "external blocker set drifted")
    require("execution_enabled: bool = False" in runtime, "runtime default-off control missing")
    for control in ("WORKFLOW_NOT_ALLOWLISTED", "DATA_CLASSIFICATION_NOT_ALLOWED", "REPLAY_REJECTED", "X-Jarvis-Signature"):
        require(control in runtime, f"missing runtime control: {control}")
    require(tests.count("    def test_") == 6, "expected six deterministic n8n tests")

    combined = json.dumps(integration) + json.dumps(matrix) + json.dumps(tracker) + runtime + tests
    for forbidden in ("OPENAI_API_KEY=", "GITHUB_TOKEN=", "SUPABASE_SERVICE_ROLE_KEY=", "N8N_API_KEY="):
        require(forbidden not in combined, f"possible secret assignment detected: {forbidden}")

    print(json.dumps({
        "status": "DONE_VERIFIED",
        "scope": "FOLDER0_CAPABILITY_TRACEABILITY_AND_LOCAL_N8N_ADAPTER_V1",
        "connected_n8n_proven": False,
        "whole_program_complete": False
    }, indent=2))


if __name__ == "__main__":
    main()
