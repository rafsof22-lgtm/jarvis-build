# Bill CFO OCR MCP Service

Purpose: isolated Railway-ready service shell for the Bill CFO OCR MCP module. This scaffold prepares health, readiness, and deployment-status routes before any OCR provider, workbook write, queue, or external integration is claimed live.

## Service root

```text
services/bill-cfo-ocr-mcp/
```

## Current Railway boundary

User-supplied Railway logs from 2026-07-07 show the active connected Railway deployment is Bill CFO:

```text
@jarvis/bill-cfo-ocr-mcp@0.1.0 start
node src/server.js
bill-cfo-ocr-mcp listening on port 8080
snapshot-target-unpack/services/bill-cfo-ocr-mcp
/health healthcheck succeeded
```

Keep this service connected as the Bill-CFO runtime. Do not repurpose it for XRP/HBAR. XRP/HBAR must use a separate Railway service rooted at `services/xrp-hbar-apex/`.

## Isolation and namespace rules

- Route namespace: `/bill-cfo-ocr-mcp/*`
- Env prefix: `BILL_CFO_OCR_MCP_`
- Queue/job prefix: `bill_cfo_ocr_mcp_`
- Database prefix: `bill_cfo_ocr_mcp_`
- Webhook prefix: `bill-cfo-ocr-mcp-`

Do not merge this service into another runtime root and do not assume shared secrets are safe.

## Required routes

- `GET /health`
- `GET /ready`
- `GET /deployment/status`

The same route contract is also available under the service namespace, for example `/bill-cfo-ocr-mcp/health`.

## Env expectations

Use `.env.example` as the non-secret template. Store real values only in Railway variables, GitHub secrets, or an approved vault. Never commit real secrets.

Required-now placeholders:

- `APP_ENV`
- `BASE_URL`
- `LOG_LEVEL`

Route/provider-specific placeholders are listed in `.env.example` and stay optional until the OCR or workbook route is implemented.

## Railway mapping

Use the existing dedicated Railway service mapped to:

```text
services/bill-cfo-ocr-mcp/
```

Deploy branch: `main`.

Do not change the Bill-CFO Railway root, variables, start command, deploy branch, or domain while creating or fixing XRP/HBAR.

## Smoke test

After Railway provides a live URL and required env vars are set, run:

```bash
BILL_CFO_OCR_MCP_URL=https://<service-url> bash scripts/smoke-test.sh
```

For JSON route detail, run:

```bash
BILL_CFO_OCR_MCP_URL=https://<service-url> npm run live:verify
```

## Rollback

Use `docs/rollback.md` for repo and Railway rollback notes. Roll back only this service root unless a separate shared-service change is proven.

## Proof boundary

`AGENT_REGISTRY_UPDATED` / `MODULE_OWNERSHIP_MAPPED` means the scaffold exists in GitHub. User-supplied Railway logs prove shell startup and `/health` only. They do not prove OCR provider auth, workbook writes, queue workers, or finance workflow completion.
