# XRP/HBAR Apex Deployment Ledger

Last updated: 2026-07-07

## Service identity

- Service root: `services/xrp-hbar-apex/`
- Deploy branch: `main`
- Railway service target: pending dedicated Railway service mapped to `services/xrp-hbar-apex/`
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
- Smallest current live route: `/mcp/tools` returns an implemented empty tool list
- Expected not-yet-implemented route: `POST /mcp` returns HTTP 501
- Smoke test path: `scripts/smoke-test.sh`
- Live verification script: `scripts/verify-live.mjs`

## 2026-07-07 repo-side push

- `GITHUB_REPO_TRUTH`: `rafsof22-lgtm/jarvis-build`
- `BRANCH_TRUTH`: `main`
- `MODULE_OWNERSHIP_MAPPED`: `services/xrp-hbar-apex/`
- `AGENT_REGISTRY_UPDATED`: root README now lists the XRP/HBAR Apex service root.
- `DEPLOY_CONFIG_TRUTH`: `services/xrp-hbar-apex/railway.json` defines Nixpacks, `npm start`, and `/health`.
- `RAILWAY_SERVICE_HANDOFF_READY`: `docs/railway-new-service.md` gives the exact Railway new-service setup and approval checks.
- `NO_FAKE_SUCCESS_CLAIM`: Railway service truth, env var truth, live URL, runtime health, readiness, deployment status, and smoke test are not proven until Railway verification passes.

## Current blockers

- `NEEDS_RAILWAY_ACCESS`: Railway service creation and approval still happen in Railway.
- `BLOCKED_BY_MISSING_ACCESS`: live deployment and route verification cannot be completed from this repo-only push.
- `MISSING_ENV_VAR`: live smoke requires `XRP_HBAR_APEX_URL` or `BASE_URL` after Railway creates a public URL.
- `SECRET_OWNER_ACTION_REQUIRED`: future real provider secrets must be set outside chat.

## Minimum Railway approval action

Create or approve a dedicated Railway service with:

- Repository: `rafsof22-lgtm/jarvis-build`
- Branch: `main`
- Root directory: `services/xrp-hbar-apex`
- Start command: `npm start`
- Health path: `/health`

Then verify `/health`, `/ready`, `/deployment/status`, `/xrp-hbar-apex/health`, and `/mcp/tools`.

## Rollback path

Use `docs/rollback.md`. Repo rollback should revert only XRP/HBAR service-root commits unless a separate shared-service change is proven. Railway rollback should target only the dedicated XRP/HBAR Railway service.

## Proof boundary

This ledger is a prepared deployment record. It is not proof that Railway is connected, variables are valid, public URLs exist, or live routes work.
