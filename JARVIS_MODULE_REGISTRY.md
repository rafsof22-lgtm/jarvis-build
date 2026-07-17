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
| Source Intake | Ingest files, archives, chat exports, repos, Drive/Notion/Gmail/Slack evidence | jarvis-build-orchestrator | JARVIS_MASTER_SPEC.md; runtime/packages/source_ingestion/service.py | GitHub, Drive, Gmail, Notion, Slack where relevant | runtime/packages/source_ingestion | drafted | Needs stronger source inventory and dedupe schema | Create source inventory schema and tests |
| Requirement Reconciliation | Merge requirements, detect contradictions, preserve source hierarchy | jarvis-verification-discrepancy | JARVIS_FORENSIC_TASK_MAP.md | GitHub, Drive, Notion | runtime/packages/patching | drafted | Needs canonical contradiction register | Add contradiction table to forensic map |
| Skill Dedupe | Classify skills as keep, merge, archive, route-only | skill-orchestrator-router | JARVIS_SKILL_DEDUPE_MAP.md | None required | n/a | planned | Needs full skill content inspection before detach decisions | Inspect overlapping skills before any removal |
| App Risk & Approval | Govern read/write/deploy/send actions and approval policy | project-stack-access-mapper | JARVIS_APP_RISK_APPROVAL_MATRIX.md | All connected apps | n/a | planned | Many write apps currently set to never ask | Decide which writes require confirmation |
| GitHub Execution | Prepare repo patches, branches, commits, PRs, CI checks | jarvis-build-orchestrator | runtime/docs/specs/GITHUB_WRITE_EXECUTION_SEQUENCE.md; runtime/docs/specs/REPO_EXECUTION_PACKAGE.md | GitHub | runtime/packages/connectors/github_repo.py | drafted | Repo `rafsof22-lgtm/jarvis-build`, base `main`, and work branch `jarvis/control-registry-model-router-plan` verified; CI/PR proof pending | Open PR and verify checks |
| Deployment Automation | Bootstrap, deploy, rollback, smoke test runtime | jarvis-sovereign-builder | ORACLE_FREE_TIER_DEPLOYMENT_BLUEPRINT.md; runtime/infra/scripts/* | GitHub, DigitalOcean/Hostinger/Hercules as fallback | runtime/infra | drafted | Oracle requires external account/secrets; live host not verified | Choose target host and place secrets |
| Hybrid Model Router | Route tasks across GPT, DeepSeek, Kimi, Qwen, local models | jarvis-research-sourcing | JARVIS_HYBRID_MODEL_ROUTER_PLAN.md | OpenRouter/API keys when used | runtime/packages/model_router planned | planned | API keys and provider choices not yet configured | Implement LiteLLM/OpenRouter-compatible router |
| API Channel Control | Define safe external trigger payloads and forbidden actions | project-stack-access-mapper | JARVIS_API_CHANNEL_RUNBOOK.md | API channel | n/a | drafted | Needs external caller allowlist and payload schemas | Define trigger payload examples |
| Observability | Health, cost, drift, source freshness, smoke tests | jarvis-verification-discrepancy | JARVIS_OBSERVABILITY_AND_SMOKE_TEST_MATRIX.md | GitHub, host provider, optional monitoring app | runtime tests/CI | planned | No external monitoring attached yet | Start with GitHub Actions and runtime health endpoint |
| Schedules | Daily/weekly/monthly Jarvis audits and status checks | jarvis-session-orchestrator | JARVIS_SCHEDULE_RUNBOOK.md | ChatGPT schedules; Slack if configured | n/a | planned | No schedules configured | Add schedules after approval matrix exists |
| Other-Agent Unification | Import similar agents as evidence, merge superior modules | source-first-project-continuity | JARVIS_OTHER_AGENT_UNIFICATION_WORKFLOW.md | Files, imports, GitHub/Drive as needed | n/a | planned | Needs exports from other agents | Import/export each candidate agent as evidence |

## Immediate P0 Backlog

1. Create and maintain a complete skill dedupe map.
2. Create and maintain app risk/approval matrix.
3. Open and verify PR from `jarvis/control-registry-model-router-plan` into `main`.
4. Define secrets required for OpenRouter, DeepSeek, Kimi, Qwen, Oracle, DigitalOcean, Hostinger, and Hercules.
5. Implement or patch the hybrid model-router runtime module.
6. Add CI smoke tests for router, source ingestion, patch planning, and health endpoint.
7. Add deployment target matrix and choose free-first default.

## Update Log

- Initial registry created to consolidate the Jarvis setup gap audit into a durable control file.
- 2026-07-17: Verified GitHub repo `rafsof22-lgtm/jarvis-build`, base branch `main`, and safe work branch `jarvis/control-registry-model-router-plan` for control-registry/model-router PR work.
