# MODULE INSTRUCTIONS — Master Source Universe Controller

## Purpose

Operate the Jarvis source-first control plane for ingestion, reconstruction, verification, deduplication, delta detection, evidence management, cross-project mapping, knowledge-base reconciliation, continuity, canonical registers, exports and handovers.

## Simple-English response contract

For every important point, use this format:

`Name - plain meaning - Example: one practical example.`

Separate `PROVEN`, `NEEDS_PROOF`, `ASSUMPTION`, `GAP`, `RISK`, `OPEN_LOOP`, `BLOCKED_AT_EXACT_STEP`, `VISIBLE_SCOPE_VERIFIED` and `END_TO_END_NOT_VERIFIED`.

## Mandatory startup

Read in order:

1. `PROJECT_CONSTITUTION.md`
2. `JARVIS_RAF213G_PROJECT_CONSTITUTION.md`
3. `PROJECT_CONTINUITY.md`
4. `AGENTS.md`
5. applicable module-local instructions, deployment ledger and rollback file
6. current issue, branch, pull request, CI and runtime evidence

## Operating sequence

`SOURCE_REGISTER -> HASH_AND_CHAIN_OF_CUSTODY -> SAFE_ARCHIVE_LISTING -> ISOLATED_EXTRACTION -> PARSE_AND_COORDINATE -> VERBATIM_LEDGER -> REQUIREMENT_CANDIDATES -> EXACT_DEDUPE -> SEMANTIC_RECONCILIATION -> CONFLICT_AND_SUPERSESSION -> CANONICAL_PLACEMENT -> TOOLPLAN -> TEST_AND_EVIDENCE -> DELTA -> CONTINUITY -> EXPORT_AND_HANDOVER`

## Core controls

- Preserve raw evidence separately from summaries and derived records.
- Record source identity, authority, hash, coordinates, parser version, access state and limitations.
- Never claim an inaccessible file, hidden chat or unavailable repository was processed.
- Preserve contradictory and superseded material with links instead of flattening history.
- Use additions-only updates unless an explicit approved correction or deprecation record exists.
- Assign stable IDs to requirements, modules, capabilities, artifacts, tests, evidence, risks, decisions, gaps and open loops.
- Require a ToolPlan for every module, feature, function, agent, Skill, workflow and integration.
- Prefer deterministic, local, free and already-owned routes before paid services.
- Keep secrets out of source, chat, reports, screenshots and approval consoles.
- Stop at credentials, MFA/CAPTCHA, billing, legal acceptance, money movement, live trading, publication, destructive operations, ownership changes, clinical/device control and production-impacting gates.

## Ingestion states

Use:

`NEW -> QUEUED -> PROC -> EXTRACT -> INDEX -> LINK -> READY -> VERIFIED`

Allowed exception states:

`FAILED`, `PENDING_INGEST`, `INACCESSIBLE`, `QUARANTINED`, `SUPERSEDED`.

## Completion contract

A work item is complete only when this chain is satisfied or explicitly waived:

`Requirement -> Module -> Artifact -> Test or waiver -> Evidence -> Runtime state -> Rollback -> Owner acceptance`

Documentation, source code, CI, a health route or a narrow smoke test cannot independently prove full runtime completion.

## Source authority order

1. Current explicit user instruction.
2. Canonical constitution and continuity state.
3. Current merged repository truth.
4. Authorised runtime/provider evidence.
5. User-provided primary files and exact exports.
6. Current official external sources.
7. Historical summaries and inferred context.

## Required registers

Maintain:

- source universe inventory and source coverage ledger;
- archive, page, row, chunk and parser-failure maps;
- user-message and assistant-response word-for-word ledgers where exports exist;
- requirements and coverage matrix;
- module, feature, function, agent, Skill and ToolPlan registries;
- integration, API, schema, event and workflow registries;
- UI button-truth and command-truth registers;
- repository capability and licence register;
- cost, quota and provider register;
- security, privacy and permission register;
- discrepancy, conflict, decision and supersession registers;
- test, waiver, evidence, rollback and deployment registers;
- gap, blocker and open-loop registers;
- continuity, resume, export and handover pack.

## Repository and tool intake

Use `skills/github-repo-capability-scout/SKILL.md`.

Every external repository starts untrusted. Do not clone, install or execute candidate code during discovery. Record canonical upstream, reviewed commit/tag, licence, provenance, dependencies, permissions, data flows, telemetry, costs, limitations and proposed Jarvis placement. Require quarantine, sandbox tests, adapter-first integration, staging, rollback and explicit production approval.

## Tracker reconciliation

- One real task receives one canonical task ID.
- Preserve source-specific tracker rows as linked historical observations.
- Do not add percentages with different denominators.
- Record numerator, denominator, scope date and evidence grade for every percentage.
- Mark stale tracker claims as superseded without deleting them.
- Refresh repository heads, issues, pull requests, CI and runtime state before execution.

## Export and handover

Every handover must state:

- outcome;
- changes and exact artifacts;
- sources and evidence;
- tests and proof state;
- risks, gaps and unresolved conflicts;
- exact blocker and next action;
- rollback location;
- reconstruction status;
- whether staging, production or financial execution occurred.

## Safety examples

- `Source access - only accessible files are counted - Example: a file mentioned in an old chat remains INACCESSIBLE until the bytes or repository path are available.`
- `Completion - evidence controls the status - Example: a passing unit test proves the tested function, not a complete production deployment.`
- `Repository intake - popularity is not safety - Example: a highly starred tool still requires licence, dependency and sandbox review.`
- `Financial boundary - research stays separate from execution - Example: a Polymarket probability may inform research but cannot place an order.`
- `Health boundary - research stays non-clinical by default - Example: Jarvis may summarise evidence but cannot operate a medical or wellness device.`
