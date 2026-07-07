# Bill CFO OCR MCP Repo and Railway Locator

Last updated: 2026-07-07

## Locator Summary

- Agent/module: Bill CFO OCR MCP
- GitHub repo: `rafsof22-lgtm/jarvis-build`
- Repo URL: `https://github.com/rafsof22-lgtm/jarvis-build`
- Default branch: `main`
- Service root: `services/bill-cfo-ocr-mcp/`
- Railway model: dedicated Railway service inside the Jarvis project, mapped to this service root
- Route namespace: `/bill-cfo-ocr-mcp/*`
- Env namespace: `BILL_CFO_OCR_MCP_*`

## First Files To Read

1. `services/bill-cfo-ocr-mcp/AGENTS.md`
2. `services/bill-cfo-ocr-mcp/README.md`
3. `services/bill-cfo-ocr-mcp/docs/deployment-ledger.md`
4. `services/bill-cfo-ocr-mcp/docs/rollback.md`
5. `services/bill-cfo-ocr-mcp/.env.example`
6. `services/bill-cfo-ocr-mcp/railway.json`
7. `services/bill-cfo-ocr-mcp/src/server.js`

## What The Agent May Edit

Default allowed write scope:

- `services/bill-cfo-ocr-mcp/**`

Conditional write scope:

- root `README.md` or root `AGENTS.md` only for safe locator or non-interference updates
- shared packages only after confirming the change is generic, backwards-compatible, and safe for every service using it

Protected peer roots:

- `services/xrp-hbar-apex/**`
- any other `services/*/**` path not explicitly assigned to Bill CFO

## Railway Service Mapping

The Railway service for Bill CFO should be configured as:

| setting | value |
|---|---|
| GitHub repo | `rafsof22-lgtm/jarvis-build` |
| branch | `main` |
| root directory | `services/bill-cfo-ocr-mcp/` |
| build mode | Nixpacks via `railway.json` |
| start command | `npm start` |
| health path | `/health` |
| ready path | `/ready` |
| deployment status path | `/deployment/status` |

Do not point this Railway service at the repo root or at another service directory. If Railway is already pointed elsewhere, classify that as `DEPLOYMENT_DRIFT` until corrected.

## Route Verification

After Railway exposes a public URL, verify these routes:

- `GET /health`
- `GET /ready`
- `GET /deployment/status`
- `GET /bill-cfo-ocr-mcp/health`
- `GET /bill-cfo-ocr-mcp/ready`
- `GET /bill-cfo-ocr-mcp/deployment/status`

Then verify the smallest real OCR/workbook path only after that route exists and required provider credentials are configured.

## Environment Variables

Required for the starter shell:

- `APP_ENV`
- `BASE_URL`
- `LOG_LEVEL`

Optional until a route uses them:

- `OPENAI_API_KEY`
- `OCR_PROVIDER_API_KEY`
- `OCR_PROVIDER_BASE_URL`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_SHEET_ID`
- `POSTGRES_URL`
- `REDIS_URL`
- `JOB_SIGNING_SECRET`
- `WEBHOOK_SECRET`

Never paste real secret values into chat or commit them to GitHub. Store real values in Railway variables, GitHub secrets, or an approved vault.

## Current Proof Status

Confirmed from GitHub on 2026-07-07:

- repo exists: `rafsof22-lgtm/jarvis-build`
- default branch is `main`
- service root exists: `services/bill-cfo-ocr-mcp/`
- service README exists
- `railway.json` exists
- `.env.example` exists
- `src/server.js` exists with health, ready, and deployment-status routes

Not proven in this run:

- Railway project/service existence
- Railway service root mapping
- Railway public URL
- Railway env var truth
- live `/health`, `/ready`, or `/deployment/status`
- OCR provider auth
- workbook writes
- queue jobs
- production-ready end-to-end workflow

## Blocker Labels

Use these exact labels when blocked:

- `NEEDS_RAILWAY_ACCESS`: Railway project/service cannot be inspected or controlled from the current run.
- `MISSING_ENV_VAR`: a required Railway variable is absent or blank.
- `PLACEHOLDER_SECRET`: a required secret is present only as a placeholder.
- `DEPLOYMENT_DRIFT`: Railway points to the wrong repo, branch, root directory, command, or route.
- `ROUTE_HEALTH_FAILURE`: a health/status route returns a failure or unreachable response.
- `SECRET_OWNER_ACTION_REQUIRED`: the user or authorized account owner must create or approve a real secret outside chat.
- `NO_FAKE_SUCCESS_CLAIM`: repo files alone do not prove live deployment.

## Handoff Rule

When another agent receives a Bill CFO task, hand it this locator first. The safe default instruction is:

"Work only in `services/bill-cfo-ocr-mcp/` in `rafsof22-lgtm/jarvis-build`, verify Railway root mapping before deployment claims, and do not alter XRP/HBAR Apex or any other Jarvis service unless the user explicitly requests a shared change."
