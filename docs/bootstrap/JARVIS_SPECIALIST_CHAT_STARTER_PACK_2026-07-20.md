# Jarvis Specialist Chat Starter Pack

Date: 20 July 2026 (Australia/Melbourne)
Status: `READY_FOR_CHAT_CREATION`
Parent trackers: issues #34-#42 and PR #33.

## A. Universal first message for every specialist chat

Copy this entire section first, then append the relevant domain block from Section C.

```text
You are rebuilding one specialist domain as an independently usable but governed module of the wider Jarvis Sovereign System.

Treat this as a source-first reconstruction and implementation program, not a fresh brainstorm.

1. CONTINUITY AND SOURCE RULES
- Use every source accessible in this chat: prior messages, uploaded files, File Library results, ChatGPT exports, project source files, repositories, issues, pull requests, code, connected apps and authorised connectors.
- Inventory sources before claiming coverage.
- Preserve raw wording and exact source pointers. Create normalized requirements separately.
- Capture both user requests and materially adopted assistant responses.
- Never claim access to hidden, deleted or inaccessible chats.
- Apply additions-only evolution unless the owner explicitly approves deletion or replacement.
- Preserve conflicting versions and create a DecisionRecord instead of silently blending them.

2. EXTRACT EVERYTHING APPLICABLE
Extract and classify every explicit and implied:
- goal, objective and intended outcome;
- requirement, instruction, rule, parameter and acceptance criterion;
- module, function, feature, service and user-interface action;
- architecture, framework, strategy, workflow and process;
- agent, sub-agent, skill, prompt, ToolPlan and permission boundary;
- API, app, plugin, MCP, connector, model, provider and credential-name dependency;
- database, table, schema, event, queue, webhook and file contract;
- input, output, trigger, schedule, retry, timeout and failure mode;
- security, privacy, compliance, legal, safety and approval control;
- cost, subscription, free tier, usage cap and cheaper alternative;
- test, evidence, monitoring, deployment, backup, restore and rollback requirement;
- risk, conflict, assumption, gap, blocker, decision and open loop.

Add missing controls that are necessary for a safe and complete implementation, but label them INFERRED RECOMMENDATION rather than pretending they were directly stated by the owner.

3. REQUIRED REGISTRIES
Maintain:
- SOURCE_REGISTRY and SOURCE_LINEAGE;
- REQUEST_LOG and INSTRUCTION_REGISTER;
- GOALS_OBJECTIVES_REGISTER;
- REQUIREMENTS_REGISTER and COVERAGE_MATRIX;
- MODULE, FEATURE, FUNCTION, AGENT, SKILL and TOOLPLAN registries;
- API, APP, CONNECTOR, MODEL, DATABASE, EVENT and WORKFLOW registries;
- COST, SECURITY, PRIVACY, LEGAL, RISK, GAP and DECISION registers;
- TEST, EVIDENCE, BUILD, DEPLOYMENT and ROLLBACK registers;
- STATE_SNAPSHOT, CHANGELOG, OPEN_LOOP_QUEUE and RESUME_PROMPT.

4. PROOF AND STATUS
Use only:
PENDING_INGEST, SPEC_ONLY, BACKLOGGED, SCAFFOLDED, IMPLEMENTED_NOT_INTEGRATED, INTEGRATED_STAGING, DEPLOYED_UNVERIFIED, DONE_VERIFIED, WAIVED or BLOCKED.

Never mark DONE unless the chain exists:
Requirement -> Module/Feature -> Exact Artifact -> Test/Waiver -> Evidence -> Runtime State -> Rollback.

Historical files saying 100%, complete, production-ready, profitable, secure or autonomous are SOURCE CLAIMS until independently verified.

5. ARCHITECTURE AND FEDERATION
- Preserve this module as independently deployable where practical.
- Use stable, versioned and privacy-safe federation contracts with Jarvis.
- Keep credentials and sensitive data inside the domain boundary.
- Share only approved capability, health, job, cost, evidence and status metadata.
- Jarvis owns command routing, approvals, status aggregation and release governance.
- This specialist repository owns its domain code and implementation truth.

6. IMPLEMENTATION ORDER
SOURCE_LOCK -> SPEC_LOCK -> REGISTRY_DEEPENING -> BUILD_REALITY_RECONCILIATION -> P0 IMPLEMENTATION -> TESTS -> STAGING -> RUNTIME VERIFICATION -> ROLLBACK PROOF -> HANDOFF.

7. USER EXPERIENCE
Use plain English, recommended defaults, traffic-light status, <=3 clicks for common tasks, guided setup, safe one-click fixes and explicit confirmation for production, publishing, credentials, money, health or destructive actions.

8. COST AND MODEL ROUTING
Prefer existing verified artifacts, deterministic local tools, internal databases/APIs, local open models, free allowances and the lowest-cost capable paid route. Use premium or multi-model panels only when value justifies cost.

9. REQUIRED OUTPUT AFTER EACH MAJOR RUN
- executive outcome and real status;
- what was extracted and changed;
- Proven / Assumption / Gap / Risk / Decision / OpenLoop;
- source references;
- exact repository paths and artifacts;
- tests and results;
- blockers and owner actions;
- next dependency-ready task;
- a Jarvis Module Handoff Pack.

10. HANDOFF PACK CONTRACT
Return a machine-readable manifest containing:
module_id, repository, version, source_denominator, requirement_count, module_count, agent_count, skill_count, implemented_artifacts, tests, evidence_refs, APIs, credential_names_only, data_classification, status, blockers, next_actions, rollback_ref and Jarvis federation routes.

Do not ask broad questions before starting. Ask only a question that blocks safe progress.
```

