import unittest

from src.jarvis_chathub.intake_v2 import ChatHubTextParserV2, build_applicability_matrix, sha256_bytes


class ChatHubTextParserV2Tests(unittest.TestCase):
    def test_role_aware_boundaries_and_verbatim_content(self):
        text = (
            "header\n"
            "**user**: exact user text\n\n"
            "**cloud-mistral-large**: # Heading\nExact answer.\n"
            "**Not a model label**: must remain inside answer\n"
            "**cloud-deepseek-v4**: second answer\n"
        )
        parsed = ChatHubTextParserV2().parse(text)
        self.assertEqual(parsed["message_count"], 3)
        self.assertEqual(parsed["response_count"], 2)
        self.assertEqual(parsed["models"], ["DeepSeek V4", "Mistral Large"])
        self.assertIn("**Not a model label**", parsed["messages"][1]["content"])
        self.assertEqual(parsed["messages"][0]["content"], "exact user text\n\n")

    def test_exact_duplicate_tracking_does_not_delete_evidence(self):
        text = "**user**: same\n**user**: same\n"
        parsed = ChatHubTextParserV2().parse(text)
        self.assertEqual(parsed["message_count"], 2)
        self.assertEqual(parsed["exact_duplicate_message_count"], 1)
        self.assertIsNone(parsed["messages"][0]["exact_duplicate_of"])
        self.assertEqual(parsed["messages"][1]["exact_duplicate_of"], 1)
        self.assertEqual(len(ChatHubTextParserV2().reproduction_view(parsed)), 1)

    def test_hash_is_deterministic(self):
        self.assertEqual(sha256_bytes(b"abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_applicability_matrix_keeps_existing_owners(self):
        matrix = build_applicability_matrix("upload:test")
        repos = {row["repository"] for row in matrix["routes"]}
        self.assertIn("Jarvis-Health", repos)
        self.assertIn("property-agent-mcp", repos)
        self.assertIn("videotranscribe", repos)
        self.assertEqual(matrix["status"], "ROUTED_NOT_FULLY_IMPLEMENTED")


if __name__ == "__main__":
    unittest.main()
