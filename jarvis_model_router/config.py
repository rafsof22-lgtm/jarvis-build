"""Configuration helpers for the Jarvis model-router scaffold.

The scaffold is intentionally safe by default: deterministic and local routes are
preferred, cloud routes are disabled until explicitly enabled, and no provider call
is made here. The user-facing "Jailbroken LLM Model Routing" label means the least
unnecessarily restrictive *approved and compliant* route; it never bypasses law,
security, privacy, provider terms, approval gates or Jarvis policy.
"""

from __future__ import annotations

from dataclasses import dataclass
import os


ROUTING_MODES = {
    "normal",
    "lowest_restriction",
    "local_sovereign",
    "offline_private",
    "highest_parameter_local",
    "fast_local",
    "free_first",
    "cheapest_effective",
    "quality_first",
    "parallel_intelligence",
    "manual_model",
}


@dataclass(frozen=True)
class ModelRoute:
    """A configured model route without exposing secret values."""

    name: str
    provider: str
    endpoint_env: str | None = None
    api_key_env: str | None = None
    default_model_env: str | None = None
    local_first: bool = False
    cost_class: str = "unknown"
    privacy_class: str = "provider_policy_required"
    restriction_class: str = "standard_compliant"

    def is_configured(self) -> bool:
        if self.local_first:
            return True
        if not self.api_key_env:
            return False
        return bool(os.getenv(self.api_key_env))


@dataclass(frozen=True)
class RouterConfig:
    """Runtime config loaded from environment variable names only."""

    environment: str
    default_route: str
    allow_cloud: bool
    routes: tuple[ModelRoute, ...]
    routing_mode: str = "free_first"
    manual_route: str | None = None

    @classmethod
    def from_env(cls) -> "RouterConfig":
        allow_cloud = os.getenv("JARVIS_ROUTER_ALLOW_CLOUD", "").lower() in {
            "1",
            "true",
            "yes",
        }
        requested_mode = os.getenv("JARVIS_ROUTER_MODE", "free_first").strip().lower()
        routing_mode = requested_mode if requested_mode in ROUTING_MODES else "free_first"
        routes = (
            ModelRoute("local", "ollama", "OLLAMA_BASE_URL", None, "OLLAMA_DEFAULT_MODEL", True, "owned_compute", "local_private", "lowest_restriction_compliant"),
            ModelRoute("llamacpp", "llama.cpp", "LLAMACPP_BASE_URL", None, "LLAMACPP_DEFAULT_MODEL", True, "owned_compute", "local_private", "lowest_restriction_compliant"),
            ModelRoute("vllm", "vllm", "VLLM_BASE_URL", None, "VLLM_DEFAULT_MODEL", True, "owned_compute", "local_private", "lowest_restriction_compliant"),
            ModelRoute("openrouter", "openrouter", "OPENROUTER_BASE_URL", "OPENROUTER_API_KEY", "OPENROUTER_DEFAULT_MODEL", False, "variable", "provider_policy_required", "route_specific"),
            ModelRoute("deepseek", "deepseek", "DEEPSEEK_BASE_URL", "DEEPSEEK_API_KEY", "DEEPSEEK_DEFAULT_MODEL", False, "economy", "provider_policy_required", "standard_compliant"),
            ModelRoute("kimi", "kimi", "KIMI_BASE_URL", "KIMI_API_KEY", "KIMI_DEFAULT_MODEL", False, "economy", "provider_policy_required", "standard_compliant"),
            ModelRoute("qwen", "qwen", "QWEN_BASE_URL", "QWEN_API_KEY", "QWEN_DEFAULT_MODEL", False, "economy", "provider_policy_required", "standard_compliant"),
            ModelRoute("groq", "groq", "GROQ_BASE_URL", "GROQ_API_KEY", "GROQ_DEFAULT_MODEL", False, "economy", "provider_policy_required", "standard_compliant"),
            ModelRoute("mistral", "mistral", "MISTRAL_BASE_URL", "MISTRAL_API_KEY", "MISTRAL_DEFAULT_MODEL", False, "balanced", "provider_policy_required", "standard_compliant"),
            ModelRoute("google", "google", "GOOGLE_BASE_URL", "GOOGLE_API_KEY", "GOOGLE_DEFAULT_MODEL", False, "balanced", "provider_policy_required", "standard_compliant"),
            ModelRoute("anthropic", "anthropic", "ANTHROPIC_BASE_URL", "ANTHROPIC_API_KEY", "ANTHROPIC_DEFAULT_MODEL", False, "premium", "provider_policy_required", "standard_compliant"),
            ModelRoute("openai", "openai", "OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_DEFAULT_MODEL", False, "premium", "provider_policy_required", "standard_compliant"),
        )
        return cls(
            environment=os.getenv("JARVIS_ENV", "development"),
            default_route=os.getenv("JARVIS_ROUTER_DEFAULT_ROUTE", "local"),
            allow_cloud=allow_cloud,
            routes=routes,
            routing_mode=routing_mode,
            manual_route=os.getenv("JARVIS_ROUTER_MANUAL_ROUTE") or None,
        )

    def available_routes(self) -> tuple[ModelRoute, ...]:
        if self.allow_cloud:
            return tuple(route for route in self.routes if route.is_configured())
        return tuple(route for route in self.routes if route.local_first)

    def route_by_name(self, name: str) -> ModelRoute | None:
        for route in self.available_routes():
            if route.name == name:
                return route
        return None
