# Practitioner Intelligence and Capability Universe

Status: SPEC_LOCKED / implementation backlog active  
Scope: Jarvis runtime/system and ChatGPT project/chat instruction layer

## Purpose

Jarvis must not limit research to official vendor documentation. It must also discover what capable builders are implementing, testing, rejecting and learning in real projects, then convert credible and applicable findings into recommendations, specifications, modules, agents, skills, workflows, tests and controlled build tasks.

This is an open-ended discovery system. It must never claim that every possible idea or component has been found. Completion means the defined source universe was searched, findings were accounted for and the current gap-exhaustion test passed at a timestamp.

## Source universe

Search and maintain dated source records across:

1. Official documentation, repositories, changelogs, standards, security advisories and primary research.
2. Maintainer repositories, releases, issues, pull requests, discussions, roadmaps, examples, benchmarks and migration guides.
3. High-quality practitioner projects and architecture write-ups from GitHub, GitLab, Hacker News, Stack Overflow, Reddit technical communities, Discord/forum summaries, engineering blogs, conference talks, podcasts and videos with verifiable implementation detail.
4. Failure reports, abandoned projects, security incidents, post-mortems, benchmark regressions and migration pain—not only success stories.
5. Competitor and app-builder capabilities using lawful public evidence.

Community evidence is discovery input, not automatic truth. Prefer reproducible code, tests, issue history, maintainer activity and independent corroboration over popularity.

## Practitioner/Jarvis-builder intelligence

For each relevant request, search for builders solving similar problems. Extract:

- architecture and orchestration patterns;
- agent roles and boundaries;
- memory, RAG and context strategies;
- tool, MCP and API integration patterns;
- workflow durability, checkpointing and human-interrupt design;
- model routing, caching, batching and cost controls;
- evaluation, observability, tracing and red-team methods;
- secrets, identity, sandboxing and permission controls;
- UI/Command Centre patterns and novice setup flows;
- deployment, scaling, migration and rollback lessons;
- failures, limitations, maintenance status and deprecations;
- useful parameters, defaults, schemas and tests.

Convert each finding through:

`DISCOVERED -> PROVENANCE_CAPTURED -> SOURCE_SCORED -> CLAIM_EXTRACTED -> CROSS_CHECKED -> APPLICABILITY_CLASSIFIED -> GAP_MAPPED -> PROPOSED -> SIMULATED -> TESTED -> PROMOTED / REJECTED / WATCHLIST`

## Capability-universe taxonomy

Every scan and consolidation audit must consider all applicable object classes, including named and not-yet-named equivalents:

- goals, objectives, outcomes, use cases and acceptance criteria;
- requirements, constraints, assumptions, conflicts, decisions, risks and gaps;
- architectures, frameworks, patterns, protocols, standards and contracts;
- modules, services, agents, subagents, teams, roles, skills and prompts;
- strategies, policies, rules, instructions, guardrails and approval gates;
- workflows, automations, events, schedules, queues, jobs, retries and fallbacks;
- tools, APIs, MCP servers, connectors, plugins, models and providers;
- parameters, settings, feature flags, quotas, budgets, thresholds and defaults;
- inputs, outputs, side effects, schemas, state, memory and data lineage;
- repositories, packages, dependencies, environments, infrastructure and deployments;
- UI surfaces, controls, widgets, notifications, accessibility and manual overrides;
- identity, credentials-by-name, permissions, privacy, security and compliance;
- telemetry, logs, traces, metrics, evaluations, benchmarks and red-team tests;
- errors, incidents, recovery, backups, rollback, kill switches and continuity;
- costs, tokens, credits, compute, storage, bandwidth, licences and migration paths;
- documentation, setup, training, maintenance, ownership and deprecation;
- evidence, provenance, hashes, timestamps, statuses and release gates.

Unknown object classes discovered later must be added rather than forced into an unsuitable category.

## Recommendation generation

For relevant user requests, recommendations must combine:

1. current official truth;
2. credible practitioner implementation evidence;
3. Jarvis repository and runtime reality;
4. user constraints and prior requirements;
5. cost, security, maintenance and migration analysis;
6. negative evidence and known failure modes.

Every recommendation must state whether it is `ADOPT`, `PILOT`, `WATCHLIST`, `REJECT`, `MIGRATE`, or `DEPRECATE`, with rationale, source date, confidence, cost route, dependencies, test plan and rollback.

## Framework selection rules

Do not install every popular framework. Select the smallest reliable mechanism that meets the task:

- deterministic function or workflow before an agent when the process is well-defined;
- one agent before a multi-agent system when sufficient;
- explicit graph/workflow for repeatable, stateful or high-control processes;
- durable checkpoints for long-running tasks;
- human interruption for material decisions;
- provider-neutral interfaces and versioned contracts;
- framework migration watch for maintenance-mode or superseded projects.

## Continuous intelligence loop

`UPDATE`, `SCAN`, `VERIFY`, or a relevant request must:

1. resolve the capability and source categories that apply;
2. search official and practitioner sources with recency appropriate to the topic;
3. preserve URLs, repository/ref, dates and evidence snippets;
4. deduplicate claims and identify copied/derivative reports;
5. compare findings with current Jarvis requirements and implementation;
6. create delta-only recommendations and missing-capability records;
7. update both runtime and project/chat instructions when applicability is BOTH;
8. create tests, pilots or watchlist items;
9. preserve rejected ideas and reasons to prevent repeated wasted research;
10. record search coverage and unresolved source gaps.

## Gap-exhaustion standard

A scan may report `NO_KNOWN_GAPS_WITHIN_VERIFIED_SCOPE` only when:

- source categories and queries are recorded;
- official and practitioner channels were both considered where applicable;
- current and negative evidence were checked;
- findings were deduplicated and mapped to the capability taxonomy;
- every finding is promoted, rejected, deferred, watchlisted or blocked with reason;
- unknown or inaccessible sources are listed;
- a timestamp and refresh trigger are stored.

## Initial current framework findings

- Microsoft AutoGen and Semantic Kernel are maintenance/successor paths; new evaluation should prioritise Microsoft Agent Framework rather than blindly adopting older stacks.
- Microsoft Agent Framework separates open-ended agents from explicit graph workflows and advises using deterministic functions when sufficient.
- LangGraph provides durable execution, checkpointing, human-in-the-loop and stateful long-running workflows.
- CrewAI distinguishes autonomous crews from more deterministic event-driven flows.

These are candidate patterns, not blanket framework selections. Jarvis should remain framework-neutral and use adapters where a specialist runtime is justified.

## Dual-layer application

This policy is `BOTH`:

- Runtime: SourceScout, registries, scoring, extraction, delta mapping, pilots, tests and Command Centre intelligence views.
- Chat/project instructions: automatically source current official and credible practitioner evidence for relevant recommendations and state proof limits.

## Required artifacts

Maintain:

- SourceRegistry;
- PractitionerRegistry;
- RepositoryWatchlist;
- FrameworkWatchlist;
- PatternRegistry;
- FailureLessonRegistry;
- CapabilityUniverseRegistry;
- RecommendationRegistry;
- RejectedCandidateRegistry;
- SearchCoverageLedger;
- Freshness/RevalidationQueue;
- Source-to-Requirement-to-Artifact traceability.
