# Jarvis Hybrid Model Router Plan

## Purpose

This file defines the recommended architecture for using ChatGPT as the Jarvis control plane while offloading bulk worker tasks to cheaper or local models where appropriate.

This does not replace the ChatGPT Agent Builder core reasoning model. ChatGPT remains the native orchestrator. External models are used through a deployed runtime, API, app, MCP, or repo-backed worker layer.

## Recommended Architecture

```text
ChatGPT Jarvis Agent
        |
        v
Jarvis Task Router / Runtime API
        |
        +--> GPT/OpenAI models: critical reasoning, final decisions, safety checks
        +--> DeepSeek: coding and patch generation
        +--> Kimi: long-context reading and research synthesis
        +--> Qwen: classification, extraction, bulk analysis
        +--> Local Llama/Ollama/llama.cpp: repetitive jobs and private zero-token fallback
        +--> OCR/Vision models: document/image extraction when required
```

## Why This Is The Best Route

- Preserves native ChatGPT Agent features.
- Avoids pretending the Builder core model can be replaced with third-party models.
- Reduces costs by routing lower-risk bulk work to cheaper workers.
- Keeps GPT-level reasoning for planning, verification, safety, and final decisions.
- Enables future runtime deployment with OpenRouter, LiteLLM, or direct provider APIs.

## Options Comparison

| Option | Description | Pros | Cons | Recommendation |
|---|---|---|---|---|
| ChatGPT orchestrator + cheaper workers | ChatGPT plans; runtime routes sub-tasks to cheaper/local models | Best balance of quality, native features, and cost | Requires runtime/API setup | Recommended |
| Replace GPT entirely | Standalone DeepSeek/Kimi/Qwen agent runtime | Cheap and scalable | Loses native ChatGPT Agent features | Use only for standalone workers |
| Make ChatGPT Agent internally use third-party model | Change Builder core model to Kimi/DeepSeek/Qwen | Would be ideal if supported | Not currently supported in Builder | Not available |

## Task-To-Model Routing

| Task | Preferred Model/Route | Fallback | Notes |
|---|---|---|---|
| Master planning | GPT/OpenAI in ChatGPT | High-quality reasoning model via OpenRouter | Keep final authority in Jarvis |
| Safety checks | GPT/OpenAI in ChatGPT | second verification model | Do not route high-risk decisions only to cheap workers |
| Coding | DeepSeek | Qwen Coder / GPT | Strong cost-performance for code |
| Long documents | Kimi | Qwen long-context / GPT | Good for large context if available |
| Bulk classification | Qwen | local Llama / DeepSeek | Cheap and parallelizable |
| Extraction | Qwen / DeepSeek | local model | Use schemas and validation |
| Embeddings | cheap embedding model | local embedding model | Avoid expensive embeddings unless needed |
| OCR | local OCR / vision model | cloud OCR | Prefer local/free where quality is enough |
| Repetitive workers | local Llama/Ollama | cheapest cloud worker | Zero-token after hardware |
| Final answer synthesis | GPT/OpenAI in ChatGPT | top reasoning route | Preserve quality and safety |

## Runtime Implementation Choices

### Free-First

- GitHub repo for code and CI.
- Oracle Cloud Free Tier for runtime host if available.
- Local Ollama/llama.cpp for zero-token workers.
- Free-tier model APIs where available.
- GitHub Actions for smoke tests.

### Cheapest Paid

- Hetzner-class VPS for always-on runtime.
- OpenRouter or LiteLLM for provider routing.
- DeepSeek/Kimi/Qwen cheapest capable routes for worker tasks.
- DigitalOcean only if ease/current connection outweighs cheapest hosting.

### Router Layer

Preferred implementation paths:

1. LiteLLM-compatible router for broad provider compatibility.
2. OpenRouter-compatible route table for quick multi-model access.
3. Direct provider SDKs only where pricing or reliability is better.

## Suggested Runtime Package

```text
runtime/packages/model_router/
  __init__.py
  config.py
  router.py
  providers.py
  policies.py
  cost_meter.py
  schemas.py
  README.md
```

## Suggested Environment Variables

```text
OPENROUTER_API_KEY=
DEEPSEEK_API_KEY=
KIMI_API_KEY=
QWEN_API_KEY=
DASHSCOPE_API_KEY=
LOCAL_OLLAMA_BASE_URL=http://localhost:11434
MODEL_ROUTER_DEFAULT_PLANNER=openai:gpt-5
MODEL_ROUTER_DEFAULT_CODER=deepseek:deepseek-coder
MODEL_ROUTER_DEFAULT_LONG_CONTEXT=kimi:kimi-k2-or-current
MODEL_ROUTER_DEFAULT_CLASSIFIER=qwen:qwen-classifier-or-current
MODEL_ROUTER_DEFAULT_LOCAL=ollama:llama-or-current
MODEL_ROUTER_MAX_DAILY_COST_USD=
MODEL_ROUTER_REQUIRE_APPROVAL_ABOVE_USD=
```

Use `.env.example` for names only. Put real values in GitHub Secrets, host secrets, or local environment.

## Cost Control Rules

- Use ChatGPT/GPT for planning, verification, high-risk reasoning, and final decisions.
- Use cheap workers for bulk extraction, classification, coding drafts, and long-document passes.
- Use local models for repetitive or private low-risk work.
- Cache repeated source reads.
- Deduplicate before model calls.
- Summarize source packs before expensive reasoning.
- Cap daily/monthly spend.
- Log provider, model, token estimate, cost estimate, latency, and failure mode.

## Safety Rules

- Cheap models can draft, classify, extract, summarize, and propose.
- Jarvis must verify important outputs before acting externally.
- External writes, sends, deployments, cloud resource changes, and cost-increasing actions remain approval-gated by the app risk matrix.
- Never send secrets to models unless absolutely required and explicitly approved; prefer provider secret stores.

## Deployment Roadmap

1. Create model-router runtime package.
2. Add route policy config.
3. Add provider adapters for OpenRouter, DeepSeek, Kimi/Qwen where available, and local Ollama.
4. Add cost meter and budget guard.
5. Add mock tests for route selection.
6. Add integration tests after secrets are configured.
7. Deploy to Oracle Free Tier or cheapest selected VPS.
8. Add health and smoke checks.
9. Expose safe API endpoints for Jarvis-triggered worker tasks.

## Current Blockers

- Target GitHub repo/branch is confirmed for this pass: `rafsof22-lgtm/jarvis-build`, base `main`, work branch `jarvis/control-registry-model-router-plan`.
- Secrets must be placed outside chat.
- Live runtime host is not confirmed.
- Provider availability/pricing should be verified before final paid choice.

## Immediate Next Action

Open and verify the GitHub PR carrying the control-registry and model-router plan files, then implement the runtime model-router package, `.env.example` entries, tests, and docs after secrets/host readiness are confirmed.
