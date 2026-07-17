# Jarvis Module Registry

## Purpose

This file is the canonical registry for Jarvis modules, runtime packages, skills, files, app dependencies, deployment status, and next actions.

Use it to prevent duplicate modules, preserve source authority, and keep Jarvis expansion unified as other ChatGPT agents, skills, repos, and external sources are consolidated.

## Registry Rules

- Treat every major Jarvis capability as a module.
- Do not create duplicate modules without recording why the split is necessary.
- Link each module to its owning skill, files, runtime package, apps, tests, and deployment state when known.
- Update this file after substantial Jarvis build, deployment, app, skill, or framework changes.
- Treat missing evidence as a gap, not as proof that a module does not exist.
- Use one primary owner per module and add supporting owners only when their scope is narrow and required.
- Preserve module, repository, deployment and service isolation unless a shared component is explicitly designed, tested and approved.
- Repositories may operate simultaneously. Jarvis coordinates them through versioned contracts, registries, events and APIs rather than destructive consolidation.

## Status Legend

- `planned` — desired but not yet implemented
- `drafted` — spec or file exists, implementation incomplete
- `implemented` — runtime or workflow exists in usable form
- `connected` — required apps/accounts are configured
- `tested` — smoke test or preview evidence exists
- `deployed` — live deployment evidence exists
- `blocked` — external blocker prevents progress
- `deprecated` — replaced by a better module

## Core Modules