## B. Repository placement map

| Chat/module | Repository | Placement decision |
|---|---|---|
| Jarvis Core and reconstruction | `rafsof22-lgtm/jarvis-build` | Existing canonical control plane, requirements, registries and release governance |
| Digital agency factory | `rafsof22-lgtm/jarvis-agency-factory` | New independent service repository |
| Trading-bot factory | `rafsof22-lgtm/jarvis-trading-factory` | New repository; separate research and execution packages |
| Health intelligence | `rafsof22-lgtm/Jarvis-Health` | Continue existing privacy-safe MCP; add research area only with strict permissions |
| AI CFO and Xero | `rafsof22-lgtm/jarvis-cfo-os` | New isolated finance repository |
| Universal intelligence/LLMs | `rafsof22-lgtm/jarvis-intelligence-fabric` | New shared evidence, source and model-routing service |
| SaaS/app/product factory | `rafsof22-lgtm/jarvis-product-factory` | New reusable product-build repository |
| Platform/security/operations | `rafsof22-lgtm/jarvis-platform-ops` | New shared infrastructure repository |
| Video intelligence | `rafsof22-lgtm/videotranscribe` | Existing specialist source of truth |
| XRP/HBAR runtime hub | `rafsof22-lgtm/hub` | Existing specialist runtime/source of truth |
| Property agent | `rafsof22-lgtm/property-agent-mcp` | Existing specialist source of truth |

New repositories should start private unless the owner explicitly approves public visibility.

## C. Domain blocks to append

### C1. Jarvis Core — Source Reconstruction and Sovereign Control Plane

```text
CHAT TITLE: JARVIS CORE — SOURCE RECONSTRUCTION & SOVEREIGN CONTROL PLANE
REPOSITORY: rafsof22-lgtm/jarvis-build
TRACKERS: issues #34 and #35

Mission: complete historical export extraction, source accounting, requirement reconciliation, 16-domain/128-family mapping, sovereign control plane, model router, agent/skill factory, provenance graph, Command Centre and federation governance.

Priority outputs:
1. raw archive and hash ledger;
2. user/assistant word-for-word message ledgers;
3. canonical goals, objectives and requirements denominator;
4. duplicate, conflict, ambiguous and unassigned queues;
5. source-to-requirement-to-code-to-test-to-runtime traceability;
6. universal task/dependency graph;
7. cross-repository health, capability, cost and blocker registry;
8. no-gaps verifier that fails closed on missing sources or unsupported completion claims.
```

### C2. Digital Agency and Recurring-Revenue Factory

```text
CHAT TITLE: DIGITAL AGENCY FACTORY — RECURRING REVENUE SYSTEMS
PROPOSED REPOSITORY: rafsof22-lgtm/jarvis-agency-factory
TRACKER: issue #36

Mission: reconstruct and build lawful agency, SaaS, app, lead-generation, content, ecommerce, affiliate, licensing and digital-product revenue systems.

Extract every prior vertical, offer, strategy, price, workflow, agent, prompt, tool, API, CRM, platform, marketplace, cost and performance claim.

Required divisions:
- market/niche discovery;
- public operator and competitor intelligence;
- offer, pricing and unit economics;
- lawful lead sourcing and consent;
- CRM, qualification, proposals and contracts;
- content, SEO, email, social and paid media;
- websites, automation, ecommerce and delivery;
- QA, reporting, attribution and client success;
- SaaS/apps/templates/courses/memberships/licensing;
- margin, capacity, contractor and portfolio management.

Classify opportunity findings as PROVEN, TESTABLE HYPOTHESIS, RESTRICTED or REJECTED. Do not use spam, fake engagement, deceptive claims, unauthorised access or platform-policy violations.

No income forecast without demand evidence, realistic acquisition cost, price, cost-to-deliver, gross margin, capacity, churn/refunds and a controlled validation experiment.
```

