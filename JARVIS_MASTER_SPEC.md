# JARVIS Master Specification

## Status

This file is the repository-tracked counterpart to the persistent Google Doc `JARVIS_BUILD_FRAMEWORK_CURRENT`. The Google Doc preserves the user-supplied framework and dated deltas; this file keeps the implementation-facing master specification versioned with the Jarvis codebase.

## Controlling objective

Build and operate one unified Jarvis / RAF213G / Emergent App Builder system by reconstructing, reconciling, expanding, testing, connecting, automating, deploying, monitoring, repairing, and continuously improving all approved modules from available chats, exports, files, repositories, skills, apps, APIs, tools, runtime evidence, and future sources.

## Baseline preservation

- Treat the user-supplied framework in `JARVIS_BUILD_FRAMEWORK_CURRENT` as the controlling wording baseline.
- Preserve it word-for-word by default.
- Stack dated additions in the best applicable section.
- Make only minimal edits when required for safety, correctness, obsolete dependencies, broken references, or implementation blockers.
- Record all material changes and rollback instructions.
- Never silently remove, weaken, compress away, or overwrite approved requirements.

## Five-pass consolidation

For every major build pass:

1. Discover available sources and aliases.
2. Extract goals, objectives, requirements, features, functions, workflows, constraints, decisions, and implied controls.
3. Map each applicable item to one primary module, agent, skill, integration, artifact, UI location, and test path.
4. Define implementation, runtime, cost, deployment, security, recovery, evidence, and maintenance requirements.
5. Detect conflicts, duplication, orphaned requirements, fake controls, missing ownership, missing tests, and missing operational controls.

After five passes, continue all safe unblocked work. Record unavailable historical material for future intake rather than stopping the entire build.

## Standing agent-editor authorization

The user authorizes Jarvis to:

- update the persistent framework and repository master spec;
- inspect connected repositories and applications;
- create safe branches, commits, pull requests, CI workflows, tests, docs, registries, runtime scaffolds, integration adapters, deployment manifests, health checks, and rollback instructions;
- automatically repair ordinary repository, workflow, configuration, test, build, and staging failures;
- use existing approved connectors and secret references by name only;
- run read-only checks, dry runs, simulations, previews, CI, staging deployments, smoke tests, and post-change verification;
- execute production deployment only when an existing signed/pre-authorized playbook covers the target, scope, budget, tests, rollback, and blast radius.

User involvement is reserved for unavoidable login, MFA, CAPTCHA, OAuth consent, billing acceptance, KYC, legal attestation, new secret values, destructive data changes, financial transactions, ownership transfer, or unapproved public/production exposure.

## Unified architecture

`Interfaces -> Gateway -> Sovereign Control Plane -> Supervisor -> Domain Modules -> Tool/Skill/Integration Fabric -> Model Router -> Memory/Knowledge/Audit -> Evidence/Verification -> Runtime/Deployment -> UX Command Centre`

### Shared core

- identity and owner controls;
- request, requirement, decision, risk, gap, test, evidence, and build registries;
- routing and dependency graph;
- authorization and approval engine;
- secrets and connection lifecycle;
- cost/token/resource governance;
- memory and knowledge isolation;
- provenance, contradiction, freshness, and audit;
- observability, incident response, rollback, backup, restore, and kill switches.

### Domain modules

Retain existing ChatGPT agents and repositories as lightweight interfaces or bounded modules, including:

- Jarvis Build;
- XRP/HBAR Apex;
- autonomous trading and market intelligence;
- universal intelligence gathering;
- Bill CFO and CFO Audit;
- Jarvis Health and mental-health/care coordination;
- Fast 8 Auto operations;
- family office, trust, SMSF, tax and wealth intelligence;
- passive-income and autonomous-business research;
- video/transcript/social intelligence;
- property and buyer intelligence;
- source, OCR and document intake;
- software scouting and governed clean-room build-versus-integrate decisions;
- infrastructure, workstation, local model and hosting planning;
- future modules discovered from source passes.

Each module must have one primary owner, isolated data/permissions, explicit service root where applicable, input/output contracts, tests, evidence, cost limits, failure handling, rollback, and deployment state.

## Current repository map

| Repository | Initial Jarvis placement |
|---|---|
| `rafsof22-lgtm/jarvis-build` | Primary implementation spine and shared control repository |
| `rafsof22-lgtm/hub` | Existing XRP/HBAR or deployed hub evidence to reconcile before reuse |
| `rafsof22-lgtm/Jarvis-Health` | Health-domain source/module repository |
| `rafsof22-lgtm/videotranscribe` | Video and transcript intelligence module repository |
| `rafsof22-lgtm/property-agent-mcp` | Property/buyer MCP module repository |

Do not merge repositories blindly. Build a repository registry, preserve service boundaries, extract reusable shared components, and migrate through tested branches and pull requests.

## Current verified control-plane state

As of 17 July 2026, repository evidence shows merged pull requests that added:

- control registries and hybrid model-router planning;
- free-first CI, model-router scaffolding, and deployment dry-run controls;
- Google-family GitHub secret-name preflight scaffolding;
- a safe Google secret-bundle format classifier that does not expose values.

Update registries to reflect those merged states rather than carrying stale pending-PR entries.

## Cost and token routing

Use this order:

`existing verified artifact -> cache -> deterministic tool -> internal database/API -> local software -> local model -> included ChatGPT/Codex route -> free provider allowance -> lowest-cost validated cloud model -> specialist premium model -> multi-model panel only when justified`

