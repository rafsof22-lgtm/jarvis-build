#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "tracker": ROOT / "registry/trackers/all_progress_tracker_reconciliation_v17.json",
    "architecture": ROOT / "registry/architecture/jarvis_full_stack_18_layer_reference_v1.json",
    "surface": ROOT / "registry/ux/command_centre_full_stack_surface_v17.json",
    "delta": ROOT / "registry/source-accounting/post_2026_06_25_project_chat_delta_v17.json",
    "instruction_delta": ROOT / "registry/source-accounting/v17_uploaded_instruction_delta.json",
    "health_manifest": ROOT / "registry/health/health_claim_review_manifest_v17.json",
    "projects": ROOT / "registry/projects/remaining_requested_projects_reconstruction_v17.json",
    "staging": ROOT / "registry/staging/full_stack_local_staging_v17.json",
    "continuity": ROOT / "PROJECT_CONTINUITY.md",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    for name, path in FILES.items():
        require(path.exists(), f"missing {name}: {path}")
    tracker = load(FILES["tracker"])
    architecture = load(FILES["architecture"])
    surface = load(FILES["surface"])
    delta = load(FILES["delta"])
    health = load(FILES["health_manifest"])
    projects = load(FILES["projects"])
    staging = load(FILES["staging"])
    instruction_delta = load(FILES["instruction_delta"])
    continuity = FILES["continuity"].read_text(encoding="utf-8")

    require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "false completion state")
    require(tracker["version"] == "17.0.0", "tracker version mismatch")
    require(len(architecture["layers"]) == 18, "canonical layer count must remain 18")
    require(surface["layers"] == 18 and surface["route"] == "/api/v1/full-stack", "Command Centre surface mismatch")
    require(delta["comparison"] == "EXACT_ARCHIVE_DUPLICATE", "post-cutoff archive must be duplicate")
    require(delta["novel_export_bytes"] == 0 and not delta["post_cutoff_delta_generated"], "false chat delta")
    require(delta["state"] == "PENDING_INGEST", "real later-chat delta must remain pending")
    require(health["conversation_count"] == 194, "Health handover denominator mismatch")
    require(health["flag_occurrence_count"] > 0, "Health claim manifest is empty")
    require(len(health["overall_merkle_root"]) == 64, "Health Merkle root invalid")
    require("items" not in health, "repository Health summary must not contain detailed claim rows")
    require({row["project_name"] for row in projects["projects"]} == {"XRP Tracking New", "Longevity Plan", "Tax", "Active Trust", "Finance Planning", "Financial New"}, "remaining project set mismatch")
    require(staging["layer_count"] == 18, "staging did not exercise 18 layers")
    require(staging["state"] == "DONE_VERIFIED_LOCAL_STAGING_SIMULATION", "local staging state mismatch")
    require(staging["retry_test"] == "PASS", "retry test missing")
    require(staging["backup_test"] == "BACKUP_CREATED", "backup test missing")
    require(staging["restore_test"]["state"] == "RESTORE_VERIFIED", "restore test missing")
    require(staging["rollback_test"]["state"] == "ROLLED_BACK", "rollback test missing")
    require(staging["projected_cost_aud"] == 0.0, "local staging must remain zero-spend")
    require(not staging["connected_external_staging"] and not staging["production_authorised"], "external staging/production overclaim")
    require(len(instruction_delta["sources"]) == 5, "uploaded instruction delta mismatch")
    require("all_progress_tracker_reconciliation_v17.json" in continuity, "continuity tracker pointer stale")
    require("Command Centre v1.4" in continuity, "continuity missing Command Centre v1.4")
    require("Four images remain without OCR" in continuity, "legacy verifier phrase not preserved")
    require("three opaque archives" in continuity, "legacy verifier phrase not preserved")
    require("ACTIVE_PROGRAM_NOT_100_PERCENT" in continuity, "completion boundary missing")

    return {
        "verification_id": "JARVIS-V17-COMPLETION-TRANCHE-VERIFY",
        "verified": True,
        "tracker_version": tracker["version"],
        "layer_count": 18,
        "health_flag_occurrence_count": health["flag_occurrence_count"],
        "remaining_project_count": len(projects["projects"]),
        "post_cutoff_novel_bytes": delta["novel_export_bytes"],
        "staging_test_dimensions": staging["test_dimensions"],
        "files": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in FILES.items()},
        "truth_boundary": "Repository, bounded-source and local-simulation verification only; connected external staging, production and owner acceptance remain open.",
    }


def main() -> int:
    evidence = verify()
    destination = ROOT / "evidence/v17-completion-tranche-verification.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
