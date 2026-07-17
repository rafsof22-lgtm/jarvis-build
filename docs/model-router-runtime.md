# Jarvis Model-Router Runtime Scaffold

## Purpose

This scaffold gives Jarvis a small, testable runtime layer for selecting worker-model routes without calling any provider APIs. It supports the standing free-first direction:

- local Ollama or llama.cpp routes first
- optional cloud routes only when explicitly enabled
- no secrets committed to the repository
- CI smoke checks before any deployment work

## Files

- `jarvis_model_router/config.py` loads route names and provider environment-variable names.
- `jarvis_model_router/router.py` maps task types to the safest available route.
- `scripts/smoke_model_router.py` proves the default local/free-first routing behavior.
- `.env.example` lists variable names only and keeps values blank.

## Default Behavior

Cloud routing is disabled unless `JARVIS_ROUTER_ALLOW_CLOUD` is set to `true`, `yes`, or `1` in the runtime environment.

With no secrets present, the router should still return local/free-first routes for smoke-testable task classes. This is deliberate: Jarvis must remain useful in local and free-tier environments before paid or external API routes are added.

## Later Implementation Gates

Before adding live provider clients, prove the following:

- selected provider is still available and cost-effective
- secret is stored in GitHub/provider secret storage, not in repository files
- route has a smoke test that can run without spending paid credits
- high-risk decisions still route through an approval or verification layer
- fallback behavior is explicit when a provider is unavailable
