# JARVIS Sovereign Request-Capture Build Compiler

**State:** `SPEC_ONLY_CANDIDATE_FOR_V21`  
**Owner:** Jarvis Build  
**Target:** Original Jarvis Framework and approved control/domain layers

## Purpose

Convert each relevant human request into a traceable, executable, approval-aware Build Contract without losing the original wording or confusing request capture with task execution.

## Compiler pipeline

`RECEIVE -> PRESERVE_WFW -> RESOLVE_CONTEXT -> CLASSIFY -> EXTRACT -> DEDUPE_WITH_LINEAGE -> PLACE -> PLAN -> GATE -> EXECUTE_SAFE_SCOPE -> VERIFY -> RECORD -> CONTINUE`

## Mandatory input record

```yaml
request_id: stable identifier
source_pointer: exact chat/file/message coordinate
request_wfw: immutable original request
received_at: UTC and Australia/Melbourne
requester: human owner or authorised actor
project_context: current project and related projects
attachments: available, missing, or reference-only
access_boundary: exact accessible and inaccessible sources
```

## Compiled Build Contract

Every significant request compiles to:

- objective and measurable acceptance criteria;
- target classification: Original Jarvis, Jarvis Build, control overlay, domain module, shared service, or one-off response;
- explicit and implied requirements;
- inputs, dependencies, data classes, repositories, services, Skills, tools, models, APIs, and workflows;
- source and evidence requirements;
- cost, token, time, retry, concurrency, and capacity ceilings;
- permissions and owner approval gates;
- security, privacy, legal, financial, health, and publication boundaries;
- implementation artifacts and exact save paths;
- tests, independent verification, release criteria, failure modes, rollback, and safe stop;
- status, gaps, risks, decisions, assumptions, and open loops;
- next exact action.

## Placement rules

1. Preserve raw requests separately from normalized requirements.
2. Use one canonical requirement with unlimited lineage links rather than duplicate requirement text.
3. Place target behavior inside the Original Jarvis Framework.
4. Place reconstruction/build/deployment mechanics inside Jarvis Build.
5. Place Prompt Cowboy, role-council, forensic, universal-execution, and SOP/OJT logic as control overlays.
6. Keep regulated and independently deployable domain modules isolated.
7. Flag contradictions for DecisionRecord review.

## Automatic depth selection

The compiler selects the smallest route that can prove the outcome:

- trivial deterministic task: direct tool or concise response;
- bounded document/framework update: source inspection, append-only patch, verifier;
- archive/project reconstruction: deterministic extraction, ledgers, classification, review queue;
- repository change: branch, tests/scans, draft PR, independent review;
- runtime change: staging, health, persistence, retry, backup/restore, rollback;
- consequential action: stop at explicit approval.

## Non-execution rule

Compiling a request does not authorise credentials, billing, merge, deployment, publication, destructive action, money movement, live trading, legal acceptance, or health/device action.

## Required tests

- exact request hash and source pointer retained;
- all explicit constraints represented;
- target-builder-overlay classification present;
- duplicate and conflict handling recorded;
- approval gates correctly fail closed;
- every artifact has a test/evidence/rollback path;
- no unsupported 100% or zero-gap claim;
- regression test against simple, multi-constraint, ambiguous, multilingual, file-heavy, contradictory, scope-creep, and prompt-vs-execution requests.
