#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs" / "dual-layer-autonomy-and-applicability-policy.md"
PROJECT = ROOT / "docs" / "chatgpt-project-instructions.txt"
REGISTER = ROOT / "registry" / "instruction-applicability.json"


def main() -> int:
    policy = POLICY.read_text(encoding="utf-8")
    project = PROJECT.read_text(encoding="utf-8")
    register = json.loads(REGISTER.read_text(encoding="utf-8"))

    required_policy = [
        "Dual-layer propagation rule",
        "Maximum-safe-automation default",
        "Mandatory pre-task gate",
        "Mandatory post-task gate",
        "Auto-fix protocol",
        "Forensic and no-gaps protocol",
        "Instruction-to-runtime synchronization",
    ]
    for phrase in required_policy:
        assert phrase in policy, phrase

    required_project = [
        "DUAL-LAYER APPLICABILITY",
        "MAXIMUM SAFE AUTOMATION",
        "PREFLIGHT AND POSTFLIGHT",
        "AUTO-FIX",
        "NO_KNOWN_ERRORS_AFTER_DEFINED_CHECKS",
        "Instruction Applicability Register",
    ]
    for phrase in required_project:
        assert phrase in project, phrase

    rules = register.get("rules", [])
    assert rules
    valid = {"BOTH", "SYSTEM_ONLY", "INSTRUCTION_ONLY", "MODULE_ONLY", "CONFLICT_REVIEW"}
    assert all(item.get("applicability_class") in valid for item in rules)
    both = [item for item in rules if item["applicability_class"] == "BOTH"]
    assert both
    for item in both:
        artifacts = item.get("affected_artifacts", [])
        assert "docs/chatgpt-project-instructions.txt" in artifacts
        assert item.get("runtime_controls")
        assert item.get("chat_controls")
        assert item.get("tests")

    truth_boundary = "never claim done, live, 100%, zero errors or zero gaps"
    assert truth_boundary in project.lower()
    assert "no_known_errors_after_defined_checks" in project.lower()
    assert "no_known_gaps_within_verified_scope" in project.lower()
    print("dual-layer policy smoke checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
