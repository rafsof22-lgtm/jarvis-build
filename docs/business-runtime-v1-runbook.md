# Jarvis Business Runtime V1

## Scope

This release turns the Jenok and Cost + $1 Auto Parts governance scaffolds into executable, dependency-free Python components for:

- measured source reconstruction and SHA-256 manifests;
- catalogue CSV/JSON normalization, validation and deterministic deduplication;
- auditable Cost + A$1 pricing with stale-data and missing-evidence fail-closed controls;
- purchase-order construction, spend approval gates and evidence-backed state transitions;
- received-order reconciliation with scan or photo/manual fallback evidence;
- local, staging and owner-gated production deployment plans.

The two businesses retain separate namespaces. Shared code does not merge brands, catalogues, ledgers, customers, suppliers, warranties or legal responsibilities.

## Commands

```bash
PYTHONPATH=. python -m src.jarvis_business.cli reconstruct-sources ./source-pack --output evidence/source-manifest.json
PYTHONPATH=. python -m src.jarvis_business.cli import-catalogue catalogue.csv --output evidence/catalogue-import.json
PYTHONPATH=. python -m src.jarvis_business.cli price quote-input.json
PYTHONPATH=. python -m src.jarvis_business.cli deployment-plan BUSINESS-JENOK staging --required-env DATABASE_URL
```

## Source reconstruction truth boundary

Only paths actually supplied to the runtime are inventoried and hashed. A declared but inaccessible path is retained as `PENDING_INGEST`; it is never silently treated as processed. Full historical completion requires the complete ChatGPT export/source pack, attachments and generated artifacts to be supplied and reconciled against the canonical requirement ledger.

## Deployment sequence

1. Run compilation and deterministic tests.
2. Generate a staging deployment plan.
3. Configure secrets through the target platform secret manager; never commit values.
4. Deploy to an isolated staging service and database.
5. Run catalogue, price, procurement, order-verification, audit-write and rollback smoke tests.
6. Record evidence and discrepancies.
7. Obtain owner approval for production, paid resources, credentials, domains, payments, supplier contact and public publishing.
8. Promote by canary; monitor and roll back on failed health checks.

## Current blockers

- Complete historical Jarvis/Jenok/Cost + $1 source bodies and attachments are not all ingested.
- Live supplier feeds, agreements, current freight/tax terms and credentials are not proven.
- Production database, hosting, payments, Xero, logistics, domains and marketplace integrations require scoped credentials and owner approval.
- Legal, GST, consumer-guarantee, warranty, insurance and accounting treatment require authoritative professional confirmation before commercial launch.

These blockers do not prevent deterministic local testing or staging preparation, but they prevent a truthful `DONE_VERIFIED` production claim.
