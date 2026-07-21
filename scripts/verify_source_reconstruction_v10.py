from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def main() -> None:
    chat = load("registry/sources/chatgpt_export_2026_06_25_denominator_v1.json")
    sources = load("registry/sources/uploaded_source_universe_2026_07_21_v1.json")
    tracker = load("registry/trackers/all_progress_tracker_reconciliation_v10.json")

    assert chat["counts"]["conversations"] == 2610
    assert chat["counts"]["messages"] == 357835
    assert sum(chat["role_counts"].values()) == 357835
    assert chat["parse_errors"] == 0

    projects = chat["requested_project_denominator"]
    assert projects["project_count"] == 10
    assert projects["conversation_count"] == 430
    assert projects["message_count"] == 123175

    assert sources["top_level_source_count"] == 51
    assert sources["archive_count"] >= 11
    assert all(item["unsafe_member_count"] == 0 for item in sources["archives"])

    assert tracker["program_state"] == "ACTIVE_PROGRAM_NOT_100_PERCENT"
    assert tracker["next_safe_openloop"]

    serialized = json.dumps([chat, sources, tracker]).lower()
    for token in ["api_key=", "access_token=", "private_key=", "password="]:
        assert token not in serialized

    print("source-reconstruction-v10 verification passed")


if __name__ == "__main__":
    main()
