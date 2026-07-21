from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence
from urllib.parse import urlencode, urlparse


@dataclass(frozen=True)
class APIVaultPolicy:
    network_enabled: bool = False
    allowed_origins: frozenset[str] = frozenset({"https://apivault.dev"})
    timeout_seconds: int = 10
    maximum_results: int = 25
    allowed_categories: frozenset[str] = frozenset()
    require_https_candidates: bool = True
    discovery_only: bool = True
    commercial_catalogue_reuse_allowed: bool = False


@dataclass(frozen=True)
class DiscoveryRequest:
    query: str
    category: str | None = None
    maximum_results: int = 10


class APIVaultTransport(Protocol):
    def get_json(self, url: str, timeout: int) -> Any: ...


class APIVaultDiscovery:
    """Discovery-only adapter. APIVault entries are never execution approval."""

    def __init__(self, base_url: str = "https://apivault.dev", *, transport: APIVaultTransport | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.transport = transport

    def preflight(self, request: DiscoveryRequest, policy: APIVaultPolicy) -> dict[str, Any]:
        reasons: list[str] = []
        parsed = urlparse(self.base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.netloc else "UNRESOLVED"
        if not policy.network_enabled:
            reasons.append("NETWORK_NOT_EXPLICITLY_ENABLED")
        if origin not in policy.allowed_origins:
            reasons.append("ORIGIN_NOT_ALLOWLISTED")
        if parsed.scheme != "https":
            reasons.append("HTTPS_REQUIRED")
        if not request.query.strip():
            reasons.append("QUERY_REQUIRED")
        if request.category and policy.allowed_categories and request.category not in policy.allowed_categories:
            reasons.append("CATEGORY_NOT_ALLOWLISTED")
        if not 1 <= request.maximum_results <= policy.maximum_results <= 100:
            reasons.append("RESULT_LIMIT_OUT_OF_RANGE")
        if not 1 <= policy.timeout_seconds <= 30:
            reasons.append("TIMEOUT_OUT_OF_RANGE")
        if not policy.discovery_only:
            reasons.append("DISCOVERY_ONLY_REQUIRED")
        if policy.commercial_catalogue_reuse_allowed:
            reasons.append("COMMERCIAL_CATALOGUE_REUSE_PROHIBITED")
        if self.transport is None:
            reasons.append("TRANSPORT_NOT_CONFIGURED")
        return {
            "allowed": not reasons,
            "reasons": reasons,
            "origin": origin,
            "query_sha256": hashlib.sha256(request.query.strip().lower().encode()).hexdigest(),
            "catalogue_persisted": False,
            "candidate_execution_approved": False,
        }

    @staticmethod
    def normalize(item: Mapping[str, Any]) -> dict[str, Any]:
        url = str(item.get("url") or "").strip()
        category = str(item.get("category") or "unknown").strip()
        auth = str(item.get("auth") or "unknown").strip()
        cors = item.get("cors")
        https = item.get("https")
        if isinstance(https, str):
            https = https.lower() in {"yes", "true", "1"}
        if isinstance(cors, str):
            cors = cors.lower() in {"yes", "true", "1"}
        return {
            "source_id": item.get("id"),
            "name": str(item.get("name") or "Unnamed API").strip(),
            "description": str(item.get("description") or "").strip(),
            "category": category,
            "auth": auth,
            "https": bool(https),
            "cors": bool(cors) if cors is not None else None,
            "documentation_url": url,
            "source": "APIVAULT_DISCOVERY_ONLY",
            "independently_verified": False,
            "execution_approved": False,
        }

    @staticmethod
    def score(candidate: Mapping[str, Any]) -> dict[str, Any]:
        score = 0
        reasons: list[str] = []
        if candidate.get("https") is True:
            score += 30
            reasons.append("HTTPS_LISTED")
        else:
            reasons.append("HTTPS_NOT_PROVEN")
        auth = str(candidate.get("auth") or "unknown").lower()
        if auth in {"", "none", "no", "null"}:
            score += 25
            reasons.append("NO_AUTH_LISTED")
        elif auth not in {"unknown", "null"}:
            score += 10
            reasons.append("AUTH_METHOD_LISTED")
        if candidate.get("cors") is True:
            score += 10
            reasons.append("CORS_LISTED")
        if str(candidate.get("description") or "").strip():
            score += 10
            reasons.append("DESCRIPTION_PRESENT")
        if str(candidate.get("documentation_url") or "").startswith("https://"):
            score += 15
            reasons.append("HTTPS_DOCUMENTATION_URL")
        if str(candidate.get("category") or "unknown").lower() != "unknown":
            score += 10
            reasons.append("CATEGORY_PRESENT")
        return {
            **dict(candidate),
            "discovery_score": score,
            "score_reasons": reasons,
            "adoption_state": "REQUIRES_INDEPENDENT_VERIFICATION",
        }

    def search(self, request: DiscoveryRequest, policy: APIVaultPolicy) -> dict[str, Any]:
        preflight = self.preflight(request, policy)
        if not preflight["allowed"]:
            return {"state": "BLOCKED", "preflight": preflight, "provider_call_executed": False, "candidates": []}
        params = {"query": request.query.strip()}
        url = f"{self.base_url}/api/search?{urlencode(params)}"
        payload = self.transport.get_json(url, policy.timeout_seconds)
        if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes, bytearray)):
            raise ValueError("APIVault search response must be a list")
        candidates = [self.score(self.normalize(item)) for item in payload[: request.maximum_results] if isinstance(item, Mapping)]
        if policy.require_https_candidates:
            candidates = [item for item in candidates if item["https"]]
        evidence = json.dumps(candidates, sort_keys=True, separators=(",", ":"))
        return {
            "state": "DISCOVERED_NOT_VERIFIED",
            "preflight": preflight,
            "provider_call_executed": True,
            "candidate_count": len(candidates),
            "candidate_set_sha256": hashlib.sha256(evidence.encode()).hexdigest(),
            "catalogue_persisted": False,
            "candidates": candidates,
            "next_gate": "VERIFY_OFFICIAL_DOCS_TERMS_SECURITY_FREE_TIER_AND_CANARY",
        }


