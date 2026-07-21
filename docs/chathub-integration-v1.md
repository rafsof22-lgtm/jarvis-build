# ChatHub and Free AI Capability Intake V1

## Purpose

This tranche adds a governed intake path for ChatHub multi-LLM uploads and free/open AI capability discovery.

## Source preservation

A filename containing `ChatHub` or `Chat Hub`, case-insensitively, is treated as a ChatHub source candidate. Jarvis must:

1. read and hash the exact bytes;
2. save an immutable raw copy before parsing;
3. preserve every model response word-for-word;
4. store parsing, normalized requirements and any consolidated answer as separate derived records;
5. preserve conflicts and model disagreement instead of silently blending them.

The original framework text is evidence. It is not silently rewritten. Execution of instructions remains separately governed by law, platform terms, security, permissions, credentials, costs and owner approvals.

## Multi-LLM consolidation

The intake parser supports parallel JSON response arrays and labelled text sections. It records model identity and response content. A consolidated answer is a separate derivative with one of these strategies:

- synthesis;
- consensus;
- best-evidenced answer;
- structured consolidation;
- disagreement map.

Consensus is not treated as factual proof.

## ChatHub operating route

The cost-effective route is:

- use the owner's paid ChatHub membership as the interactive browser/web multi-model front end;
- use supported exports or owner uploads for source intake;
- validate ChatHub Custom Chatbot against a scoped OpenAI-compatible Jarvis staging endpoint;
- do not scrape authenticated browser sessions or assume the paid subscription includes a server API;
- use local or self-hosted Jarvis services for durable storage, tracing, orchestration and automation.

## Free AI repository discovery

When a request or upload names a tool, app, plugin, connector, model or related capability, the intake program should automatically:

1. check existing Jarvis capabilities;
2. search current GitHub and official sources;
3. capture repository and commit provenance;
4. inspect licence, dependencies, security and total cost;
5. identify duplicates, replacements and complementary capabilities;
6. map connectors, logs, approvals and rollback;
7. integrate through an adapter only after sandbox and staging evidence.

Public or open-source code is quarantined until reviewed. No package installation, code execution, credential use or production connection is implied by discovery.

## Current proof state

- ChatHub filename detection: implemented.
- Exact-byte raw vault copy: implemented.
- Parallel JSON response extraction: implemented.
- Labelled text response extraction: implemented.
- Separate consolidation manifest: implemented.
- Capability registry: implemented.
- CI tests: implemented, pending pull-request run.
- ChatHub current export-schema validation: pending owner export intake.
- ChatHub Custom Chatbot staging validation: blocked by endpoint and scoped credential design.
- Full Jarvis Knowledge Fabric integration: not yet integrated.
