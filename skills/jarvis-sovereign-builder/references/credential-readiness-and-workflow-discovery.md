# Credential Readiness and Workflow Discovery

## Credential boundary
Inventory only configuration and credential names, owning module, purpose, auth type, minimum scopes, environment, secure storage location, presence/readiness, expiry/rotation state, test method, and rollback. Never recover, display, log, commit, infer, or request protected values in chat. Prefer OIDC or short-lived delegated credentials over static keys.

## Readiness states
Use `ACTIVE`, `PRESENT_UNVERIFIED`, `REQUIRED_BUT_MISSING`, `OPTIONAL`, `FAILED`, `DUPLICATE_CANDIDATE`, `STALE_CANDIDATE`, `ROTATION_REQUIRED`, `SAFE_TO_REMOVE_AFTER_PROOF`, and `REMOVED_WITH_ROLLBACK`.

## One-click setup
For missing access, generate a novice flow with provider page, exact field/secret name, minimum scopes, safe public metadata/redirect URIs, validation action, revoke/rollback, and evidence. The owner enters the protected value directly into the platform secret manager. Do not create billable resources or broaden scopes silently.

## Cross-repository federation
Run redacted configuration scans independently for each authorized repository; merge reports into the Command Centre; show repository/environment selection, configuration coverage, provider readiness, duplicate/stale candidates, and exact blockers. A missing private-repository read grant must produce a blocker record, not false coverage.

## Provider adapters
Each adapter defines capability discovery, public metadata, credential names only, least-privilege scopes, read-only/status test, bounded write test where approved, rate limits, cost, timeout/retry, redacted errors, health, revoke/rollback, and evidence. Distinguish connection proof from token rotation/revocation proof.

## Workflow discovery
Discover GitHub Actions, provider deployments, schedulers, n8n/automation flows, queues, workers, webhooks, cron, backups, restore jobs, incident workflows, dependency updates, and source scans. Every workflow records owner, trigger, inputs, outputs, side effects, permissions, credential names, environment, cost, timeout, retries, idempotency, dead-letter/reconciliation, observability, tests, evidence, and rollback.

## Cleanup
Automatically clean only proven harmless artifacts such as duplicate blank template entries, casing/description normalization, generated temporary files, and missing ignore rules. Never remove secrets, service identities, OAuth clients, production URLs, databases, rollback credentials, or provider configuration without no-reference proof, passing tests, owner authorization, and rollback evidence.