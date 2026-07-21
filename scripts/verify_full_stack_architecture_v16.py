from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def verify() -> dict[str, object]:
    architecture = load("registry/architecture/jarvis_full_stack_18_layer_reference_v1.json")
    aliases = load("registry/sources/health_split_upload_aliases_v16.json")
    access = load("registry/source-accounting/project_chat_access_reconciliation_v1.json")
    tracker = load("registry/trackers/all_progress_tracker_reconciliation_v16.json")

    layers = architecture["layers"]
    assert architecture["declared_layer_count"] == len(layers)
    assert len(layers) >= architecture["minimum_required_layers"] >= 13
    assert [row["order"] for row in layers] == list(range(1, len(layers) + 1))
    assert len({row["layer_id"] for row in layers}) == len(layers)
    allowed_states = {
        "DONE_VERIFIED",
        "IMPLEMENTED_NOT_INTEGRATED",
        "INTEGRATED_STAGING",
        "SPEC_ONLY",
        "BLOCKED",
    }
    for row in layers:
        assert row["state"] in allowed_states
        assert row["purpose"].strip()
        assert row["existing_evidence"]
        assert row["open_gaps"]

    assert aliases["novel_source_bytes"] == 0
    assert len(aliases["records"]) == 3
    expected = {
        "part001": (94371840, "8bd8bc179a0bb5ed8f806198f535525697f8b2db597dfecf54b174623614016d"),
        "part002": (94371840, "f66c2acfcad9b9133bdc7a3061e85ff38791967ce48336384fd6a3c85eb07aee"),
        "part003": (94371840, "83223326e6af37eaaefce9f406d2247d4c02e1890e9d9d64a8c53ce560a3fa2b"),
    }
    for row in aliases["records"]:
        assert row["state"] == "DUPLICATE_WITH_LINEAGE"
        assert (row["bytes"], row["sha256"]) == expected[row["canonical_member"]]

    assert access["all_live_project_chats_accessible"] is False
    states = {row["source_class"]: row["state"] for row in access["sources"]}
    assert states["POST_EXPORT_PROJECT_CHAT_DELTA"] == "PENDING_INGEST"
    assert states["LIVE_PROJECT_UI_CHAT_ENUMERATION"] == "BLOCKED_BY_ACCESS"

    assert tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    assert tracker["full_stack_state"]["declared_layers"] == 18
    assert tracker["full_stack_state"]["end_to_end_connected_runtime"] == "NOT_VERIFIED"
    assert tracker["project_chat_state"]["all_chats_current_claim"] is False

    continuity = (ROOT / "PROJECT_CONTINUITY.md").read_text(encoding="utf-8")
    assert "all_progress_tracker_reconciliation_v16.json" in continuity
    assert "18-layer" in continuity
    assert "Never claim all project chats are current" in continuity
    assert "ACTIVE_PROGRAM_NOT_100_PERCENT" in continuity

    return {
        "verified": True,
        "layer_count": len(layers),
        "minimum_layer_count": architecture["minimum_required_layers"],
        "upload_aliases": len(aliases["records"]),
        "novel_source_bytes": aliases["novel_source_bytes"],
        "all_live_project_chats_accessible": access["all_live_project_chats_accessible"],
        "program_state": tracker["program_state"],
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
