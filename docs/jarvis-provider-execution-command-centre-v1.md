# Jarvis Provider Execution, Panel Persistence and Command Centre v1.3

## Outcome

This tranche connects the concrete model selector to the primary local Command Centre, adds dependency-free provider-adapter contracts, persists panel evidence in SQLite and exposes the same control across all registered editor and builder surfaces.

## Safe execution boundary

Provider calls remain disabled by default. Execution requires all of the following:

1. an explicit execution-enabled policy;
2. a concrete configured model and endpoint;
3. a credential reference for cloud providers;
4. a known or explicitly approved cost ceiling;
5. a compatible privacy classification;
6. no more than eight concurrent calls;
7. bounded timeout and retry limits;
8. qualified review for medical, legal, financial or other high-risk conclusions.

Restricted data is local-only. Confidential cloud routing requires explicit approval. Snapshot and UI rendering never call a provider.

## Provider contracts

The standard-library runtime supports Ollama, llama.cpp, vLLM, OpenAI-compatible providers, Anthropic and Google payload/response shapes. Provider clients use injected transport interfaces for deterministic testing. Real network operation remains separately gated and evidenced.

## Durable panel evidence

SQLite stores panel identity, models, assigned roles, preflight decisions, immutable per-model raw responses, response hashes, synthesis packets, verification results and audit events. The proof key remains `selector_id + response_sha256`.

## Command Centre v1.3

The package entrypoint now runs a non-destructive v1.3 wrapper over the existing Command Centre. It adds:

- connected concrete model count;
- multi-select model control;
- `Parallel Thinking · Up to 8 LLMs`;
- panel and verified-run metrics;
- model-control, editor-surface and progress-tracker APIs;
- progress reconciliation through PRs 83–85;
- explicit live-provider and production blockers.

The original asset-intelligence and federation implementation remains intact beneath the wrapper.

## Status boundary

The adapter, persistence and local UI contracts can be `DONE_VERIFIED` or `INTEGRATED_STAGING` after exact-head CI. No external model call, provider billing, authenticated deployment, live staging canary or production service is proven by this tranche.
