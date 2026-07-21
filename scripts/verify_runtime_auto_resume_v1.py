#!/usr/bin/env python3
"""Verify the bounded runtime auto-resume controller and manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry/platform/runtime_auto_resume_manifest_v1.json"
CONTROLLER = ROOT / "scripts/runtime_auto_resume.py"
EVIDENCE = ROOT / "evidence/runtime-auto-resume-policy-verification-v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    controller = CONTROLLER.read_text(encoding="utf-8")
    policy = manifest["policy"]

    require(manifest["id"] == "JARVIS-RUNTIME-AUTO-RESUME-MANIFEST-V1", "Unexpected manifest id")
    require(policy["read_only_network_checks_only"] is True, "Network checks must remain read-only")
    require(policy["no_secret_values_in_output"] is True, "Secret values must remain excluded")
    require(policy["no_provider_mutation"] is True, "Provider mutation must remain disabled")
    require(policy["no_production_promotion"] is True, "Production promotion must remain disabled")
    require(policy["no_money_movement"] is True, "Money movement must remain disabled")
    require(policy["maximum_attempts"] <= 2, "Retry ceiling exceeded")
    require(policy["timeouts_seconds"] <= 10, "Timeout ceiling exceeded")

    allowed_types = {"presence", "url_parse", "hmac_self_test", "http_get"}
    groups = manifest.get("groups", [])
    require(len(groups) >= 4, "Expected core runtime groups")
    for group in groups:
        require(group.get("group_id"), "Missing group id")
        for check in group.get("checks", []):
            require(check.get("type") in allowed_types, f"Unsafe or unsupported check: {check.get('type')}")

    forbidden = ["method=\"POST\"", "method=\"PUT\"", "method=\"DELETE\"", "subprocess", "os.system", "requests.post"]
    for token in forbidden:
        require(token not in controller, f"Controller contains forbidden operation: {token}")
    require("value_exposed\": False" in controller, "Controller lacks redaction markers")
    require("provider_state_changed\": False" in controller, "Controller lacks provider mutation proof boundary")

    report = {
        "id": "EVIDENCE-RUNTIME-AUTO-RESUME-POLICY-V1",
        "status": "PASSED",
        "groups_checked": len(groups),
        "allowed_check_types": sorted(allowed_types),
        "secret_values_exposed": False,
        "proof_boundary": "Static policy and controller verification. Live endpoint success requires configured staging values and execution evidence."
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
