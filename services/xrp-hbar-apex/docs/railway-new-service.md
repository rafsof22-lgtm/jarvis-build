# XRP/HBAR Apex Railway New Service Handoff

Last updated: 2026-07-07

## Purpose

Use this file when creating the dedicated Railway service for XRP/HBAR Apex from the shared `rafsof22-lgtm/jarvis-build` monorepo.

## GitHub source truth

- Repository: `rafsof22-lgtm/jarvis-build`
- Deploy branch: `main`
- Service root directory: `services/xrp-hbar-apex`
- Runtime package: `@jarvis/xrp-hbar-apex`
- Start command: `npm start`
- Railway config file: `services/xrp-hbar-apex/railway.json`

## Railway service creation

Create a new Railway service, separate from Bill CFO OCR MCP and any other future service.

Required Railway settings:

- Service name: `xrp-hbar-intelligence` or `xrp-hbar-apex`
- Source repo: `rafsof22-lgtm/jarvis-build`
- Branch: `main`
- Root directory: `services/xrp-hbar-apex`
- Builder: Nixpacks
- Start command: `npm start`
- Health check path: `/health`
- Optional watch path: `/services/xrp-hbar-apex/**`

Do not deploy from the repo root. Do not reuse the Bill CFO OCR MCP Railway service. Do not change Bill-CFO variables, start command, deploy branch, domain, or root directory.

## Minimum variables for the current MCP runtime

Required now:

- `APP_ENV=production`
- `BASE_URL=<Railway public URL after Railway creates it>`
- `LOG_LEVEL=info`
- `MCP_AUTH_MODE=bearer`
- `MCP_BEARER_TOKEN=<set as a Railway secret only>`

Railway normally injects `PORT` automatically. Do not hardcode Railway service IDs or project IDs in repo code.

## Future-only secrets

Do not add these until the corresponding feature is implemented and verified:

- `OPENAI_API_KEY`
- `TRANSCRIPT_PROVIDER_API_KEY`
- `OCR_PROVIDER_API_KEY`
- `JOB_SIGNING_SECRET`
- `POSTGRES_URL`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_SHEET_ID`
- `GITHUB_TOKEN`
- `N8N_WEBHOOK_BASE_URL`
- `N8N_WEBHOOK_SECRET`

Never paste real secret values into chat or commit them to GitHub.

## Approval and verification chain

After Railway creates the service and deploys this branch, verify:

1. Railway service root is `services/xrp-hbar-apex`.
2. Latest deployment commit is from `main` after the 2026-07-07 MCP service commits.
3. `GET /health` returns HTTP 200 JSON.
4. `GET /ready` returns HTTP 200 JSON.
5. `GET /deployment/status` returns HTTP 200 JSON and shows `railwayRootDirectory: services/xrp-hbar-apex`.
6. `GET /xrp-hbar-apex/health` returns HTTP 200 JSON.
7. `GET /mcp` returns HTTP 200 JSON and shows the request shape.
8. `GET /mcp/tools` returns HTTP 200 JSON listing the implemented tools.
9. Authenticated `POST /mcp` with `extract_metadata` returns HTTP 200 JSON with `ok:true`.

Repo-side smoke command after Railway URL and auth exist:

```bash
cd services/xrp-hbar-apex
XRP_HBAR_APEX_URL="https://your-service.up.railway.app" \
MCP_AUTH_MODE="bearer" \
MCP_BEARER_TOKEN="<Railway secret>" \
npm run live:verify
```

Alternative shell smoke command:

```bash
cd services/xrp-hbar-apex
XRP_HBAR_APEX_URL="https://your-service.up.railway.app" \
MCP_AUTH_MODE="bearer" \
MCP_BEARER_TOKEN="<Railway secret>" \
npm run smoke
```

## Proof boundary

This handoff proves the GitHub service root and Railway setup contract are prepared. It is not proof that Railway created the XRP/HBAR service, deployed it, assigned a public domain, or passed live route checks.

Use these labels after successful Railway verification:

- `RAILWAY_SERVICE_TRUTH`
- `AUTO_DEPLOY_TRIGGERED`
- `RUNTIME_HEALTH_VERIFIED`
- `RUNTIME_READY_VERIFIED`
- `MCP_ROUTE_VERIFIED_LIVE`
- `ROUTE_SMOKE_VERIFIED`

Until then, keep these blockers active:

- `MISSING_RAILWAY_SERVICE_FOR_XRP_HBAR` if no separate XRP/HBAR service exists
- `DEPLOYMENT_DRIFT` if the active deployment is still Bill-CFO
- `RAILWAY_ROOT_DIRECTORY_MISCONFIGURATION` if an XRP/HBAR service exists but is not rooted at `services/xrp-hbar-apex`
- `NEEDS_RAILWAY_ACCESS` when no Railway control surface is available here
- `MISSING_ENV_VAR` for `BASE_URL`, `MCP_AUTH_MODE`, or `MCP_BEARER_TOKEN` before live smoke verification
