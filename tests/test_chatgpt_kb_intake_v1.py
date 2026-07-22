from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chatgpt_kb_intake_v1 import IntakeError, build_outputs, delta_scan, inspect_zip


def conversation(conversation_id: str, title: str, messages: list[tuple[str, str]]) -> dict:
    mapping: dict[str, dict] = {}
    previous = None
    for index, (role, text) in enumerate(messages):
        node_id = f"node-{conversation_id}-{index}"
        message_id = f"message-{conversation_id}-{index}"
        mapping[node_id] = {
            "id": node_id,
            "parent": previous,
            "children": [],
            "message": {
                "id": message_id,
                "author": {"role": role},
                "create_time": 1700000000 + index,
                "content": {"content_type": "text", "parts": [text]},
            },
        }
        if previous:
            mapping[previous]["children"].append(node_id)
        previous = node_id
    return {
        "id": conversation_id,
        "title": title,
        "create_time": 1700000000,
        "update_time": 1700000100,
        "mapping": mapping,
    }


class ChatGPTKBIntakeTests(unittest.TestCase):
    def test_json_zip_and_delta(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline_json = root / "baseline.json"
            current_json = root / "current.json"
            baseline_json.write_text(json.dumps([
                conversation("c1", "Jarvis plan", [("user", "Build Jarvis agent"), ("assistant", "Plan")]),
            ]), encoding="utf-8")
            current_json.write_text(json.dumps([
                conversation("c1", "Jarvis plan", [("user", "Build Jarvis agent updated"), ("assistant", "Plan")]),
                conversation("c2", "XRP update", [("user", "Track Ripple XRP"), ("assistant", "Research only")]),
            ]), encoding="utf-8")

            baseline_output = root / "baseline-output"
            current_output = root / "current-output"
            baseline_report = build_outputs(baseline_json, baseline_output)
            current_report = build_outputs(current_json, current_output)
            self.assertEqual(baseline_report["conversation_count"], 1)
            self.assertEqual(current_report["conversation_count"], 2)
            self.assertTrue(current_report["reconciled"])

            delta = delta_scan(baseline_output, current_output, root / "delta")
            self.assertEqual(delta["new_count"], 1)
            self.assertEqual(delta["changed_count"], 1)
            self.assertEqual(delta["removed_or_missing_review_count"], 0)

            archive = root / "export.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("account/conversations.json", current_json.read_bytes())
            zip_report = build_outputs(archive, root / "zip-output")
            self.assertEqual(zip_report["conversation_count"], 2)

    def test_unsafe_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("../conversations.json", "[]")
            with self.assertRaises(IntakeError):
                inspect_zip(archive)

    def test_executable_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("conversations.json", "[]")
                handle.writestr("payload.exe", b"MZ")
            with self.assertRaises(IntakeError):
                inspect_zip(archive)


if __name__ == "__main__":
    unittest.main()