- Do not use an LLM for deterministic deployment mechanics, file transforms, validation, calculations, health checks, or routine workflow steps.
- Prefer GitHub Actions, scripts, queues, webhooks, deployment hooks, and scheduled jobs for deterministic automation.
- Track cost by task, module, provider, model, environment, and period.
- Paid routes are disabled by default unless the task requires them or a budget playbook authorizes them.

## Connection and integration fabric

For every app, API, MCP, plugin-like connector, OAuth application, webhook, database, queue, storage system, model provider, and deployment platform:

- record provider, purpose, module owner, scopes, auth mode, secret names, environment, rate limits, cost tier, data classes, health checks, retry/backoff, idempotency, circuit breaker, webhook events, audit events, revoke/rotate path, fallback, and exit route;
- prefer official APIs and OAuth, then approved export/import, then safe user-approved browser automation;
- prefer existing connected apps and free/native routes;
- keep secrets out of prompts, logs, evidence packs, code, and model memory;
- use GitHub Secrets or provider vaults for repository-backed deployments;
- use safe presence, metadata, whoami, dry-run, and health tests before live writes.

## Runtime and deployment fabric

Maintain distinct states and policies for:

- local development;
- ChatGPT/Custom GPT Preview;
- Codex repository work;
- CI validation;
- preview deployment;
- development;
- staging;
- canary/shadow;
- production;
- scheduled/event-driven operation;
- rollback and disaster recovery.

Default repository flow:

`inspect -> branch -> implement -> lint/type/test/build/security/cost checks -> commit -> push -> PR -> independent verification -> merge under policy -> staging -> smoke/reconciliation -> controlled production promotion -> monitor -> rollback if thresholds fail`

## Tools and skill governance

- Use one primary skill and normally no more than two narrow supporting skills per request.
- Keep broad shared controls centralized and lazy-loaded.
- Treat `npx skills` as a governed acquisition mechanism, not permission to install everything.
- Candidate skills move through discovery, quarantine, source pinning, script/dependency/security review, baseline evaluation, cost/latency comparison, approval, canary, deployment, monitoring, and rollback.
- Maintain approved, custom, quarantine, rejected, and superseded-preserved skill states.

## Required build systems

Jarvis must progressively implement and maintain:

- source and ChatGPT-export ingestion;
- requirement and contradiction reconciliation;
- module, agent, skill, integration, model, tool, workflow, secret, deployment, test, evidence, cost, incident, and decision registries;
- agent/skill/integration factories;
- workflow engine and durable state machines;
- event bus, queues, schedulers, webhooks and reconciliation workers;
- hybrid model router with local/free/cheap/premium routes;
- shared connector broker and OAuth lifecycle;
- secrets discovery and safe placement maps;
- policy engine and approval inheritance;
- observability, tracing, logs, metrics, alerts, dead-letter queues and stuck-job rescue;
- automated evaluation, regression, security, accessibility, load, chaos, cost, backup, restore and rollback tests;
- setup wizard, diagnostics, guided connection setup, update/uninstall and recovery;
- web command centre, JarvisDock, voice, upload, actions, timeline, fix, notifications and cost/security views;
- deployment adapters and health verification;
- continuity snapshots, exports and resume state.

## Button and workflow truth

No UI control may exist without:

- purpose;
- required inputs;
- handler/tool/workflow;
- permission and approval rule;
- state transition;
- exact output and save location;
- run/evidence ID;
- failure and recovery state;
- rollback/retry;
- next-step loop.

Planned-only controls must be disabled and labelled clearly.

## Missing-control auto-expansion

For every new feature, module or workflow, automatically add applicable requirements for:

- goals, objectives and acceptance criteria;
- basic and advanced UX;
- accessibility, mobile, offline and degraded operation;
- schemas, APIs, events and versioning;
- auth, permissions, privacy and retention;
- cost, quotas and capacity;
- setup, migration, update and uninstall;
- tests, monitoring, incidents, backup, restore and rollback;
- documentation, onboarding and support;
- evidence, provenance, audit and continuity;
- legal, medical, financial or regulated boundaries;
- vendor exit and lock-in reduction;
- maintenance ownership and deprecation.

## Build phases

1. Baseline completion and source/register reconciliation.
2. Repository and module reality map.
3. Shared control plane and canonical registries.
4. Connection, secret and integration fabric.
5. Runtime, workflow, queue, event and model-router foundation.
6. Unified dashboard and guided setup experience.
7. Module-by-module integration and migration.
8. CI/CD, deployment, observability, security and recovery hardening.
9. Preview, staging, canary and controlled production activation.
10. Continuous source, tool, model, cost, security and capability improvement.

Continue the earliest unblocked phase automatically while maintaining safe module boundaries.

## Response and progress tracking

For substantial Jarvis work, update the persistent Google Doc and relevant repository files, then report:

- Done;
- Proven;
- Gaps;
- Next Step.

Also state branches, commits, pull requests, checks, deployment IDs, health evidence, cost impact, rollback point, and any irreducible user action when applicable.

## Change log

### 17 July 2026

- Established repository-tracked master specification.
- Added standing agent-editor authorization.
- Added five-pass best-available consolidation and auto-expansion.
- Added current repository map and merged-control-plane state.
- Added full connection, runtime, CI/CD, deployment, tool, app, API, workflow, observability, security, cost and recovery scope.
- No production deployment or destructive action performed by this change.
