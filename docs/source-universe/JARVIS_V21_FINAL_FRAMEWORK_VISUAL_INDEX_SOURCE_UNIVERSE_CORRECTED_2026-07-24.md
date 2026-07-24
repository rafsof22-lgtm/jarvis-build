# JARVIS V21 — Final Framework Visual Index — Source-Universe Correction v2

**Correction date:** 24 July 2026 — Australia/Melbourne  
**Repository state:** V21 merged; V22/V22.1 runtime reconciliation subsequently merged  
**Truth state:** `SOURCE_UNIVERSE_CORRECTED_BOUNDED — UNIVERSAL_COMPLETENESS_NOT_CLAIMED`

## 🔴 Correction to the original index

The original V21 visual index counts—51 modules, 38 functions, 10 tools and 7 APIs—were **high-level canonical counts**, not complete named-item counts. It did not visibly enumerate every source pack, agent file, repository, service-local instruction, child module, UI component, route, connector, model provider, application or external repository candidate.

## 📊 Expanded audit counts

| Registry layer | Count | Meaning |
|---|---:|---|
| Canonical requirement families | 38 | Broad deduplicated outcomes retained |
| Original V21 module rows | 51 | Top-level canonical module layer |
| Unique module manifest IDs located | 68 | Includes top-level modules, aliases and child modules |
| Manifest IDs absent from original V21 module table | 30 | Must be mapped, merged, retained as aliases or promoted |
| Agent/instruction/runtime file candidates | 134 | Filename-based candidates requiring semantic dedupe |
| Integration/tool/API/model/workflow file candidates | 131 | Filename-based candidates requiring semantic dedupe |
| Explicit code/UI/API surfaces located | 433 | Child functions, routes, pages, components and handlers |
| Curated named tools/apps/connectors/repository candidates | 174 | Current accessible named-item register |
| Named items absent as explicit original V21 rows | 155 | Missing explicit display, not necessarily missing intent |
| Accessible owned GitHub repositories | 5 | Current connector-visible repository set |
| Known unresolved source-universe gaps | 13 | Must remain visible until closed or waived |

## 🗃️ Accessible repository and codebase universe

### Connected GitHub repositories

1. `rafsof22-lgtm/jarvis-build` — governance, registries, control plane and isolated service roots.
2. `rafsof22-lgtm/hub` — XRP/HBAR and video/email runtime hub.
3. `rafsof22-lgtm/Jarvis-Health` — privacy-isolated Health MCP/runtime.
4. `rafsof22-lgtm/property-agent-mcp` — Property Buyer Intelligence MCP and provider integrations.
5. `rafsof22-lgtm/videotranscribe` — video/social intelligence console.

### Historical and packaged codebases

- `apex-jarvis-unified-framework`
- `JARVIS_CODE_BUILD_BASELINE_V35`
- `JARVIS_EXECUTABLE_BUILD_PACKAGE_V3`
- `JARVIS-OS-v1`
- `jarvis-os`
- `jarvis-unified-ai-platform`
- `Kimi_Agent_物业销售自动化`
- historical `jarvis-master`
- historical `universal_integration_layer`

These must be preserved as separate lineage layers until capability ownership, duplication and supersession are independently resolved.

## 🤖 Agent and instruction coverage

The audit located 134 agent/instruction/runtime file candidates, including:

- root and service-local `AGENTS.md` files;
- `agents/openai.yaml` agent metadata;
- role-council, agent-role and agent-playbook files;
- V35 agent loops and agent runtime routes;
- V3 advanced-agent architecture, agent runtime and agent factory code;
- `AgentSwarmDashboard`, `AgentHeartbeatMonitor`, `AgentSkillsDashboard`, `ManualOverridePanel`, `ApprovalQueue`, `KillSwitches` and related control surfaces;
- Bill-CFO and XRP/HBAR isolated agent/service instructions;
- specialist Skill entrypoints, snapshots and routing instructions.

