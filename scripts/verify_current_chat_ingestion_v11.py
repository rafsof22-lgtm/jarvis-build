#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT = ROOT / "evidence/chat_transcripts/2026-07-21-current-chat-visible-transcript.md"
MANIFEST = ROOT / "registry/source_intake/current_chat_conversation_manifest_v1.json"
REQUIREMENTS = ROOT / "registry/requirements/current_chat_requirement_candidates_v1.json"
TRACKER = ROOT / "registry/trackers/all_progress_tracker_reconciliation_v11.json"
HANDOFF = ROOT / "docs/current-chat-ingestion-and-handoff-2026-07-21.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    required = [TRANSCRIPT, MANIFEST, REQUIREMENTS, TRACKER, HANDOFF]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    assert not missing, f"missing artifacts: {missing}"

    transcript_bytes = TRANSCRIPT.read_bytes()
    manifest = load_json(MANIFEST)
    requirements = load_json(REQUIREMENTS)
    tracker = load_json(TRACKER)

    assert manifest["id"] == "JARVIS-CURRENT-CHAT-CONVERSATION-MANIFEST-V1"
    assert manifest["raw_artifact"]["sha256"] == hashlib.sha256(transcript_bytes).hexdigest()
    assert manifest["raw_artifact"]["size_bytes"] == len(transcript_bytes)
    assert manifest["raw_artifact"]["verbatim_visible_message_count"] == 3
    assert manifest["controls"]["raw_and_derived_separated"] is True
    assert manifest["controls"]["no_hidden_content_exported"] is True
    assert manifest["exact_gap"]["blocker_id"] == "CURRENT_CHAT_FULL_UI_EXPORT_REQUIRED"

    assert requirements["id"] == "JARVIS-CURRENT-CHAT-REQUIREMENT-CANDIDATES-V1"
    assert len(requirements["requirements"]) == 5
    assert {item["classification"] for item in requirements["requirements"]} == {"BOTH"}
    assert any(item["state"] == "BLOCKED_AT_EXACT_STEP" for item in requirements["requirements"])

    assert tracker["id"] == "JARVIS-ALL-PROGRESS-TRACKER-RECONCILIATION-V11"
    assert tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    assert tracker["new_exact_gate"]["blocker_id"] == "CURRENT_CHAT_FULL_UI_EXPORT_REQUIRED"
    assert len(tracker["inherited_exact_gates"]) == 11
    assert "FULL_CHATGPT_UI_TRANSCRIPT_NOT_PROVEN" in tracker["completion_assertion"]

    text = TRANSCRIPT.read_text(encoding="utf-8")
    assert "COMPLETE ALL TASKS AND RECONDILE PROGRSS TRACKSERS" in text
    assert "CAN U SHARE THIS ENTIRE CHAT" in text
    assert "private chain-of-thought" in text
    assert "BLOCKED_AT_EXACT_STEP: CURRENT_CHAT_FULL_UI_EXPORT_REQUIRED" in text

    print("current chat ingestion v11 verification passed")


if __name__ == "__main__":
    main()
