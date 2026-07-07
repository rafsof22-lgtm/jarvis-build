# XRP/HBAR Apex Intelligence OS Service

Status: metadata-first MCP runtime, not a full deployed intelligence engine.

This directory is the isolated Jarvis monorepo service root for XRP/HBAR Apex Intelligence OS. Railway should deploy this service with the root directory set to:

```text
services/xrp-hbar-apex
```

## Implemented now

- `GET /health` for Railway health checks.
- `GET /ready` for runtime readiness checks.
- `GET /deployment/status` for no-fake-automation runtime truth.
- `GET /` for a plain service summary.
- `GET /mcp` for MCP request-shape discovery.
- `GET /mcp/tools` for implemented tool discovery.
- `POST /mcp` for authenticated MCP dispatch.

## Implemented MCP tools

- `extract_metadata`: validates and normalizes a source URL into a metadata-only evidence record.
- `reprocess_transcript`: extracts XRP/HBAR claim candidates from user-supplied transcript text.
- `transcribe_url`: records URL intake and returns honest provider limitations when transcription is not configured.
- `transcribe_file`: records file intake and returns honest provider limitations when file transcription is not configured.
- `extract_ocr`: records OCR intake and returns honest provider limitations when OCR is not configured.

## Not implemented yet

- Provider-backed URL transcription.
- Provider-backed file transcription.
- Provider-backed OCR extraction.
- Full XRP/HBAR tracker execution inside this service.
- Live market, on-chain, social, transcript, or proof-gate scans.
- ChatGPT Memory access from this external service.
- Scheduled worker execution.
- Google Drive, Sheets, GitHub mutation, n8n, or database persistence.
- Archive ingestion or full historical reconstruction.

## Railway setup

1. Create a dedicated Railway service from `rafsof22-lgtm/jarvis-build`.
2. Set the service root directory to `services/xrp-hbar-apex`.
3. Set `APP_ENV=production`, `BASE_URL=<public service URL>`, and production MCP auth.
4. Deploy and verify:
   - `/health`
   - `/ready`
   - `/deployment/status`
   - `/mcp/tools`
   - authenticated `POST /mcp`

## Required variables

- `APP_ENV=production`
- `BASE_URL=https://your-xrp-hbar-apex-service.up.railway.app`
- `MCP_AUTH_MODE=bearer`
- `MCP_BEARER_TOKEN=<set in Railway only>`

Future secret variables must be stored in Railway variables, GitHub secrets, or a vault. Do not paste secrets into chat and do not commit real `.env` files.

## Runtime truth

This service proves that an isolated XRP/HBAR Apex HTTP runtime can boot and dispatch metadata-first MCP calls under the Jarvis monorepo. It does not prove that Railway is connected, that a public Railway domain exists, that provider-backed transcription/OCR is available, or that the full XRP/HBAR intelligence framework is running externally.
