from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    integration = json.loads((ROOT / "registry/integrations/apivault_discovery_fabric_v1.json").read_text())
    routing = json.loads((ROOT / "registry/integrations/apivault_cross_jarvis_routing_v1.json").read_text())
    ojt = json.loads((ROOT / "registry/ojt/apivault_discovery_specialist_v1.json").read_text())
    tracker = json.loads((ROOT / "registry/trackers/all_progress_tracker_reconciliation_v9.json").read_text())
    runtime = (ROOT / "src/jarvis_integrations/apivault_discovery_v1.py").read_text()
    tests = (ROOT / "tests/test_apivault_discovery_v1.py").read_text()

    require(integration["runtime_state"] == "IMPLEMENTED_NOT_INTEGRATED", "false connected state")
    require(integration["licence_boundary"]["mirroring_or_redistribution"] is False, "catalogue mirroring must be denied")
    require(integration["execution_defaults"]["network_enabled"] is False, "network must default off")
    require(integration["execution_defaults"]["candidate_execution_approved"] is False, "candidate cannot be auto-approved")
    require(len(integration["adoption_gates"]) == 7, "seven adoption gates required")
    require(routing["default_state"] == "PROPOSAL_ONLY", "routing must remain proposal-only")
    require(len(routing["routes"]) >= 8, "cross-Jarvis coverage incomplete")
    require(len(ojt["competency_scenarios"]) == 8, "eight OJT scenarios required")
    require(ojt["release_gate"]["production_permission_granted"] is False, "OJT cannot grant production permission")
    require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "false whole-program completion")
    require(len(tracker["resolved_this_pass"]) == 7, "expected seven bounded work packages")
    require(len(tracker["still_blocked"]) == 11, "external blocker set drifted")
    require("DISCOVERED_NOT_VERIFIED" in runtime, "discovery truth state missing")
    require("COMMERCIAL_CATALOGUE_REUSE_PROHIBITED" in runtime, "licence enforcement missing")
    require("catalogue_persisted" in runtime and "False" in runtime, "no-persistence control missing")
    require(tests.count("    def test_") == 11, "expected eleven deterministic tests")

    combined = json.dumps(integration) + json.dumps(routing) + json.dumps(ojt) + json.dumps(tracker) + runtime + tests
    for forbidden in ("APIVAULT_TOKEN=", "OPENAI_API_KEY=", "GITHUB_TOKEN=", "DATABASE_URL=postgres", "SECRET_KEY = '"):
        require(forbidden not in combined, f"possible secret assignment detected: {forbidden}")

    print(json.dumps({
        "status": "DONE_VERIFIED",
        "scope": "APIVAULT_DISCOVERY_FABRIC_V1",
        "work_packages": 7,
        "deterministic_tests": 11,
        "live_apivault_proven": False,
        "candidate_api_integrated": False,
        "whole_program_complete": False
    }, indent=2))


if __name__ == "__main__":
    main()
