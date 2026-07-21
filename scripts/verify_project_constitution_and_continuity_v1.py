#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import py_compile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "PROJECT_CONSTITUTION.md",
    ROOT / "JARVIS_RAF213G_PROJECT_CONSTITUTION.md",
    ROOT / "PROJECT_CONTINUITY.md",
    ROOT / "AGENTS.md",
    ROOT / "docs/full-completion-priority-plan.md",
    ROOT / "registry/full_completion_priority_plan_v1.json",
    ROOT / "registry/project_constitution_manifest_v1.json",
    ROOT / "registry/skills/github_repo_capability_scout_v1.json",
    ROOT / "skills/github-repo-capability-scout/SKILL.md",
    ROOT / "skills/github-repo-capability-scout/references/verbatim-content-manifest.json",
    ROOT / "skills/github-repo-capability-scout/references/verbatim-source-pointer.md",
]
TASK_FIELDS = {"task_id", "priority", "repository", "title", "state", "next_action"}


def main() -> None:
    checks = {"required_files": all(path.is_file() for path in REQUIRED)}
    entry = (ROOT / "PROJECT_CONSTITUTION.md").read_text(encoding="utf-8")
    constitution = (ROOT / "JARVIS_RAF213G_PROJECT_CONSTITUTION.md").read_text(encoding="utf-8")
    continuity = (ROOT / "PROJECT_CONTINUITY.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    skill = (ROOT / "skills/github-repo-capability-scout/SKILL.md").read_text(encoding="utf-8")
    checks["entry_links"] = all(name in entry for name in ["JARVIS_RAF213G_PROJECT_CONSTITUTION.md", "PROJECT_CONTINUITY.md", "AGENTS.md"])
    checks["constitution_contract"] = "Requirement -> Module -> Artifact -> Test or waiver -> Evidence -> Runtime state -> Rollback -> Owner acceptance" in constitution
    checks["continuity_truth"] = "ACTIVE_PROGRAM_NOT_100_PERCENT" in continuity
    checks["agent_startup_order"] = all(name in agents for name in ["PROJECT_CONSTITUTION.md", "JARVIS_RAF213G_PROJECT_CONSTITUTION.md", "PROJECT_CONTINUITY.md"])
    plan = json.loads((ROOT / "registry/full_completion_priority_plan_v1.json").read_text(encoding="utf-8"))
    tasks = plan.get("tasks", [])
    checks["task_count"] = len(tasks) >= 28
    checks["task_fields"] = all(TASK_FIELDS.issubset(task) for task in tasks)
    checks["blocker_fields"] = all(task.get("blocker_class") for task in tasks if task.get("state") in {"BLOCKED", "BACKLOGGED", "SPEC_ONLY", "SCAFFOLDED", "IMPLEMENTED_NOT_INTEGRATED", "INTEGRATED_STAGING", "DEPLOYED_UNVERIFIED"})
    checks["priority_coverage"] = {task.get("priority") for task in tasks}.issuperset({"P0", "P1", "P2", "P3", "P4", "P5", "P6"})
    checks["top_level_completion_rule"] = "Requirement -> Module -> Artifact" in plan.get("completion_rule", "")
    manifest = json.loads((ROOT / "skills/github-repo-capability-scout/references/verbatim-content-manifest.json").read_text(encoding="utf-8"))
    pointer = (ROOT / "skills/github-repo-capability-scout/references/verbatim-source-pointer.md").read_text(encoding="utf-8")
    checks["verbatim_pointer"] = manifest["sha256"] in pointer and str(manifest["size_bytes"]) in pointer
    checks["skill_workflow"] = "STATIC_SECURITY_QUARANTINE" in skill and "CANONICAL_CONSTITUTION_UNAVAILABLE" in skill
    scripts = sorted((ROOT / "skills/github-repo-capability-scout/scripts").glob("*.py"))
    try:
        with tempfile.TemporaryDirectory() as temp:
            for script in scripts:
                py_compile.compile(str(script), cfile=str(Path(temp) / (script.name + "c")), doraise=True)
        checks["skill_scripts_compile"] = len(scripts) == 5
    except Exception:
        checks["skill_scripts_compile"] = False
    report = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "task_count": len(tasks),
        "constitution_sha256": hashlib.sha256(constitution.encode("utf-8")).hexdigest(),
        "runtime_state": "REPOSITORY_GOVERNANCE_ONLY",
        "external_actions": "NOT_ATTEMPTED",
    }
    output = ROOT / "evidence/project-constitution-continuity-v1-verification.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
