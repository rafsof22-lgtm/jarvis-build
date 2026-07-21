# Jarvis Full-Stack 18-Layer Architecture

**Snapshot:** 21 July 2026 — Melbourne  
**State:** `ARCHITECTURE_REFERENCE_VERIFIED / END_TO_END_NOT_VERIFIED`

## Outcome

Jarvis now has an explicit **18-layer full-stack architecture**, exceeding the owner's minimum requirement of 13 layers. The architecture expands the original core chain without replacing it:

`Experience -> Gateway -> Identity -> Sovereign Control -> Agents -> Skills/Tools -> Models -> Workflow/Queue -> Domain Services -> Transactional Data -> Memory/Knowledge -> Evidence/Audit -> Security/Privacy -> Observability/Cost -> Verification/Release -> Infrastructure/Resilience -> Continuity/Rollback -> Source Reconstruction/Learning`

## Layer map

| # | Layer | Current repository state | Principal remaining gate |
|---:|---|---|---|
| 1 | Experience and Omnichannel Interface | `INTEGRATED_STAGING` | Authenticated staging and accessibility journeys |
| 2 | Gateway, API and Edge | `IMPLEMENTED_NOT_INTEGRATED` | Connected ingress and authenticated canary |
| 3 | Identity, Consent and Tenant Boundary | `IMPLEMENTED_NOT_INTEGRATED` | OIDC/RBAC and tenant-isolation proof |
| 4 | Sovereign Governance and Approval Control Plane | `DONE_VERIFIED` | Connected enforcement and owner acceptance |
| 5 | Agent Orchestration and Role Council | `IMPLEMENTED_NOT_INTEGRATED` | Connected lifecycle and termination proof |
| 6 | Skill, Tool and Connector Fabric | `IMPLEMENTED_NOT_INTEGRATED` | Full connector inventory and sandbox canaries |
| 7 | Model Routing and Inference | `INTEGRATED_STAGING` | Approved live-provider and failover proof |
| 8 | Workflow, Event, Queue and Scheduler | `IMPLEMENTED_NOT_INTEGRATED` | Connected queue/scheduler and cross-module replay |
| 9 | Domain Application Services | `IMPLEMENTED_NOT_INTEGRATED` | Connected service contracts and isolation proof |
| 10 | Transactional Data and State | `IMPLEMENTED_NOT_INTEGRATED` | Approved PostgreSQL, migrations and retention proof |
| 11 | Memory and Knowledge Fabric | `IMPLEMENTED_NOT_INTEGRATED` | Connected hybrid retrieval benchmark |
| 12 | Evidence, Provenance and Audit | `DONE_VERIFIED` | Post-export chat delta and final acceptance |
| 13 | Security, Privacy and Supply Chain | `IMPLEMENTED_NOT_INTEGRATED` | Connected IAM, SBOM/signing and incident drill |
| 14 | Observability, Cost and Operations | `IMPLEMENTED_NOT_INTEGRATED` | Connected telemetry and authoritative usage evidence |
| 15 | Verification, Simulation and Release Gates | `DONE_VERIFIED` | Connected E2E, canary and production acceptance |
| 16 | Infrastructure, Deployment and Resilience | `IMPLEMENTED_NOT_INTEGRATED` | Connected topology, restore and DR proof |
| 17 | Continuity, Versioning and Rollback | `DONE_VERIFIED` | Fresh chat delta, restore drills and final archive |
| 18 | Source Reconstruction and Continuous Learning | `IMPLEMENTED_NOT_INTEGRATED` | Post-25 June chat delta and connected hybrid index |

## Project-chat access truth

Jarvis can consolidate every chat or source that is actually visible, uploaded or present in an authorised export. This runtime cannot directly enumerate every live sibling chat in the ChatGPT project UI. The June 2026 export is historically broad, but chats created or changed after 25 June require a new export or explicit chat pack.

The continuous policy is therefore:

1. ingest current visible conversation and uploads;
2. reconcile the historical export and existing ledgers;
3. treat later chats as a delta denominator;
4. never describe live-project coverage as complete until the project-chat list and post-export delta reconcile;
5. propagate approved requirements through the 18 layers using stable IDs, source pointers, tests and evidence.

## Release boundary

The 18-layer map is a canonical architecture and gap model. It is not evidence that all 18 layers are connected or production-ready. Production still requires connected staging, identity, data isolation, security, observability, backup/restore, rollback, cost proof and owner acceptance.
