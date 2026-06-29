# XRP/HBAR Apex Intelligence OS Service

Status: deployment-ready service shell, not a full deployed intelligence engine.

This directory is the isolated Jarvis monorepo service root for XRP/HBAR Apex Intelligence OS. Railway should deploy this service with the root directory set to:

```text
services/xrp-hbar-apex
```

## Implemented now

- `GET /health` for Railway health checks.
- `GET /ready` for runtime readiness checks.
- `GET /deployment/status` for no-fake-automation runtime truth.
- `GET /` for a plain service summary.
- `GET /mcp/tools` as an explicit empty tool surface until real tools are implemented.
- `POST /mcp` returns `501 not_implemented` so no MCP capability is implied.

## Not implemented yet

- Full XRP/HBAR tracker execution.
- Live market, on-chain, social, transcript, or proof-gate scans.
- ChatGPT Memory access from this external service.
- Scheduled worker execution.
- Google Drive, Sheets, GitHub mutation, n8n, or database persistence.
- Archive ingestion or full historical reconstruction.

## Railway setup

1. Create a dedicated Railway service from `rafsof22-lgtm/jarvis-build`.
2. Set the service root directory to `services/xrp-hbar-apex`.
3. Set only the variables the deployed code actually uses.
4. Deploy and verify:
   - `/health`
   - `/ready`
   - `/deployment/status`

## Required variables

No secret is required for the current shell. Railway should provide `PORT`.

Recommended non-secret variables:

- `APP_ENV=production`
- `LOG_LEVEL=info`

Future secret variables must be stored in Railway variables, GitHub secrets, or a vault. Do not paste secrets into chat and do not commit real `.env` files.

## Runtime truth

This service proves that an isolated XRP/HBAR Apex HTTP runtime can boot under the Jarvis monorepo. It does not prove that Railway is connected, that a public Railway domain exists, or that the full XRP/HBAR intelligence framework is running externally.
