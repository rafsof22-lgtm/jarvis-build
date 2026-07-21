#!/usr/bin/env python3
"""Verify Jarvis credential and novice-setup automation policy."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "registry/policies/credential_and_setup_automation_v1.json"
REFERENCE_PATH = ROOT / "skills/jarvis-sovereign-builder/references/credential-readiness-and-workflow-discovery.md"
SKILL_PATH = ROOT / "skills/jarvis-sovereign-builder/SKILL.md"
EVIDENCE_PATH = ROOT / "evidence/credential-setup-automation-v1-verification.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    reference = REFERENCE_PATH.read_text(encoding="utf-8")
    skill = SKILL_PATH.read_text(encoding="utf-8")

    require(policy["policy_id"] == "JARVIS-CREDENTIAL-AND-SETUP-AUTOMATION-V1", "Unexpected policy id")
    require(policy["security_controls"]["never_echo_secret_values"] is True, "Secret echo must remain disabled")
    require(policy["security_controls"]["never_commit_secret_values"] is True, "Secret commits must remain disabled")
    require(policy["security_controls"]["prefer_oidc_and_short_lived_tokens"] is True, "OIDC preference missing")
    require(policy["human_action_experience"]["maximum_clicks_target"] <= 3, "Novice setup exceeds three-click target")
    require("HUMAN ACTION REQUIRED" in skill, "Skill lacks consolidated human-action presentation rule")
    require("AUTO_RESUME" in reference, "Reference lacks automatic resume sequence")
    require("Do not ask the owner to re-enter" in reference, "Reference lacks reuse rule")

    unsafe_locations = set(policy["value_classes"]["NEVER_AUTO_DISCOVER_FROM_UNSAFE_LOCATIONS"])
    require("chat messages" in unsafe_locations, "Chat must not be used as a secret source")
    require("repository history" in unsafe_locations, "Repository history must not be used as a secret source")
    require("logs" in unsafe_locations, "Logs must not be used as a secret source")

    evidence = {
        "verification_id": "JARVIS-CREDENTIAL-SETUP-AUTOMATION-V1-VERIFY",
        "status": "PASSED",
        "checked": [
            str(POLICY_PATH.relative_to(ROOT)),
            str(REFERENCE_PATH.relative_to(ROOT)),
            str(SKILL_PATH.relative_to(ROOT)),
        ],
        "proof_boundary": "Repository policy and deterministic validation only. No protected values were read, printed, changed or uploaded.",
    }
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print("Credential and setup automation verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
