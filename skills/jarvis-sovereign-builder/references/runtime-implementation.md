# Runtime Implementation and Adaptive Delivery

Runtime truth hierarchy: explicit owner corrections/approvals -> canonical requirements -> verbatim provenance -> code/infrastructure/configuration/deployments -> tests/logs/traces/evidence. Preserve discrepancies between intent and runtime.

For every module, agent, workflow, integration or UI action define purpose, requirement/source IDs, inputs/outputs/state/side effects, APIs/events/files/queues/UI contracts, allowed/denied tools, auth/scopes/data class, autonomy/approvals, model/cost route, observability, tests, failures/retries/timeouts/idempotency/compensation, implementation path, deployment target, version/hash, evidence and rollback. Missing credentials or external access must produce a disabled state with a tested enable path, not a production placeholder.

Each AgentSpec includes identity/version/owner, role/non-goals, triggers, schemas, memory/retention, tools/minimum scopes, model/fallback, data policy, autonomy ceiling, budgets/limits, health, verifier/release authority, shutdown/rollback and tests. Agents may not widen scopes, modify policy, inherit owner credentials, approve high-risk actions or deploy directly to production.

Build order: source/requirement proof; contracts; repo/CI; identity/policy/audit/kill switch; memory/provenance; model router/cost governor; agent/tool layer; integration fabric; builder/repair; Command Centre/setup; domain modules; staging; independent verification/red team; controlled production; post-deploy monitoring.

Change protocol: `Detect -> Scope -> Diff -> Simulate -> Implement -> Test -> Security Review -> Approval -> Canary -> Observe -> Promote/Rollback`. Use branches, machine-readable plans, blast-radius analysis, backups, static/dynamic checks, feature flags, canary/shadow runs, release notes and automatic rollback thresholds.

Instrument correlation logs, latency/throughput/error/saturation/queue/cost/token/tool/approval/retry metrics, distributed traces, health/readiness/dependencies, drift/cost alerts, replay timelines, SLOs and incident runbooks. No hidden action.

Require contract, unit, integration, policy, prompt-injection, E2E, accessibility, load/concurrency/failure-injection, cost-cap, backup/restore, rollback and post-deploy smoke tests with machine-readable evidence.

Every side effect is idempotent or compensatable and defines bounded backoff, circuit breaker, dead-letter handling, dedupe, reconciliation, partial-failure behavior, restore point, manual recovery and safe degradation.

Evidence outputs: implementation manifest, file/service/config/dependency diffs, tests, security/policy results, deployment record, health/cost evidence, rollback reference, traceability and evidence-backed status.