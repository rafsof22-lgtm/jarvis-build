# Bill CFO OCR MCP Agent Instructions

## Purpose
This folder is the isolated service root for the Bill CFO OCR MCP module inside the shared Jarvis build repository.

Repository: `rafsof22-lgtm/jarvis-build`
Service root: `services/bill-cfo-ocr-mcp/`
Railway target: a dedicated Railway service mapped to this exact root directory.
Deploy branch: `main`

## Agent Locator
When an agent is asked to work on Bill CFO OCR MCP, it should start here:

1. Read this file.
2. Read `README.md`.
3. Read `docs/agent-locator.md`.
4. Read `docs/deployment-ledger.md`.
5. Inspect `railway.json`, `.env.example`, `package.json`, and `src/server.js` before editing.

Do not search for or edit another Bill CFO root unless the user explicitly says this root has been superseded.

## Editable Scope
Bill CFO agents may edit files under:

- `services/bill-cfo-ocr-mcp/`

Bill CFO agents must not edit these sibling roots unless the user explicitly asks for a cross-module change:

- `services/xrp-hbar-apex/`
- other `services/*` module roots
- repo-wide deployment files that could change another service's build, start command, routes, env names, or Railway behavior

Top-level documentation edits are allowed only when they are locator, registry, or non-interference updates that are safe for all modules.

## Non-Interference Rules
- Keep this service's runtime, routes, env vars, queues, database objects, webhooks, smoke tests, and rollback notes separate from XRP/HBAR Apex and all other Jarvis modules.
- Do not reuse another service's Railway root directory, start command, port assumption, env variables, secrets, health route, ready route, or deployment status route.
- Do not rename, move, delete, or repurpose another module's files to make Bill CFO work.
- If a shared helper is needed, add it only after confirming it is generic and safe for every affected module.
- If a change might affect another agent or module, classify it as safe, risky, blocked, or requires user confirmation before editing.

## Route Contract
The starter shell must preserve these routes:

- `GET /health`
- `GET /ready`
- `GET /deployment/status`
- `GET /bill-cfo-ocr-mcp/health`
- `GET /bill-cfo-ocr-mcp/ready`
- `GET /bill-cfo-ocr-mcp/deployment/status`

Do not claim OCR, workbook writes, queue workers, provider auth, or downstream finance workflows are live until implemented and smoke-tested.

## Env and Secret Rules
Use `.env.example` only for non-secret names and placeholders. Store real values in Railway variables, GitHub secrets, or an approved vault.

Never commit real secrets, API keys, OAuth client secrets, service-account private keys, passwords, cookies, tokens, 2FA codes, seed phrases, or production-only values.

Env namespace prefix for Bill CFO: `BILL_CFO_OCR_MCP_` where service-specific names are needed.

## Railway Rules
Railway is not proven live from repo files alone. Before claiming deployment success, verify:

1. Railway project/service exists.
2. Service root is exactly `services/bill-cfo-ocr-mcp/`.
3. Deploy branch is `main` unless explicitly changed.
4. Required env vars are set and non-placeholder.
5. `/health` works.
6. `/ready` works.
7. `/deployment/status` works.
8. The smallest real Bill CFO OCR/workbook route smoke test passes after those routes exist.

If Railway cannot be inspected, report `NEEDS_RAILWAY_ACCESS` or `BLOCKED_BY_MISSING_ACCESS`; do not imply live runtime proof.

## Verification
For code edits, run the smallest available checks from this service root. At minimum, inspect package scripts and run available unit/smoke checks that do not require secrets.

For deployment edits, update `docs/deployment-ledger.md` and `docs/rollback.md` when behavior changes.

## Proof Labels
Use these labels when reporting status:

- `REPO_LOCATOR_SET`
- `SERVICE_ROOT_CONFIRMED`
- `MODULE_OWNERSHIP_MAPPED`
- `RAILWAY_SERVICE_UNVERIFIED`
- `NEEDS_RAILWAY_ACCESS`
- `SECRET_OWNER_ACTION_REQUIRED`
- `NO_FAKE_SUCCESS_CLAIM`
