#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "environment-completion.json"
EVIDENCE = ROOT / "evidence" / "environment-completion-verification.json"

ALLOWED = {
    "COMPLETE_CURRENT_SCOPE",
    "PENDING_INGEST",
    "SPEC_ONLY",
    "BACKLOGGED",
    "SCAFFOLDED",
    "IMPLEMENTED_NOT_INTEGRATED",
    "INTEGRATED_STAGING",
    "DEPLOYED_UNVERIFIED",
    "DONE_VERIFIED",
    "WAIVED",
    "BLOCKED",
    "READY_FOR_REVIEW",
    "PR_PENDING_VERIFICATION",
}


def main() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    repos = data.get("repositories")
    if not isinstance(repos, list) or len(repos) != 5:
        raise SystemExit("environment registry must contain exactly five accessible repositories")

    ids = [row.get("repository_id") for row in repos]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate repository_id in environment registry")

    required = {
        "repository_id",
        "full_name",
        "latest_observed_commit",
        "source_inventory_status",
        "federation_contract_status",
        "handoff_status",
        "deployment_status",
        "next_action",
    }
    for row in repos:
        missing = required - set(row)
        if missing:
            raise SystemExit(f"{row.get('repository_id')} missing {sorted(missing)}")
        for field in ("source_inventory_status", "federation_contract_status", "handoff_status", "deployment_status"):
            if row[field] not in ALLOWED:
                raise SystemExit(f"{row['repository_id']} invalid {field}: {row[field]}")
        if row["deployment_status"] == "DONE_VERIFIED":
            raise SystemExit("no full deployment may be marked DONE_VERIFIED without dependency, restore and rollback evidence")

    metrics = data.get("environment_metrics", {})
    if metrics.get("accessible_repositories") != len(repos):
        raise SystemExit("accessible repository metric does not match registry")
    if metrics.get("environment_source_completion_percent") != 100:
        raise SystemExit("current GitHub source scope should be 100% inventoried")
    if metrics.get("environment_live_verification_percent") != 0:
        raise SystemExit("full live verification must remain 0 until dependency, restore and rollback evidence exists")

    public_done = sum(row.get("live_contract_status") == "DONE_VERIFIED" for row in repos)
    public_applicable = metrics.get("public_live_contracts_applicable")
    if not isinstance(public_applicable, int) or public_applicable <= 0:
        raise SystemExit("public_live_contracts_applicable must be a positive integer")
    if metrics.get("public_live_contracts_done_verified") != public_done:
        raise SystemExit("public live contract count does not match registry")
    expected_percent = round((public_done / public_applicable) * 100)
    if metrics.get("environment_public_live_contract_percent") != expected_percent:
        raise SystemExit("public live contract percentage does not match registry")

    report = {
        "schema_version": "1.1.0",
        "repository_count": len(repos),
        "source_scope_complete": True,
        "contracts_done_verified": sum(r["federation_contract_status"] == "DONE_VERIFIED" for r in repos),
        "contracts_pending": sum(r["federation_contract_status"] == "PR_PENDING_VERIFICATION" for r in repos),
        "public_live_contracts_done_verified": public_done,
        "public_live_contracts_applicable": public_applicable,
        "environment_public_live_contract_percent": expected_percent,
        "live_deployments_done_verified": 0,
        "values_exposed": False,
        "status": "NO_KNOWN_GAPS_WITHIN_VERIFIED_GITHUB_SOURCE_SCOPE",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