The original index did not provide an explicit agent registry showing every agent, agent file, role, permission boundary, service root, trigger, tool scope, memory scope, test and runtime state.

## 🧩 Module manifest deltas

Thirty manifest IDs were not explicit rows in the original V21 module table. Important examples include:

- `MOD-CHAT-FUSION` — multi-panel/ChatHub response fusion;
- `MOD-EMERGENCY-LOCKDOWN` — emergency stop and kill-switch controls;
- `MOD-INSTALLER-BOOTSTRAP` and `MOD-INSTALLER-WIN11`;
- `MOD-INSTRUCTION-REGISTRY` — editable instruction/SOUL/memory/trigger registry;
- `MOD-INTEGRATIONS-CATALOG`;
- `MOD-KNOWLEDGE-SPINE`;
- `MOD-MEMORY-AUDIT`;
- `MOD-MODEL-ROUTER`;
- `MOD-PROJECT-REGISTRY`;
- `MOD-RESEARCH-INGEST`;
- `MOD-SELF-IMPROVEMENT`;
- `MOD-THREAT-INCIDENT`;
- `MOD-UPDATE-VERIFY`;
- `MOD-VOICE-COMMS` and `MOD-VOICE-GATEWAY`;
- digital-agency, SaaS, finance-intelligence, governance-control, dashboard-UX and security-control child modules.

Some are aliases or children of existing canonical modules. They must not be silently discarded or blindly counted as new top-level modules. Each requires a source-ID-preserving disposition: `ALIAS`, `CHILD_MODULE`, `PROMOTE_TO_TOP_LEVEL`, `SUPERSEDED`, `NOT_APPLICABLE_WITH_REASON` or `CONFLICT_REVIEW`.

## ⚙️ Features, functions, routes and UI surfaces

The audit located 433 explicit public-ish code/UI/API names not individually displayed as V21 canonical function rows. Examples include:

- `ChatHub8Panel`, `MultiPanelLayout`, `JarvisPopup`;
- `AgentSwarmDashboard`, `AgentHeartbeatMonitor`, `AgentSkillsDashboard`;
- `SkillEditor`, `ManualOverridePanel`, `ApprovalQueue`, `KillSwitches`;
- `KnowledgeBase`, `KnowledgeBaseViewer`, `TaskManagerUI`;
- model/provider handlers for OpenAI, Anthropic, Google, DeepSeek, Mistral, Moonshot/Kimi, Cohere, xAI and local models;
- broker/exchange routes for Kraken, Binance, Coinbase, Alpaca and Interactive Brokers;
- transcription routes for YouTube, Facebook and Instagram;
- integration-catalog, GitHub-discovery, tool-installation and environment-file generators;
- backtesting, trading, portfolio, intelligence, OCR and workflow interfaces.

These require a child-surface registry with canonical placement, implementation state, route/handler linkage, tests, approval policy and evidence.

## 🛠️ Expanded tools, apps, connectors and repository candidates

The original index did not visibly enumerate all mentioned or implemented items. The expanded named-item universe includes, at minimum:

### Runtime and infrastructure

Python, SQLite, FastAPI, Flask, Node.js, Next.js, React, TypeScript, Tailwind CSS, Docker, Docker Compose, Kubernetes, Celery, RabbitMQ, Kafka, PostgreSQL, Redis, DuckDB, Caddy and Nginx.

### Hosting and deployment

GitHub, GitHub Actions, Railway, Vercel, DigitalOcean, Hostinger, Oracle Free Tier, AWS and Hetzner.

### Model providers and runtimes

OpenAI, Anthropic Claude, Google Gemini, DeepSeek, Kimi/Moonshot, Ollama, Qwen, Grok/xAI, Mistral, Cohere, Groq, OpenRouter, Hugging Face, `llama.cpp` and vLLM.

### Agent frameworks and external repository candidates

