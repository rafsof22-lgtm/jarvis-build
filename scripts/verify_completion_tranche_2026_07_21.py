#!/usr/bin/env python3
"""Verify the 2026-07-21 Jarvis completion tranche without network access."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION = ROOT / "JARVIS_RAF213G_PROJECT_CONSTITUTION.md"
MODULE = ROOT / "docs/module-instructions/master-source-universe-controller.md"
DECISION = ROOT / "registry/decisions/constitution_recovery_resolution_v1.json"
INTAKE = ROOT / "registry/repository-intake/screenshot_repo_intake_2026_07_21.json"
TRACKER = ROOT / "registry/trackers/all_accessible_tracker_consolidation_v1.json"
COUNCIL = ROOT / "registry/integrations/council_mode_contract_v1.json"
OBSERVER = ROOT / "registry/integrations/local_observer_sensor_policy_v1.json"
PREDICTION = ROOT / "registry/integrations/prediction_market_read_only_contract_v1.json"
EVIDENCE = ROOT / "evidence/completion-tranche-2026-07-21-verification.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    checks: dict[str, bool] = {}

    constitution_text = CONSTITUTION.read_text(encoding="utf-8")
    module_text = MODULE.read_text(encoding="utf-8")
    decision = load_json(DECISION)
    intake = load_json(INTAKE)
    tracker = load_json(TRACKER)
    council = load_json(COUNCIL)
    observer = load_json(OBSERVER)
    prediction = load_json(PREDICTION)

    checks["canonical_constitution_present"] = CONSTITUTION.exists()
    checks["completion_chain_present"] = "Requirement -> Module -> Artifact -> Test or waiver -> Evidence -> Runtime state -> Rollback -> Owner acceptance" in constitution_text
    checks["module_title_correct"] = module_text.startswith("# MODULE INSTRUCTIONS — Master Source Universe Controller")
    checks["module_simple_english_contract"] = "Name - plain meaning - Example:" in module_text
    checks["decision_points_to_exact_path"] = decision.get("canonical_source", {}).get("repository") == "rafsof22-lgtm/jarvis-build" and decision.get("canonical_source", {}).get("path") == "JARVIS_RAF213G_PROJECT_CONSTITUTION.md"
    checks["decision_preserves_historical_candidate"] = "historical recovery evidence" in decision.get("historical_candidate_policy", "")

    records = intake.get("records", [])
    checks["six_screenshot_records"] = len(records) == 6
    checks["all_candidates_disable_auto_install"] = intake.get("default_policy", {}).get("auto_install") is False
    checks["all_candidates_disable_auto_execute"] = intake.get("default_policy", {}).get("auto_execute") is False
    checks["observer_high_privilege_disabled"] = any(r.get("candidate_id") == "REPO-ROY3838-OBSERVER" and r.get("safety_defaults", {}).get("enabled") is False for r in records)
    checks["polymarket_write_blocked"] = any(r.get("candidate_id") == "TOOL-POLYMARKET-PUBLIC-DATA" and r.get("safety_defaults", {}).get("order_placement") is False and r.get("safety_defaults", {}).get("wallet_private_key") is False for r in records)
    checks["hacking_bundle_blocked"] = any(r.get("candidate_id") == "REPO-Z4NZU-HACKINGTOOL" and r.get("safety_defaults", {}).get("install_bundle") is False and r.get("safety_defaults", {}).get("external_targeting") is False for r in records)
    checks["dark_web_auto_access_blocked"] = any(r.get("candidate_id") == "INDEX-DARK-WEB-OSINT-GRAPHIC" and r.get("safety_defaults", {}).get("automatic_onion_access") is False for r in records)

    families = tracker.get("tracker_families", [])
    checks["nine_tracker_families"] = len(families) == 9
    checks["hidden_chat_scope_excluded"] = "Hidden or unsynchronised chats are excluded" in tracker.get("scope", "")
    checks["program_not_claimed_complete"] = tracker.get("current_program_state") == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    checks["external_gates_preserved"] = len(tracker.get("external_or_owner_gates", [])) >= 8
    checks["financial_execution_shortcut_prohibited"] = "No live financial execution." in tracker.get("prohibited_status_shortcuts", [])
    checks["clinical_device_shortcut_prohibited"] = "No clinical or wellness device control." in tracker.get("prohibited_status_shortcuts", [])

    checks["council_disabled_by_default"] = council.get("defaults", {}).get("enabled") is False
    checks["council_model_limit"] = council.get("defaults", {}).get("maximum_models") == 8
    checks["council_budget_gate"] = council.get("defaults", {}).get("budget_preflight_required") is True
    observer_permissions = observer.get("default_permissions", {})
    checks["observer_all_sensitive_permissions_off"] = all(value is False for value in observer_permissions.values())
    checks["observer_separate_service_boundary"] = "Separately deployed local service" in observer.get("architecture", "")
    blocked_prediction = set(prediction.get("blocked_operations", []))
    checks["prediction_market_write_surface_blocked"] = {"create_order", "sign_transaction", "connect_wallet", "read_or_store_private_key", "deposit", "withdraw"}.issubset(blocked_prediction)
    checks["prediction_market_evidence_warning"] = any("not verified fact" in rule for rule in prediction.get("evidence_rules", []))

    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "id": "EVIDENCE-COMPLETION-TRANCHE-2026-07-21",
        "status": status,
        "checks": checks,
        "proof_scope": "Repository governance, tracker consolidation, external-candidate intake and disabled-by-default integration contracts only.",
        "runtime_state": "NOT_TESTED_BY_THIS_VERIFIER",
        "production_state": "NOT_DEPLOYED_BY_THIS_TRANCHE",
        "financial_execution": "DISABLED",
        "clinical_device_control": "DISABLED",
        "rollback": "Revert this tranche commit or pull request; Git history preserves all prior states."
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
