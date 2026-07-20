# XRP/HBAR Intelligence + AI CFO Economic Engine Federation

Date: 20 July 2026
Status: `SPEC_LOCK_IN_PROGRESS`
Parent issue: #45
Parent PR: #33

## 1. Purpose

Treat XRP/HBAR intelligence as an economic-engine capability that feeds the AI CFO, treasury, tax, custody, portfolio and scenario systems. Preserve the XRP/HBAR specialist research runtime and evidence history while exposing governed recommendation candidates to the CFO layer.

This module provides decision support, scenario analysis, evidence packs and risk-aware recommendations. It does not represent itself as licensed personal financial advice, autonomously move money, place trades, change custody, alter SMSF strategy, lodge tax positions or override owner/adviser approvals.

## 2. Runtime and repository placement

- Canonical requirements, approvals, registries and release governance: `rafsof22-lgtm/jarvis-build`
- XRP/HBAR evidence, event intake and specialist intelligence runtime: `rafsof22-lgtm/hub`
- AI CFO target service: proposed private `rafsof22-lgtm/jarvis-cfo-os`
- VTI source and transcript evidence: `rafsof22-lgtm/videotranscribe`
- Portfolio execution adapters: separate approval-gated service; not part of the research runtime

## 3. End-to-end architecture

`Authorised sources -> Source registry -> Claim extraction -> Evidence/contradiction graph -> XRP/HBAR intelligence -> Asset and portfolio scenarios -> AI CFO constraints -> Recommendation candidate -> Suitability/compliance review -> Owner/adviser decision -> Optional approved execution handoff -> Reconciliation -> Outcome learning`

## 4. Intelligence domains

### XRP / Ripple / XRPL / RLUSD

- official Ripple and XRPL releases;
- regulatory, litigation and licensing developments;
- ETFs and regulated investment products;
- banks, payments, remittances and treasury products;
- RLUSD reserves, circulation, integrations and risk;
- XRPL DeFi, tokenisation, stablecoins and liquidity;
- escrow, supply, treasury and public on-chain activity;
- institutional custody and exchange support;
- competitor and substitution risk;
- direct XRP demand path versus general Ripple/XRPL adoption.

### HBAR / Hedera / Hashgraph

- official Hedera releases and network upgrades;
- governing council and enterprise adoption;
- tokenised assets, stablecoins, payments and DeFi;
- network activity, fees, staking and supply;
- institutional products, custody and exchange support;
- technical, governance and concentration risk;
- direct HBAR demand path versus general Hedera technology adoption.

### Shared market and portfolio intelligence

- price, volume, liquidity and volatility;
- market structure, derivatives and leverage;
- public on-chain and custody flows;
- macroeconomic and regulatory risk;
- catalyst, trigger and invalidation tracking;
- sentiment as a discovery signal, never proof;
- probability ranges and scenario consistency;
- correlation, concentration and portfolio drawdown;
- custody, counterparty, yield and smart-contract risk.

## 5. AI CFO federation inputs

- entity and beneficial-owner map;
- personal, trust, company and SMSF holdings;
- wallet, exchange and custody locations;
- tax lots, cost bases and holding periods;
- liquidity needs and cash-flow forecasts;
- liabilities, tax reserves and committed expenses;
- investment mandate, risk limits and prohibited actions;
- target allocation ranges and concentration limits;
- insurance, estate and succession constraints;
- adviser, accountant, auditor and trustee approval requirements.

## 6. Recommendation output contract

Every recommendation candidate must include:

- recommendation ID and version;
- question and intended decision;
- entity and portfolio scope;
- current holdings and valuation timestamp;
- relevant evidence and source classes;
- assumptions and data-quality warnings;
- base, upside, downside and stress scenarios;
- expected benefit and principal risks;
- concentration, liquidity, custody and counterparty effects;
- tax and record-keeping considerations;
- alternatives including no-action;
- invalidation conditions and review date;
- confidence and evidence sufficiency;
- regulatory/professional-review classification;
- approvals required;
- execution status, if separately approved;
- reconciliation and outcome fields.

## 7. Required editable agents

1. Source Scout and Watchlist Agent
2. Official-Source Verification Agent
3. Regulatory and Litigation Agent
4. XRP/Ripple Intelligence Agent
5. HBAR/Hedera Intelligence Agent
6. Network Utility and Direct-Demand Analyst
7. Market Data and Liquidity Agent
8. On-chain and Public Flow Agent
9. ETF and Institutional Products Agent
10. VTI Claim Intake Agent
11. Creator and Influencer Reliability Agent
12. Catalyst, Trigger and Invalidation Agent
13. Scenario and Probability Agent
14. Portfolio Exposure and Correlation Agent
15. Custody, Yield and Counterparty Risk Agent
16. Tax-Lot and Record Evidence Agent
17. Entity and Mandate Constraint Agent
18. AI CFO Recommendation Composer
19. Conflict and Contradiction Reviewer
20. Compliance and Advice-Boundary Reviewer
21. Independent Recommendation Verifier
22. Outcome and Forecast Calibration Agent
23. Knowledge Curator and Versioning Agent
24. Cost and Model Router

Each agent must be configuration-driven, versioned and editable through approved schemas. Required fields include purpose, owner, prompt/version, source scopes, models, tools, thresholds, scoring weights, permissions, denied actions, budgets, retries, tests, evidence writes, monitoring, rollback and release state.

## 8. Required editable skills

