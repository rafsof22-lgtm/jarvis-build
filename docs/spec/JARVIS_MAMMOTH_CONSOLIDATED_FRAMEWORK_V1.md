# Jarvis / RAF213G Mammoth Consolidated Framework V1

**Status:** `IMPLEMENTED_NOT_INTEGRATED`  
**Date:** 2026-07-22  
**Canonical repository:** `rafsof22-lgtm/jarvis-build`  
**Governing constitution:** `JARVIS_RAF213G_PROJECT_CONSTITUTION.md`  
**Execution plan:** `registry/plans/jarvis_full_completion_execution_plan_v1.json`  
**Blocker register:** `registry/gaps/jarvis_blocker_resolution_register_v1.json`

## 1. Executive objective

Build Jarvis as a source-first, evidence-led, modular, reversible and owner-governed operating system that can ingest project knowledge, coordinate specialist agents, route tools and models, operate isolated domain services, expose one truthful Command Centre, and progress from local simulation to authenticated staging and controlled production.

Success requires a complete evidence chain:

`Source -> Request -> Requirement -> Module -> Artifact -> Test/Waiver -> Evidence -> Runtime State -> Rollback -> Owner Acceptance`

## 2. Scope and boundaries

Included:

- all accessible Jarvis-related chats, exports, files, repositories, PRs, issues and runtime evidence;
- canonical source reconstruction and requirement traceability;
- 18-layer architecture, Command Centre, model/tool/skill routing and domain services;
- XRP/HBAR intelligence, AI CFO, Health, VTI, Property, Hub and future modules;
- local, staging and production lifecycle controls;
- security, privacy, legal, cost, rollback and continuity governance.

Excluded until separately approved:

- live trading or money movement;
- production health/device actions;
- destructive history rewriting;
- paid-resource creation, public publishing or credential scope expansion;
- claims that inaccessible chats or external systems were processed.

## 3. Source universe and denominator

Current proven source universe:

- June 2026 ChatGPT export: 2,610 conversations / 357,835 messages;
- five connected repositories: `jarvis-build`, `hub`, `videotranscribe`, `Jarvis-Health`, `property-agent-mcp`;
- V1-V18 trackers, registries, source packs, manifests and evidence;
- visible project context and current user requests;
- eight supplied shared-chat URLs registered as `BLOCKED_BY_ACCESS`.

All sources use one of:

`AVAILABLE`, `PENDING_INGEST`, `FAILED_WITH_REASON`, `DUPLICATE_WITH_LINEAGE`, `EXCLUDED_WITH_REASON`, `BLOCKED_BY_ACCESS`.

## 4. Requirement extraction and traceability

For each chat or source:

1. preserve raw content and immutable pointer;
2. separate user requests from assistant responses;
3. extract explicit requirements, inferred dependencies, decisions, corrections and open loops;
4. deduplicate canonical requirements while retaining all source links;
5. preserve contradictions and supersession;
6. map each requirement to module, artifact, test, evidence and runtime state;
7. place unresolved items in the gap register.

## 5. Stakeholders and authority

- **Owner:** final authority for credentials, budgets, production, destructive changes, regulated actions and acceptance.
- **Planner Council:** decomposes goals and dependencies.
- **Builder Council:** implements repository-safe changes.
- **Verifier Council:** independently tests and validates evidence.
- **Risk Authority:** classifies legal, privacy, security, financial and health risk.
- **Release Gatekeeper:** approves progression between local, staging, canary and production.
- **Domain Chiefs:** own XRP/HBAR, CFO, Health, VTI, Property, Hub and future modules.

No module self-certifies.

## 6. Governance and policies

Core laws:

- additions-only evolution;
- no silent deletion or weakening;
- no false completion claims;
- least privilege and service isolation;
- source-first proof and explicit uncertainty;
- free/local/cheapest-safe routing before premium spend;
- branch -> test -> PR -> review -> staging -> verification -> controlled production;
- complete rollback and evidence for every material change.

## 7. System architecture

Canonical flow:

`Experience -> Gateway -> Identity -> Sovereign Control Plane -> Agent Council -> Skill/Tool Fabric -> Model Router -> Workflow/Event Layer -> Domain Services -> Data/State -> Memory/Knowledge -> Evidence/Audit -> Security -> Observability/Cost -> Verification/Simulation -> Infrastructure -> Continuity -> Source Learning`

The 18 layers remain separately testable, permissioned and observable.

## 8. Module registry

Primary modules:

1. Sovereign Control Plane
2. Command Centre
3. Source Reconstruction and Knowledge Fabric
4. Agent and Skill Factory
5. Model Intelligence Router
6. Workflow/Event/Queue Engine
7. Evidence and Verification Engine
8. Security, IAM and Secret Governance
9. Observability, Cost and Operations
10. Deployment, Backup and Rollback
11. XRP/HBAR Apex Intelligence
12. AI CFO / Bill CFO
13. Jarvis Health and Longevity
14. VTI Video and Social Intelligence
15. Hub Integration Runtime
16. Property Buyer Intelligence
17. Product/Agency/Trading research factories
18. Continuity, Archive and Handover

