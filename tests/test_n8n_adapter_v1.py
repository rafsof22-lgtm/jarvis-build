from __future__ import annotations

import hashlib
import hmac
import unittest

from src.jarvis_completion.runtime_v1 import canonical_json
from src.jarvis_integrations import N8nAdapter, N8nExecutionPolicy, N8nRequest, ReplayStore


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str], dict, int]] = []

    def send(self, url, headers, payload, timeout):
        self.calls.append((url, dict(headers), dict(payload), timeout))
        return {"accepted": True, "execution_id": "fixture-execution"}


class N8nAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.key_material = hashlib.sha256(b"deterministic-n8n-fixture").digest()
        self.transport = FakeTransport()
        self.store = ReplayStore()
        self.adapter = N8nAdapter(
            "https://n8n.invalid/webhook/jarvis",
            self.key_material,
            replay_store=self.store,
            transport=self.transport,
        )
        self.request = N8nRequest("research-intake", {"source_id": "src-1"}, "idem-1")

    def tearDown(self) -> None:
        self.store.close()

    def policy(self, **changes) -> N8nExecutionPolicy:
        values = {
            "execution_enabled": True,
            "allowed_workflows": frozenset({"research-intake"}),
            "allowed_data_classifications": frozenset({"public", "internal"}),
        }
        values.update(changes)
        return N8nExecutionPolicy(**values)

    def test_execution_disabled_by_default(self):
        result = self.adapter.execute(self.request, N8nExecutionPolicy())
        self.assertEqual(result["state"], "BLOCKED")
        self.assertIn("EXECUTION_NOT_EXPLICITLY_ENABLED", result["preflight"]["reasons"])
        self.assertFalse(self.transport.calls)

    def test_workflow_must_be_allowlisted(self):
        result = self.adapter.execute(self.request, self.policy(allowed_workflows=frozenset()))
        self.assertIn("WORKFLOW_NOT_ALLOWLISTED", result["preflight"]["reasons"])
        self.assertFalse(self.transport.calls)

    def test_plain_http_external_endpoint_is_blocked(self):
        adapter = N8nAdapter("http://n8n.invalid/webhook/jarvis", self.key_material, transport=self.transport)
        result = adapter.execute(self.request, self.policy(allow_private_http=True))
        adapter.replay_store.close()
        self.assertIn("HTTPS_OR_APPROVED_PRIVATE_HTTP_REQUIRED", result["preflight"]["reasons"])

    def test_restricted_data_is_blocked(self):
        request = N8nRequest("research-intake", {"record": "sensitive"}, "idem-r", "restricted")
        result = self.adapter.execute(request, self.policy())
        self.assertIn("DATA_CLASSIFICATION_NOT_ALLOWED", result["preflight"]["reasons"])
        self.assertFalse(self.transport.calls)

    def test_successful_call_has_verifiable_signature_and_redacted_evidence(self):
        result = self.adapter.execute(self.request, self.policy(), timestamp=1_800_000_000)
        self.assertEqual(result["state"], "SUCCEEDED")
        self.assertTrue(result["provider_call_executed"])
        self.assertFalse(result["secret_values_exposed"])
        _, headers, payload, timeout = self.transport.calls[0]
        signed = canonical_json({
            "message_id": payload["message_id"],
            "timestamp": payload["timestamp"],
            "idempotency_key": payload["idempotency_key"],
            "payload": {"workflow_id": payload["workflow_id"], "payload": payload["payload"]},
        })
        expected = hmac.new(self.key_material, signed.encode(), hashlib.sha256).hexdigest()
        self.assertTrue(hmac.compare_digest(expected, headers["X-Jarvis-Signature"]))
        self.assertEqual(timeout, 10)
        self.assertNotIn("payload", result)
        self.assertNotIn("signature", result)

    def test_duplicate_idempotency_key_is_rejected_before_second_call(self):
        first = self.adapter.execute(self.request, self.policy())
        second = self.adapter.execute(self.request, self.policy())
        self.assertEqual(first["state"], "SUCCEEDED")
        self.assertEqual(second["state"], "REPLAY_REJECTED")
        self.assertEqual(len(self.transport.calls), 1)


if __name__ == "__main__":
    unittest.main()