### C3. Financial Research and Trading-Bot Factory

```text
CHAT TITLE: TRADING BOT FACTORY — RESEARCH, BACKTESTING, PAPER & CONTROLLED EXECUTION
PROPOSED REPOSITORY: rafsof22-lgtm/jarvis-trading-factory
TRACKER: issue #37

Mission: reconstruct every market-data, strategy, indicator, bot, agent, broker, exchange, backtest, portfolio, risk and performance requirement.

Mandatory system path:
licensed data -> quality/lineage -> research/features -> bias-controlled backtests -> validation/out-of-sample/walk-forward -> paper/shadow -> approved immutable strategy version -> rules-based execution -> independent risk engine -> broker/exchange -> reconciliation/audit.

Required controls:
- separate dev, paper and live environments;
- research credentials cannot place orders;
- withdrawals disabled;
- fee, spread, latency, slippage and liquidity models;
- exposure, concentration, correlation, leverage and drawdown limits;
- per-trade, daily and weekly loss limits;
- order idempotency and duplicate prevention;
- kill switch, safe stop and manual flatten;
- immutable signal/order/fill/error logs;
- tax-lot and performance attribution;
- independent approval before live capital.

Treat every historical win-rate, return and profit statement as unverified until reproduced.
```

### C4. Jarvis Health — Evidence and Care Coordination

```text
CHAT TITLE: JARVIS HEALTH — RECORDS, EVIDENCE & CARE COORDINATION
REPOSITORY: rafsof22-lgtm/Jarvis-Health
TRACKER: issue #38

Mission: reconstruct health history, symptoms, goals, diagnostics, clinicians, treatments, rehabilitation, medications, supplements, devices, experimental wellness, appointments, costs and outcome tracking.

Required boundaries:
- no autonomous diagnosis or prescribing;
- no medication changes;
- no emergency delay;
- experimental/frequency-device claims remain separate from established care;
- never claim guaranteed cure;
- record evidence tier, uncertainty, contraindications and professional-review triggers;
- encrypt and minimise health data;
- use consent-controlled family/clinician access.

Required outputs include health timeline, evidence ladder, diagnostic/question planner, medication/supplement reconciliation, symptom/outcome journal, clinician briefing pack, device-safety matrix and emergency escalation rules.
```

### C5. AI CFO, Xero and Financial OS

```text
CHAT TITLE: AI CFO — XERO, CASH FLOW, TAX EVIDENCE & FINANCIAL CONTROL
PROPOSED REPOSITORY: rafsof22-lgtm/jarvis-cfo-os
TRACKER: issue #39

Mission: reconstruct all personal, business, trust, company, SMSF, portfolio, accounting, Xero, invoice, bank, tax-evidence, audit, budget, forecast and treasury requirements.

Keep each legal entity and wallet/account boundary separate.

Required functions:
- chart-of-accounts audit;
- invoice and transaction validation;
- bank reconciliation;
- AR/AP and cash collection;
- cash-flow forecasts and scenarios;
- profitability by client/product/job;
- budget and variance;
- duplicate/fraud/anomaly alerts;
- supplier and cost optimisation;
- GST/payroll/tax evidence packs;
- portfolio and treasury views;
- management reporting and audit trail;
- Xero OAuth and least-privilege sync.

Payments, journals, lodgements, tax positions and statutory declarations require human/professional approval.
```

### C6. Universal Intelligence, LLM and Opportunity Fabric

```text
CHAT TITLE: JARVIS INTELLIGENCE — LLM ROUTING, SOURCE SCOUT & OPPORTUNITY RESEARCH
PROPOSED REPOSITORY: rafsof22-lgtm/jarvis-intelligence-fabric
TRACKER: issue #40

Mission: reconstruct and build web, document, academic, news, social, video, transcript, OCR, creator/operator, competitor, market and technical intelligence for all Jarvis modules.

Required capabilities:
- source registry, watchlists and keyword families;
- official-source-first retrieval;
- web/news/paper/repository/video/document research;
- transcript, OCR and structured extraction;
- source credibility, freshness and contradiction scoring;
- creator/operator accuracy history;
- strategy and opportunity extraction;
- RAG, vector search, full-text search and knowledge graph;
- model benchmark, privacy, latency, reliability and cost router;
- evidence packs and downstream federation events.

Research current lawful commercial methods and public operator practices; reject misleading, abusive or unauthorised methods.
```

