#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "registry/trackers/all_progress_tracker_reconciliation_v10.json"
MANIFEST = ROOT / "registry/source_intake/chat_closeout_uploaded_source_manifest_v1.json"
DOC = ROOT / "docs/chat-closeout-reconciliation-2026-07-21.md"


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    tracker = load(TRACKER)
    manifest = load(MANIFEST)
    assert DOC.exists(), "closeout document missing"
    assert tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    assert tracker["chat_state"] == "CLOSED_FOR_CONTINUATION_IN_ANOTHER_CURRENT_JARVIS_CHAT"
    assert len(tracker["remaining_exact_gates"]) == 11
    assert len(manifest["files"]) == 18
    assert manifest["completion_assertion"] == "VISIBLE_BYTES_HASHED_AND_REGISTERED_ONLY"
    hashes = [item["sha256"] for item in manifest["files"]]
    assert len(hashes) == len(set(hashes)), "duplicate source hashes require explicit lineage"
    assert all(len(value) == 64 for value in hashes)
    assert all(item["size_bytes"] > 0 for item in manifest["files"])
    text = DOC.read_text(encoding="utf-8")
    assert "END_TO_END_NOT_VERIFIED" in text
    assert "Do not rely on this chat as source truth after closure." in text
    print("chat closeout reconciliation v10 verified")


if __name__ == "__main__":
    main()
