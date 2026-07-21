#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_asset_intelligence import AssetIntelligenceOrchestrator

ORCHESTRATOR = ROOT / "registry/intelligence/multi_asset_intelligence_orchestrator_v1.json"
XRP = ROOT / "registry/intelligence/assets/xrp_asset_intelligence_v1.json"
HBAR = ROOT / "registry/intelligence/assets/hbar_asset_intelligence_v1.json"
TEMPLATE = ROOT / "registry/intelligence/asset_profile_template_v1.json"
COMMAND = ROOT / "registry/command-centre/jarvis_omniscient_command_centre_v1.json"
EVIDENCE = ROOT / "evidence/multi-asset-intelligence-v1-verification.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    orchestrator_doc = load(ORCHESTRATOR)
    xrp = load(XRP)
    hbar = load(HBAR)
    template = load(TEMPLATE)
    command = load(COMMAND)

    require(orchestrator_doc["contract_id"] == "JARVIS-MULTI-ASSET-INTELLIGENCE-ORCHESTRATOR-V1", "unexpected orchestrator id")
    require(orchestrator_doc["state"] == "IMPLEMENTED_NOT_INTEGRATED", "must not claim live integration")
    require(orchestrator_doc["source_budget_policy"]["apex"]["maximum"] == 100, "apex run maximum must be 100 sources per asset")
    require(orchestrator_doc["source_budget_policy"]["source_ceiling_is_per_run_not_lifetime"] is True, "source registry must keep expanding")
    require(orchestrator_doc["trigger_execution"]["ALL_INTELLIGENCE"]["includes_update"] is True, "all intelligence must include update")
    require(orchestrator_doc["trigger_execution"]["ALL_INTELLIGENCE"]["includes_deep_scan"] is True, "all intelligence must include deep scan")
    require(orchestrator_doc["trigger_execution"]["ALL_INTELLIGENCE"]["run_independent_asset_workstreams_in_parallel"] is True, "all intelligence must fan out in parallel")
    require(orchestrator_doc["trigger_execution"]["ALL_INTELLIGENCE"]["preserve_asset_separation"] is True, "asset separation must be preserved")
    require(orchestrator_doc["execution_boundary"]["no_trade_execution"] is True, "trade execution must remain disabled")

    require(xrp["primary_asset"] == "XRP" and hbar["primary_asset"] == "HBAR", "asset profiles are not separated")
    require(max(xrp["fixed_milestones"]) >= 10000, "XRP milestones must reach at least 10,000")
    require(xrp["dynamic_milestones"]["extend_above"] >= 10000, "XRP dynamic milestones must extend above 10,000")
    require(max(hbar["fixed_milestones"]) >= 100, "HBAR milestones must reach at least 100")
    require(hbar["dynamic_milestones"]["extend_above"] >= 100, "HBAR dynamic milestones must extend above 100")
    require(xrp["separation_rule"] != hbar["separation_rule"], "asset-specific value-capture rules must differ")
    require(len(xrp["xrp_specific_intelligence_layers"]) >= 15, "XRP intelligence layers incomplete")
    require(len(hbar["hbar_specific_intelligence_layers"]) >= 15, "HBAR intelligence layers incomplete")
    require(xrp["source_budget"]["source_registry_lifetime_limit"] is None, "XRP source registry must be unbounded over time")
    require(hbar["source_budget"]["source_registry_lifetime_limit"] is None, "HBAR source registry must be unbounded over time")

    extensions = template["class_specific_extensions"]
    require("crypto" in extensions and "stock" in extensions and "etf" in extensions, "future asset template lacks crypto/stock/ETF support")
    require(template["common_controls"]["maximum_meaningful_sources_per_apex_run"] == 100, "template source budget mismatch")
    require(template["common_controls"]["unique_asset_assumptions_required"] is True, "unique asset analysis must be required")

    require(command["global_jarvis_presence"]["available_on_every_page"] is True, "Jarvis popup must be global")
    require(command["global_jarvis_presence"]["voice_never_bypasses_approval"] is True, "voice must not bypass approvals")
    require(command["guided_user_experience"]["frequent_actions_target_clicks"] <= 3, "frequent actions exceed novice click target")
    require(command["asset_intelligence_experience"]["XRP_and_HBAR_never_silently_merged"] is True, "command centre must preserve asset separation")
    require("mobile_web" in command["surfaces"] and "installable_PWA" in command["surfaces"], "mobile/PWA surfaces missing")
    require(command["action_truth_contract"]["financial_actions_require_separate_non_voice_approval"] is True, "financial voice gate missing")

    runtime = AssetIntelligenceOrchestrator()
    require(runtime.active_assets() == ("HBAR", "XRP"), "active profile discovery mismatch")
    update_plan = runtime.build_plan("Update XRP")
    all_plan = runtime.build_plan("Jarvis all intelligence gathering for all assets")
    deep_plan = runtime.build_plan("Deep scan HBAR to one hundred and above")

    require(update_plan.trigger == "UPDATE" and update_plan.requested_assets == ("XRP",), "XRP update routing failed")
    require(deep_plan.trigger == "DEEP_SCAN" and deep_plan.requested_assets == ("HBAR",), "HBAR deep-scan routing failed")
    require(all_plan.trigger == "ALL_INTELLIGENCE", "all-intelligence trigger failed")
    require(all_plan.requested_assets == ("HBAR", "XRP"), "all-intelligence asset fan-out failed")
    require(all_plan.simultaneous is True, "all-intelligence plan must be simultaneous")
    require(all_plan.maximum_sources_per_asset == 100, "all-intelligence source maximum mismatch")
    require(all(task.dynamic_ceiling_enabled for task in all_plan.tasks), "dynamic ceiling must be enabled for every active asset")
    require(all("PLAN_ONLY" in all_plan.truth_boundary for _ in [0]), "planner truth boundary missing")

    report = {
        "verification_id": "JARVIS-MULTI-ASSET-INTELLIGENCE-V1",
        "status": "PASSED",
        "active_assets": list(runtime.active_assets()),
        "XRP_max_fixed_milestone": max(xrp["fixed_milestones"]),
        "HBAR_max_fixed_milestone": max(hbar["fixed_milestones"]),
        "all_intelligence_sources_per_asset_maximum": all_plan.maximum_sources_per_asset,
        "all_intelligence_tasks": [task.asset for task in all_plan.tasks],
        "voice_or_external_actions_executed": False,
        "web_sources_retrieved_by_this_verifier": False,
        "financial_execution": False,
        "proof_boundary": "Repository contracts and deterministic plan routing only. Current intelligence gathering, live data, speech runtime and production UI remain separate integration and evidence gates.",
        "rollback": "Revert the multi-asset intelligence and command-centre pull request."
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
