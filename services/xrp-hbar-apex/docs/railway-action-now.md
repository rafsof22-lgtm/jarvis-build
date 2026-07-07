# XRP/HBAR Railway Action Now

Last updated: 2026-07-07

## Decision

Create a new Railway project for XRP/HBAR and deploy the XRP/HBAR service from the existing GitHub repo. Do not reuse or edit the Bill-CFO Railway service.

This is a new Railway project/service boundary, not a new GitHub repo split.

## Exact Railway project/service settings

```text
Railway project: xrp-hbar-intelligence
Service: xrp-hbar-intelligence
Repo: rafsof22-lgtm/jarvis-build
Branch: main
Root directory: services/xrp-hbar-apex
Start command: npm start
Health path: /health
Watch path: /services/xrp-hbar-apex/**
```

## Exact variables

Set these on the new `xrp-hbar-intelligence` Railway service only:

```text
APP_ENV=production
BASE_URL=<new XRP/HBAR Railway URL>
LOG_LEVEL=info
MCP_AUTH_MODE=bearer
MCP_BEARER_TOKEN=<Railway secret>
```

Railway should inject `PORT`. Do not set real secrets in GitHub or chat.

`BASE_URL` can be set after Railway generates the public domain. If `/ready` reports missing `BASE_URL`, copy the generated public Railway URL into `BASE_URL` and redeploy/apply the variable change.

## What must not be touched

Do not change the existing Bill-CFO service:

```text
services/bill-cfo-ocr-mcp
```

Do not change Bill-CFO variables, start command, root directory, deploy branch, domain, or health path.

## Verification after deployment

Run these against the new XRP/HBAR Railway URL:

```text
GET /health
GET /ready
GET /deployment/status
GET /xrp-hbar-apex/health
GET /mcp
GET /mcp/tools
POST /mcp using extract_metadata with bearer auth
```

Expected final smoke result:

```text
MCP_ROUTE_VERIFIED_LIVE
ROUTE_SMOKE_VERIFIED
```

## Repo-side verifier

From the service root, with the Railway URL and secret available:

```bash
cd services/xrp-hbar-apex
XRP_HBAR_APEX_URL="https://<new-xrp-hbar-url>" \
MCP_AUTH_MODE="bearer" \
MCP_BEARER_TOKEN="<Railway secret>" \
npm run live:verify
```

## Current blocker

This repo is ready. The remaining step requires Railway account control:

```text
NEEDS_RAILWAY_ACCESS
NEW_RAILWAY_PROJECT_REQUIRED
MISSING_RAILWAY_SERVICE_FOR_XRP_HBAR
SECRET_OWNER_ACTION_REQUIRED
LIVE_RUNTIME_NOT_VERIFIED
```

## New-project handoff

For the full Railway UI approval sequence, use:

```text
services/xrp-hbar-apex/docs/railway-new-project-approval.md
```