| Module | Purpose | Current Owner | Key Files | Runtime Path | Status | Verified Finding / Gap | Next Action |
|---|---|---|---|---|---|---|---|
| Master Framework and Specification | Preserve the user-controlled framework and version implementation truth | jarvis-sovereign-builder | Google Doc `JARVIS_BUILD_FRAMEWORK_CURRENT`; `JARVIS_MASTER_SPEC.md` | repository control plane | implemented | PR #6 passed Free-first CI and was merged to `main` at `b4f30ba849b52931125a15f45a7eebabb089e0f7` | Continue additions-only framework deltas and baseline transfer |
| Source Intake | Ingest files, archives, chat exports, repos and connected evidence | jarvis-build-orchestrator | `JARVIS_MASTER_SPEC.md`; future source registry | `runtime/packages/source_ingestion` | drafted | Current chat and five connected repos are known; complete source denominator is still expanding | Create source, request and response schemas with immutable pointers |
| Requirement Reconciliation | Consolidate all applicable user requests and material AI responses | jarvis-verification-discrepancy | future requirement, conflict and traceability registries | `runtime/packages/patching` | drafted | Five-pass policy exists; canonical automated extraction pipeline remains incomplete | Implement RequestLog -> Requirement -> Module -> Artifact -> Test -> Evidence mapping |
| Repository Federation | Keep all repositories independently usable while sharing contracts and control-plane services | jarvis-sovereign-builder | this registry; `JARVIS_MASTER_SPEC.md`; future repository registry | multi-repository federation | drafted | All five repos can remain simultaneous; blind merge would compromise service and deployment boundaries | Add versioned API/event contracts, compatibility matrix and cross-repo release ledger |
| Skill Dedupe and Factory | Govern existing skills and generate validated skills when capability gaps appear | skill-orchestrator-router | `JARVIS_SKILL_DEDUPE_MAP.md`; future skill registry/factory | shared skill fabric | implemented | One-owner routing exists; automated candidate discovery, generation, evaluation and canary promotion remain incomplete | Build governed skill lifecycle and reusable skill store |
| Agent Factory and Elastic Mesh | Create, pool, pause and retire bounded agents for parallel work | jarvis-sovereign-builder | future agent templates, registry and policy files | supervisor and worker pools | planned | Large parallel expansion is required, but unrestricted recursive spawning is prohibited | Implement signed templates, quotas, isolated workspaces, budgets, tests and automatic retirement |
| Continuous Source and Capability Scout | Continuously discover better models, tools, frameworks, modules and lawful implementation patterns | universal-intelligence-gatherer | future source/opportunity registry | scheduled scout workers | planned | Current source scouting is manual/on-demand | Add official-first delta scans, scoring, dedupe, security review and build-task creation |
| Cost, Credit and Resource Governor | Minimise ChatGPT credits, model tokens, build credits and infrastructure cost without losing capability | universal-sourcing-stack-scout | `JARVIS_HYBRID_MODEL_ROUTER_PLAN.md`; deployment matrix; future cost ledger | shared routing and policy layer | drafted | Free-first routing exists; full credit-aware telemetry, budgets and automatic route switching remain incomplete | Add per-task cost estimates, hard caps, free allowance tracking, cache metrics and cheapest-qualified fallback |
| App Risk and Approval | Govern read/write/deploy/send actions and approval policy | project-stack-access-mapper | `JARVIS_APP_RISK_APPROVAL_MATRIX.md` | policy layer | drafted | Standing agent-editor authorization exists; consequential action gates remain | Encode repository/environment/action/budget policies |
| GitHub Execution | Branch, commit, PR, CI and controlled merge workflow | jarvis-build-orchestrator | `AGENTS.md`; CI workflows | GitHub Actions | tested | PR #6 CI passed compilation, model-router smoke and deployment dry run; public-repo Actions route is free | Retain public non-sensitive control repo where safe; keep secrets/private data out |
| Deployment Automation | Preview, staging, canary, production, rollback and smoke verification | jarvis-sovereign-builder | deployment matrix; Oracle blueprint; repo workflows | provider-specific isolated services | drafted | `hub` has DigitalOcean auto-deploy; `videotranscribe` has Vercel workflow; other repos use separate paths | Standardise deployment contracts without replacing working module deployments |
| Hybrid Model Router | Route tasks across deterministic, local, free and paid models | jarvis-research-sourcing | `jarvis_model_router/`; router plan | `jarvis_model_router` | tested | No-network scaffold passes smoke test; provider telemetry and adapters remain | Implement capability scoring, credit awareness, cache and local/free-first fallback |
| Secret Discovery and Placement | Discover names and aliases without exposing values | agent-capability-upgrader | `.env.example`; secret-preflight workflow and scripts | CI/runtime preflight | tested | Google alias classifier exists; `videotranscribe` contained an embedded Vercel credential fallback | Rotate exposed Vercel token; merge security PR; expand secret scans across all repos |
| Integration Fabric | Manage apps, APIs, MCPs, OAuth, webhooks, queues and provider lifecycle | agent-skill-integration-builder | future integration registry | shared adapter layer plus module-local connectors | planned | Each repo currently has different providers and credentials | Build shared contracts while preserving module-local secrets and scopes |
| Workflow and Event Runtime | Durable workflows, schedules, webhooks, retries, queues and reconciliation | universal-agent-autopilot-orchestrator | future event and workflow specifications | n8n/code-first runtime | planned | `property-agent-mcp` has a signed queue and optional n8n dispatch; no proven shared runtime | Define canonical event envelope, idempotency, retry and dead-letter contracts |
| Observability | Health, cost, drift, freshness, evidence and incident tracking | jarvis-verification-discrepancy | observability matrix; CI | runtime tests/CI | implemented | CI evidence exists; common cross-repo telemetry does not | Add run IDs, health schema, dependency status, cost and incident registry |
| Bill CFO OCR MCP | Isolated finance document/OCR service | bill-cfo-ocr-source-intake | `services/bill-cfo-ocr-mcp/**` | dedicated Railway service | connected | Connected shell evidence only; real OCR and workbook paths need proof | Keep isolated and test smallest real OCR/evidence flow |
| XRP/HBAR Apex | Isolated market/video/email intelligence service | xrp-hbar-apex-tracker | `services/xrp-hbar-apex/**`; `hub` runtime | Railway service plus DigitalOcean hub runtime | implemented | `hub` has Flask/API, Postgres, Redis, Caddy and deploy workflow; Gmail proof remains incomplete | Reconcile duplicate XRP/HBAR service surfaces through contracts, not destructive merge |
| Jarvis Health | Health intelligence and Drive-backed MCP work | Jarvis Health domain module | `rafsof22-lgtm/Jarvis-Health` | isolated Node service | drafted | Current server is a placeholder; README names Drive tools not yet implemented; release workflow calls missing `npm test` and attempts npm publish | Preserve repo, disable unsafe publishing until package/test policy exists, implement tools privately |
| Video Intelligence | Transcription, fact checking and evidence workflows | vti-video-intelligence-builder | `rafsof22-lgtm/videotranscribe` | Next.js/Supabase/Vercel | implemented | Rich app exists; a Vercel credential was embedded in workflow and is being removed in PR #1 | Rotate token, merge security PR, retain independent app and expose versioned Jarvis API contracts |
| Property Buyer Intelligence | Capture, dedupe, score and enrich buyer leads | property-buyer-capture | `rafsof22-lgtm/property-agent-mcp` | Railway, Postgres, n8n, Google Sheets | implemented | MCP, Apollo/Hunter, stage-only Sheets writes and signed jobs exist; promotion/merge workers remain incomplete | Preserve capture-only boundary and finish staged ingest, dedupe and audit endpoints |

