"""Governed source-adapter plans for XRP/HBAR intelligence.

This module defines allowlisted, read-only adapter metadata and request plans. It does
not call a network, read credentials, execute trades or change provider state.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class SourceAdapter:
    adapter_id: str
    assets: tuple[str, ...]
    authority: str
    base_url: str
    paths: tuple[str, ...]
    auth_env_name: str | None = None
    rate_limit_per_minute: int = 30
    timeout_seconds: int = 8
    maximum_attempts: int = 2
    cost_class: str = "free_public"
    write_enabled: bool = False

    def validate(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"Adapter {self.adapter_id} requires an HTTPS base URL")
        if self.write_enabled:
            raise ValueError(f"Adapter {self.adapter_id} must remain read-only")
        if self.maximum_attempts > 2 or self.timeout_seconds > 10:
            raise ValueError(f"Adapter {self.adapter_id} exceeds bounded retry or timeout policy")

    def request_plans(self) -> list[dict[str, object]]:
        self.validate()
        return [
            {
                "adapter_id": self.adapter_id,
                "asset_scope": list(self.assets),
                "url": self.base_url.rstrip("/") + path,
                "method": "GET",
                "authority": self.authority,
                "authentication_name_only": self.auth_env_name,
                "timeout_seconds": self.timeout_seconds,
                "maximum_attempts": self.maximum_attempts,
                "cost_class": self.cost_class,
                "write_enabled": False,
                "evidence_required": True,
            }
            for path in self.paths
        ]


OFFICIAL_ADAPTERS = (
    SourceAdapter("XRPL-DOCS", ("XRP",), "official_protocol", "https://xrpl.org", ("/blog", "/docs/concepts/networks-and-servers/amendments")),
    SourceAdapter("RIPPLE-INSIGHTS", ("XRP",), "official_company", "https://ripple.com", ("/insights/", "/insights/category/xrp/")),
    SourceAdapter("XRPL-GITHUB", ("XRP",), "official_repository", "https://api.github.com", ("/repos/XRPLF/rippled/releases",), "GITHUB_TOKEN", 20),
    SourceAdapter("SEC-FILINGS", ("XRP", "HBAR"), "official_regulator", "https://www.sec.gov", ("/edgar/search/",), None, 10),
    SourceAdapter("HEDERA-BLOG", ("HBAR",), "official_network", "https://hedera.com", ("/blog/",)),
    SourceAdapter("HEDERA-MIRROR", ("HBAR",), "official_chain_api", "https://mainnet-public.mirrornode.hedera.com", ("/api/v1/network/supply", "/api/v1/transactions?limit=1")),
    SourceAdapter("HIERO-GITHUB", ("HBAR",), "official_repository", "https://api.github.com", ("/repos/hiero-ledger/hiero-consensus-node/releases", "/repos/hiero-ledger/hiero-mirror-node/releases"), "GITHUB_TOKEN", 20),
)


def build_official_adapter_manifest() -> dict[str, object]:
    plans: list[dict[str, object]] = []
    for adapter in OFFICIAL_ADAPTERS:
        plans.extend(adapter.request_plans())
    return {
        "manifest_id": "XRP-HBAR-OFFICIAL-SOURCE-ADAPTERS-V1",
        "state": "IMPLEMENTED_NOT_INTEGRATED",
        "adapters": [asdict(adapter) for adapter in OFFICIAL_ADAPTERS],
        "request_plans": plans,
        "network_calls_performed": False,
        "writes_enabled": False,
        "secret_values_exposed": False,
        "runtime_gate": "Connect in Hub staging with persistence, rate-limit, freshness, idempotency, evidence and rollback tests.",
    }