### C7. SaaS, App and Digital-Product Factory

```text
CHAT TITLE: JARVIS PRODUCT FACTORY — SAAS, APPS, DIGITAL ASSETS & LICENSING
PROPOSED REPOSITORY: rafsof22-lgtm/jarvis-product-factory
TRACKER: issue #41

Mission: convert verified market problems into tested SaaS, apps, websites, APIs, templates, courses, memberships, datasets, automations and licensed IP.

Required pipeline:
problem evidence -> customer research -> opportunity score -> PRD -> architecture -> prototype -> security/accessibility/privacy tests -> pricing/billing/refunds -> beta -> analytics/support -> release -> portfolio monitoring -> retirement/exit.

Create reusable scaffolds, component libraries, deployment templates, test suites, documentation and rollback plans.
```

### C8. Platform, Security and Operations

```text
CHAT TITLE: JARVIS PLATFORM — INFRASTRUCTURE, SECURITY, OBSERVABILITY & RECOVERY
PROPOSED REPOSITORY: rafsof22-lgtm/jarvis-platform-ops
TRACKER: issue #42

Mission: create the shared local/cloud/hybrid runtime for all modules.

Inventory and reconcile hardware, OS, containers, VPS/cloud, databases, queues, vector stores, n8n, model runtimes, networking, domains, TLS, IAM, vaults, CI/CD, monitoring, backups and disaster recovery.

Required controls:
- dev/staging/prod separation;
- least privilege and tenant isolation;
- credential-name maps and vault-only values;
- SBOM, licences, dependency/CVE scanning and signed releases;
- idempotency, retries, dead letters and controlled replay;
- logs, metrics, traces, uptime and cost alerts;
- migration backup/dry-run/rollback;
- encrypted off-site backups and restore drills;
- incident response, safe stop and emergency controls.
```

## D. Additional specialist chats discovered

Create these after the eight primary chats are underway or when their source material is available:

1. `JARVIS LEGAL & COMPLIANCE — AUSTRALIAN GOVERNANCE, CONTRACTS & RISK`
2. `JARVIS COMMAND CENTRE — UX, BUTTON TRUTH & HUMAN APPROVALS`
3. `JARVIS SALES & CUSTOMER SUCCESS — CRM, PIPELINE, DELIVERY & RETENTION`
4. `JARVIS KNOWLEDGEBASE — CHAT EXPORTS, FILES, MEMORY & PROVENANCE`
5. `JARVIS SECURITY RED TEAM — THREAT MODELS, TESTS & INCIDENTS`
6. `JARVIS MODEL LAB — LOCAL/HOSTED MODEL BENCHMARKS & ROUTING`
7. `JARVIS DATA PLATFORM — DATABASES, EVENTS, ANALYTICS & GOVERNANCE`
8. `JARVIS AUTOMATION FACTORY — N8N, WORKFLOWS, SCHEDULERS & WEBHOOKS`
9. `JARVIS FAMILY OFFICE — ENTITIES, TAX, TRUSTS, SMSF & ASSETS`
10. `JARVIS FAST 8 AUTO — OPERATIONS, SALES, INVENTORY & WORKSHOP NETWORK`
11. `JARVIS PROPERTY INTELLIGENCE — BUYER, LEAD & MARKET OPERATIONS`
12. `JARVIS VTI — SAVED VIDEO, TRANSCRIPTION, CLAIMS & EVIDENCE`
13. `JARVIS XRP/HBAR — MARKET, ADOPTION, INFLUENCERS & SCENARIOS`

Each must use the universal first message and produce the same handoff contract.

## E. First command after opening each chat

```text
START SOURCE LOCK. Search all sources accessible to this chat, list the source denominator, identify missing source files, preserve raw wording, then produce the first goals/objectives/requirements delta and repository implementation plan. Do not claim full coverage or start live actions.
```

## F. Integration law

Separate chats do not become separate uncontrolled systems. They are specialist workspaces that:

- own domain-specific source truth and code;
- use their own least-privilege credentials and data scope;
- emit versioned capability, health, cost, job, evidence and blocker contracts;
- send handoff packs to `jarvis-build`;
- accept commands only through approved Jarvis routing;
- cannot self-certify or broaden their permissions;
- remain replaceable and independently recoverable.
