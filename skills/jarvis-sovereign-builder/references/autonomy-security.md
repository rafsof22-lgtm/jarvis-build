# Autonomy and Security

## Levels
- L0 Observe: read-only monitoring and explanation.
- L1 Recommend: plans/drafts only.
- L2 Reversible Operations: low-risk approved actions.
- L3 Gated Execution: medium/high-risk actions after approval/checkpoint.
- L4 Playbook Autonomy: pre-authorized workflows within strict scope.
- L5 Emergency Containment: defensive stop, isolate, revoke, quarantine and evidence preservation only.

Configure autonomy independently by agent, module, user/client, tool, data class, value, reversibility, legal/health consequence, external communication, credential sensitivity, production environment and confidence.

Required controls include zero-trust identity, least privilege, short-lived credentials, vaults, hardware-backed keys where practical, segmentation, per-tool permissions, data classification, sandboxing, immutable audit, signed agents/skills, SBOM, dependency/license/malicious-package scanning, prompt-injection isolation, content sanitization, egress control, transaction limits, dual control, auto-revocation, scoped kill switches, disaster recovery and continuous red teaming.

Never allow unrestricted recursive spawning, owner-credential inheritance, self-elevation, policy weakening, unlimited retries/spending, direct production self-modification, hidden leverage, unapproved money movement, public posting without policy or silent scope expansion.

Pre-authorized policies must define scope, expiry, environments, tools, accounts, repositories, branches, data classes, destinations, budgets, limits, checks and rollback. Reapproval is required for scope expansion, new providers/destinations, public exposure, production changes, billing, financial transactions, regulated data, ownership changes, destructive actions or weakened controls.