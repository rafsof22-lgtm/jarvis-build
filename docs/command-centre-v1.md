# Jarvis Command Centre v1

## Purpose

This control-plane module consolidates the five connected repositories without merging or compressing them. It reads canonical repository, integration, deployment, module, blocker, free-allowance and cost/credit records, then emits one versioned command-centre snapshot.

## Run

```bash
python -m jarvis_command_centre.command_centre
python -m jarvis_command_centre.command_centre --output command-centre.snapshot.json
python -m jarvis_command_centre.command_centre --serve --port 8787
```

Open `http://127.0.0.1:8787/` for the HTML command centre or `http://127.0.0.1:8787/api/v1/command-centre` for JSON.

`--live` enables read-only polling only where a repository base URL is supplied through the integration registry's named environment variable. No secret values are stored in the registry.

## Canonical artifacts

- `schemas/repository-registry.schema.json`
- `schemas/integration-registry.schema.json`
- `schemas/cost-credit-ledger.schema.json`
- `schemas/federation-contract-v1.schema.json`
- `registry/repositories.json`
- `registry/integrations.json`
- `registry/cost-credit-ledger.json`

## Contract endpoint

Each independently deployed repository should eventually expose a read-only response conforming to `federation-contract-v1.schema.json` at:

- `/.well-known/jarvis/health`
- `/.well-known/jarvis/capabilities`

A combined endpoint is acceptable when it returns the full v1 contract. The command centre rejects unsupported contract versions and falls back to the last canonical registry state.

## Status truth

- `verified` means a balance or allowance was obtained from a connected authoritative source.
- `estimated` must state its source and method.
- `unavailable` means no authoritative adapter is connected.
- Missing balances are never coerced to zero.
- A repository remains `partial`, `scaffold`, `blocked` or `unknown` until runtime and test evidence supports promotion.

## Security

- read-only federation credentials only;
- least-privilege, repository-specific tokens;
- no credential inheritance between modules;
- no health payload may include customer, health, financial or prospect records;
- timeouts and stale-snapshot fallback are mandatory;
- write actions, deployments and billing changes remain outside this v1 collector.

## Remaining implementation phases

### Phase 1 — Canonical control plane

Implemented in this increment: schemas, seed registries, offline aggregation, optional polling, HTML/JSON surfaces, smoke tests and CI snapshot generation.

### Phase 2 — Native contracts in all repositories

Add contract adapters and contract tests to `hub`, `Jarvis-Health`, `videotranscribe` and `property-agent-mcp`. Keep each repository's native framework and authentication boundary.

### Phase 3 — Authoritative provider adapters

Connect read-only usage/billing APIs or exports for GitHub, Vercel, Railway, DigitalOcean, Oracle, model providers, databases and storage. Store only provider/account identifiers and secret names. Record retrieval timestamps, scopes and evidence.

### Phase 4 — Persistent history and alerts

Store snapshots in Postgres or a zero-cost local SQLite fallback. Add trend calculation, allowance forecasts, threshold alerts, stale-data alerts, deployment drift and contract-version drift.

### Phase 5 — Command-centre application

Add authenticated UI filters, repository/deployment detail pages, traffic lights, evidence links, blocker ownership, safe remediation guidance and <=3-click frequent actions. Read-only remains the default.

### Phase 6 — Governed repair and release actions

Add proposal-only repair agents, simulations, branch/PR creation, CI verification, approval gates, staging promotion, rollback and audit evidence. Never permit unrestricted self-modification or autonomous paid usage.

## Current blockers

1. Production hosting for this command centre is not yet proven.
2. Four domain repositories do not yet expose the v1 contract.
3. Provider billing/usage credentials and account mappings are not connected.
4. The exposed historical Vercel credential still requires provider-side revocation/rotation.
5. Oracle tenancy, region and free-capacity availability are unproven.
6. `Jarvis-Health` remains a placeholder rather than a complete MCP service.
7. `property-agent-mcp` still lacks its documented upload, merge/dedupe, worker and forensic-audit functions.
