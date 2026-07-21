from __future__ import annotations

import unittest

from src.jarvis_integrations import APIVaultDiscovery, APIVaultPolicy, DiscoveryRequest, route_candidate


class FakeTransport:
    def __init__(self, payload=None):
        self.payload = payload if payload is not None else []
        self.calls = []

    def get_json(self, url, timeout):
        self.calls.append((url, timeout))
        return self.payload


class APIVaultDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.payload = [
            {"id": 1, "name": "Weather Alpha", "auth": "No", "category": "Weather", "cors": True, "description": "Forecast data", "https": True, "url": "https://weather.example/docs"},
            {"id": 2, "name": "Unsafe HTTP", "auth": "apiKey", "category": "Development", "cors": False, "description": "HTTP only", "https": False, "url": "http://unsafe.example/docs"},
        ]
        self.transport = FakeTransport(self.payload)
        self.adapter = APIVaultDiscovery(transport=self.transport)

    def policy(self, **changes):
        values = {"network_enabled": True}
        values.update(changes)
        return APIVaultPolicy(**values)

    def test_network_disabled_by_default(self):
        result = self.adapter.search(DiscoveryRequest("weather"), APIVaultPolicy())
        self.assertEqual(result["state"], "BLOCKED")
        self.assertIn("NETWORK_NOT_EXPLICITLY_ENABLED", result["preflight"]["reasons"])
        self.assertFalse(self.transport.calls)

    def test_origin_must_be_allowlisted(self):
        adapter = APIVaultDiscovery("https://evil.example", transport=self.transport)
        result = adapter.search(DiscoveryRequest("weather"), self.policy())
        self.assertIn("ORIGIN_NOT_ALLOWLISTED", result["preflight"]["reasons"])

    def test_plain_http_is_blocked(self):
        adapter = APIVaultDiscovery("http://apivault.dev", transport=self.transport)
        result = adapter.search(DiscoveryRequest("weather"), self.policy(allowed_origins=frozenset({"http://apivault.dev"})))
        self.assertIn("HTTPS_REQUIRED", result["preflight"]["reasons"])

    def test_query_is_required(self):
        result = self.adapter.search(DiscoveryRequest("  "), self.policy())
        self.assertIn("QUERY_REQUIRED", result["preflight"]["reasons"])

    def test_commercial_catalogue_reuse_is_rejected(self):
        result = self.adapter.search(DiscoveryRequest("weather"), self.policy(commercial_catalogue_reuse_allowed=True))
        self.assertIn("COMMERCIAL_CATALOGUE_REUSE_PROHIBITED", result["preflight"]["reasons"])

    def test_result_limit_is_bounded(self):
        result = self.adapter.search(DiscoveryRequest("weather", maximum_results=30), self.policy(maximum_results=25))
        self.assertIn("RESULT_LIMIT_OUT_OF_RANGE", result["preflight"]["reasons"])

    def test_search_filters_non_https_candidates(self):
        result = self.adapter.search(DiscoveryRequest("weather"), self.policy())
        self.assertEqual(result["state"], "DISCOVERED_NOT_VERIFIED")
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(result["candidates"][0]["name"], "Weather Alpha")
        self.assertFalse(result["catalogue_persisted"])
        self.assertFalse(result["candidates"][0]["execution_approved"])

    def test_search_encodes_query_and_observes_timeout(self):
        self.adapter.search(DiscoveryRequest("weather alerts"), self.policy(timeout_seconds=7))
        url, timeout = self.transport.calls[0]
        self.assertIn("query=weather+alerts", url)
        self.assertEqual(timeout, 7)

    def test_score_preserves_verification_gate(self):
        candidate = self.adapter.score(self.adapter.normalize(self.payload[0]))
        self.assertGreaterEqual(candidate["discovery_score"], 80)
        self.assertEqual(candidate["adoption_state"], "REQUIRES_INDEPENDENT_VERIFICATION")

    def test_route_is_proposal_only_with_seven_gates(self):
        routed = route_candidate(self.adapter.normalize(self.payload[0]))
        self.assertIn("JARVIS_CONTEXT_AND_ALERTS", routed["routes"])
        self.assertEqual(routed["execution_state"], "PROPOSAL_ONLY")
        self.assertEqual(len(routed["required_gates"]), 7)

    def test_invalid_response_shape_fails_closed(self):
        adapter = APIVaultDiscovery(transport=FakeTransport({"unexpected": True}))
        with self.assertRaises(ValueError):
            adapter.search(DiscoveryRequest("weather"), self.policy())


if __name__ == "__main__":
    unittest.main()
