"""Configuration helpers for the Jarvis model-router scaffold.

The scaffold is intentionally safe by default: local routes are preferred, cloud
routes are disabled until explicitly enabled, and no provider call is made here.
"""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class ModelRoute:
    """A configured model route without exposing secret values."""

    name: str
    provider: str
    endpoint_env: str | None = None
    api_key_env: str | None = None
    default_model_env: str | None = None
    local_first: bool = False

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

    @classmethod
    def from_env(cls) -> "RouterConfig":
        allow_cloud = os.getenv("JARVIS_ROUTER_ALLOW_CLOUD", "").lower() in {
            "1",
            "true",
            "yes",
        }
        routes = (
            ModelRoute("local", "ollama", "OLLAMA_BASE_URL", None, "OLLAMA_DEFAULT_MODEL", True),
            ModelRoute("llamacpp", "llama.cpp", "LLAMACPP_BASE_URL", None, "LLAMACPP_DEFAULT_MODEL", True),
            ModelRoute("openrouter", "openrouter", "OPENROUTER_BASE_URL", "OPENROUTER_API_KEY", "OPENROUTER_DEFAULT_MODEL"),
            ModelRoute("deepseek", "deepseek", "DEEPSEEK_BASE_URL", "DEEPSEEK_API_KEY", "DEEPSEEK_DEFAULT_MODEL"),
            ModelRoute("kimi", "kimi", "KIMI_BASE_URL", "KIMI_API_KEY", "KIMI_DEFAULT_MODEL"),
            ModelRoute("qwen", "qwen", "QWEN_BASE_URL", "QWEN_API_KEY", "QWEN_DEFAULT_MODEL"),
            ModelRoute("openai", "openai", "OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_DEFAULT_MODEL"),
        )
        return cls(
            environment=os.getenv("JARVIS_ENV", "development"),
            default_route=os.getenv("JARVIS_ROUTER_DEFAULT_ROUTE", "local"),
            allow_cloud=allow_cloud,
            routes=routes,
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
