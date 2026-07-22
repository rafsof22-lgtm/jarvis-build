from __future__ import annotations

import csv
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from chatgpt_jsonl_attachment_preprocessor_v1 import (
    PreprocessError,
    inspect_attachment_zip,
    prepare,
)


def conversation(conversation_id: str, reference: str | None = None) -> dict:
    part = {"asset_pointer": reference, "filename": "photo.png", "mime_type": "image/png"} if reference else "hello"
    return {
        "id": conversation_id,
        "title": "Jarvis attachment test",
        "create_time": 1700000000,
        "update_time": 1700000100,
        "mapping": {
            "node-1": {
                "parent": None,
                "message": {
                    "id": "message-1",
                    "author": {"role": "user"},
                    "content": {"content_type": "multimodal_text", "parts": [part]},
                },
            }
        },
    }


class JSONLAttachmentPreprocessorTests(unittest.TestCase):
    def test_zero_byte_jsonl_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "empty.jsonl"
            source.write_bytes(b"")
            with self.assertRaises(PreprocessError):
                prepare(source, Path(temporary) / "out")

    def test_jsonl_normalization_and_exact_attachment_linkage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "export.jsonl"
            source.write_text(
                json.dumps(conversation("c1", "file-abc")) + "\n" +
                json.dumps({"conversation": conversation("c2")}) + "\n",
                encoding="utf-8",
            )
            archive = root / "attachments.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("c1/file-abc-photo.png", b"image")
                handle.writestr("other/duplicate-a.txt", b"same")
                handle.writestr("other/duplicate-b.txt", b"same")
            out = root / "out"
            report = prepare(source, out, archive)
            self.assertEqual(report["conversation_count"], 2)
            self.assertEqual(report["attachment_reference_count"], 1)
            self.assertEqual(report["linkage_status_counts"]["EXACT_IDENTIFIER"], 1)
            normalized = json.loads((out / "normalized_conversations.json").read_text(encoding="utf-8"))
            self.assertEqual([item["id"] for item in normalized], ["c1", "c2"])
            duplicates = json.loads((out / "duplicate_attachment_groups.json").read_text(encoding="utf-8"))
            self.assertEqual(len(duplicates), 1)
            with (out / "attachment_linkage.csv").open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["linkage_status"], "EXACT_IDENTIFIER")

    def test_jsonl_envelope_list_supported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "export.jsonl"
            source.write_text(json.dumps({"conversations": [conversation("c1"), conversation("c2")]}) + "\n", encoding="utf-8")
            report = prepare(source, root / "out")
            self.assertEqual(report["conversation_count"], 2)

    def test_unsafe_zip_member_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as handle:
                handle.writestr("../escape.txt", b"bad")
            with self.assertRaises(PreprocessError):
                inspect_attachment_zip(archive)


if __name__ == "__main__":
    unittest.main()
