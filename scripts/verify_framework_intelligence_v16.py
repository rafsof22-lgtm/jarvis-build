#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "governance": ROOT / "registry/framework_trigger_governance_v16.json",
    "scout": ROOT / "registry/github_capability_scout_v16.json",
    "gaps": ROOT / "registry/framework_questions_and_gap_register_v16.json",
}


def load(name):
    path = FILES[name]
    if not path.exists():
        raise SystemExit(f"missing:{path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    governance = load("governance")
    scout = load("scout")
    gaps = load("gaps")

    require(governance.get("schema_version") == "16.0.0", "invalid governance schema")
    require("framework" in governance.get("trigger_terms", []), "framework trigger missing")
    require(governance.get("health_quantum_boundary", {}).get("live_device_control") == "DISABLED", "live device control must remain disabled")
    require(governance.get("financial_boundary") == "RESEARCH_ONLY_PAPER_FIRST", "financial boundary weakened")
    require("100 percent coverage" in governance.get("coverage_rule", ""), "coverage proof rule missing")

    require(scout.get("default_policy") == "DENY_UNTIL_REVIEWED", "capability scout must deny by default")
    require("blind bulk installation" in scout.get("prohibited", []), "blind installation prohibition missing")
    require("rollback_and_removal" in scout.get("minimum_review", []), "rollback review missing")

    require(gaps.get("status") == "OPEN_REGISTER", "gap register status invalid")
    require(len(gaps.get("mandatory_questions", [])) >= 15, "mandatory question coverage too small")
    require(len(gaps.get("coverage_dimensions", [])) >= 13, "coverage dimensions incomplete")
    require("ZERO_GAP" in gaps.get("proof_rule", ""), "zero-gap proof rule missing")

    evidence_dir = ROOT / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    report = {
        "status": "PASS",
        "schema_version": "16.0.0",
        "validated_files": [str(path.relative_to(ROOT)) for path in FILES.values()],
        "safety": {
            "health_research_only": True,
            "live_device_control_disabled": True,
            "financial_research_only_paper_first": True,
            "deny_until_reviewed": True,
            "zero_gap_claim_requires_proof": True,
        },
    }
    with (evidence_dir / "framework-intelligence-v16-verification.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
