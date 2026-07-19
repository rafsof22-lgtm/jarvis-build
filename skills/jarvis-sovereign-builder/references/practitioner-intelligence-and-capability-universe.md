# Practitioner Intelligence and Capability Universe

## Purpose
For relevant recommendations and builds, research both authoritative sources and credible practitioners implementing comparable systems. Search official repositories/docs/changelogs first, then maintained GitHub projects, issues, pull requests, discussions, benchmarks, engineering forums, post-mortems, conference material, technical blogs, and high-quality community evidence. Extract successful patterns and negative lessons; popularity alone is not proof.

## Source scoring
Record source class, URL/pointer, owner, date, maintenance activity, release recency, tests, reproducibility, security posture, issue quality, independent use, deprecation/migration status, conflicts, and confidence. Prefer primary evidence. Preserve rejected and deferred findings with reasons.

## Finding pipeline
`DISCOVERED -> PROVENANCE_CAPTURED -> SOURCE_SCORED -> CLAIM_EXTRACTED -> CROSS_CHECKED -> APPLICABILITY_CLASSIFIED -> GAP_MAPPED -> PROPOSED -> SIMULATED -> TESTED -> ADOPT/PILOT/WATCHLIST/REJECT/MIGRATE/DEPRECATE/BLOCKED`.

Do not auto-adopt a forum claim. Newer is not automatically better. Route low-risk pre-authorized improvements through tests and rollback; gate high-risk changes.

## Capability-universe taxonomy
Inventory and map, when applicable:

1. Intent: goals, objectives, use cases, outcomes, acceptance criteria, requirements, constraints, assumptions, conflicts, decisions, risks, gaps.
2. Architecture/governance: architectures, frameworks, patterns, protocols, standards, contracts, policies, rules, instructions, guardrails, approval gates.
3. Intelligence: modules, services, agents, subagents, teams, roles, skills, prompts, strategies, planners, verifiers, evaluators, routers.
4. Execution: workflows, automations, events, schedules, queues, jobs, webhooks, retries, fallbacks, checkpoints, idempotency, reconciliation, compensation, dead letters.
5. Tools/integrations: tools, APIs, MCP servers, connectors, plugins, models, providers, databases, storage, search, browsers, local executors.
6. Configuration: parameters, settings, feature flags, thresholds, budgets, quotas, limits, defaults, environment names, regions, timeouts, weights, model settings.
7. Data contract: inputs, outputs, state, side effects, schemas, memory, context, provenance, lineage, retention, access, classification.
8. Runtime: repositories, packages, dependencies, environments, containers, deployments, workers, networks, databases, queues, storage, backups.
9. UX: interfaces, dashboards, widgets, forms, notifications, wizards, accessibility, overrides, approval inboxes, kill switches.
10. Security/reliability: identity, authentication, authorization, privacy, compliance, telemetry, logs, traces, metrics, evaluations, red teams, incidents, recovery, rollback.
11. Economics/lifecycle: tokens, API calls, compute, storage, bandwidth, licences, subscriptions, free tiers, migration, ownership, documentation, maintenance, training, support, deprecation.
12. Proof: sources, evidence, hashes, timestamps, tests, waivers, statuses, deployment proof, rollback proof, release gates.

Add new categories rather than forcing unmatched findings into an incorrect class.

## Gap-exhaustion rule
Never claim every possible idea has been found. Report the dated source denominator, searched classes, query families, exclusions, inaccessible sources, negative results, dedupe/disposition counts, and remaining blind spots. Use `NO_KNOWN_GAPS_WITHIN_VERIFIED_SCOPE` only when its denominator and checks are shown.