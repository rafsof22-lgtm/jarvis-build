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

## Sof Property Scout boundary
Default mode is capture-only: discover, source-proof, dedupe, score, enrich selectively, verify selectively, write to raw/master sheets or console, log costs/source quality. Do not send outreach or activate campaigns unless separately approved.