Each module must have a module contract, service root, owner, inputs, outputs, permissions, tests, evidence and rollback.

## 9. Agent hierarchy

Use a hierarchical mesh:

- Orchestrator
- Source Intake Agent
- Requirement Analyst
- Architecture Planner
- Domain Specialists
- Builder Agents
- Security Reviewer
- Cost Governor
- Independent Verifier
- Release Gatekeeper
- Continuity Archivist

Agents use signed templates, scoped tools, quotas, retry limits, isolated memory and explicit termination conditions. Recursive unrestricted spawning is prohibited.

## 10. Skill routing

Skills are referenced, not copied into the control plane. Every route records:

`Skill -> Capability -> Module -> Trigger -> Inputs -> Outputs -> Tests -> Evidence -> Status`

Trigger collisions and overlapping ownership are logged. Specialist skills retain the strictest applicable controls.

## 11. Tools, APIs and integrations

Integration lifecycle:

`PROPOSED -> SANDBOX -> STAGED -> ACTIVE -> SUSPENDED -> REVOKED`

Every connector records:

- scopes and owner;
- secret reference, not value;
- rate limits and costs;
- schema/version monitoring;
- retry/idempotency rules;
- health check and smallest real route;
- revoke/export/vendor-exit path;
- rollback and evidence.

## 12. Data architecture

Required data classes:

- raw immutable sources;
- normalized requests and requirements;
- modules, agents, skills, tools and models;
- events, workflows and checkpoints;
- evidence, tests, risks, decisions and gaps;
- domain-specific data with strict isolation;
- audit, cost, health and deployment telemetry.

PII, health and financial data receive separate classifications, retention rules and access controls.

## 13. Memory architecture

Memory types:

- working memory;
- episodic task memory;
- semantic knowledge memory;
- procedural SOP/OJT memory;
- project continuity memory;
- immutable audit memory.

Every memory write has provenance, scope, expiry, correction and deletion rules. Unverified external text cannot silently become policy or production memory.

## 14. Knowledge ingestion

Pipeline:

`Discover -> Hash -> Inventory -> Extract -> OCR/Transcribe -> Chunk -> Index -> Link -> Verify -> Ready`

Use lexical, vector, graph, chronological, provenance, freshness and contradiction indexes. Every chunk retains exact source coordinates.

## 15. Intelligence gathering

The intelligence fabric performs:

- question generation;
- official-source prioritization;
- source expansion;
- claim extraction and contradiction analysis;
- freshness and event-date separation;
- social/video verification queues;
- source-budget control;
- gap-exhaustion checks;
- evidence-pack generation.

XRP/HBAR updates use a configurable 50-100-source target when justified, with independent-source and syndicated-copy deduplication.

## 16. Model routing

Routing order:

1. cached verified result;
2. deterministic local tool;
3. internal database/API;
4. local open model;
5. free allowance;
6. cheapest suitable paid model;
7. specialist premium model;
8. multi-model panel only when justified;
9. qualified human escalation.

Model records include capability, context, latency, privacy, benchmark, cost, reliability, licence and deprecation state.

## 17. Workflow engine

Every workflow defines:

- state machine;
- dependency graph;
- idempotency key;
- retries and dead-letter handling;
- checkpoints and resume points;
- cost/time/token ceilings;
- approval gates;
- rollback and safe stop;
- output and evidence contract.

## 18. Security and identity

Required controls:

- least privilege and zero trust;
- separate service identities and environments;
- secret manager only;
- network egress restrictions;
- prompt-injection and memory-poisoning defenses;
- SBOM, dependency, licence and malicious-package scans;
- signed artifacts and deployment provenance;
- immutable audit and incident response;
- kill switches and break-glass review.

## 19. Human approval gates

Owner approval is mandatory for:

- credentials and scope changes;
- billing or paid resources;
- production deployment;
- destructive or irreversible changes;
- public communication/publishing;
- money movement or live trading;
- sensitive health or device actions;
- legal attestations and domain ownership.

## 20. Command Centre UX

The Command Centre must provide:

- one canonical progress tally;
- 18-layer traffic lights;
- source and evidence drill-down;
- blocker and exact-next-action cards;
- safe one-click repository fixes;
- approval queue;
- cost, risk and runtime status;
- chronology and audit timeline;
- rollback controls;
- novice golden path and expert progressive disclosure.

## 21. SOP and OJT

Each role receives:

- role card;
- SOP;
- task checklist;
- failure playbook;
- simulation exercises;
- competency test;
- supervised probation;
- permission ceiling;
- retraining triggers;
- evidence of qualification.

