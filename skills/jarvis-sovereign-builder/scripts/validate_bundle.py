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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    missing = [item for item in REQUIRED if not (ROOT / item).is_file()]
    require(not missing, f"missing files: {missing}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    require(skill.startswith("---\n"), "SKILL.md frontmatter start missing")
    require(bool(re.search(r"^name:\s*jarvis-sovereign-builder\s*$", skill, re.MULTILINE)), "skill name missing or invalid")
    require(bool(re.search(r"^description:\s*.+$", skill, re.MULTILINE)), "skill description missing")

    required_sections = [
        "Dual-layer applicability",
        "Practitioner intelligence",
        "Capability-universe",
        "Automatic skill-update governance",
        "Credential and workflow readiness",
        "Auto-fix and proof",
    ]
    missing_sections = [phrase for phrase in required_sections if phrase not in skill]
    require(not missing_sections, f"missing SKILL.md controls: {missing_sections}")

    refs = re.findall(r"`(references/[^`]+\.md)`", skill)
    unresolved = sorted({ref for ref in refs if not (ROOT / ref).is_file()})
    require(not unresolved, f"unresolved references: {unresolved}")

    syntax_errors: list[str] = []
    for script in sorted((ROOT / "scripts").glob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            syntax_errors.append(f"{script.relative_to(ROOT)}:{exc.lineno}:{exc.msg}")
    require(not syntax_errors, f"Python syntax errors: {syntax_errors}")

    require("zero errors" in skill.lower(), "truth-boundary language for zero errors is missing")
    dual = (ROOT / "references/dual-layer-applicability-and-autonomy.md").read_text(encoding="utf-8")
    require("NO_KNOWN_ERRORS_AFTER_DEFINED_CHECKS" in dual, "bounded zero-error status missing")
    require("NO_KNOWN_GAPS_WITHIN_VERIFIED_SCOPE" in dual, "bounded no-gap status missing")

    files = [path for path in ROOT.rglob("*") if path.is_file()]
    print(f"skill bundle valid: files={len(files)} references={len(refs)} scripts={len(list((ROOT / 'scripts').glob('*.py')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
