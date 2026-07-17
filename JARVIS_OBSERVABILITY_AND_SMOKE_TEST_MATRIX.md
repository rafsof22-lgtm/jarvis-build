# Jarvis Observability And Smoke Test Matrix

## Purpose

This file defines how Jarvis proves that modules, app routes, deployment targets, and runtime services actually work.

## Observability Layers

| Layer | What To Monitor | First Free Route | Paid/Advanced Route |
|---|---|---|---|
| Agent config | instructions, files, skills, app setup, schedules, channels | manual/preview audits | scheduled audits |
| Runtime API | health endpoint, errors, latency | GitHub Actions curl checks | uptime monitor / Datadog / Coralogix |
| Worker queue | queued, running, failed jobs | logs and DB query | managed queue dashboards |
| Model router | provider used, cost, latency, failures | structured logs | tracing/metrics dashboard |
| Source ingestion | source count, freshness, duplicates | registry reports | data quality dashboard |
| GitHub execution | branch, commit, PR, CI status | GitHub Actions | external CI observability |
| Deployment | deploy success, rollback readiness | deploy logs + health checks | host monitoring |
| Cost | daily/monthly model/API/host estimates | Memory + reports | billing API integrations |

## Minimum Smoke Tests

### Agent Configuration

- Instructions reference all required control files.
- Starter prompts exist and match core workflows.
- Memory is enabled and named files are defined.
- API channel is live when external triggers are expected.

### Runtime

- `/health` returns OK.
- Source ingestion service imports a test source.
- Patch planner produces a test patch plan.
- Model router routes mock tasks to expected providers.
- Deployment script supports dry run or safe failure.

### GitHub

- Target repo accessible.
- Branch can be created.
- File can be added or updated on branch.
- PR can be opened.
- CI runs successfully.

### Deployment

- Secrets exist in GitHub Secrets or provider store.
- Docker build succeeds.
- Service starts.
- Health endpoint passes.
- Rollback script exists.

## First Free Observability Route

1. GitHub Actions CI and smoke checks.
2. Runtime structured logs.
3. Health endpoint.
4. Scheduled ChatGPT audits.
5. Memory files for build status, blockers, cost notes, and recent decisions.

## Paid Observability Upgrade

Add Datadog, Coralogix, or similar only after a real deployed runtime exists and free observability is insufficient.

## Open Gaps

- Target repo/branch confirmed for this pass: `rafsof22-lgtm/jarvis-build`, base `main`, work branch `jarvis/control-registry-model-router-plan`.
- Live runtime host not confirmed.
- External secrets not placed.
- Model router module not yet implemented.
- CI smoke tests need verification after the PR is opened.
