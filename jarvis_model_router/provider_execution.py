"""Governed provider execution for Jarvis parallel panels.

Network calls are disabled by default. Preflight never exposes credentials and execution
requires an explicit policy, a configured concrete model, privacy approval and a bounded
cost/timeout envelope. Tests inject a transport; no external provider is contacted.
"""
from __future__ import annotations

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import ModelRoute, RouterConfig
from .selector import ConnectedModel, ModelCatalogue, ModelResponseRecord, ParallelPanelPlan

DATA_CLASSES = {"public", "internal", "confidential", "restricted"}
OPENAI_COMPATIBLE = {"openai", "openrouter", "deepseek", "kimi", "qwen", "groq", "mistral", "vllm", "llama.cpp"}
DEFAULT_ENDPOINTS = {
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "mistral": "https://api.mistral.ai/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta",
    "ollama": "http://127.0.0.1:11434",
    "llama.cpp": "http://127.0.0.1:8080/v1",
    "vllm": "http://127.0.0.1:8000/v1",
}


def _safe_env_key(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


@dataclass(frozen=True)
class ExecutionPolicy:
    execution_enabled: bool = False
    data_classification: str = "internal"
    maximum_total_cost_usd: float = 0.0
    allow_cloud_confidential: bool = False
    allow_unknown_cost: bool = False
    timeout_seconds: int = 60
    maximum_retries: int = 1
    maximum_parallel_calls: int = 8
    maximum_prompt_characters: int = 200_000
    high_risk_domain: bool = False

    def validate(self) -> None:
        if self.data_classification not in DATA_CLASSES:
            raise ValueError("invalid data classification")
        if self.maximum_total_cost_usd < 0:
            raise ValueError("maximum cost cannot be negative")
        if not 1 <= self.maximum_parallel_calls <= 8:
            raise ValueError("maximum_parallel_calls must be 1-8")
        if not 1 <= self.timeout_seconds <= 600:
            raise ValueError("timeout_seconds must be 1-600")
        if not 0 <= self.maximum_retries <= 3:
            raise ValueError("maximum_retries must be 0-3")


@dataclass(frozen=True)
class ProviderCallRequest:
    selector_id: str
    role: str
    prompt: str
    system_prompt: str = ""
    max_output_tokens: int = 2048


@dataclass(frozen=True)
class PreflightDecision:
    selector_id: str
    allowed: bool
    reasons: tuple[str, ...]
    route_name: str
    provider: str
    model_id: str
    endpoint_source: str
    credential_reference: str | None
    estimated_cost_usd: float | None
    cost_known: bool
    data_classification: str
    execution_enabled: bool
    secret_values_exposed: bool = False


@dataclass(frozen=True)
class ProviderCallResult:
    selector_id: str
    role: str
    state: str
    raw_text: str
    latency_ms: int
    attempts: int
    estimated_cost_usd: float | None
    error_type: str | None = None
    citations: tuple[str, ...] = ()

    def response_record(self) -> ModelResponseRecord:
        if self.state != "SUCCEEDED":
            raise RuntimeError("failed provider call cannot become a response record")
        return ModelResponseRecord(self.selector_id, self.role, self.raw_text, self.citations)


class Transport(Protocol):
    def send(self, url: str, headers: Mapping[str, str], payload: Mapping[str, Any], timeout: int) -> Mapping[str, Any]: ...


class UrllibJsonTransport:
    def send(self, url: str, headers: Mapping[str, str], payload: Mapping[str, Any], timeout: int) -> Mapping[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(url, data=body, headers={**headers, "Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))


class ProviderExecutor:
    def __init__(self, config: RouterConfig, catalogue: ModelCatalogue, *, environ: Mapping[str, str] | None = None, transport: Transport | None = None) -> None:
        self.config = config
        self.catalogue = catalogue
        self.env = environ if environ is not None else os.environ
        self.transport = transport or UrllibJsonTransport()
        self.routes = {route.name: route for route in config.routes}

    def _route(self, model: ConnectedModel) -> ModelRoute:
        route = self.routes.get(model.route_name)
        if route is None:
            raise KeyError(model.route_name)
        return route

    def _endpoint(self, route: ModelRoute) -> tuple[str | None, str]:
        if route.endpoint_env and self.env.get(route.endpoint_env):
            return self.env[route.endpoint_env].rstrip("/"), f"env:{route.endpoint_env}"
        default = DEFAULT_ENDPOINTS.get(route.provider)
        return (default.rstrip("/"), "provider_default") if default else (None, "missing")

    def _cost(self, model: ConnectedModel, prompt: str, max_output_tokens: int) -> tuple[float | None, bool]:
        if model.local_first:
            return 0.0, True
        selector_key = _safe_env_key(model.selector_id)
        direct = self.env.get(f"JARVIS_MODEL_ESTIMATED_COST_USD_{selector_key}")
        if direct is not None:
            try:
                return max(0.0, float(direct)), True
            except ValueError:
                return None, False
        route_key = _safe_env_key(model.route_name)
        input_rate = self.env.get(f"JARVIS_{route_key}_INPUT_USD_PER_1M")
        output_rate = self.env.get(f"JARVIS_{route_key}_OUTPUT_USD_PER_1M")
        if input_rate is None or output_rate is None:
            return None, False
        try:
            in_tokens = max(1, len(prompt) // 4)
            return (in_tokens * float(input_rate) + max_output_tokens * float(output_rate)) / 1_000_000, True
        except ValueError:
            return None, False

    def preflight(self, request: ProviderCallRequest, policy: ExecutionPolicy) -> PreflightDecision:
        policy.validate()
        model = self.catalogue.get(request.selector_id)
        route = self._route(model)
        endpoint, endpoint_source = self._endpoint(route)
        reasons: list[str] = []
        if not request.prompt.strip(): reasons.append("EMPTY_PROMPT")
        if len(request.prompt) > policy.maximum_prompt_characters: reasons.append("PROMPT_LIMIT_EXCEEDED")
        if policy.data_classification == "restricted" and not model.local_first: reasons.append("RESTRICTED_DATA_LOCAL_ONLY")
        if policy.data_classification == "confidential" and not model.local_first and not policy.allow_cloud_confidential: reasons.append("CONFIDENTIAL_CLOUD_NOT_APPROVED")
        if not model.local_first and not self.config.allow_cloud: reasons.append("CLOUD_ROUTING_DISABLED")
        if not endpoint: reasons.append("ENDPOINT_NOT_CONFIGURED")
        credential_ref = route.api_key_env
        if route.api_key_env and not self.env.get(route.api_key_env): reasons.append("CREDENTIAL_REFERENCE_NOT_READY")
        estimated, cost_known = self._cost(model, request.prompt, request.max_output_tokens)
        if not cost_known and not model.local_first and not policy.allow_unknown_cost: reasons.append("COST_UNKNOWN")
        if estimated is not None and estimated > policy.maximum_total_cost_usd: reasons.append("BUDGET_EXCEEDED")
        if not policy.execution_enabled: reasons.append("EXECUTION_NOT_EXPLICITLY_ENABLED")
        if policy.high_risk_domain: reasons.append("QUALIFIED_REVIEW_REQUIRED_AFTER_EXECUTION")
        blocking = [reason for reason in reasons if reason != "QUALIFIED_REVIEW_REQUIRED_AFTER_EXECUTION"]
        return PreflightDecision(request.selector_id, not blocking, tuple(reasons), route.name, route.provider, model.model_id, endpoint_source, credential_ref, estimated, cost_known, policy.data_classification, policy.execution_enabled)

    def _build_call(self, request: ProviderCallRequest) -> tuple[str, dict[str, str], dict[str, Any]]:
        model = self.catalogue.get(request.selector_id)
        route = self._route(model)
        endpoint, _ = self._endpoint(route)
        if not endpoint:
            raise RuntimeError("endpoint missing")
        key = self.env.get(route.api_key_env or "") if route.api_key_env else None
        provider = route.provider
        if provider == "ollama":
            messages = ([{"role": "system", "content": request.system_prompt}] if request.system_prompt else []) + [{"role": "user", "content": request.prompt}]
            return endpoint + "/api/chat", {}, {"model": model.model_id, "messages": messages, "stream": False}
        if provider == "anthropic":
            headers = {"x-api-key": key or "", "anthropic-version": "2023-06-01"}
            payload: dict[str, Any] = {"model": model.model_id, "max_tokens": request.max_output_tokens, "messages": [{"role": "user", "content": request.prompt}]}
            if request.system_prompt:
                payload["system"] = request.system_prompt
            return endpoint + "/messages", headers, payload
        if provider == "google":
            suffix = f"/models/{model.model_id}:generateContent"
            return endpoint + suffix, {"x-goog-api-key": key or ""}, {"contents": [{"role": "user", "parts": [{"text": request.prompt}]}], "generationConfig": {"maxOutputTokens": request.max_output_tokens}}
        if provider in OPENAI_COMPATIBLE:
            headers = {"Authorization": f"Bearer {key}"} if key else {}
            messages = ([{"role": "system", "content": request.system_prompt}] if request.system_prompt else []) + [{"role": "user", "content": request.prompt}]
            return endpoint + "/chat/completions", headers, {"model": model.model_id, "messages": messages, "max_tokens": request.max_output_tokens}
        raise RuntimeError("unsupported provider adapter")

    @staticmethod
    def _extract(provider: str, payload: Mapping[str, Any]) -> str:
        if provider == "ollama":
            return str(payload.get("message", {}).get("content", ""))
        if provider == "anthropic":
            return "\n".join(str(item.get("text", "")) for item in payload.get("content", []) if isinstance(item, Mapping))
        if provider == "google":
            candidates = payload.get("candidates", [])
            if not candidates:
                return ""
            return "\n".join(str(item.get("text", "")) for item in candidates[0].get("content", {}).get("parts", []))
        choices = payload.get("choices", [])
        return str(choices[0].get("message", {}).get("content", "")) if choices else ""

    def execute(self, request: ProviderCallRequest, policy: ExecutionPolicy) -> tuple[PreflightDecision, ProviderCallResult]:
        decision = self.preflight(request, policy)
        if not decision.allowed:
            return decision, ProviderCallResult(request.selector_id, request.role, "BLOCKED", "", 0, 0, decision.estimated_cost_usd, "PREFLIGHT_BLOCKED")
        model = self.catalogue.get(request.selector_id)
        route = self._route(model)
        url, headers, payload = self._build_call(request)
        started = time.monotonic()
        attempts = 0
        last_error: Exception | None = None
        while attempts <= policy.maximum_retries:
            attempts += 1
            try:
                response = self.transport.send(url, headers, payload, policy.timeout_seconds)
                text = self._extract(route.provider, response)
                if not text.strip():
                    raise ValueError("empty provider response")
                return decision, ProviderCallResult(request.selector_id, request.role, "SUCCEEDED", text, round((time.monotonic() - started) * 1000), attempts, decision.estimated_cost_usd)
            except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError, OSError) as exc:
                last_error = exc
        return decision, ProviderCallResult(request.selector_id, request.role, "FAILED", "", round((time.monotonic() - started) * 1000), attempts, decision.estimated_cost_usd, last_error.__class__.__name__ if last_error else "UNKNOWN")

    def execute_panel(self, plan: ParallelPanelPlan, prompt: str, policy: ExecutionPolicy, *, system_prompt: str = "") -> dict[str, Any]:
        policy.validate()
        requests = [ProviderCallRequest(model.selector_id, role, prompt, system_prompt) for model, role in zip(plan.selected_models, plan.roles)]
        decisions = [self.preflight(request, policy) for request in requests]
        estimated = sum(decision.estimated_cost_usd or 0.0 for decision in decisions)
        if estimated > policy.maximum_total_cost_usd:
            return {"state": "PREFLIGHT_BLOCKED", "reason": "PANEL_BUDGET_EXCEEDED", "preflights": [asdict(decision) for decision in decisions], "results": []}
        if any(not decision.allowed for decision in decisions):
            return {"state": "PREFLIGHT_BLOCKED", "preflights": [asdict(decision) for decision in decisions], "results": []}
        results: list[ProviderCallResult] = []
        workers = min(len(requests), policy.maximum_parallel_calls, 8)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(self.execute, request, policy): request.selector_id for request in requests}
            for future in as_completed(futures):
                _, result = future.result()
                results.append(result)
        request_order = [request.selector_id for request in requests]
        results.sort(key=lambda result: request_order.index(result.selector_id))
        state = "RESPONSES_CAPTURED" if all(result.state == "SUCCEEDED" for result in results) else "FAILED"
        return {"state": state, "preflights": [asdict(decision) for decision in decisions], "results": [asdict(result) for result in results], "qualified_review_required": policy.high_risk_domain, "secret_values_exposed": False}
