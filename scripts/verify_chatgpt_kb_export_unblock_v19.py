#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "intake": ROOT / "scripts/chatgpt_kb_intake_v1.py",
    "ledgers": ROOT / "scripts/create_kb_integrity_ledgers.py",
    "tests": ROOT / "tests/test_chatgpt_kb_intake_v1.py",
    "register": ROOT / "registry/source-accounting/chatgpt_kb_export_unblock_v19.json",
    "runbook": ROOT / "docs/kb/CHATGPT_EXPORT_UNBLOCK_AND_DELTA_RUNBOOK_V19.md",
    "tracker": ROOT / "registry/trackers/all_progress_tracker_reconciliation_v19.json",
    "visual": ROOT / "docs/trackers/JARVIS_MASTER_VISUAL_PROGRESS_TALLY_V19.md",
    "continuity": ROOT / "PROJECT_CONTINUITY.md",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> dict[str, Any]:
    for name, path in FILES.items():
        require(path.is_file(), f"missing {name}: {path}")

    register = load(FILES["register"])
    tracker = load(FILES["tracker"])
    runbook = FILES["runbook"].read_text(encoding="utf-8")
    continuity = FILES["continuity"].read_text(encoding="utf-8")
    intake = FILES["intake"].read_text(encoding="utf-8")
    ledgers = FILES["ledgers"].read_text(encoding="utf-8")

    require(register["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "false completion state")
    require(register["source_discovery"]["actual_export_bytes_found"] is False, "source access overclaim")
    require(register["source_discovery"]["state"] == "BLOCKED_BY_ACCESS", "wrong source state")
    require(register["known_baseline"]["conversation_count"] == 2610, "conversation denominator mismatch")
    require(register["known_baseline"]["message_count"] == 357835, "message denominator mismatch")
    require(len(register["intake_output_contract"]) == 13, "intake/delta output contract mismatch")

    require(tracker["version"] == "19.0.0", "tracker version mismatch")
    require(tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT", "tracker completion overclaim")
    require(any(row["workstream"] == "Master ChatGPT KB export intake and delta pipeline" for row in tracker["priority_tally"]), "V19 workstream missing")
    require(any(row["state"] == "BLOCKED_BY_ACCESS" for row in tracker["priority_tally"]), "source blocker missing")

    for token in ("delta_new_chats.csv", "delta_changed_chats.csv", "delta_removed_or_missing_review.csv", "source_manifest.json"):
        require(token in runbook, f"runbook missing {token}")
    for token in ("safe_member_name", "sha256_file", "conversation_index.jsonl", "messages.jsonl", "py7zr"):
        require(token in intake, f"intake control missing {token}")
    require(ledgers.count(".csv") >= 9, "nine KB ledgers not defined")

    for phrase in (
        "Visible Health handover denominator v2",
        "Runtime auto-resume controller",
        "Four images remain without OCR",
        "three opaque archives",
        "Command Centre v1.4",
        "Never claim all project chats are current",
        "ACTIVE_PROGRAM_NOT_100_PERCENT",
        "END_TO_END_VERIFIED",
    ):
        require(phrase in continuity, f"continuity compatibility phrase missing: {phrase}")
    require("all_progress_tracker_reconciliation_v19.json" in continuity, "continuity does not point to V19")

    return {
        "verification_id": "JARVIS-CHATGPT-KB-EXPORT-UNBLOCK-V19-VERIFY",
        "status": "PASS",
        "source_bytes_available": False,
        "known_baseline": {"conversations": 2610, "messages": 357835},
        "pipeline_state": "IMPLEMENTED_NOT_INTEGRATED",
        "remaining_blocker": "Upload a newest original ChatGPT export ZIP, conversations.json, or explicit later-chat source pack.",
        "truth_boundary": "This proves repository intake controls, tests, ledgers, tracker and blocker routing. It does not prove inaccessible archive ingestion or project-chat reconstruction.",
    }


def main() -> int:
    report = verify()
    destination = ROOT / "evidence/chatgpt-kb-export-unblock-v19-verification.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
