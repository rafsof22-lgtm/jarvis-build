#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "assets/icon.svg",
    "references/dual-layer-applicability-and-autonomy.md",
    "references/practitioner-intelligence-and-capability-universe.md",
    "references/credential-readiness-and-workflow-discovery.md",
    "references/skill-update-and-release-governance.md",
    "references/approval-permission-and-push.md",
    "references/autonomy-security.md",
    "references/runtime-implementation.md",
    "references/historical-knowledgebase-ingestion.md",
    "references/registry-and-evidence-contracts.md",
    "references/role-and-agent-council.md",
    "references/model-cost-routing.md",
    "references/source-scout-and-opportunity-fabric.md",
    "references/missing-controls-checklist.md",
    "references/domain-modules.md",
    "references/maximum-automation-and-auto-applicability.md",
    "scripts/inventory_source_tree.py",
    "scripts/validate_evidence_chain.py",
]


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    assert not missing, f"missing files: {missing}"

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert skill.startswith("---\n")
    assert re.search(r"^name:\s*jarvis-sovereign-builder\s*$", skill, re.MULTILINE)
    assert re.search(r"^description:\s*.+$", skill, re.MULTILINE)
    for phrase in [
        "Dual-layer applicability",
        "Practitioner intelligence",
        "Capability-universe",
        "Automatic skill-update governance",
        "Credential and workflow readiness",
        "Completion truth",
    ]:
        assert phrase in skill, phrase

    refs = re.findall(r"`(references/[^`]+\.md)`", skill)
    unresolved = sorted({ref for ref in refs if not (ROOT / ref).is_file()})
    assert not unresolved, f"unresolved references: {unresolved}"

    for script in (ROOT / "scripts").glob("*.py"):
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))

    assert "zero errors" in skill.lower()
    assert "NO_KNOWN_ERRORS_AFTER_DEFINED_CHECKS" in (ROOT / "references/dual-layer-applicability-and-autonomy.md").read_text(encoding="utf-8")
    print(f"skill bundle valid: files={len([p for p in ROOT.rglob('*') if p.is_file()])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
