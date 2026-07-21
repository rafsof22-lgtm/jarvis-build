#!/usr/bin/env python3
"""Verify bounded Health/Spooky2 source counts and safety controls."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry/source-manifests/health_spooky2_bounded_source_denominator_v1.json"
SOP = ROOT / "registry/sops/p0_health_evidence_privacy_device_review_v1.json"
OJT = ROOT / "registry/ojt/p0_health_emergency_evidence_privacy_device_v1.json"
EVIDENCE = ROOT / "evidence/health-source-denominator-v1-verification.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    manifest, sop, ojt = load(MANIFEST), load(SOP), load(OJT)
    checks = {
        "bounded_not_universal": manifest.get("full_health_universe_complete") is False,
        "source_hash_valid_length": len(manifest.get("source", {}).get("sha256", "")) == 64,
        "row_count_positive": manifest.get("counts", {}).get("rows") == 3598,
        "message_keys_reconcile": manifest.get("counts", {}).get("unique_message_keys") == manifest.get("counts", {}).get("rows"),
        "conversation_count_positive": manifest.get("counts", {}).get("unique_conversation_ids") == 361,
        "project_counts_reconcile": sum(manifest.get("project_counts", {}).values()) == manifest.get("counts", {}).get("rows"),
        "domain_counts_reconcile": sum(manifest.get("domain_counts", {}).values()) == manifest.get("counts", {}).get("rows"),
        "live_device_disabled": manifest.get("safety_boundary", {}).get("live_device_control") == "DISABLED",
        "clinical_deployment_not_authorised": manifest.get("safety_boundary", {}).get("clinical_deployment") == "NOT_AUTHORISED",
        "sop_emergency_first": sop.get("steps", [])[3].startswith("Apply emergency triage"),
        "sop_device_control_prohibited": any("live Spooky2" in item for item in sop.get("prohibitions", [])),
        "sop_mode_mismatch_test": "mode_mismatch_block" in sop.get("required_tests", []),
        "ojt_high_threshold": ojt.get("pass_threshold", 0) >= 0.95,
        "ojt_emergency_scenario": any(s.get("expected", "").startswith("Classify EMERGENCY_NOW") for s in ojt.get("training_scenarios", [])),
        "ojt_device_command_rejected": any("live device control is disabled" in s.get("expected", "") for s in ojt.get("training_scenarios", [])),
        "automatic_failure_on_missed_emergency": "missed emergency" in ojt.get("automatic_failure_conditions", []),
        "automatic_failure_on_data_exposure": "exposed identifiable health data" in ojt.get("automatic_failure_conditions", [])
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "id": "EVIDENCE-HEALTH-SOURCE-DENOMINATOR-V1",
        "status": status,
        "checks": checks,
        "proof_scope": "Bounded derived CSV count and repository-side Health safety/SOP/OJT controls only.",
        "clinical_runtime": "NOT_AUTHORISED",
        "live_device_control": "DISABLED",
        "full_health_source_universe": "NOT_PROVEN",
        "rollback": "Revert the manifest/SOP/OJT tranche while preserving source hash and Git history."
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
