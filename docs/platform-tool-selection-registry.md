# Platform Tool Selection Registry

Status: active append-only registry  
Last updated: 2026-06-10  
Scope: Jarvis, Sof Property Scout, coding agents, workflow automation, AI app builders, deployment platforms, prospecting/enrichment, Google Sheets/console outputs, and future AI tools discovered from screenshots, ads, web research, connected sources, or user requests.

## Platform Selection Rule v2 - cost, tiers, credits, tokens, build-token evaluation

For every future platform or tool recommendation, evaluate not only best free, cheapest, most cost-effective, most user-friendly, and best all-in-one fit, but also every visible pricing tier, AI credits, build tokens, task credits, model credits, token pools, included usage, overage pricing, expiry/rollover rules, workflow runs, agent runs, concurrent agents, scheduled jobs, queue limits, action/step limits, execution duration limits, model-token costs, BYO API key support, model-router support, cheap-model-first routing, cache/batch support, API-key handling, vault/secrets support, OAuth scopes, audit logs, RBAC, SSO, permissioning, export, rollback, GitHub/Railway/n8n/Google Sheets/Postgres/Redis/MCP/webhook/browser automation compatibility, code export, repo sync, lock-in risk, deployment portability, self-hosting option, data export, and true cost per large task.

Default decision policy:
1. Prefer free/self-host/open-source/cheapest-safe tools when they meet the requirement.
2. Prefer all-in-one only when it actually reduces cost, complexity, and lock-in while still meeting security, audit, API, and export requirements.
3. Do not recommend paid tools until current pricing, tier limits, credits/tokens, and overage rules are checked.
4. Mark weakly verified tools as PENDING_VERIFICATION and do not connect credentials until official docs, pricing, security, export, and integration evidence are checked.
5. Preserve historical recommendations; re-rank with reason/date instead of replacing prior conclusions.

## Current core stack decision

| Layer | Preferred tool | Decision |
|---|---|---|
| Command brain | ChatGPT Agent | Keep as planner, auditor, researcher, and task supervisor. Do not use as cheap always-on backend worker. |
| Code/source truth | GitHub | Keep for repo, PRs, issues, history, rollback. |
| Runtime/backend | Railway | Keep as API/runtime/secrets/database base; control always-on costs with queues/workers. |
| Workflow cockpit | n8n self-hosted on Railway or n8n Cloud | Add as central workflow/agent builder. |
| Human database/console | Google Sheets or custom console | Keep for Sof Property Scout review/output. |
| Coding agent layer | Cursor / Codex where available | Add for write-capable coding, multi-agent repo edits, fixes, refactors. |
| App/dashboard builder | Hercules, Atoms.dev, Base44, Lovable, Bolt | Optional UI acceleration, not core workflow engine. |
| Sales/prospecting add-ons | Apollo, Hunter, A-Leads, Flyfish test | Use only with dedupe, proof, scoring, and credit controls. |

## Priority additions from latest screenshot scan

| Platform | Category | Placement | Priority | Current decision | Status |
|---|---|---|---:|---|---|
| Cursor | AI coding IDE/agents | Local repo editing and code agents | 2 | Add now for coding gap | Verified enough |
| PandaOS | Local AI workspace | Possible Jarvis local cockpit | 3 | High watchlist | Early verified / pricing gap |
| Atoms.dev | AI app/startup builder | Dashboard/app prototype | 3 | Test free/cheap tier; monitor credits | Verified enough |
| ShoalStack / Shoal | Visual deployment | Railway alternative/watchlist | 4 | Watchlist vs Railway | Pricing gap |
| Flyfish AI | Sales intelligence | Sof account-intelligence add-on | 4 | Test free tier only | Verified enough |
| Jarvio | Amazon/e-commerce AI teammate | Amazon/e-commerce module only | 7 | Hold; no credentials | PENDING_VERIFICATION |
| Wingman | SMB 24/7 business engine | Business ops watchlist | 7 | Hold | PENDING_VERIFICATION |
| Vincen AI | AI agents/tasks | General agent watchlist | 7 | Hold | PENDING_VERIFICATION |
| DenovoAI | Startup/business OS | Startup builder watchlist | 7 | Hold | PENDING_VERIFICATION |

## Active Jarvis platform ranking

1. ChatGPT Agent + GitHub + Railway + n8n + Google Sheets/console.
2. Cursor / Codex for write-capable coding and PR work.
3. Hercules / Atoms / Base44 / Lovable / Bolt for app/dashboard prototyping.
4. PandaOS as all-in-one local cockpit watchlist.
5. ShoalStack as deployment alternative watchlist.
6. Gumloop and Activepieces as workflow alternatives depending UX/cost.
7. Flyfish as Sof Property Scout account-intelligence test only.
8. Jarvio, Wingman, Vincen, DenovoAI remain PENDING_VERIFICATION.

## Sof Property Scout placement

Core stack: ChatGPT Agent -> n8n -> Railway/Postgres/queue -> Apollo + Hunter + A-Leads-if-confirmed + public search/Apify -> Raw Capture Google Sheet -> Master Verified Google Sheet/console -> Source Quality + Cost Dashboard.

## Cost-control gates

- Dedupe before paid enrichment or verification.
- Score before verification; verify only realistic, unique, high-fit leads.
- Track credit cost per raw lead, verified email, Tier 1 buyer, and usable source-proofed company.
- Keep capture-only boundary until the user explicitly authorizes outreach.
- Never connect credentials to PENDING_VERIFICATION tools.
