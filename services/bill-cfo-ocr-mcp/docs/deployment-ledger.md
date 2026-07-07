# Bill CFO OCR MCP Deployment Ledger

Last updated: 2026-07-07

## Current state

- `REPO_LOCATOR_SET`: locator added at `services/bill-cfo-ocr-mcp/docs/agent-locator.md`.
- `SERVICE_ROOT_CONFIRMED`: root `services/bill-cfo-ocr-mcp/` is present in GitHub.
- `MODULE_OWNERSHIP_MAPPED`: Bill CFO agent default edit scope is `services/bill-cfo-ocr-mcp/**`.
- `AGENT_REGISTRY_UPDATED`: service-local instructions added at `services/bill-cfo-ocr-mcp/AGENTS.md`.
- `NO_FAKE_SUCCESS_CLAIM`: Railway service truth, env var truth, runtime health, readiness, service URL, and OCR route smoke are not proven until Railway verification passes.

## Repo locator

- GitHub repo: `rafsof22-lgtm/jarvis-build`
- Repo URL: `https://github.com/rafsof22-lgtm/jarvis-build`
- Default branch: `main`
- Service root: `services/bill-cfo-ocr-mcp/`
- Service-local instructions: `services/bill-cfo-ocr-mcp/AGENTS.md`
- Locator: `services/bill-cfo-ocr-mcp/docs/agent-locator.md`

## Required Railway mapping

- Railway service model: dedicated service inside the Jarvis Railway project
- Railway service root: `services/bill-cfo-ocr-mcp/`
- Deploy branch: `main`
- Build mode: Nixpacks via `railway.json`
- Start command: `npm start`
- Health path: `/health`
- Ready path: `/ready`
- Status path: `/deployment/status`

Do not map Bill CFO to repo root, `services/xrp-hbar-apex/`, or any other module root.

## Route proof chain

Verify these before any live claim:

1. `GET /health`
2. `GET /ready`
3. `GET /deployment/status`
4. `GET /bill-cfo-ocr-mcp/health`
5. `GET /bill-cfo-ocr-mcp/ready`
6. `GET /bill-cfo-ocr-mcp/deployment/status`
7. smallest real OCR route smoke test after an OCR route exists
8. workbook/queue smoke test only after those integrations are implemented

## Protected peer systems

Bill CFO work must not compromise:

- `services/xrp-hbar-apex/**`
- other `services/*/**` roots
- repo-wide deployment behavior used by another service
- another service's secrets, env var names, health routes, ready routes, start commands, smoke tests, rollback docs, or Railway mapping

## Blockers until runtime access exists

- `NEEDS_RAILWAY_ACCESS`
- `SECRET_OWNER_ACTION_REQUIRED` for real provider/API secrets
- `MISSING_ENV_VAR` until Railway variables are set
- `BLOCKED_BY_MISSING_ACCESS` for live route verification in environments without Railway control
- `DEPLOYMENT_DRIFT` if Railway points to the wrong repo, branch, service root, command, or route

## Current proof boundary

GitHub locator and service shell are proven. Railway deployment, public URL, live health, live readiness, OCR provider auth, workbook writes, queue jobs, and end-to-end finance workflows are not proven in this run.