CrewAI, LangGraph, LangGraph Swarm, LangChain, LlamaIndex, SuperAGI, MetaGPT, Auto-GPT, BabyAGI, OpenInterpreter, GPT Engineer, Sweep, Continue, Aider, Dify, Leon AI, OpenJarvis, `isair/jarvis`, `eadmin2/jarvis_ai`, `Avinashb722/jarvis-ai-assistant`, `LUCIFERx01/Personal-AI-Assistant`, `maniotrix/offline-ai-assistant` and `vercel-labs/agent-skills`.

These are candidates only until licence, provenance, security, maintenance, duplication, sandbox and integration reviews pass.

### Memory, vector and RAG routes

Pinecone, Weaviate, ChromaDB, Qdrant and Supabase/pgvector.

### Google and collaboration connectors

Google Drive, Google Sheets, Gmail, Google Calendar, Google Contacts, Google Cloud OAuth, service accounts, Slack and Notion.

### Workflow, business and payment tools

n8n, Zapier, Make.com, ManyChat, RapidAPI and Stripe.

### Property and prospecting routes

Apollo, Hunter, A-Leads, Apify and Flyfish.

### Trading, market data and blockchain research

Kraken, Binance, Coinbase Advanced, Alpaca, Interactive Brokers, Yahoo Finance, CoinGecko, Twelve Data, CoinMarketCap, CryptoCompare, Glassnode, Santiment, CryptoQuant, IntoTheBlock, DeFiLlama, Token Terminal, Messari, Nansen, Financial Datasets, Fiscal.ai, AlphaStocks, Bigdata.com, Bloomberg Terminal, Forex Factory, Upsideonly.com and Alchemy.

### Media, transcription and social routes

OpenAI Whisper, AssemblyAI, Rev.ai, YouTube Transcript API, YouTube Data API, Meta Graph API, X/Twitter API, TikTok API, Reddit API, Telegram Bot API, Discord, Instagram, LinkedIn, Facebook, ElevenLabs, Wispr, Cobalt, NotebookLM, LumaLabs Dream Machine, browser extensions and React Native mobile share targets.

### Research and legal/patent sources

Elicit, Consensus, Exa, Context7, SEC EDGAR, CourtListener, PACER, PubMed, bioRxiv, USPTO and EPO.

### App builders and creative platforms

Emergent AI, Base44, Lovable, Bolt, Hercules, Atoms, Softgen, ComfyUI, Madethis.com, Infinitai.org, Aifimap.com, Potion and Money Printer Turbo.

### Commerce and passive-income platforms

Shopify, Gumroad, Etsy, Amazon Associates, ShareASale and CJ Affiliate.

### Interface protocols

Model Context Protocol, OpenAPI/GPT Actions, webhooks and JSON-RPC 2.0.

## ⚠️ Remaining source gaps

The following remain unproven or incomplete:

- attachment and referenced-file resolution;
- embedded connector/document reference recovery;
- complete branch-tree, system-node and tool-node reconstruction;
- full semantic extraction of every archive member;
- owner-reviewed resolution of low-confidence and multi-placement records;
- exact crosswalk from every assistant commitment to artifact/runtime evidence;
- current source-file indexing and semantic search proof for every connected repository;
- licence/security/sandbox review of external repository candidates;
- authoritative runtime proof for every service, connector and provider route;
- complete app/tool cost, permission, OAuth, secret-placement and revoke-path records;
- native ChatGPT Project membership and sibling-branch proof;
- full source denominator reconciliation across June and July exports;
- final owner acceptance.

## ✅ Corrected conclusion

- The original V21 index captured the primary architecture and broad canonical requirements.
- It did **not** visibly capture every agent file, previous codebase, tool, app, connector, repository candidate, manifest module, child feature, route, UI component or function.
- This correction preserves those missing layers and prevents the high-level counts from being mistaken for universal completeness.
- The next required artefact is a fully deduplicated source-to-agent/module/feature/function/tool/app/connector/repository traceability matrix with evidence-backed inclusion, alias, supersession or exclusion decisions.