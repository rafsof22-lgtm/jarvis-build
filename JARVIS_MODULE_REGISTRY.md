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
- Preserve module and service isolation unless a shared component is explicitly designed, tested, and approved.

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

| Module | Purpose | Current Owner | Key Files | Apps Needed | Runtime Path | Status | Gaps | Next Action |
|---|---|---|---|---|---|---|---|---|
| Master Framework and Specification | Preserve the user-controlled framework, stack dated deltas, and keep implementation truth versioned | jarvis-sovereign-builder | Google Doc `JARVIS_BUILD_FRAMEWORK_CURRENT`; `JARVIS_MASTER_SPEC.md` | Google Drive, GitHub | repository control plane | drafted | Full user-supplied baseline still requires controlled verbatim transfer into the persistent document; repo spec requires review/merge | Complete baseline transfer in chunks; review and merge the master-spec PR |
| Source Intake | Ingest files, archives, chat exports, repos, Drive/Notion/Gmail/Slack evidence | jarvis-build-orchestrator | `JARVIS_MASTER_SPEC.md`; `runtime/packages/source_ingestion/service.py` | GitHub, Drive, Gmail, Notion, Slack where relevant | `runtime/packages/source_ingestion` | drafted | Needs stronger source inventory and dedupe schema | Create source inventory schema and tests |
| Requirement Reconciliation | Merge requirements, detect contradictions, preserve source hierarchy | jarvis-verification-discrepancy | `JARVIS_FORENSIC_TASK_MAP.md` | GitHub, Drive, Notion | `runtime/packages/patching` | drafted | Needs canonical contradiction register | Add contradiction table to forensic map |
| Skill Dedupe | Classify skills as keep, merge, archive, route-only | skill-orchestrator-router | `JARVIS_SKILL_DEDUPE_MAP.md` | None required | n/a | implemented | Imported skill behavior still requires post-install routing tests | Keep one-primary-owner routing and run positive/negative tests after imports |
| App Risk and Approval | Govern read/write/deploy/send actions and approval policy | project-stack-access-mapper | `JARVIS_APP_RISK_APPROVAL_MATRIX.md` | All connected apps | n/a | drafted | Standing agent-editor authorization must be reconciled with action-class and environment limits | Add explicit pre-authorized safe actions and retained approval gates |
| GitHub Execution | Prepare repo patches, branches, commits, PRs, CI checks | jarvis-build-orchestrator | `runtime/docs/specs/GITHUB_WRITE_EXECUTION_SEQUENCE.md`; `runtime/docs/specs/REPO_EXECUTION_PACKAGE.md`; `AGENTS.md` | GitHub | `runtime/packages/connectors/github_repo.py` | implemented | Merged PRs #2-#5 prove write/PR workflow; automatic CI and merge policies still need explicit verification | Verify the new master-spec PR checks; define bounded auto-merge policy |
| Deployment Automation | Bootstrap, deploy, rollback, smoke test runtime | jarvis-sovereign-builder | `ORACLE_FREE_TIER_DEPLOYMENT_BLUEPRINT.md`; `JARVIS_DEPLOYMENT_TARGET_MATRIX.md`; `runtime/infra/scripts/*`; `.github/workflows/deploy.yml` | GitHub and selected host provider | `runtime/infra` | drafted | Current deploy workflow is readiness-only; target host and production playbook are not yet selected and verified | Reconcile Oracle, Railway, DigitalOcean and local routes; implement staging adapter first |
| Hybrid Model Router | Route tasks across GPT, DeepSeek, Kimi, Qwen, local models | jarvis-research-sourcing | `JARVIS_HYBRID_MODEL_ROUTER_PLAN.md`; `jarvis_model_router/`; `scripts/smoke_model_router.py` | OpenRouter/provider APIs only when enabled | `jarvis_model_router` | tested | Repo-side no-network scaffold and smoke test exist; real provider adapters, usage metering and fallback health remain | Add provider-neutral adapter contracts and local-first usage/cost telemetry |
| Secret Discovery and Placement | Discover required secret names and aliases, classify safe presence/format, and generate exact placement steps | agent-capability-upgrader | `.env.example`; `.github/workflows/secret-preflight.yml`; `scripts/google_secret_preflight.py`; `docs/github-secret-preflight-checklist.md` | GitHub Actions, provider secret stores | CI/runtime preflight | tested | PRs #4 and #5 are merged; provider authentication and destination-specific mappings are incomplete | Expand names-only preflight across all current modules and providers without exposing values |
| API Channel Control | Define safe external trigger payloads and forbidden actions | project-stack-access-mapper | `JARVIS_API_CHANNEL_RUNBOOK.md` | API channel | n/a | drafted | Needs external caller allowlist and payload schemas | Define trigger payload examples and signed request policy |
| Integration Fabric | Maintain apps, APIs, MCPs, OAuth, webhooks, queues and provider lifecycle | agent-skill-integration-builder | `JARVIS_MASTER_SPEC.md`; future `INTEGRATION_REGISTRY` | Connected apps/providers | shared adapter layer plus module-local connectors | planned | No complete integration registry, health matrix, scope map or revoke/exit map | Create canonical integration registry and module connection priorities |
| Workflow and Event Runtime | Execute durable workflows, schedules, webhooks, retries, queues, reconciliation and dead-letter handling | universal-agent-autopilot-orchestrator | future workflow/event specifications | n8n or code-first runtime; database/queue as justified | shared workflow runtime | planned | No proven shared durable runtime | Define minimum event envelope, workflow state machine, queue and idempotency contracts |
| Observability | Health, cost, drift, source freshness, smoke tests | jarvis-verification-discrepancy | `JARVIS_OBSERVABILITY_AND_SMOKE_TEST_MATRIX.md`; CI workflows | GitHub, host provider, optional monitoring app | runtime tests/CI | implemented | CI/dry-run evidence exists; external runtime metrics, traces, alerts and cost telemetry are incomplete | Add shared health schema, run IDs, evidence pointers and module cost metrics |
| Schedules | Daily/weekly/monthly Jarvis audits and status checks | jarvis-session-orchestrator | `JARVIS_SCHEDULE_RUNBOOK.md` | ChatGPT schedules; runtime scheduler; Slack if configured | n/a | planned | No schedules configured | Add schedules only after approval, cost and notification policies are reconciled |
| Other-Agent Unification | Import similar agents as evidence and merge superior modules | source-first-project-continuity | `JARVIS_OTHER_AGENT_UNIFICATION_WORKFLOW.md`; `JARVIS_MASTER_SPEC.md` | Files, GitHub, Drive as needed | module migration pipeline | drafted | Known agents/repos are identified but not fully reconciled | Inventory `hub`, `Jarvis-Health`, `videotranscribe`, and `property-agent-mcp` before shared-core migration |
| Bill CFO OCR MCP | Isolated OCR, evidence intake and finance document service shell | bill-cfo-ocr-source-intake | `services/bill-cfo-ocr-mcp/**` | Dedicated Railway service and finance sources | `services/bill-cfo-ocr-mcp` | connected | Historical Railway health proves shell only; OCR auth, workbook write and queue flows remain unproven | Verify current Railway health and smallest real OCR/evidence flow |
| XRP/HBAR Apex | Isolated XRP/HBAR intelligence MCP/runtime service | xrp-hbar-apex-tracker | `services/xrp-hbar-apex/**` | Dedicated Railway or other isolated service | `services/xrp-hbar-apex` | implemented | Repo routes exist; separate live service and authenticated MCP smoke are not yet proven | Create/verify dedicated service and run authenticated MCP smoke |
| Jarvis Health | Health intelligence, records, evidence grading and care coordination | Jarvis Health domain module | `rafsof22-lgtm/Jarvis-Health` and future module map | Health data connectors under consent | isolated health domain | drafted | Repository requires content and security reconciliation | Inventory repo, map sensitive data boundaries and generate module integration plan |
| Video Intelligence | Transcription, OCR, social/video intake, extraction and evidence workflows | vti-video-intelligence-builder | `rafsof22-lgtm/videotranscribe` | Platform/API sources as approved | isolated video domain | implemented | Must reconcile with XRP/HBAR transcript tools and shared ingestion without duplication | Audit repo and define shared transcript contract plus domain-specific consumers |
| Property Buyer Intelligence | Capture, source-proof, dedupe, score and enrich property buyers | property-buyer-capture | `rafsof22-lgtm/property-agent-mcp` | Search/enrichment sources and sheets/DB | isolated property domain | implemented | Capture-only boundary and deployment/integration state require verification | Audit MCP routes, data stores and buyer database workflow; preserve no-outreach default |

