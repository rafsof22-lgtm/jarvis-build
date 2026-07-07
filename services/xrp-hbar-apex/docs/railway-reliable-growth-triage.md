# Railway Reliable-Growth Triage Handoff

Last updated: 2026-07-07

## User-reported Railway state

Railway project:

```text
reliable-growth
```

User reports:

```text
2 services online
jarvis-build failed about 14 minutes ago
```

This is not final proof that XRP/HBAR is live. It means the Railway agent must do service-level triage and route verification.

## Safety rules

```text
Do not delete any service.
Do not redeploy repo root.
Do not copy variables between services.
Do not change Bill-CFO except read-only verification unless user explicitly approves.
```

Expected service split:

```text
Bill-CFO root: services/bill-cfo-ocr-mcp
XRP/HBAR root: services/xrp-hbar-apex
```

## Required triage steps

1. List all services in Railway project `reliable-growth`.
2. For each service, report:

```text
service name
online/failed/crashed status
linked GitHub repo
branch
root directory
start command
health path
watch path
public URL
latest deploy SHA/time/status
```

3. Identify the failed `jarvis-build` deploy.
4. Classify it as one of:

```text
BILL_CFO_SERVICE
XRP_HBAR_SERVICE
OLD_REPO_ROOT_DEPLOY
ORPHAN_SERVICE
WRONG_ROOT_DEPLOYMENT
UNKNOWN
```

5. If it is building from repo root, classify:

```text
DEPLOYMENT_DRIFT + RAILWAY_ROOT_DIRECTORY_MISCONFIGURATION
```

6. Do not fix the failed service until classification is clear.

## XRP/HBAR verification target

The correct XRP/HBAR service should be:

```text
Service: xrp-hbar-intelligence
Repo: rafsof22-lgtm/jarvis-build
Branch: main
Root directory: services/xrp-hbar-apex
Start command: npm start
Health path: /health
Watch path: /services/xrp-hbar-apex/**
```

Variables on XRP/HBAR service only:

```text
APP_ENV=production
BASE_URL=<XRP/HBAR public Railway URL>
LOG_LEVEL=info
MCP_AUTH_MODE=bearer
MCP_BEARER_TOKEN=<present, never reveal>
```

Optional safety variables, if present:

```text
TRADING_MODE=paper
LIVE_TRADING_ENABLED=false
APPROVAL_REQUIRED=true
```

## XRP/HBAR live route checks

Run in this order against the XRP/HBAR public URL:

```text
GET /health
GET /ready
GET /deployment/status
GET /mcp
GET /mcp/tools
POST /mcp with bearer token and extract_metadata
```

Authenticated `POST /mcp` body:

```json
{
  "tool": "extract_metadata",
  "input": {
    "url": "https://example.com/test"
  }
}
```

## Bill-CFO isolation verification

Confirm:

```text
Bill-CFO is separate from XRP/HBAR.
Bill-CFO root is services/bill-cfo-ocr-mcp.
Bill-CFO has its own public URL.
Bill-CFO variables are separate.
Bill-CFO still responds to /health.
```

## Final report format

Return:

```text
A. Services online
- service 1:
- service 2:

B. Failed jarvis-build deploy
- service/deploy name:
- root directory:
- classification:
- exact failure log lines:
- fixed: yes/no/not changed

C. XRP/HBAR verification
- URL:
- root:
- variables present yes/no only:
- /health:
- /ready:
- /deployment/status:
- /mcp:
- /mcp/tools:
- POST /mcp:

D. Bill-CFO isolation
- URL:
- root:
- /health:
- changed: yes/no

E. Blockers
Use exact blocker labels.

F. Final truth statement
Choose exactly one:
1. XRP/HBAR Railway service is live and verified.
2. XRP/HBAR Railway service was created but live verification is blocked.
3. XRP/HBAR Railway service could not be created, blocker is: <label>.
```

## Blocker labels

```text
RAILWAY_STAGED_PATCH_NOT_PERSISTED
MISSING_RAILWAY_SERVICE_FOR_XRP_HBAR
MISSING_RAILWAY_SERVICE_FOR_BILL_CFO
MISSING_ENV_VAR
SECRET_OWNER_ACTION_REQUIRED
BUILD_FAILURE
START_COMMAND_FAILURE
PORT_BINDING_FAILURE
ROUTE_HEALTH_FAILURE
AUTH_FAILURE
LIVE_ROUTE_VERIFICATION_REQUIRED
DEPLOYMENT_DRIFT
RAILWAY_ROOT_DIRECTORY_MISCONFIGURATION
UNKNOWN_RUNTIME_ERROR
```
