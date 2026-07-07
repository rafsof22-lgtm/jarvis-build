# Bill CFO OCR MCP Deployment Ledger

Last updated: 2026-07-07

## Current state

- `REPO_LOCATOR_SET`: locator added at `services/bill-cfo-ocr-mcp/docs/agent-locator.md`.
- `SERVICE_ROOT_CONFIRMED`: root `services/bill-cfo-ocr-mcp/` is present in GitHub.
- `MODULE_OWNERSHIP_MAPPED`: Bill CFO agent default edit scope is `services/bill-cfo-ocr-mcp/**`.
- `AGENT_REGISTRY_UPDATED`: service-local instructions added at `services/bill-cfo-ocr-mcp/AGENTS.md`.
- `LIVE_SHELL_LOG_SUPPLIED_BY_USER`: Railway logs supplied on 2026-07-07 show the connected active deployment is Bill CFO: `@jarvis/bill-cfo-ocr-mcp@0.1.0 start`, `node src/server.js`, `bill-cfo-ocr-mcp listening on port 8080`, build snapshot rooted at `services/bill-cfo-ocr-mcp`, and `/health` healthcheck succeeded.
- `NO_FAKE_SUCCESS_CLAIM`: The supplied logs prove Bill CFO shell startup and healthcheck only. OCR provider auth, workbook writes, queue jobs, and finance workflows are not proven until route-level smoke tests pass.

## Repo locator

- GitHub repo: `rafsof22-lgtm/jarvis-build`
- Repo URL: `https://github.com/rafsof22-lgtm/jarvis-build`
- Default branch: `main`
- Service root: `services/bill-cfo-ocr-mcp/`
- Service-local instructions: `services/bill-cfo-ocr-mcp/AGENTS.md`
- Locator: `services/bill-cfo-ocr-mcp/docs/agent-locator.md`
- Live verifier: `services/bill-cfo-ocr-mcp/scripts/verify-live.mjs`

## Required Railway mapping

- Railway service model: dedicated service inside the Jarvis Railway project
- Railway service root: `services/bill-cfo-ocr-mcp/`
- Deploy branch: `main`
- Build mode: Nixpacks via `railway.json`
- Start command: `npm start`
- Health path: `/health`
- Ready path: `/ready`
- Status path: `/deployment/status`

Do not map Bill CFO to repo root, `services/xrp-hbar-apex/`, or any other module root. Do not change Bill-CFO service settings while creating or fixing XRP/HBAR.

## Route proof chain

Verify these before any broader live claim:

1. `GET /health`
2. `GET /ready`
3. `GET /deployment/status`
4. `GET /bill-cfo-ocr-mcp/health`
5. `GET /bill-cfo-ocr-mcp/ready`
6. `GET /bill-cfo-ocr-mcp/deployment/status`
7. smallest real OCR route smoke test after an OCR route exists
8. workbook/queue smoke test only after those integrations are implemented

Live verification command after Railway URL exists:

```bash
cd services/bill-cfo-ocr-mcp
BILL_CFO_OCR_MCP_URL="https://jarvis-build-production.up.railway.app" npm run live:verify
```

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

GitHub locator and service shell are proven. User-supplied Railway logs prove Bill-CFO shell startup and `/health` healthcheck. Railway `/ready`, `/deployment/status`, OCR provider auth, workbook writes, queue jobs, and end-to-end finance workflows are not proven in this run.