def route_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    category = str(candidate.get("category") or "").lower()
    text = f"{candidate.get('name', '')} {candidate.get('description', '')} {category}".lower()
    routes = []
    mapping = {
        "finance": "JARVIS_CFO_AND_MARKET_RESEARCH",
        "crypt": "JARVIS_ASSET_INTELLIGENCE_RESEARCH_ONLY",
        "health": "JARVIS_HEALTH_RESEARCH_ONLY",
        "weather": "JARVIS_CONTEXT_AND_ALERTS",
        "news": "JARVIS_INTELLIGENCE_FABRIC",
        "machine learning": "JARVIS_MODEL_AND_DATA_LAB",
        "development": "JARVIS_PRODUCT_AND_AUTOMATION_FACTORY",
        "business": "JARVIS_AGENCY_AND_CFO",
        "government": "JARVIS_LEGAL_AND_COMPLIANCE_RESEARCH",
        "transportation": "JARVIS_OPERATIONS_AND_LOGISTICS",
    }
    for token, route in mapping.items():
        if token in text and route not in routes:
            routes.append(route)
    if not routes:
        routes.append("JARVIS_GENERAL_RESEARCH_INTAKE")
    return {
        "candidate_name": candidate.get("name"),
        "routes": routes,
        "execution_state": "PROPOSAL_ONLY",
        "required_gates": [
            "OFFICIAL_DOCUMENTATION_VERIFIED",
            "CURRENT_FREE_TIER_VERIFIED",
            "TERMS_AND_LICENCE_REVIEWED",
            "SECURITY_AND_PRIVACY_REVIEWED",
            "RATE_LIMIT_AND_COST_CEILING_DEFINED",
            "BOUNDED_STAGING_CANARY_PASSED",
            "ROLLBACK_PROVEN",
        ],
    }
