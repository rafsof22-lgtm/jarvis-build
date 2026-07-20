# Jarvis One-Page Command Centre Specification

**Date:** 20 July 2026  
**Status:** `SPEC_ONLY`

## Design objective

Present the full Jarvis system through one owner-facing page without deleting backend modules, specialist agents, evidence, parameters or audit data.

Frequent owner actions should be reachable within three clicks. Advanced records remain available through progressive disclosure and global search.

## Page layout

### 1. Global command bar

A single plain-English command field supports:

- ask Jarvis;
- create a task;
- search sources, evidence and modules;
- run `UPDATE`, `VERIFY`, `ZERO`, `CONTINUE`, `EXPORT` or approved deployment commands;
- attach files or links;
- select a workspace when routing is ambiguous.

The command bar must show the planned module, tools, cost class, approval requirement and expected output before consequential execution.

### 2. Global status strip

Display:

- overall system state;
- environment;
- service-health summary;
- unresolved blocker count;
- approvals waiting;
- current monthly cost and budget;
- security alerts;
- last verified backup;
- latest rollback point.

### 3. Seven workspace cards

Cards:

1. Jarvis Control
2. Wealth and Family Office
3. Revenue Factory
4. Trading and Markets Lab
5. XRP/HBAR Intelligence
6. Health and Care
7. Business, Property and Assets

Each card displays:

- traffic-light state;
- one-sentence current outcome;
- next recommended action;
- jobs running and queued;
- blockers;
- cost this month;
- risk level;
- latest evidence timestamp;
- `Open workspace` button.

### 4. Today panel

Show the highest-value actionable items across domains, deduplicated and ranked by urgency, dependency, owner effort, cost, risk and expected benefit.

### 5. Approval inbox

Every approval card states:

- requested action;
- module and agent;
- why it is required;
- exact side effect;
- estimated cost;
- affected data and environment;
- tests already passed;
- rollback path;
- approve, reject or modify controls.

### 6. Evidence and source panel

Show:

- source coverage percentage only for a declared denominator;
- pending-ingest objects;
- recent evidence packs;
- contradictions;
- stale sources;
- requirements lacking artifacts, tests or evidence.

### 7. Health, incidents and deployments

Show:

- service health;
- active incidents;
- failed or stuck jobs;
- current repository commits;
- deployment states;
- backup and restore state;
- safe one-click diagnostic or rollback options when pre-authorised.

## Workspace drill-down

Each workspace uses consistent tabs:

- Overview
- Tasks
- Sources
- Requirements
- Agents and Skills
- Workflows
- Integrations
- Data and Evidence
- Costs
- Risks and Approvals
- Tests and Deployments
- History and Rollback

Novice mode hides technical detail and explains consequences. Expert mode shows schemas, events, parameters, logs, traces, model routes and implementation references.

## Backend-only information

Do not place these on the default page:

- raw prompt and agent internals;
- full event payloads;
- source chunks and hashes;
- secret names unless needed for setup;
- advanced strategy parameters;
- full log streams;
- CI fixtures;
- superseded requirement text;
- raw database and queue administration;
- provider-specific implementation details.

These remain searchable and available in expert mode with access controls.

## Button Truth contract

Every interactive control requires:

- purpose;
- input requirements;
- handler or workflow;
- permission and approval policy;
- exact state transition;
- expected output and save location;
- run and evidence ID;
- failure state;
- retry or rollback;
- next-step loop.

Controls without implemented handlers must be disabled and labelled `PLANNED` or `BLOCKED`.

## Privacy and domain isolation

- Health and finance data are not shown in global summaries beyond sanitized status and counts.
- Cross-domain search respects purpose and permissions.
- Credentials are never displayed.
- Public repository data never includes raw confidential finance or health records.
- Every sensitive access creates an audit event.

## Acceptance criteria

The one-page console is not `DONE_VERIFIED` until:

1. all seven workspace cards use live or explicitly simulated state;
2. no button claims unsupported capability;
3. sensitive-domain summaries pass privacy tests;
4. keyboard and mobile accessibility tests pass;
5. cost and approval previews are accurate;
6. task correlation and evidence links work end to end;
7. failure, retry and rollback paths are proven;
8. an owner can locate any module, task, source or requirement through search or workspace navigation.
