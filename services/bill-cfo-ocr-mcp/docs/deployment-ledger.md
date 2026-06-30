# Bill CFO OCR MCP Deployment Ledger

Last updated: 2026-06-30

## Current state

- `MODULE_OWNERSHIP_MAPPED`: root `services/bill-cfo-ocr-mcp/`.
- `AGENT_REGISTRY_UPDATED`: service scaffold added to the shared monorepo as an isolated root.
- `NO_FAKE_SUCCESS_CLAIM`: Railway service truth, env var truth, runtime health, readiness, service URL, and OCR route smoke are not proven until Railway verification passes.

## Required Railway mapping

- Railway service root: `services/bill-cfo-ocr-mcp/`
- Deploy branch: `main`
- Health path: `/health`
- Ready path: `/ready`
- Status path: `/deployment/status`

## Blockers until runtime access exists

- `NEEDS_RAILWAY_ACCESS`
- `SECRET_OWNER_ACTION_REQUIRED` for real provider/API secrets
- `MISSING_ENV_VAR` until Railway variables are set
- `BLOCKED_BY_MISSING_ACCESS` for live route verification in environments without Railway control