- official-source search and retrieval;
- web/news/regulator research;
- VTI transcript claim extraction;
- source credibility and freshness scoring;
- XRP/Ripple and HBAR/Hedera query expansion;
- direct-token-demand analysis;
- on-chain/public-flow analysis;
- market/liquidity analysis;
- catalyst and probability modelling;
- portfolio scenario simulation;
- concentration/correlation/drawdown analysis;
- custody and counterparty assessment;
- yield and passive-income assessment;
- Australian crypto record and tax-evidence preparation;
- entity/SMSF/trust/company constraint checks;
- recommendation evidence-pack generation;
- contradiction and invalidation review;
- forecast scoring and calibration;
- model/provider benchmarking;
- knowledgebase ingestion and retrieval;
- dashboard and alert generation;
- adviser/accountant handoff pack generation.

Skills follow: `DISCOVER -> QUARANTINE -> INSPECT -> TEST -> BENCHMARK -> APPROVE -> PIN -> DEPLOY -> MONITOR -> ROLLBACK`.

## 9. Continuous intelligence and learning loops

### Knowledge learning

- preserve raw sources and exact evidence pointers;
- update entities, relationships, claims and contradictions;
- maintain source reliability and freshness history;
- separate verified facts, reported facts, opinions, forecasts and promotions.

### Forecast and recommendation learning

- record forecast date, horizon, probability and invalidation condition;
- record recommendation version and decision taken;
- record later outcomes, costs, tax effects and operational issues;
- score calibration, false positives, false negatives and missed opportunities;
- propose updated weights or source rankings.

### User and professional feedback learning

- record owner preferences and explicit mandate changes;
- preserve accountant, auditor, adviser and legal feedback;
- distinguish accepted, rejected, superseded and temporary decisions;
- never infer permission from repeated behaviour alone.

### Governed improvement route

`Observe -> Detect -> Diagnose -> Propose -> Simulate -> Evaluate -> Security/Compliance Review -> Owner Approval -> Canary -> Monitor -> Promote or Rollback`

Learning may propose changes. It may not silently change risk limits, investment mandates, tax rules, custody rules, advice boundaries, approval gates, model permissions or live execution capabilities.

## 10. Knowledgebase organisation

Required collections/graphs:

- source registry;
- claim and evidence graph;
- entity/holding/wallet/account graph;
- catalyst and event timeline;
- forecast and probability registry;
- recommendation and decision ledger;
- tax-lot and transaction evidence;
- custody and counterparty registry;
- source/creator reliability history;
- conflict, discrepancy and invalidation register;
- agent/skill/model version registry;
- evaluation and replay datasets;
- outcome and calibration history;
- current-state and historical snapshots.

Every derived record must link to the raw source and transformation version.

## 11. Source and API map

Source priority:

1. official Ripple, XRPL, Hedera and regulator sources;
2. courts, government, exchange filings and licensed-market notices;
3. official company announcements and technical documentation;
4. primary datasets and public ledgers;
5. credible financial and technology reporting;
6. independent secondary analysis;
7. social, creator and video claims as discovery leads only.

Potential data adapters, subject to current documentation, cost, rights and approval checks:

- Ripple/XRPL and Hedera official APIs/documentation;
- public ledger/indexer providers;
- market price, liquidity and derivatives providers;
- ETF/exchange/issuer disclosures;
- VTI evidence events;
- Xero accounting data;
- approved portfolio/custody exports;
- Koinly or equivalent tax-lot exports;
- CSV/manual evidence ingestion.

No private data source is presumed accessible without explicit connector or upload evidence.

## 12. Safety, legal and professional gates

- separate information, research, general guidance and personalised regulated advice;
- require legal/professional review where licensing boundaries may apply;
- require accountant/auditor review for tax, SMSF and statutory matters;
- require owner approval for portfolio mandate changes;
- require separate execution approval for any trade or transfer;
- disable withdrawals by default on machine credentials;
- never expose secret values in chat, logs or evidence packs;
- preserve full audit and rollback history;
- do not turn social repetition into probability or price proof;
- do not convert technology adoption directly into token-demand conclusions.

## 13. Evaluation suite

- source citation correctness;
- claim classification accuracy;
- direct-demand versus indirect-adoption classification;
- contradiction detection;
- stale-data detection;
- portfolio calculation accuracy;
- scenario reproducibility;
- recommendation schema validation;
- compliance boundary classification;
- model hallucination and unsupported-claim tests;
- prompt-injection and malicious-source tests;
- historical forecast calibration;
- transaction/reconciliation fixtures;
- backup, restore and replay tests.

## 14. Current proof state

- Historical XRP/HBAR source files and trackers: `EVIDENCE_PRESENT_UNVERIFIED`
- VTI-to-Hub claim-event design: `SPECIFIED_AND_PARTIALLY_IMPLEMENTED`
- AI CFO/Xero integration: `PARTIAL_SOURCE_CLAIMS_RUNTIME_UNVERIFIED`
- XRP/HBAR + AI CFO economic federation: `SPEC_ONLY`
- Personalised regulated recommendation service: `BLOCKED_PENDING_LEGAL_AND_PROFESSIONAL_BOUNDARY`
- Autonomous execution: `BLOCKED`
- Continuous production learning: `BACKLOGGED`

## 15. Next implementation order

1. complete source denominator for XRP/HBAR, CFO and portfolio materials;
2. define canonical event and recommendation schemas;
3. implement read-only holdings/entity/tax-lot fixtures;
4. implement evidence graph and contradiction registry;
5. implement portfolio/scenario engine with deterministic tests;
6. implement recommendation composer and independent verifier;
7. implement compliance/advice-boundary classifier;
8. connect VTI and Hub staging events;
9. connect CFO staging read model;
10. execute replay, security, calibration and rollback tests;
11. request owner and professional approval before any live recommendation or execution boundary.
