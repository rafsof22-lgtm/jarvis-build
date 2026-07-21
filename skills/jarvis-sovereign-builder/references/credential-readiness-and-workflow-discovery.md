# Credential Readiness and Workflow Discovery

## Credential boundary
Inventory only configuration and credential names, owning module, purpose, auth type, minimum scopes, environment, secure storage location, presence/readiness, expiry/rotation state, test method, and rollback. Never recover, display, log, commit, infer, or request protected values in chat. Prefer OIDC or short-lived delegated credentials over static keys.

## Maximum-safe automatic application
Automatically apply every safe accessible non-secret value and every already-configured approved secret reference. Reuse repository metadata, verified public URLs, deterministic defaults, existing environment variables, GitHub Actions secret references, provider-vault references, OIDC identities and short-lived delegated credentials when the current authorised tool or workflow can do so without exposing the protected value.

Do not ask the owner to re-enter a value that is already safely available to an authorised workflow. Do not show resolved values in the action list. Continue automatically from presence check to harmless connection test when the required secret references are present and the task is within the approved staging playbook.

Never search for secret values in chat, issues, pull requests, logs, screenshots, repository history, browser storage, clipboard or uploaded files not explicitly designated as an approved secret source. Convenience never justifies secret exfiltration.

## Readiness states
Use `ACTIVE`, `PRESENT_UNVERIFIED`, `REQUIRED_BUT_MISSING`, `OPTIONAL`, `FAILED`, `DUPLICATE_CANDIDATE`, `STALE_CANDIDATE`, `ROTATION_REQUIRED`, `SAFE_TO_REMOVE_AFTER_PROOF`, and `REMOVED_WITH_ROLLBACK`.

## One-click setup
For missing access, generate a novice flow with provider page, exact field/secret name, minimum scopes, safe public metadata/redirect URIs, validation action, revoke/rollback, and evidence. The owner enters the protected value directly into the platform secret manager. Do not create billable resources or broaden scopes silently.

The default human-action experience is one consolidated card and a target of three clicks or fewer after the owner reaches the correct provider or GitHub settings page. Include only unresolved blockers. Provide exact copy-ready public values, the exact secret or variable name, the minimum scope, the validation workflow and the automatic resume condition.

## Cross-repository federation
Run redacted configuration scans independently for each authorized repository; merge reports into the Command Centre; show repository/environment selection, configuration coverage, provider readiness, duplicate/stale candidates, and exact blockers. A missing private-repository read grant must produce a blocker record, not false coverage.

## Provider adapters
Each adapter defines capability discovery, public metadata, credential names only, least-privilege scopes, read-only/status test, bounded write test where approved, rate limits, cost, timeout/retry, redacted errors, health, revoke/rollback, and evidence. Distinguish connection proof from token rotation/revocation proof.

## Automatic setup sequence
Use:

`INVENTORY -> DERIVE_SAFE_VALUES -> REUSE_APPROVED_REFERENCES -> PRESENCE_CHECK -> SCOPE_CHECK -> APPLY_REVERSIBLE_DEFAULTS -> HARMLESS_TEST -> HUMAN_ACTION_CARD_IF_NEEDED -> AUTO_RESUME`

Stop only for login, MFA, CAPTCHA, required OAuth consent, billing or legal acceptance, domain ownership, missing secret creation without an authorised secret-manager connector, production promotion, permission elevation, money movement or clinical/wellness-device control.

## Workflow discovery
Discover GitHub Actions, provider deployments, schedulers, n8n/automation flows, queues, workers, webhooks, cron, backups, restore jobs, incident workflows, dependency updates, and source scans. Every workflow records owner, trigger, inputs, outputs, side effects, permissions, credential names, environment, cost, timeout, retries, idempotency, dead-letter/reconciliation, observability, tests, evidence, and rollback.

## Cleanup
Automatically clean only proven harmless artifacts such as duplicate blank template entries, casing/description normalization, generated temporary files, and missing ignore rules. Never remove secrets, service identities, OAuth clients, production URLs, databases, rollback credentials, or provider configuration without no-reference proof, passing tests, owner authorization, and rollback evidence.