## Connected Repository Map

| Repository | Role | Current handling |
|---|---|---|
| `rafsof22-lgtm/jarvis-build` | Primary implementation spine and shared control repository | Continue through branches, PRs, CI and service isolation |
| `rafsof22-lgtm/hub` | Existing hub/XRP-HBAR deployment evidence | Reconcile before reuse; do not treat as automatic canonical replacement |
| `rafsof22-lgtm/Jarvis-Health` | Health-domain repository | Keep privacy-isolated and map into Jarvis Health module |
| `rafsof22-lgtm/videotranscribe` | Video/transcript intelligence repository | Extract reusable ingestion contracts without erasing domain logic |
| `rafsof22-lgtm/property-agent-mcp` | Property/buyer MCP repository | Preserve capture-only policy unless outreach is separately approved |

## Immediate P0 Backlog

1. Merge the repository-tracked `JARVIS_MASTER_SPEC.md` after checks and review.
2. Complete controlled verbatim transfer of the full user-supplied baseline into `JARVIS_BUILD_FRAMEWORK_CURRENT`.
3. Create the canonical source, requirement, decision, integration, secret, workflow, deployment, test, evidence, cost and incident registry schemas.
4. Inventory and reconcile all five connected repositories into the module map without blind merging.
5. Expand secret requirement discovery across each repository and service using names and aliases only.
6. Implement provider-neutral model adapter and usage/cost telemetry around the tested no-network router scaffold.
7. Define the shared workflow/event envelope, queue, retry, idempotency, dead-letter and reconciliation contracts.
8. Select and verify a staging deployment path before adding production deployment steps.
9. Add runtime health, readiness, dependency, cost, freshness and rollback evidence contracts.
10. Reconcile standing agent-editor authorization with explicit environment, repository, action-class and budget policies.

## Update Log

- Initial registry created to consolidate the Jarvis setup gap audit into a durable control file.
- 2026-07-17: Verified GitHub repo `rafsof22-lgtm/jarvis-build`, base branch `main`, and safe work branch for control-registry/model-router PR work.
- 2026-07-17: Reconciled merged PRs #2-#5 and removed the stale pending-PR statement.
- 2026-07-17: Added master framework/spec, secret discovery, integration fabric, workflow/event runtime, connected repository, and known domain module rows.
- 2026-07-17: Added P0 work for full baseline transfer, cross-repository reconciliation, model telemetry, shared workflow contracts, staging deployment and evidence schemas.
