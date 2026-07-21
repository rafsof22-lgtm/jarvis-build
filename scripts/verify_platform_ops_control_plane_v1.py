#!/usr/bin/env python3
"""Verify the Jarvis platform operations control-plane contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "platform" / "platform_ops_control_plane_v1.json"
DOC = ROOT / "docs" / "platform-ops-control-plane.md"
EVIDENCE = ROOT / "evidence" / "platform-ops-control-plane-v1-verification.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    require(data["id"] == "JARVIS-PLATFORM-OPS-CONTROL-PLANE-V1", "unexpected control-plane id")
    require(data["state"] == "IMPLEMENTED_NOT_INTEGRATED", "repository policy must not claim live integration")
    require(data["architecture"]["service_isolation_required"] is True, "service isolation missing")
    require(data["iam"]["default"] == "deny", "IAM must default deny")
    require(data["iam"]["self_elevation"] is False, "self-elevation must remain disabled")
    require(data["secrets"]["values_in_repository"] is False, "secret values must not enter repository")
    require(data["secrets"]["values_in_chat"] is False, "secret values must not enter chat")
    require(data["observability"]["log_redaction_required"] is True, "log redaction missing")
    require(data["resilience"]["restore_into_isolated_target"] is True, "isolated restore test missing")
    require(data["incident_response"]["kill_switch_required"] is True, "kill switch missing")
    require(data["cost_governance"]["automatic_paid_scale_out"] is False, "paid scale-out must be disabled")
    require(data["cost_governance"]["automatic_billing_acceptance"] is False, "billing acceptance must be disabled")
    require("owner_approval_for_production" in data["release_gates"], "production approval gate missing")
    require(len(data["agent_separation"]) >= 8, "required role separation incomplete")
    require("A backup is not proven" in doc, "backup proof boundary missing")
    require("repository policy/scaffold" in doc, "repository/runtime distinction missing")

    report = {
        "verification_id": "JARVIS-PLATFORM-OPS-CONTROL-PLANE-V1",
        "status": "PASSED",
        "state": data["state"],
        "release_gate_count": len(data["release_gates"]),
        "agent_role_count": len(data["agent_separation"]),
        "secret_values_exposed": False,
        "provider_changes_attempted": False,
        "proof_boundary": "Repository control-plane contract and deterministic checks only; live topology, IAM, monitoring, backup, restore, DR and production remain separate runtime gates.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
