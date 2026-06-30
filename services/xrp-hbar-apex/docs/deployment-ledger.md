# XRP/HBAR Apex Deployment Ledger

Last updated: 2026-06-30

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
- Smoke test path: `scripts/smoke-test.sh`

## Verified state

- `GITHUB_REPO_TRUTH`: `rafsof22-lgtm/jarvis-build`
- `BRANCH_TRUTH`: `main`
- `MODULE_OWNERSHIP_MAPPED`: `services/xrp-hbar-apex/`
- `AGENT_REGISTRY_UPDATED`: service scaffold and operational files are tracked in GitHub.
- `NO_FAKE_SUCCESS_CLAIM`: Railway service truth, env var truth, live URL, runtime health, readiness, deployment status, and smoke test are not proven until Railway verification passes.

## Current blockers

- `NEEDS_RAILWAY_ACCESS`: no Railway control surface was available in the authoring session.
- `BLOCKED_BY_MISSING_ACCESS`: live deployment and route verification cannot be completed without Railway access.
- `MISSING_ENV_VAR`: live smoke requires `XRP_HBAR_APEX_URL` or `BASE_URL` after Railway creates a public URL.
- `SECRET_OWNER_ACTION_REQUIRED`: future real provider secrets must be set outside chat.

## Rollback path

Use `docs/rollback.md`. Repo rollback should revert only XRP/HBAR service-root commits unless a separate shared-service change is proven. Railway rollback should target only the dedicated XRP/HBAR Railway service.

## Proof boundary

This ledger is a prepared deployment record. It is not proof that Railway is connected, variables are valid, public URLs exist, or live routes work.
