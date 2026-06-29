# XRP/HBAR Apex Railway Deployment Notes

## Service classification

- Jarvis module: `xrp-hbar-apex`
- Runtime class: `RAILWAY_SERVICE`
- Repo: `rafsof22-lgtm/jarvis-build`
- Root directory: `services/xrp-hbar-apex`
- Start command: `npm start`
- Health path: `/health`
- Readiness path: `/ready`

## Current proof boundary

The repo files can be committed and tested through GitHub. Railway live state still requires external Railway access. Do not claim a live Railway deployment until a Railway URL returns successful responses for `/health`, `/ready`, and `/deployment/status`.

## Variables

Required for current shell:

- none beyond Railway-provided `PORT`

Recommended:

- `APP_ENV=production`
- `LOG_LEVEL=info`

Future only:

- `OPENAI_API_KEY`
- `JOB_SIGNING_SECRET`
- `POSTGRES_URL`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `GOOGLE_SHEET_ID`
- `GITHUB_TOKEN`
- `N8N_WEBHOOK_BASE_URL`
- `N8N_WEBHOOK_SECRET`

## Smoke test

After Railway deploys the service, verify:

```text
GET /health
GET /ready
GET /deployment/status
```

Expected first-run result:

- health and readiness return `200`
- deployment status returns `200`
- `/mcp` returns `501` until real MCP handling is implemented

## Next implementation steps

1. Add a real signed job route only after `JOB_SIGNING_SECRET` is configured.
2. Add tracker execution endpoints only after a durable source/register persistence model exists.
3. Add Postgres only when the service writes persistent tracker state.
4. Add scheduled workers only when Railway cron or an external scheduler is explicitly connected.
