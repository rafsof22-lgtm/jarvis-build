# Jarvis Platform Operations Control Plane v1

## Purpose

This control plane defines the minimum operational contract for every isolated Jarvis service. It standardises topology, identity, secrets-by-reference, observability, backup/restore, disaster recovery, incident handling, cost protection, release evidence and rollback without pretending that repository policy is a live deployment.

## Golden path

`Inventory -> Classify -> Isolate -> Configure by reference -> Build -> Test -> Scan -> Backup -> Restore test -> Stage -> Observe -> Independent verification -> Owner-approved production promotion -> Monitor/Rollback`

## Service onboarding checklist

1. Assign a stable service ID, repository and service root.
2. Record development, staging and production boundaries.
3. Map public routes, private dependencies, databases, queues and external providers.
4. Create separate least-privilege human and service identities.
5. Store only secret names and locations in source control.
6. Implement `/health`, `/ready` and a redacted status/capability contract.
7. Enable structured redacted logs, metrics, alerts and deployment-SHA reporting.
8. Define RPO, RTO, backup schedule, retention and isolated restore test.
9. Define retries, idempotency, dead-letter/reconciliation and kill switch.
10. Set service budget, soft/hard alerts and workload-shedding policy.
11. Run security, negative, restore, rollback and cost tests.
12. Preserve independent verification and obtain separate production approval.

## Incident levels

- `SEV0` — immediate risk to life, major financial loss or widespread sensitive-data exposure. Stop affected automation and escalate immediately.
- `SEV1` — confirmed credential compromise, production outage or material data-integrity loss.
- `SEV2` — degraded service, repeated queue failure or partial provider outage.
- `SEV3` — low-impact defect, warning or maintenance issue.

## Automatic safe containment

Jarvis may stop new jobs, switch an affected integration to read-only, disable an optional connector, quarantine untrusted input and open an incident record. Credential rotation, destructive cleanup, public communication, billable failover and legal notification remain owner-gated.

## Backup and restore proof

A backup is not proven merely because a provider says backups are enabled. Evidence must include backup identity and timestamp, encryption and retention policy, restore target, restore logs, integrity checks, application smoke test, cleanup/retention decision and rollback path. Production promotion is blocked until the applicable restore and rollback tests pass.

## Cost protection

Use deterministic/local/cached routes first. Every service records a monthly or task budget, 70% soft alert and 90% hard alert unless a stricter service rule applies. Optional workloads may be shed at the hard limit. Jarvis must not silently accept billing, increase paid capacity or create a paid failover service.

## Proof boundary

This document and its machine-readable registry complete the repository policy/scaffold for P1-6. Live topology discovery, provider IAM, monitoring connection, backups, restore tests, failover and production evidence remain `IMPLEMENTED_NOT_INTEGRATED` or `BLOCKED` until independently proven.
