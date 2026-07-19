#!/usr/bin/env python3
"""Validate Jarvis source denominator and module handoff controls."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    source_path = ROOT / "registry" / "source-ledger.json"
    handoff_path = ROOT / "registry" / "module-handoffs.json"
    sources = load_json(source_path)
    handoffs = load_json(handoff_path)

    source_rows = sources.get("sources")
    if not isinstance(source_rows, list) or len(source_rows) < 8:
        raise SystemExit("source ledger must contain the canonical source denominator")

    required_source_fields = {
        "source_id", "title", "source_type", "origin", "owner", "access",
        "stage", "hash_status", "extraction_map", "applicability", "failure_reason",
    }
    valid_stages = {"NEW", "QUEUED", "PROC", "EXTRACT", "INDEX", "LINK", "READY", "PENDING_INGEST"}
    seen_source_ids: set[str] = set()
    for row in source_rows:
        missing = required_source_fields - set(row)
        if missing:
            raise SystemExit(f"source {row.get('source_id')} missing {sorted(missing)}")
        source_id = row["source_id"]
        if source_id in seen_source_ids:
            raise SystemExit(f"duplicate source_id: {source_id}")
        seen_source_ids.add(source_id)
        if row["stage"] not in valid_stages:
            raise SystemExit(f"source {source_id} has invalid stage {row['stage']}")
        if row["stage"] == "READY" and not row.get("extraction_map"):
            raise SystemExit(f"READY source {source_id} requires extraction_map")
        if row["access"] in {"not_directly_accessible", "not_currently_available"} and not row.get("failure_reason"):
            raise SystemExit(f"inaccessible source {source_id} requires failure_reason")

    module_rows = handoffs.get("modules")
    if not isinstance(module_rows, list) or len(module_rows) < 4:
        raise SystemExit("module handoff registry must contain all external domain repositories")

    required_module_fields = {
        "module_id", "repository", "owner", "handoff_status", "independent_operation",
        "canonical_interface", "source_pack", "requirements_manifest", "tests",
        "evidence", "conflicts", "next_action",
    }
    valid_statuses = {"PENDING", "PARTIAL", "READY_FOR_REVIEW", "VERIFIED", "BLOCKED"}
    seen_modules: set[str] = set()
    for row in module_rows:
        missing = required_module_fields - set(row)
        if missing:
            raise SystemExit(f"module {row.get('module_id')} missing {sorted(missing)}")
        module_id = row["module_id"]
        if module_id in seen_modules:
            raise SystemExit(f"duplicate module_id: {module_id}")
        seen_modules.add(module_id)
        if row["handoff_status"] not in valid_statuses:
            raise SystemExit(f"module {module_id} has invalid status")
        if not row["independent_operation"]:
            raise SystemExit(f"module {module_id} must preserve independent operation")
        if row["handoff_status"] == "VERIFIED":
            if not row.get("source_pack") or not row.get("requirements_manifest"):
                raise SystemExit(f"VERIFIED module {module_id} requires source pack and requirements manifest")
            if not row.get("tests") or not row.get("evidence"):
                raise SystemExit(f"VERIFIED module {module_id} requires tests and evidence")

    known_repositories = {row["origin"] for row in source_rows if row["source_type"] == "github_repository"}
    for row in module_rows:
        if row["repository"] not in known_repositories:
            raise SystemExit(f"module repository absent from source denominator: {row['repository']}")

    summary = {
        "source_count": len(source_rows),
        "ready_sources": sum(row["stage"] == "READY" for row in source_rows),
        "pending_sources": sum(row["stage"] == "PENDING_INGEST" for row in source_rows),
        "module_count": len(module_rows),
        "verified_handoffs": sum(row["handoff_status"] == "VERIFIED" for row in module_rows),
        "partial_handoffs": sum(row["handoff_status"] == "PARTIAL" for row in module_rows),
        "universal_completion_claimed": False,
    }
    evidence_dir = ROOT / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    (evidence_dir / "module-federation-verification.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
