# Jarvis Agent Instructions

## Purpose
This repository is the Jarvis build/source-control layer. AI coding agents may read, edit, test, and propose updates when the user authorizes it, but must preserve source truth, prior versions, auditability, and rollback.

## Core rules
- Preserve historical versions and append rather than silently replace.
- Do not delete, weaken, compress away, or overwrite Jarvis/RAF213G/Sof Property Scout requirements unless the user explicitly approves.
- Do not commit secrets, API keys, tokens, cookies, `.env` files, private credentials, or production-only values.
- Use Railway variables, n8n credentials, GitHub secrets, or a proper vault for credentials.
- Separate Proven, Assumption, Gap, Risk, Decision, and OpenLoop in major planning/build outputs.
- Do not claim done, deployed, zero-gaps, or production-ready without implementation refs, tests/waivers, evidence, and rollback notes.

## Platform/tool selection rule
Before recommending or adding a platform, tool, workflow engine, AI app builder, coding agent, deployment host, prospecting source, or sales-intelligence tool, consult `docs/platform-tool-selection-registry.md`.

Evaluate:
- best free, cheapest, best all-in-one, and best cost-effective path;
- all pricing tiers, AI credits, build tokens, task credits, workflow runs, agent/concurrency limits, overage rules, and expiry/rollover;
- model-token costs, BYO API keys, model-router options, caching, batch processing, and cheap-model-first escalation;
- GitHub, Railway, n8n, Google Sheets/Drive, Postgres, Redis/queue, MCP, webhook, export, and rollback compatibility;
- secrets, OAuth scopes, RBAC, audit logs, security, lock-in, and production readiness;
- true cost per large Jarvis/Sof task, not only the monthly plan price.

## Current preferred stack
ChatGPT Agent = command brain and auditor.  
GitHub = code/source truth.  
Railway = backend/runtime/secrets/database.  
n8n = central workflow/agent cockpit.  
Google Sheets/custom console = human review layer.  
Cursor/Codex = write-capable coding layer.  
Hercules/Atoms/Base44/Lovable/Bolt = optional app/dashboard builders.  
Apollo/Hunter/A-Leads/Apify/Flyfish = Sof Property Scout source/enrichment/intelligence layer with strict cost gates.

## Coding workflow
1. Inspect existing files before editing.
2. Prefer branch and pull request for non-trivial changes.
3. Make the smallest safe change.
4. Run available lint/test/build/migration checks where possible.
5. Record changed files, tests, risks, gaps, rollback, and next steps.
6. Never ship node_modules.
7. Do not deploy or merge production-impacting changes unless explicitly approved.

## Bill CFO OCR MCP locator
Bill CFO OCR MCP is an isolated Jarvis service, not a repo-wide runtime.

- Repo: `rafsof22-lgtm/jarvis-build`
- Service root: `services/bill-cfo-ocr-mcp/`
- Service-local instructions: `services/bill-cfo-ocr-mcp/AGENTS.md`
- Locator: `services/bill-cfo-ocr-mcp/docs/agent-locator.md`
- Deployment ledger: `services/bill-cfo-ocr-mcp/docs/deployment-ledger.md`
- Railway target: a dedicated Railway service mapped to `services/bill-cfo-ocr-mcp/`
- Deploy branch: `main`

When a Bill CFO agent starts work, it must read the service-local `AGENTS.md`, the locator, the deployment ledger, `railway.json`, `.env.example`, `package.json`, and `src/server.js` before editing.

Bill CFO agents may edit `services/bill-cfo-ocr-mcp/**` by default. They must not edit `services/xrp-hbar-apex/**`, other `services/*` roots, or repo-wide deployment behavior unless the user explicitly requests a shared change and the impact is classified first.

Do not claim Railway deployment success from repo files alone. Verify the Railway project/service, root directory, env vars, public URL, `/health`, `/ready`, `/deployment/status`, and the smallest real OCR/workbook smoke route before marking Bill CFO live.

Use these labels where applicable: `REPO_LOCATOR_SET`, `SERVICE_ROOT_CONFIRMED`, `MODULE_OWNERSHIP_MAPPED`, `RAILWAY_SERVICE_UNVERIFIED`, `NEEDS_RAILWAY_ACCESS`, `SECRET_OWNER_ACTION_REQUIRED`, `NO_FAKE_SUCCESS_CLAIM`.

## Shared service isolation
This repo may hold multiple Jarvis services. Shared repo does not mean shared runtime.

- Keep each service in its own root directory.
- Prefer separate Railway services and separate root directories per module.
- Keep env vars, secrets, routes, health checks, smoke tests, queues, database objects, webhooks, and rollback paths service-specific unless a shared component is explicitly designed and verified.
- Do not rename, move, delete, or repurpose another module's files to make the current module work.
- If a change can affect more than one module, classify the impact as safe, risky, blocked, or requires user confirmation before editing.

## Sof Property Scout boundary
Default mode is capture-only: discover, source-proof, dedupe, score, enrich selectively, verify selectively, write to raw/master sheets or console, log costs/source quality. Do not send outreach or activate campaigns unless separately approved.
