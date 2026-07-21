"""Jarvis free-first model-router and cost-governor runtime."""
from .config import ModelRoute, ROUTING_MODES, RouterConfig
from .router import PanelDecision, RouteDecision, route_panel, route_task
from .selector import (
    ConnectedModel, ModelCatalogue, ModelResponseRecord, ParallelPanelPlan,
    SHARED_SELECTOR_SURFACES, build_model_catalogue, build_synthesis_packet,
    plan_parallel_panel, selector_surface_contract, verify_consolidated_response,
)
from .provider_execution import (
    ExecutionPolicy, PreflightDecision, ProviderCallRequest, ProviderCallResult,
    ProviderExecutor, UrllibJsonTransport,
)
from .local_models import HostCapacity, LocalModelDecision, LocalModelProfile, select_local_model
from .cost_governor import (
    BudgetPolicy, RouteQuote, UsageEstimate, cache_key, estimate_cost,
    load_provider_registry, make_batches, quote_routes, run_measured_pilot,
    select_route,
)
__all__ = [
    "BudgetPolicy", "ConnectedModel", "ExecutionPolicy", "HostCapacity",
    "LocalModelDecision", "LocalModelProfile", "ModelCatalogue", "ModelResponseRecord",
    "ModelRoute", "PanelDecision", "ParallelPanelPlan", "PreflightDecision",
    "ProviderCallRequest", "ProviderCallResult", "ProviderExecutor", "ROUTING_MODES",
    "RouteDecision", "RouteQuote", "RouterConfig", "SHARED_SELECTOR_SURFACES",
    "UrllibJsonTransport", "UsageEstimate", "build_model_catalogue",
    "build_synthesis_packet", "cache_key", "estimate_cost", "load_provider_registry",
    "make_batches", "plan_parallel_panel", "quote_routes", "route_panel", "route_task",
    "run_measured_pilot", "select_local_model", "select_route",
    "selector_surface_contract", "verify_consolidated_response",
]