## 22. Testing

Required test matrix:

- unit and schema;
- contract and integration;
- end-to-end;
- security and policy;
- privacy and access control;
- accessibility;
- load, latency and capacity;
- cost ceiling;
- retries, idempotency and reconciliation;
- backup, restore and disaster recovery;
- canary, rollback and kill switch;
- regression and historical-verifier compatibility.

## 23. Observability and operations

Track:

- service health and readiness;
- workflow latency, errors and retries;
- source coverage and freshness;
- model quality and drift;
- security findings;
- cost by task/module/provider;
- queue depth and dead letters;
- backup/restore status;
- unresolved evidence gaps;
- owner approvals and waivers.

## 24. Deployment architecture

Environments:

- local deterministic development;
- isolated test;
- authenticated staging;
- canary;
- controlled production;
- offline/degraded mode.

Each service has its own root, variables, domain, database, queue, health routes, backup, restore and rollback. Shared repository does not mean shared runtime.

## 25. Reliability and continuity

Required:

- RPO/RTO definitions;
- automated backups;
- periodic restore tests;
- queue durability;
- idempotent event replay;
- failover and degraded mode;
- continuity snapshot;
- resume prompt;
- release and rollback runbooks;
- exportable handover pack.

## 26. Cost model

Controls:

- zero-spend local baseline;
- task/module/provider budgets;
- hard cost ceilings;
- usage alerts;
- cache/batch/cheap-model routing;
- subscription consolidation;
- vendor lock-in and exit analysis;
- unit economics for business modules;
- no guaranteed income or investment outcomes.

## 27. Implementation roadmap

### Phase 0 — CI and governance repair

- fix V18, V17, V16, free-first and security-history checks;
- preserve historical verifier compatibility;
- merge V18 only after all required checks pass.

### Phase 1 — Source denominator lock

- ingest genuinely newer export;
- process eight shared chats or explicit source pack;
- recover attachments and binaries;
- complete thread/source/chunk ledgers.

### Phase 2 — Direct project reconstruction

- classify 83 XRP chats;
- reconstruct Tax and Active Trust separately;
- reconstruct Finance Planning and Financial New into AI CFO;
- reconstruct six Longevity chats under restricted-health controls.

### Phase 3 — Canonical mammoth specification lock

- reconcile every requirement to one canonical module;
- complete module, agent, skill, tool, model and integration registries;
- close conflicts through DecisionRecords;
- run no-gaps verifier.

### Phase 4 — Repository and runtime reconciliation

- map five repositories and all closed PR lineage;
- resolve capability overlap without deleting history;
- compare specification to implementation and deployment truth;
- implement missing repository-safe controls.

### Phase 5 — Authenticated staging

- approve IAM, secrets, endpoints, databases, budgets and rollback owners;
- prove Hub, VTI, Health, Property, CFO, XRP/HBAR and Command Centre routes;
- run privacy, security, persistence, retry, backup, restore and cost tests.

### Phase 6 — Canary and production

- security/risk review;
- owner approvals;
- canary deployment;
- monitor and reconcile;
- promote or rollback;
- owner acceptance.

### Phase 7 — Final acceptance and continuity pack

- all requirements mapped;
- all tests passed/waived;
- all evidence hashed;
- final discrepancy and no-gaps reports;
- release notes, rollback, archive and resume package.

## 28. Release and maintenance

Every release includes:

- versioned branch and PR;
- changed-file and requirement delta;
- tests and evidence;
- risks and residual gaps;
- migration and rollback;
- runtime proof;
- owner acceptance;
- maintenance and update cadence.

## 29. Evidence matrix

The canonical evidence matrix must link:

`Requirement ID -> Source Pointer -> Module ID -> Artifact Path -> Test ID -> Evidence Path -> Runtime State -> Rollback Path -> Owner Decision`

No task is `DONE_VERIFIED` without this chain.

## 30. Open loops and exact blockers

Current blockers:

- inaccessible direct chats and post-25-June delta;
- missing or unresolved referenced attachments;
- DigitalOcean recovery-console access;
- VTI historical-token rotation;
- Jarvis Health Railway domain/secrets;
- Property Sheets/Apps Script configuration;
- Hub workflow dispatch;
- protected Cobalt host and canary;
- VTI-Hub staging endpoint/signing-secret reference;
- authenticated Command Centre environment;
- external IAM, databases, provider credentials, budgets and rollback ownership;
- production owner acceptance.

These blockers are tracked in `registry/gaps/jarvis_blocker_resolution_register_v1.json`. Repository-safe work continues around them; external or irreversible actions stop at the exact gate.

## Completion truth

This framework is the canonical implementation contract for the accessible source universe. It is not a claim that inaccessible chats, external staging or production are complete. Final 100% status requires every source and requirement to pass the evidence chain or receive an explicit owner waiver.
