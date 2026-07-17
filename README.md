# Jarvis Build

This repository is the durable source-control layer for the Jarvis / RAF213G / Sof Property Scout build program.

## Current installed governance files

- `AGENTS.md` - agent instructions for coding agents and future automated edits.
- `docs/platform-tool-selection-registry.md` - platform/tool registry and cost/tier/token/build-token evaluation rule.
- `JARVIS_MODULE_REGISTRY.md` - Jarvis module/status map.
- `JARVIS_APP_RISK_APPROVAL_MATRIX.md` - approval and write-risk control matrix.
- `JARVIS_DEPLOYMENT_TARGET_MATRIX.md` - free-first and cheapest practical deployment target map.
- `JARVIS_HYBRID_MODEL_ROUTER_PLAN.md` - model-router planning baseline.
- `JARVIS_OBSERVABILITY_AND_SMOKE_TEST_MATRIX.md` - smoke-test and observability gates.

## Current runtime scaffold

- `.github/workflows/ci.yml` - free-first CI for syntax, model-router smoke checks, and deployment dry run.
- `.github/workflows/deploy.yml` - manual deployment readiness gate only; it does not deploy.
- `.env.example` - variable names only, with blank values.
- `jarvis_model_router/` - safe model-route selection scaffold with cloud routes disabled by default.
- `scripts/smoke_model_router.py` - no-network router smoke test.
- `scripts/deploy_dry_run.py` - host/secret readiness check that never performs live deployment.
- `docs/model-router-runtime.md` - setup notes for the router scaffold.
- `docs/deployment-blockers.md` - current missing host and secret blockers.

## Current service roots

- `services/bill-cfo-ocr-mcp/` - isolated Bill CFO OCR MCP service shell. Start with `services/bill-cfo-ocr-mcp/AGENTS.md` and `services/bill-cfo-ocr-mcp/docs/agent-locator.md` before editing.
- `services/xrp-hbar-apex/` - isolated XRP/HBAR Apex Intelligence OS service shell for a dedicated Railway service. Start with `services/xrp-hbar-apex/README.md`, `services/xrp-hbar-apex/docs/railway-new-service.md`, and `services/xrp-hbar-apex/docs/deployment-ledger.md` before editing or deploying.

## Current preferred stack

ChatGPT Agent -> GitHub -> GitHub Actions checks -> Oracle Free Tier or local/cheap VPS-ready runtime scaffold -> n8n/Postgres/Redis/queue when proven -> Google Sheets/custom console.

Cursor/Codex are preferred for write-capable code editing and PR workflows. Hercules/Atoms/Base44/Lovable/Bolt are optional app/dashboard builders. Apollo/Hunter/A-Leads/Apify/Flyfish support Sof Property Scout only under source-proof, scoring, dedupe, and cost-control gates.

## Platform selection rule

Before selecting or recommending any platform, compare free/cheapest/cost-effective/all-in-one fit plus pricing tiers, AI credits, build tokens, model-token costs, workflow runs, concurrency, API-key handling, GitHub/Railway/n8n/Google Sheets compatibility, export/lock-in risk, security, audit logs, and true large-task cost.

## Service isolation rule

Shared repo does not mean shared runtime. Each service must keep its own service root, Railway service mapping, env variables, secrets, routes, smoke tests, deployment ledger, and rollback notes unless a shared component is explicitly designed and verified.

Bill CFO OCR MCP belongs under `services/bill-cfo-ocr-mcp/` and should be mapped to a dedicated Railway service using that exact root directory. Do not point Bill CFO Railway deployment at the repo root or at another service root.

XRP/HBAR Apex belongs under `services/xrp-hbar-apex/` and should be mapped to a dedicated Railway service using that exact root directory. Do not point XRP/HBAR Apex Railway deployment at the repo root, Bill CFO OCR MCP, or any future shared module root.

## Safe local checks

```bash
python -m compileall jarvis_model_router scripts
python scripts/smoke_model_router.py
python scripts/deploy_dry_run.py --check-only --target oracle
```

## Deployment status

Live deployment is blocked until the selected host exists and required secrets are configured outside the repository. See `docs/deployment-blockers.md` for the exact missing values. Do not add live SSH/provider deployment steps until those blockers are proven resolved.

## Status

This repo contains governance files, CI/deployment-readiness scaffolds, a safe model-router scaffold, and isolated service shells for Bill CFO OCR MCP and XRP/HBAR Apex. Do not claim full Jarvis implementation, live deployment, OCR provider readiness, XRP/HBAR external intelligence-engine readiness, workbook-write readiness, production readiness, or zero-gaps completion from this repository alone.
