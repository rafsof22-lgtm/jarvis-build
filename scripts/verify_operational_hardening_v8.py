from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    tracker = json.loads((ROOT / "registry/trackers/all_progress_tracker_reconciliation_v8.json").read_text())
    competency = json.loads((ROOT / "registry/ojt/command_centre_knowledge_fabric_competency_v1.json").read_text())
    controls = (ROOT / "jarvis_command_centre/operational_controls_v1.py").read_text()
    lifecycle = (ROOT / "jarvis_command_centre/alert_lifecycle_v1.py").read_text()
    benchmark = (ROOT / "src/jarvis_knowledge_fabric_benchmark_v2.py").read_text()
    tests = (ROOT / "tests/test_operational_hardening_v8.py").read_text()

    require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "false whole-program completion")
    require(len(tracker["resolved_this_pass"]) == 5, "expected five bounded work packages")
    require(len(tracker["still_blocked"]) == 11, "external blocker set drifted")
    for item in tracker["resolved_this_pass"]:
        require(item["state"] in {"IMPLEMENTED_NOT_INTEGRATED", "DONE_VERIFIED"}, "invalid bounded state")
        for path in item["evidence"]:
            require((ROOT / path).exists(), f"missing evidence path: {path}")

    require(competency["runtime_state"] == "IMPLEMENTED_NOT_INTEGRATED", "competency truth boundary weakened")
    require(competency["release_gate"]["production_permission_granted"] is False, "OJT cannot grant production permission")
    require(sum(len(role["competency_scenarios"]) for role in competency["roles"]) == 8, "expected eight competency scenarios")

    require('"authoritative_balances_inferred": False' in controls, "no-inference result flag missing")
    require("balance_status" in controls and "last_verified_at" in controls, "authoritative evidence checks missing")
    require("PROPOSAL_ONLY" in controls, "proposal-only remediation missing")
    require("resolution evidence is required" in lifecycle, "evidence-backed alert resolution missing")
    require("alert_suppressions" in lifecycle and "expires_at" in lifecycle, "suppression lifecycle missing")
    require("permission IN ('public',?)" in benchmark, "permission filter missing")
    require("duplicate_of IS NULL" in benchmark, "duplicate suppression missing")
    require("contradiction_pairs" in benchmark, "contradiction retrieval missing")
    require("NOT_CONNECTED" in benchmark and "NOT_EXECUTED_DEPENDENCY_NOT_SELECTED" in benchmark, "unconnected backend truth boundary missing")
    require(tests.count("    def test_") == 16, "expected sixteen deterministic tests")

    combined = json.dumps(tracker) + json.dumps(competency) + controls + lifecycle + benchmark + tests
    for forbidden in ("OPENAI_API_KEY=", "GITHUB_TOKEN=", "SUPABASE_SERVICE_ROLE_KEY=", "DATABASE_URL=postgres", "VERCEL_TOKEN="):
        require(forbidden not in combined, f"possible secret assignment detected: {forbidden}")

    print(json.dumps({
        "status": "DONE_VERIFIED",
        "scope": "OPERATIONAL_HARDENING_AND_KNOWLEDGE_BENCHMARK_V8",
        "work_packages": 5,
        "deterministic_tests": 16,
        "connected_provider_balances_proven": False,
        "whole_program_complete": False
    }, indent=2))


if __name__ == "__main__":
    main()
