#!/usr/bin/env python3
"""Verify bounded XRP/HBAR reconciliation batch 002."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry/reconciliation/xrp_hbar_batch_002_manifest.json"
CLAIMS = ROOT / "registry/reconciliation/xrp_hbar_batch_002_claims.json"
DISCREPANCIES = ROOT / "registry/reconciliation/xrp_hbar_batch_002_discrepancies.json"
EVIDENCE = ROOT / "evidence/xrp-hbar-batch-002-verification.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    manifest, claims_doc, discrepancy_doc = load(MANIFEST), load(CLAIMS), load(DISCREPANCIES)
    sources = manifest.get("sources", [])
    claims = claims_doc.get("claims", [])
    discrepancies = discrepancy_doc.get("discrepancies", [])

    checks = {
        "two_source_denominator": len(sources) == 2,
        "source_hashes_valid": all(len(source.get("sha256", "")) == 64 for source in sources),
        "archive_member_counts": sources[0].get("archive_entries") == 76 and sources[0].get("file_entries") == 74,
        "archive_member_types_reconcile": sum(sources[0].get("member_types", {}).values()) == 74,
        "text_line_count": sources[1].get("line_count") == 22672,
        "eleven_snapshot_records": manifest.get("archive_observations", {}).get("tracker_json_snapshots") == 11,
        "empty_tracking_registers_recorded": all(manifest.get("archive_observations", {}).get(key) == 0 for key in ["populated_trigger_records", "populated_discrepancy_records", "populated_forecast_accuracy_records", "populated_social_claim_records"]),
        "live_network_not_claimed": manifest.get("archive_observations", {}).get("live_network_source_state") == "FAILED_DNS_OR_SKIPPED",
        "twelve_claim_records": len(claims) == 12,
        "historical_819_rejected": any(c.get("claim_id") == "XH-B002-C002" and c.get("disposition") == "REJECTED_AS_VERIFIED_PROBABILITY" for c in claims),
        "trigger_claim_invalidated": any(c.get("claim_id") == "XH-B002-C004" and "INVALIDATED" in c.get("disposition", "") for c in claims),
        "offline_engine_scope_adopted": any(c.get("claim_id") == "XH-B002-C006" and c.get("disposition") == "ADOPTED_WITH_SCOPE_LIMIT" for c in claims),
        "fixture_not_current_price": any(c.get("claim_id") == "XH-B002-C008" and c.get("disposition") == "ADOPTED_AS_FIXTURE_ONLY" for c in claims),
        "five_discrepancies": len(discrepancies) == 5,
        "all_discrepancies_resolved_for_batch": all(d.get("state") == "RESOLVED_FOR_BATCH" for d in discrepancies),
        "direct_demand_pathway_required": len(discrepancy_doc.get("direct_token_demand_policy", {}).get("required_pathway_fields", [])) >= 10,
        "financial_boundary_present": "No personalised regulated advice" in claims_doc.get("financial_boundary", ""),
        "full_reconstruction_not_claimed": "full XRP/HBAR historical reconstruction remains open" in manifest.get("completion_scope", "")
    }

    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "id": "EVIDENCE-XRP-HBAR-BATCH-002",
        "status": status,
        "checks": checks,
        "proof_scope": "Two-source historical reconciliation batch only.",
        "current_market_facts": "NOT_REVALIDATED_BY_THIS_BATCH",
        "live_data_runtime": "NOT_PROVEN",
        "financial_execution": "DISABLED",
        "full_historical_reconstruction": "OPEN",
        "rollback": "Revert the batch files through Git and preserve source hashes and supersession history."
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
