import json
import tempfile
import unittest
from pathlib import Path

from src.jarvis_chathub.intake import (
    ChatHubDetector,
    MultiLLMConsolidator,
    RepositoryCapabilityRecord,
    write_capability_registry,
)


class ChatHubIntakeTests(unittest.TestCase):
    def test_filename_detection(self):
        self.assertTrue(ChatHubDetector.is_chathub_filename("PC Build & Stack ChatHub.txt"))
        self.assertTrue(ChatHubDetector.is_chathub_filename("chathub-export.json"))
        self.assertFalse(ChatHubDetector.is_chathub_filename("ordinary-notes.txt"))

    def test_lossless_ingest_and_parallel_json(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "project ChatHub.json"
            payload = {
                "models": ["alpha", "beta"],
                "messages": [{"user": "question", "responses": ["Exact A", "Exact B"]}],
            }
            raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            source.write_bytes(raw)
            record = ChatHubDetector().ingest_file(source, root / "vault")
            self.assertEqual(record.response_count, 2)
            self.assertEqual(record.models, ("alpha", "beta"))
            self.assertTrue(record.raw_text_preserved)
            vault_files = list((root / "vault").iterdir())
            self.assertEqual(len(vault_files), 1)
            self.assertEqual(vault_files[0].read_bytes(), raw)

    def test_text_responses_are_not_rewritten(self):
        text = "Model: GPT\nFirst exact response.\nLLM: Claude\nSecond exact response.\n"
        parsed = MultiLLMConsolidator().parse_bytes(text.encode("utf-8"), ".txt")
        self.assertEqual(parsed["responses"][0]["content"], "First exact response.\n")
        self.assertEqual(parsed["responses"][1]["content"], "Second exact response.\n")
        manifest = MultiLLMConsolidator().consolidate_manifest(parsed, "upload:test")
        self.assertEqual(manifest["synthesis_status"], "PENDING_SEPARATE_DERIVATION")

    def test_non_chathub_filename_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "notes.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                ChatHubDetector().ingest_file(source, Path(temp) / "vault")

    def test_capability_registry(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "registry.json"
            result = write_capability_registry(
                [RepositoryCapabilityRecord("chathub-dev/chathub", "main", "GPL-3.0", "MULTI_LLM_UI", "STATICALLY_REVIEWED", "MODERATE_REVIEW_REQUIRED", "github:README")],
                output,
            )
            self.assertEqual(result["count"], 1)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
