# XRP/HBAR Apex Intelligence OS — Stage Specification and Jarvis Handoff

**Date:** 2026-07-19 (Australia/Melbourne)  
**Module ID:** `XRP-HBAR-FRAMEWORK-OPTIONS`  
**Owner:** Tas Raptis / RAF213G  
**Control plane:** `rafsof22-lgtm/jarvis-build`  
**Runtime:** `rafsof22-lgtm/hub`  
**Media evidence service:** `rafsof22-lgtm/videotranscribe`  
**Operating mode:** `RESEARCH_ONLY / PAPER_FIRST`  
**Stage status:** `PARTIAL` — repository implementation is substantially complete; live DigitalOcean reachability, provider credentials, production rollback and live cross-repository event exchange remain unverified.

## 1. Purpose

The module provides a source-first XRP, Ripple, HBAR and Hedera intelligence operating system that preserves raw evidence, converts requests into governed requirements, routes work across independent repositories, and exposes versioned contracts for Jarvis orchestration. It must reduce repeated agent-editor prompting, lower token and provider cost, preserve owner authority, and prevent unsupported claims of live readiness, price certainty, profitability or zero gaps.

## 2. Non-negotiable principles

1. Preserve raw sources, hashes, pointers, versions, amendments and conflicts.
2. Use additions-only evolution unless the owner explicitly approves replacement.
3. Maintain a known source denominator with accessible, inaccessible, excluded, failed and pending sources.
4. Keep `jarvis-build`, `hub` and `videotranscribe` independently usable.
5. Integrate through versioned APIs, events, schemas, MCPs and contracts; never flatten repositories.
6. Separate baseline, addition, normalized requirement, implementation, deployment and verified evidence.
7. Require `Source -> Request -> Requirement -> Module -> Artifact -> Test/Waiver -> Evidence -> Deployment -> Rollback` before a complete claim.
8. Never expose secret values. Track credential names, owners, stores, scopes and readiness only.
9. No component self-certifies. Production and consequential actions require independent evidence and applicable owner gates.
10. Investment operations remain research-only or paper-first unless separate live-trading approval, exchange controls, portfolio limits and kill switches are proven.

## 3. Source denominator

### Accessible and used

- Current project conversation and approved assistant outputs.
- Installed XRP/HBAR Apex Live Deployer Skill and Jarvis project constitution.
- `jarvis-build` repository, merged PRs #16, #18 and #19.
- `hub` repository, merged PRs #3 and #4 plus issues #1 and #2.
- `videotranscribe` repository, merged PR #4 and existing federation routes.
- Existing XRP/HBAR handoff pack and repository registries referenced in project continuity.
- GitHub Actions evidence for contract, security, packaging, route, Docker build and ephemeral container checks.

### Inaccessible or unresolved

- Complete historical ChatGPT export denominator for every prior XRP/HBAR chat.
- Provider-side Vercel token rotation evidence.
- Valid Gmail OAuth secret values and token-refresh proof.
- DigitalOcean host shell state after the latest merge.
- Live database, Redis, Caddy, firewall and container state after production promotion.
- Live market, on-chain, social, news and premium-model provider credentials.
- Live Jarvis-to-Hub-to-VTI event exchange and persistent retry/dead-letter state.

These are recorded as gaps and must not be silently treated as complete.

## 4. Canonical objectives

- Track XRP/Ripple and HBAR/Hedera adoption, regulation, institutional usage, tokenization, liquidity, ETFs, custody, payments, CBDCs, stablecoins, on-chain flows, social/video claims and major catalysts.
- Maintain separate network-adoption, token-demand, capital-flow, contradiction and invalidation analyses.
- Support milestone and scenario modelling without treating speculative price targets as facts.
- Produce evidence-backed alerts, discrepancy records, source packs, probability updates and handoff artifacts.
- Route video/transcript evidence through VTI and runtime/status evidence through Hub.
- Surface status, blockers, costs, security controls and next actions through the Jarvis Command Centre.

## 5. Architecture

```text
Evidence and source intake
  -> Jarvis Gateway
  -> Sovereign Control Plane (`jarvis-build`)
  -> Agent Core and governed workflows
  -> Tool / Skill / MCP / API layer
  -> Model and cost router
  -> Memory, registries and audit
  -> Evidence and verification layer
  -> Command Centre

Independent services:
  `hub`                XRP/HBAR runtime, persistence, health and deployment
  `videotranscribe`     video/transcript intake and evidence events
  `jarvis-build`        policy, schemas, fixtures, registries and orchestration
```

## 6. Repository responsibilities

### `jarvis-build`

- Owns federation policy and module handoff standard.
- Owns canonical XRP/HBAR federation event schema.
- Owns repository registry and role mapping.
- Owns shared cross-repository fixtures and deterministic validation.
- Owns Command Centre integration, cost policy, approval policy and source coverage logic.
- Must not store runtime secret values.

### `hub`