## Connected Repository Federation

| Repository | Independent role | Simultaneous-use policy | Current risk / gap |
|---|---|---|---|
| `rafsof22-lgtm/jarvis-build` | Canonical control plane, registries and shared service shells | Always usable as implementation spine; changes through branch/PR/CI | Avoid storing private source content in the public repo |
| `rafsof22-lgtm/hub` | XRP/HBAR DigitalOcean runtime and deployment evidence | Keep operational while contracts are reconciled | Gmail credential validity and proof gates remain |
| `rafsof22-lgtm/Jarvis-Health` | Private health/Drive MCP module | Keep private and separately deployable | Placeholder implementation and unsafe/unnecessary npm publish workflow |
| `rafsof22-lgtm/videotranscribe` | Private VTI application | Keep separately buildable and previewable | Exposed Vercel token requires rotation and history-aware remediation |
| `rafsof22-lgtm/property-agent-mcp` | Private property MCP and Railway service | Keep separately deployable with capture-only policy | Several ingestion/merge/audit workers remain unimplemented |

## Free and Cheapest Route Policy

Use this live decision order and re-evaluate it continuously:

`existing artifact/cache -> deterministic local tool -> GitHub/connected native tool -> local runtime/model -> free public-repo CI -> free preview/static/serverless tier -> existing paid infrastructure -> lowest-cost qualified paid route -> premium route only with measured justification`

Current validated defaults:

- GitHub public-repository Actions for non-sensitive CI where safe.
- Local editor, Git, Docker, scripts, Ollama/llama.cpp and browser preview for zero-usage work.
- Cloudflare Pages/Workers free tier for lightweight preview, gateway and event workloads where technically compatible.
- Existing Vercel/Railway/DigitalOcean deployments remain usable; migrate only when measured savings and compatibility justify it.
- Oracle Cloud Always Free remains the planned always-on controller route after account/host setup.
- Paid model and infrastructure routes are disabled by default unless free/native routes fail acceptance criteria or an approved budget applies.

Continuously compare current official pricing, limits, reliability, lock-in, exportability, credits, quotas, latency and maintenance cost. Never assume a promotional free tier remains permanent.

## Immediate P0 Backlog

1. Complete and merge the `videotranscribe` security remediation after checks; revoke and rotate the exposed Vercel credential.
2. Disable or repair the `Jarvis-Health` release publishing workflow before any release is created.
3. Create canonical repository, request/response, source, requirement, agent, skill, integration, model, cost, test, evidence and incident registries.
4. Implement the governed agent and skill factory with signed templates, quotas, evaluation, canary and rollback.
5. Add credit-aware model/build routing and cost telemetry.
6. Define shared cross-repository API/event/version contracts while leaving every repository independently usable.
7. Reconcile XRP/HBAR surfaces between `jarvis-build` and `hub` without replacing the proven DigitalOcean path.
8. Establish free preview and staging adapters before production changes.
9. Add secret scanning and history-aware incident handling across all repositories.
10. Continue the full baseline transfer and additions-only Google framework updates.

## Update Log

- 2026-07-17: PR #6 passed Free-first CI and was merged, establishing `JARVIS_MASTER_SPEC.md` on `main`.
- 2026-07-17: Completed initial five-repository forensic inventory and confirmed simultaneous-operation federation policy.
- 2026-07-17: Identified a P0 embedded Vercel credential in `videotranscribe`; opened a removal PR and required rotation.
- 2026-07-17: Added continuous free/cheapest route optimization, cost/credit governance, elastic agent mesh, skill factory and source/capability scout modules.
