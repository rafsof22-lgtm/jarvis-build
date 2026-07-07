# XRP/HBAR Railway New Project Approval Handoff

Last updated: 2026-07-07

## Decision

Create a new Railway project for the XRP/HBAR agent while keeping the same GitHub repository.

This is not a new GitHub repository request. The GitHub source stays:

```text
rafsof22-lgtm/jarvis-build
```

The Bill-CFO Railway project/service must remain untouched.

## Target Railway project

```text
Project name: xrp-hbar-intelligence
Purpose: dedicated Railway project boundary for XRP/HBAR Apex Intelligence OS
Source repo: rafsof22-lgtm/jarvis-build
Deploy branch: main
Service name: xrp-hbar-intelligence
Root directory: services/xrp-hbar-apex
Watch path: /services/xrp-hbar-apex/**
Start command: npm start
Healthcheck path: /health
```

## Protected Bill-CFO boundary

Do not modify, redeploy, rename, re-root, or repurpose the existing Bill-CFO Railway service.

```text
Protected service root: services/bill-cfo-ocr-mcp
Protected current purpose: Bill-CFO OCR MCP runtime
```

Bill-CFO must keep its own Railway service, variables, domain, root directory, start command, deploy branch, and health path.

## Required XRP/HBAR service variables

Set these only on the new XRP/HBAR Railway project/service:

```text
APP_ENV=production
BASE_URL=<new XRP/HBAR Railway public URL>
LOG_LEVEL=info
MCP_AUTH_MODE=bearer
MCP_BEARER_TOKEN=<Railway-generated secret value>
```

Do not paste the real token into GitHub or chat. Store it only in Railway service variables or another approved secret store.

Railway should provide the runtime `PORT`; the service already reads `process.env.PORT`.

## GitHub source proof

The service package is located at:

```text
services/xrp-hbar-apex/package.json
```

Its start command is:

```text
npm start
```

which runs:

```text
node src/server.js
```

The server exposes:

```text
GET /health
GET /ready
GET /deployment/status
GET /xrp-hbar-apex/health
GET /xrp-hbar-apex/ready
GET /xrp-hbar-apex/deployment/status
GET /mcp
GET /mcp/tools
POST /mcp
```

`POST /mcp` must be tested with bearer authentication when `MCP_AUTH_MODE=bearer`.

## Railway UI approval steps

1. Open Railway.
2. Create a new project.
3. Choose deploy from GitHub repo.
4. Select `rafsof22-lgtm/jarvis-build`.
5. Name the project `xrp-hbar-intelligence`.
6. Create/select service `xrp-hbar-intelligence`.
7. Set root directory to `services/xrp-hbar-apex`.
8. Set watch path to `/services/xrp-hbar-apex/**`.
9. Set start command to `npm start` if Railway does not auto-detect it.
10. Set healthcheck path to `/health`.
11. Add only the XRP/HBAR variables listed above.
12. Generate a public Railway domain for this new service.
13. Deploy.
14. Copy the new public URL into `BASE_URL` and redeploy if required.
15. Run the smoke tests below.

## Smoke-test order

```text
GET /health
GET /ready
GET /deployment/status
GET /xrp-hbar-apex/health
GET /mcp
GET /mcp/tools
POST /mcp with Authorization: Bearer <MCP_BEARER_TOKEN>
```

Repo-side verifier:

```bash
cd services/xrp-hbar-apex
XRP_HBAR_APEX_URL="https://<new-xrp-hbar-url>" \
MCP_AUTH_MODE="bearer" \
MCP_BEARER_TOKEN="<Railway secret>" \
npm run live:verify
```

## Blocker labels until user completes Railway UI approval

```text
NEEDS_RAILWAY_ACCESS
NEW_RAILWAY_PROJECT_REQUIRED
MISSING_RAILWAY_SERVICE_FOR_XRP_HBAR
SECRET_OWNER_ACTION_REQUIRED
LIVE_RUNTIME_NOT_VERIFIED
```

## Success labels after live verification

```text
RAILWAY_PROJECT_CREATED
RAILWAY_SERVICE_VERIFIED
RUNTIME_HEALTH_VERIFIED
RUNTIME_READY_VERIFIED
MCP_ROUTE_VERIFIED_LIVE
ROUTE_SMOKE_VERIFIED
```
