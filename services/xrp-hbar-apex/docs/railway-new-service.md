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

- Source repo: `rafsof22-lgtm/jarvis-build`
- Branch: `main`
- Root directory: `services/xrp-hbar-apex`
- Builder: Nixpacks
- Start command: `npm start`
- Health check path: `/health`

Do not deploy from the repo root. Do not reuse the Bill CFO OCR MCP Railway service.

## Minimum variables for the current shell

No secret is required for the current starter shell.

Recommended variables:

- `APP_ENV=production`
- `LOG_LEVEL=info`
- `BASE_URL=<Railway public URL after Railway creates it>`

Railway normally injects `PORT` automatically.

## Future-only secrets

Do not add these until the corresponding feature is implemented and verified:

- `OPENAI_API_KEY`
- `MCP_BEARER_TOKEN`
- `MCP_API_KEY`
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
2. Latest deployment commit is from `main` after the 2026-07-07 service-prep commits.
3. `GET /health` returns HTTP 200 JSON.
4. `GET /ready` returns HTTP 200 JSON.
5. `GET /deployment/status` returns HTTP 200 JSON and shows `railwayRootDirectory: services/xrp-hbar-apex`.
6. `GET /xrp-hbar-apex/health` returns HTTP 200 JSON.
7. `GET /mcp/tools` returns HTTP 200 JSON with an empty tool list.
8. `POST /mcp` returns HTTP 501 JSON because MCP handling is intentionally not implemented yet.

Repo-side smoke command after Railway URL exists:

```bash
cd services/xrp-hbar-apex
XRP_HBAR_APEX_URL="https://your-service.up.railway.app" npm run live:verify
```

Alternative shell smoke command:

```bash
cd services/xrp-hbar-apex
XRP_HBAR_APEX_URL="https://your-service.up.railway.app" npm run smoke
```

## Proof boundary

This handoff proves the GitHub service root and Railway setup contract are prepared. It is not proof that Railway created the service, deployed it, assigned a public domain, or passed live route checks.

Use these labels after successful Railway verification:

- `RAILWAY_SERVICE_TRUTH`
- `AUTO_DEPLOY_TRIGGERED`
- `RUNTIME_HEALTH_VERIFIED`
- `RUNTIME_READY_VERIFIED`
- `ROUTE_SMOKE_VERIFIED`

Until then, keep these blockers active:

- `NEEDS_RAILWAY_ACCESS`
- `BLOCKED_BY_MISSING_ACCESS`
- `MISSING_ENV_VAR` for the live URL before Railway assigns it
