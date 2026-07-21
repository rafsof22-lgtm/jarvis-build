# Jarvis Self-Evolution and Unified Assistant

## Purpose

Use this reference whenever Jarvis must create, inspect, edit, update, repair, refactor, migrate, reconcile, test, version, roll back, or explain any framework, specification, workflow, stack, architecture, orchestrator, Skill, agent, prompt, instruction, policy, schema, model route, tool, integration, connector, UI, test, deployment profile, memory policy, source, module, service, SOP, or OJT artifact.

The goal is one governed, user-visible control plane where every editable Jarvis object can be viewed and safely changed by automation or explicit user request without allowing hidden or direct production self-modification.

## Editable object model

Register every editable object with:

- stable object ID, type, name, owner, version, status, scope, and exact location;
- content or immutable pointer plus SHA-256;
- editable and protected fields;
- dependencies and blast radius;
- validators, tests, evidence, and health checks;
- automation mode and autonomy ceiling;
- approval requirements;
- prior versions and rollback reference;
- last actor, reason, source request, and audit event.

Supported object classes include frameworks, specs, workflows, stacks, architecture, orchestrators, Skills, agents, prompts, instructions, policies, schemas, model routes, tools, integrations, connectors, UI, tests, deployment profiles, memory policies, sources, modules, services, SOPs, and OJT packs. Add new classes through a schema-versioned extension rather than untyped free text.

## Change modes

- `MANUAL_ONLY`: Jarvis may explain and draft, but only the owner may authorize application.
- `RECOMMEND`: Jarvis produces a diff, tests, risks, alternatives, and rollback plan.
- `AUTO_REVERSIBLE`: Jarvis may apply a low-risk staging change when all deterministic checks pass and an automatic rollback point exists.
- `GATED_EXECUTION`: Jarvis may prepare and simulate, but named authorities must approve before application.

Manual override may pause, reject, select an alternative, change the model route, request another test, or roll back. Manual override never bypasses secret handling, law, policy, financial, health, destructive, ownership, production, or evidence gates.

## Self-coding, self-repair, and self-update loop

Use:

`Observe -> Detect -> Classify -> Contain -> Diagnose -> Propose -> Diff -> Simulate -> Test -> Security Review -> Approval -> Canary -> Observe -> Promote or Rollback`

Requirements:

1. Capture the originating request and source pointer.
2. Identify affected objects, dependencies, compatibility constraints, and blast radius.
3. Create an isolated branch, worktree, sandbox, or staging record.
4. Back up affected state and record known-good versions.
5. Generate the smallest sufficient change.
6. Run schema, unit, integration, regression, security, policy, accessibility, cost, backup, restore, and rollback checks as applicable.
7. Use an independent verifier; the builder cannot self-certify.
8. Apply only to staging or an approved canary.
9. Monitor defined success and failure signals.
10. Promote only through the release gate; otherwise roll back automatically.

Never allow direct production self-modification, self-elevation, owner-credential inheritance, self-approval, policy weakening, unlimited retries, silent scope expansion, hidden background actions, or deletion of source history.

## Object browser and editor

The Command Centre must provide:

- global search, filters, tags, owners, status, dependencies, and affected modules;
- side-by-side current and proposed versions;
- plain-English explanation and technical view;
- source, requirement, implementation, test, evidence, runtime, and rollback links;
- form editor for safe fields and raw editor for authorised expert use;
- diff preview, compatibility report, blast-radius map, and cost estimate;
- simulation, test, approval, apply-to-staging, canary, promote, pause, reject, and rollback controls;
- complete version history and immutable action timeline;
- bulk update only through typed filters, limits, dry-run, and per-object results.

Every button must implement ButtonTruth: purpose, inputs, action, approval, exact output, next step, failure state, retry or rollback, and evidence written.

## Unified Jarvis Pop assistant

Jarvis Pop is the same assistant across every page and module, not a separate ungoverned chatbot. It must support:

- persistent popup, docked panel, full-screen workspace, and mobile layout;
- text chat, push-to-talk, wake-word-ready voice, transcript, captions, mute, stop, cancel, barge-in, and replay;
- the same policy and approval engine for text and voice;
- active-page, selected-object, source, requirement, evidence, test, and runtime context;
- model and LLM route selector with deterministic/local/free-first defaults, manual route selection, cost estimate, privacy label, and fallback chain;
- one or more LLM response panels when justified, with provenance and clear model identity;
- quick actions, suggested prompts, explain-this, show-dependencies, propose-update, run-checks, compare-versions, and rollback helpers;
- preview before external communication or code/system change;
- approval queue, human-action cards, activity timeline, test results, health, cost, and rollback history;
- keyboard navigation, screen-reader labels, high contrast, reduced motion, transcript export, localization-ready text, and novice/expert modes.

Voice is an input channel, not an authorization factor. Voice can request or prepare an action, but cannot replace MFA, owner approval, professional review, or a production release gate.

## LLM and panel routing

Expose model choices through governed profiles rather than raw provider keys. Show capability, privacy, context, speed, reliability, estimated cost, enabled state, and reason selected. Route through verified artifact, deterministic tool, internal data, local/private model, included/free allowance, cheapest qualified paid route, specialist premium, and justified panel.

The user may manually select a model or panel, but unavailable, unsafe, over-budget, unlicensed, or unapproved routes remain disabled with an exact reason and setup path.

## Automatic update classes

Jarvis may automatically propose updates for:

- framework and spec drift;
- stale workflow or stack references;
- architecture and dependency conflicts;
- agent or Skill trigger collisions;
- deprecated models, APIs, packages, schemas, or providers;
- failed tests, health checks, security scans, or policy checks;
- missing documentation, SOP, OJT, evidence, rollback, and observability;
- cost, token, latency, reliability, and duplicate-service improvements;
- source freshness, contradiction, and unresolved-gap changes.

Only low-risk, reversible staging updates covered by signed policies may be auto-applied. All other updates remain proposals or gated execution.

## Source and consolidation truth

The object registry does not prove that every historical source was captured. Maintain a separate source denominator with one state per known source: `AVAILABLE`, `PENDING_INGEST`, `FAILED_WITH_REASON`, `DUPLICATE_WITH_LINEAGE`, `EXCLUDED_WITH_REASON`, or `BLOCKED_BY_ACCESS`.

Do not state whole-project 100 percent until every known source is accounted for and every accepted requirement maps to implementation, tests or waiver, evidence, runtime state, and rollback. Historical reports that say 100 percent, zero gaps, production ready, or fully operational remain source claims until independently verified.

## Required evidence

For each change, store:

- source request and normalized requirement;
- baseline object version and digest;
- proposed diff and change plan;
- dependencies and blast radius;
- test and security results;
- approvals and manual overrides;
- staging or canary evidence;
- promoted version or rollback result;
- cost and runtime impact;
- final evidence-backed status.
