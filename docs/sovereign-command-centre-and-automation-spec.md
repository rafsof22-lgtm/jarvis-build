# Sovereign Command Centre and Automation Specification

Status: SPEC_LOCKED / IMPLEMENTATION_BACKLOG

## Purpose
Create one cost-governed, novice-first, science-fiction-inspired Jarvis controller that unifies repositories, modules, agents, workflows, tools, APIs, models, costs, credentials readiness, tests, evidence, deployments, incidents and owner approvals without destroying independent service boundaries.

## Universal applicability
For every applicable request, module, tool, API, model, workflow, app, website, platform or integration:
1. capture the source request and acceptance criteria;
2. map goals, objectives, features, dependencies and best placement;
3. run reuse -> configure -> extend -> compose -> create;
4. compare free/local, included, cheapest-qualified, best-value, scalable and premium routes;
5. define automation, manual override, security, costs, tests, evidence, deployment and rollback;
6. update canonical registries and the Command Centre;
7. never claim complete without implementation and proof.

## Controller surfaces
- Mission Control: overall status, modules, blockers and next executable OpenLoop.
- Build Studio: prompt-to-plan, architecture, code, tests, preview, staging and release gates.
- Agent Mesh: agents, roles, tools, memory, budgets, queues and safe-stop controls.
- Workflow Observatory: schedules, events, webhooks, retries, dead letters and run evidence.
- Tool/API/Model Exchange: capabilities, providers, prices, quotas, latency, quality and route selection.
- Credential Readiness: secret names and readiness only; never values. Show missing, present-unverified, tested, expired, rotation-required and revoked states.
- Cost Galaxy: budgets, credits, tokens, API calls, workflow runs, compute, storage, forecasts and hard stops.
- Evidence Vault: source pointers, tests, hashes, deployment proof, incidents and rollback points.
- Module Federation: independent repository health and versioned contract compatibility.
- Owner Console: approvals, manual overrides, edit/update controls and emergency kill switches.
- AI Helper: plain-language explanations, guided fixes and next-best actions.

## UI rules
- Desktop, tablet and mobile responsive.
- Accessible keyboard navigation, readable contrast, reduced-motion option and screen-reader labels.
- Sci-fi visual language may use holographic panels, orbital maps, status rings, animated data flows and interactive graphs, but must never reduce clarity or performance.
- Every major action must expose purpose, inputs, cost, permissions, exact effect, evidence, failure state and rollback.
- Frequent safe actions should take no more than three clicks.
- Manual override must remain available within owner permissions.
- Dangerous actions require explicit confirmation and cannot be hidden behind decorative controls.

## Workflow automation coverage
Discover and register all applicable:
- GitHub Actions;
- repository CI/CD;
- Railway, Vercel and DigitalOcean deployments;
- n8n workflows and webhooks;
- queues, workers and scheduled jobs;
- Gmail and source-monitoring jobs;
- ingestion, OCR, transcription and enrichment pipelines;
- backups, restore drills, incident response and rotation reminders;
- cost revalidation, provider-health and dependency-update scans.

For each workflow record trigger, owner, inputs, outputs, secrets by name only, permissions, cost, retries, idempotency, timeout, dead-letter handling, tests, evidence and rollback.

## Credential safety and environment handling
- Secret values remain in approved GitHub, Vercel, Railway, cloud or vault secret stores.
- Jarvis may inventory secret names and readiness but must not reveal values.
- Generate `.env.example` with names and descriptions only.
- Runtime `.env` files may be generated only in ephemeral or explicitly gitignored environments from authorised secret stores.
- Never commit `.env`, credentials, private keys, refresh tokens or recovery codes.
- Prefer OIDC, workload identity and short-lived tokens when supported.
- Test one integration at a time using least privilege and a bounded read-only or sandbox operation.
- Log status and sanitized errors only.
- Missing credentials produce one exact owner action, placement path and validation step.

## Deployment route
- Existing Vercel remains preferred for the Next.js `videotranscribe` application because it already has a working integration path.
- The Jarvis Command Centre should begin as a static/read-mostly or serverless preview using the cheapest compatible route, then separate always-on control-plane services from the UI.
- Compare Vercel, Cloudflare Pages/Workers, existing Railway, existing DigitalOcean and Oracle Free Tier using current official pricing, capability, privacy, exportability, cold starts and maintenance effort before production selection.
- Do not migrate working services solely for theoretical savings; require measured benefit and rollback.

## SourceScout expansion
Continuously monitor and rank official documentation, repositories, release notes, standards, research papers, security advisories, benchmarks, provider pricing, app-builder changelogs and reference implementations covering:
- OpenAI, Anthropic, Google, Meta, Mistral and major open-model ecosystems;
- Agents SDK, MCP, LangGraph, AutoGen, CrewAI and emerging orchestration frameworks;
- GitHub, Vercel, Cloudflare, Railway, DigitalOcean, Oracle, Supabase, Postgres, Redis and queues;
- n8n, Activepieces, Temporal, Windmill and workflow systems;
- OpenTelemetry, evaluation, guardrails, policy, prompt-injection defence and supply-chain security;
- Lovable, Base44, Emergent, Softr/Sofgen, Bolt, Replit, Bubble, Retool, Glide and similar builders;
- OWASP, NIST, ISO, cloud security and privacy guidance.

Official sources first. Community claims remain secondary until verified. Every new finding must be dated, deduplicated, scored, mapped to a module and converted into a proposal or build task.

## New project MODULE chat rule
On the first substantive request in any new project chat identified as `MODULE`, ask once:

`Should this MODULE be merged into the canonical Jarvis build, framework, specifications, registries and implementation backlog using additions-only, zero-loss reconciliation?`

If the user says yes, or the current Project Instructions already provide standing approval, preserve the full chat as a source, extract requirements, deduplicate semantically, map best placement, preserve conflicts and link the module through versioned contracts. Never destructively merge repositories, data boundaries or deployment ownership.

## Completion gate
The consolidated architecture is not 100% complete until source denominator, requirements, semantic consolidation, repository implementation, workflow inventory, credential readiness, UI, tests, staging, deployment, evidence and rollback all pass independent verification.
