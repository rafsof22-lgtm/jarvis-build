# XRP/HBAR Apex Deployment Ledger

Last updated: 2026-07-07

## Service identity

- Service root: `services/xrp-hbar-apex/`
- Deploy branch: `main`
- Railway service target: `xrp-hbar-intelligence` as a new dedicated Railway service mapped to `services/xrp-hbar-apex/`
- GitHub tracking issue: `https://github.com/rafsof22-lgtm/jarvis-build/issues/1`
- Env namespace: `XRP_HBAR_APEX_`
- Queue/job namespace: `xrp_hbar_apex_`
- Database object prefix: `xrp_hbar_apex_`
- Webhook namespace: `xrp-hbar-apex-*`

## Route contract

- Health path: `/health`
- Ready path: `/ready`
- Deployment-status path: `/deployment/status`
- Namespaced health path: `/xrp-hbar-apex/health`
- Namespaced ready path: `/xrp-hbar-apex/ready`
- Namespaced deployment-status path: `/xrp-hbar-apex/deployment/status`
- MCP discovery path: `/mcp`
- MCP tool list path: `/mcp/tools`
- MCP execution path: authenticated `POST /mcp`
- Smoke test path: `scripts/smoke-test.sh`
- Live verification script: `scripts/verify-live.mjs`

## 2026-07-07 metadata-first MCP patch

- `GITHUB_REPO_TRUTH`: `rafsof22-lgtm/jarvis-build`
- `BRANCH_TRUTH`: `main`
- `MODULE_OWNERSHIP_MAPPED`: `services/xrp-hbar-apex/`
- `POST_MCP_PATCH`: implemented authenticated MCP dispatch.
- `MCP_TOOLS_EXPOSED`: `extract_metadata`, `reprocess_transcript`, `transcribe_url`, `transcribe_file`, `extract_ocr`.
- `MCP_LIMITATION_TRUTH`: metadata and supplied-transcript processing are implemented; provider-backed transcription/OCR is still not connected.
- `SMOKE_EXPECTATION`: `/health`, `/ready`, `/deployment/status`, namespaced aliases, `/mcp`, `/mcp/tools`, and authenticated `POST /mcp` with `extract_metadata`.
- `NO_FAKE_SUCCESS_CLAIM`: Railway service truth, env var truth, live URL, runtime health, readiness, deployment status, and live smoke test are not proven until Railway verification passes.

## 2026-07-07 exact Railway action

- Exact service name locked: `xrp-hbar-intelligence`.
- Exact root directory: `services/xrp-hbar-apex`.
- Exact watch path: `/services/xrp-hbar-apex/**`.
- Exact start command: `npm start`.
- Exact health path: `/health`.
- GitHub issue created for Railway account step: `https://github.com/rafsof22-lgtm/jarvis-build/issues/1`.
- Action checklist file: `services/xrp-hbar-apex/docs/railway-action-now.md`.

## Current blockers

- `NEEDS_RAILWAY_ACCESS`: Railway service creation and approval still happen in Railway.
- `MISSING_RAILWAY_SERVICE_FOR_XRP_HBAR`: no direct proof of a separate `xrp-hbar-intelligence` service exists yet.
- `MISSING_ENV_VAR`: live smoke requires `BASE_URL` and production MCP auth variables after Railway creates a public URL.
- `SECRET_OWNER_ACTION_REQUIRED`: `MCP_BEARER_TOKEN` must be created as a Railway secret outside chat.
- `PROVIDER_NOT_CONNECTED`: transcription, OCR, storage, database, and scheduled-worker providers are not wired.

## Minimum Railway approval action

Create or approve a dedicated Railway service with:

- Service: `xrp-hbar-intelligence`
- Repository: `rafsof22-lgtm/jarvis-build`
- Branch: `main`
- Root directory: `services/xrp-hbar-apex`
- Start command: `npm start`
- Health path: `/health`
- Watch path: `/services/xrp-hbar-apex/**`

Then set:

- `APP_ENV=production`
- `BASE_URL=<public Railway URL>`
- `LOG_LEVEL=info`
- `MCP_AUTH_MODE=bearer`
- `MCP_BEARER_TOKEN=<Railway secret>`

Then verify `/health`, `/ready`, `/deployment/status`, `/xrp-hbar-apex/health`, `/mcp`, `/mcp/tools`, and authenticated `POST /mcp`.

## Rollback path

Use `docs/rollback.md`. Repo rollback should revert only XRP/HBAR service-root commits unless a separate shared-service change is proven. Railway rollback should target only the dedicated XRP/HBAR Railway service.

## Proof boundary

This ledger is a prepared deployment record. It is not proof that Railway is connected, variables are valid, public URLs exist, or live routes work.
