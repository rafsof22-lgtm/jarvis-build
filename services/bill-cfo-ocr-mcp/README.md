# Bill CFO OCR MCP Service

Purpose: isolated Railway-ready service shell for the Bill CFO OCR MCP module. This scaffold prepares health, readiness, and deployment-status routes before any OCR provider, workbook write, queue, or external integration is claimed live.

## Service root

```text
services/bill-cfo-ocr-mcp/
```

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

Create a dedicated Railway service mapped to:

```text
services/bill-cfo-ocr-mcp/
```

Deploy branch: `main`.

## Smoke test

After Railway provides a live URL and required env vars are set, run:

```bash
BILL_CFO_OCR_MCP_URL=https://<service-url> bash scripts/smoke-test.sh
```

## Rollback

Use `docs/rollback.md` for repo and Railway rollback notes. Roll back only this service root unless a separate shared-service change is proven.

## Proof boundary

`AGENT_REGISTRY_UPDATED` / `MODULE_OWNERSHIP_MAPPED` means the scaffold exists in GitHub. It does not prove Railway deployment, valid secrets, OCR provider auth, workbook writes, runtime health, readiness, or route smoke success.