- Owns Flask runtime, PostgreSQL, Redis, Caddy and DigitalOcean deployment.
- Owns health, readiness, deployment, VTI, newsletter, Gmail proof and evidence-pack routes.
- Owns well-known Jarvis health and capability routes.
- Owns service-local federation contract packaging and runtime proof.
- Owns runtime backup, restore and rollback evidence.

### `videotranscribe`

- Owns Next.js/Supabase/Vercel application and media-intelligence workflows.
- Owns well-known Jarvis health and capability routes.
- Owns typed XRP/HBAR event builder for transcript and evidence events.
- Owns provider-live-proof and Vercel token-rotation blockers.

## 7. Federation contract

### Contract version

`1.0.0`

### Required envelope fields

- `event_id`
- `contract_version`
- `event_type`
- `producer`
- `consumer`
- `observed_at`
- `correlation_id`
- `idempotency_key`
- `source_refs`
- `evidence_refs`
- `approval_state`
- `retry_count`
- governed `status`
- structured `payload`

### Core event classes

- research started/completed/blocked
- transcript completed
- evidence pack created
- health changed
- alert generated
- discrepancy detected
- incident opened/resolved
- cost threshold reached
- deployment state changed

### Contract controls

- Unique event IDs and idempotency keys.
- Non-negative retry count.
- Explicit producer and consumer allowlists.
- No secret-like keys or values.
- Evidence and source references required where applicable.
- Unknown runtime state is never treated as passing.

## 8. Runtime interfaces

### Hub core

- `GET /health`
- `GET /ready`
- `GET /deployment/status`
- `GET /vti/status`
- `GET /email/newsletter/status`
- `GET /evidence-pack/status`

### Hub federation

- `GET /.well-known/jarvis/health`
- `GET /.well-known/jarvis/capabilities`

### Hub Gmail proof

- `GET /email/newsletter/gmail/status`
- `POST /email/newsletter/gmail/fetch`
- proof retrieval routes

### VTI federation

- `GET /.well-known/jarvis/health`
- `GET /.well-known/jarvis/capabilities`
- typed transcript/evidence event builder in `src/lib/jarvis-federation-event.ts`

## 9. Data and memory

### Hub stores

- PostgreSQL tables for VTI smoke evidence, newsletter proof, Gmail fetch proof, phase checkpoints, claim candidates and evidence-pack exports.
- Redis for runtime queue/cache capability.
- Caddy for public routing.

### Jarvis registries

- source and pending-ingest registry
- requirements and coverage registry
- repository and module registry
- agent, Skill, tool, API, model and integration registries
- credentials-by-name registry
- risk, gap, decision, test, evidence, deployment and rollback registries

### VTI stores

- Supabase-backed application data and media workflow state.
- Deployment and provider state exposed only through sanitized contracts.

## 10. Credentials and scopes

No secret values may appear in chat, repositories, issues, logs or handoff packs.

Known credential names include:

- `DIGITALOCEAN_SSH_KEY` — SSH deployment to the approved droplet.
- `GMAIL_OAUTH_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GMAIL_OAUTH_REFRESH_TOKEN`
- Gmail required scope: `https://www.googleapis.com/auth/gmail.readonly`
- Vercel, Supabase, Groq, OpenRouter, OpenAI, Anthropic and Gemini credentials by provider-specific minimum scope.

All credentials require an approved secret store, least privilege, owner attribution, expiry/rotation tracking and readiness evidence.

## 11. Workflows

### Source and requirements workflow

`SOURCE_ACCOUNTING -> EXTRACTION -> RECONSTRUCTION -> RECONCILIATION -> DELTA -> DEDUPE -> CONFLICT -> GAP -> APPLICABILITY -> TRACEABILITY`

### Build workflow

`SPEC_LOCK -> BUILD_REALITY_AUDIT -> BRANCH -> IMPLEMENT -> STATIC_TEST -> CONTRACT_TEST -> IMAGE_BUILD -> EPHEMERAL_RUNTIME -> REVIEW -> MERGE`

### Deployment workflow

`MERGE_TO_MAIN -> DIGITALOCEAN SSH DEPLOY -> HOST SELF-HEAL -> CONTAINER CHECKS -> PUBLIC PROOF GATES -> GMAIL PROOF GATE -> EVIDENCE RECORD`

### Failure workflow

`DETECT -> CLASSIFY -> CONTAIN -> DIAGNOSE -> PATCH -> REGRESSION TEST -> STAGING/EPHEMERAL PROOF -> PROMOTE OR ROLLBACK`

## 12. Implemented artifacts

### Jarvis

- `docs/modules/xrp-hbar-framework-options-integration.md`
- `schemas/xrp-hbar-federation-contract-v1.json`
- repository role registry updates
- `docs/policies/verified-jarvis-module-handoff-standard.md`
- shared cross-repository fixtures
- deterministic fixture validator
- dedicated XRP/HBAR contract CI

### Hub

