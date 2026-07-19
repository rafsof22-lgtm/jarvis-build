# Approval, Permission, Creation, Push, and Release Authority

Use pre-authorized, signed, versioned policies rather than unlimited consent. Approval modes: `MANUAL_EACH_ACTION`, `CHECKPOINT_APPROVAL`, `PLAYBOOK_PREAUTH`, `BUDGET_PREAUTH`, `ENVIRONMENT_PREAUTH`, and narrow `EMERGENCY_DEFENSIVE` containment. Record owner, approver, scope, expiry/revocation, accounts, repositories, branches, environments, data classes, destinations, budgets, required tests/evidence, rollback, inheritance and deny rules.

Prepare OAuth apps, service identities, scopes, redirect URIs, variable names and test calls automatically, but pause for login, MFA, CAPTCHA, billing/legal acceptance, domain ownership, hardware-key touch and consent. Request minimum scopes, separate read/write/admin/billing/delete/publish rights, prefer short-lived credentials, store protected values only in approved secret stores, test with harmless pings, and provide revoke/rotate/recovery.

Within approved Build Contracts Jarvis may create/edit repositories, branches, issues, PRs, code, schemas, queues, dashboards, agents, skills, workflows, tests, docs, backups and manifests. Identities, credentials, billing resources, public endpoints, production stores and privileged roles require explicit policy coverage.

Default release: `branch -> implement -> test/scan -> signed commit -> push -> PR -> independent review -> approval/policy -> merge -> tag -> staging -> verify -> production promotion`. Deny unknown remotes, force-push/history rewriting, direct untested production changes and weakened controls. Auto-merge only low-risk reversible changes in pre-authorized repositories after all checks and independent verification.

Production publication, DNS/domain changes, customer communication, purchases, subscriptions, money movement, contract acceptance, filings, deletion, ownership transfer and permission elevation require explicit or narrowly signed playbook approval. Subagents inherit only bounded, logged, revocable task scopes and never broader authority than parents. No agent approves its own high-risk action.

Record request, plan, approval, identity, tool, account, repository, branch, environment, before/after diff, tests/scans, signatures, commit/PR/release/deployment IDs, runtime health, costs, side effects, rollback and final status.