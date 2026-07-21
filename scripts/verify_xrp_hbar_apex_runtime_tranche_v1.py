#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jarvis_asset_intelligence.adapters import build_official_adapter_manifest
from jarvis_command_centre.auth import authenticate_bearer, authentication_contract
from jarvis_voice_gateway.local_runtime import build_local_speech_plan

FRAMEWORK = ROOT / "registry/asset-intelligence/xrp_hbar_apex_agent_framework_v1.json"
RUN = ROOT / "registry/asset-intelligence/runs/xrp_hbar_all_intelligence_20260721.json"
EVIDENCE = ROOT / "evidence/xrp-hbar-apex-runtime-tranche-v1-verification.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    framework = json.loads(FRAMEWORK.read_text(encoding="utf-8"))
    run = json.loads(RUN.read_text(encoding="utf-8"))
    adapters = build_official_adapter_manifest()
    speech = build_local_speech_plan()
    auth_contract = authentication_contract()

    require(framework["framework_id"] == "JARVIS-XRP-HBAR-APEX-AGENT-FRAMEWORK-V1", "framework id mismatch")
    require(framework["state"] == "IMPLEMENTED_NOT_INTEGRATED", "framework must not claim live integration")
    require(len(framework["shared_agents"]) >= 15, "agent council incomplete")
    require(framework["xrp_domain"]["namespace"] == "asset/XRP", "XRP namespace missing")
    require(framework["hbar_domain"]["namespace"] == "asset/HBAR", "HBAR namespace missing")
    require("all Jarvis modules" in framework["unified_inheritance"]["applies_to"], "unified inheritance incomplete")
    require("research-only and paper-first financial operation" in framework["unified_inheritance"]["rules"], "financial boundary missing")

    denominator = run["source_denominator"]
    require(denominator["processed"] + denominator["pending"] + denominator["inaccessible"] == denominator["inventoried"], "run denominator arithmetic invalid")
    require(denominator["inventoried"] == 12 and denominator["xrp"] == 6 and denominator["hbar"] == 6, "bounded current run scope changed")
    require(run["milestone_effect"]["XRP_10000"] == "NO_VERIFIED_UPLIFT_FROM_THIS_BOUNDED_RUN", "unsupported XRP uplift")
    require(run["milestone_effect"]["HBAR_100"] == "NO_VERIFIED_UPLIFT_FROM_THIS_BOUNDED_RUN", "unsupported HBAR uplift")
    require(run["knowledge_fabric"]["live_backend_write"] == "NOT_CONNECTED", "live Knowledge Fabric must not be claimed")

    require(len(adapters["adapters"]) >= 7, "official adapter coverage incomplete")
    require(adapters["network_calls_performed"] is False and adapters["writes_enabled"] is False, "adapter verifier must remain offline/read-only")
    require(all(plan["method"] == "GET" and plan["write_enabled"] is False for plan in adapters["request_plans"]), "unsafe source adapter plan")

    old = os.environ.get("JARVIS_COMMAND_CENTRE_BEARER_TOKEN")
    os.environ["JARVIS_COMMAND_CENTRE_BEARER_TOKEN"] = "offline-test-token"
    try:
        valid = authenticate_bearer("Bearer offline-test-token")
        invalid = authenticate_bearer("Bearer wrong-token")
        missing = authenticate_bearer(None)
    finally:
        if old is None:
            os.environ.pop("JARVIS_COMMAND_CENTRE_BEARER_TOKEN", None)
        else:
            os.environ["JARVIS_COMMAND_CENTRE_BEARER_TOKEN"] = old
    require(valid.authorised and not invalid.authorised and not missing.authorised, "authentication decisions invalid")
    require(not valid.token_value_exposed and auth_contract["token_values_logged"] is False, "authentication value exposure")

    require(speech["state"] == "IMPLEMENTED_NOT_INTEGRATED", "speech must not claim live connection")
    require(speech["microphone_access"] is False and speech["raw_audio_retention"] is False, "speech privacy boundary failed")
    require(speech["voice_authorises_financial_actions"] is False and speech["voice_authorises_production"] is False, "voice authority boundary failed")

    report = {
        "verification_id": "XRP-HBAR-APEX-RUNTIME-TRANCHE-V1",
        "status": "PASSED",
        "shared_agents": len(framework["shared_agents"]),
        "current_sources": denominator["inventoried"],
        "official_adapters": len(adapters["adapters"]),
        "adapter_request_plans": len(adapters["request_plans"]),
        "speech_components": len(speech["components"]),
        "authenticated_boundary_verified_offline": True,
        "network_calls_performed": False,
        "secret_values_exposed": False,
        "financial_execution": False,
        "live_runtime_connected": False,
        "proof_boundary": "Repository contracts, bounded current-source evidence and deterministic offline tests only; staging providers, persistent Knowledge Fabric, interactive identity and microphone runtime remain separate gates."
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