- `federation/jarvis_contract.py`
- contract unit tests
- contract CI
- service-local `jarvis_contract.py`
- `jarvis_runtime.py`
- Docker image packaging for app, contract and wrapper
- Gunicorn target `jarvis_runtime:app`
- Flask route tests
- Docker build and ephemeral endpoint smoke tests

### VTI

- existing Jarvis contract and well-known routes
- typed XRP/HBAR federation event builder
- extended TypeScript contract CI

## 13. Test and evidence matrix

### Verified

- Jarvis Free-first CI.
- Cross-repository readiness checks.
- Skill packaging.
- Full-history secret scanning.
- Hub contract unit tests.
- Hub Flask route tests.
- Root/service contract synchronization check.
- Exact Hub production Docker image build.
- Ephemeral container boot using the production image.
- HTTP 200 checks for `/health`, Jarvis health and Jarvis capabilities in the ephemeral container.
- VTI TypeScript type-check, lint and build.
- Shared event fixture validation and secret exclusion.

### Unverified live evidence

- Latest DigitalOcean Actions run details are not available through the current connector surface.
- Direct TCP probes to `134.199.144.115:80` failed from the execution container after merge.
- This does not identify whether the cause is deployment failure, host outage, Caddy/firewall state or egress restriction.
- Gmail OAuth and bounded Gmail fetch remain unverified.
- Production backup/restore and rollback remain unverified.

## 14. Security controls

- Least privilege and named secret scopes.
- No secret values in code, documentation, contracts or evidence.
- Full-history secret scanning in Jarvis.
- Secret-file exclusion in Hub CI.
- Sanitized Gmail evidence and hashed identifiers.
- Explicit owner gates for production, credential changes, billing, public publishing, money movement and live trading.
- Unknown or partial health cannot be promoted to verified.

## 15. Cost and model routing

Use this routing order:

`deterministic local -> internal API/database -> local/open model -> included/free provider -> cheapest qualified paid provider -> premium specialist -> human review`

Track usage, cost, quality, expiry, lock-in, quotas and migration. No paid resource may be created silently.

## 16. Rollback and disaster recovery

### Repository rollback

- Revert the merge commit through a new PR.
- Re-run contract, route, image and ephemeral runtime tests.
- Promote only after green evidence.

### Runtime rollback

Required but not yet proven:

1. Capture currently deployed commit and container image identifiers.
2. Preserve `.env.production` without disclosing values.
3. Back up PostgreSQL and verify backup integrity.
4. Record Redis persistence state.
5. Reset the host repository to the prior known-good commit.
6. Rebuild/restart the production stack.
7. Verify core and federation routes.
8. Restore data only when necessary and independently validated.
9. Record rollback evidence and final state.

A rollback must not be executed blindly while the deployed state and known-good target are unknown.

## 17. Current decisions

- Preserve independent repositories and federate them.
- Use the well-known contract routes as the read-only integration surface.
- Keep investment execution paper-first.
- Treat the Hub merge as approved production promotion.
- Do not claim deployment success while the public endpoint is unreachable and the Actions run is unavailable.
- Do not attempt Gmail fetch until valid OAuth proof exists.

## 18. Risks and gaps

1. DigitalOcean public endpoint currently unreachable from the available execution environment.
2. Deployment-run details unavailable through the connector used in this session.
3. No host-side proof of Caddy, API, PostgreSQL or Redis state after the latest merge.
4. Gmail refresh token may be missing or invalid.
5. Historical Vercel token rotation remains provider-side.
6. VTI handlers do not yet emit events through a verified live exchange.
7. Jarvis Command Centre does not yet poll live contracts.
8. Durable idempotency, retry and dead-letter persistence are incomplete.
9. Backup, restore and rollback drills are incomplete.
10. Live market/on-chain/social providers are not configured or proven.

## 19. Exact next actions

1. Open the GitHub Actions run for Hub commit `6320e90c6b46c7508702994f8fb2dc1e413a2f40` and capture the DigitalOcean deployment job result.
2. If failed, diagnose the first failed step and patch through a branch/PR.
3. If successful, inspect the droplet: synced commit, Docker Compose state, Caddy logs, API logs and port/firewall state.
4. Verify `/health`, `/ready`, `/deployment/status`, both Jarvis routes and the VTI/newsletter/evidence status routes from the host and an external runner.
5. Verify Gmail status; replace provider secrets only through the approved secret store if required.
6. Capture a PostgreSQL backup and execute a controlled restore test in non-production or an isolated database.
7. Execute a controlled rollback drill to the previous known-good commit, then re-promote the tested release.
8. Add read-only Jarvis Command Centre polling and live VTI-to-Hub event exchange.
9. Add persistent idempotency, retry and dead-letter handling.
10. Regenerate the final handoff pack with deployment and rollback evidence.

## 20. Stage completion statement

Within the accessible repository and CI scope, requirements capture, code implementation and executable tests reached full coverage for the known denominator. The module is not globally or permanently 100% complete because live deployment, provider credentials, runtime dependency health, backup/restore, rollback and live event exchange lack the required evidence chain.

Current recommended external status: `PARTIAL`.
