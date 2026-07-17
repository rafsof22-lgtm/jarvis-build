# Jarvis App Risk And Approval Matrix

## Purpose

This file governs Jarvis app usage, write risk, approvals, and safe automation boundaries.

The goal is maximum automation without unsafe external writes, surprise sends, destructive changes, unwanted deployments, or uncontrolled cost exposure.

## Approval Policy Standard

Default policy:

- Reads: allow automatically when relevant and privacy-safe.
- Drafts and plans: allow automatically.
- External writes: require confirmation unless explicitly approved as low-risk automation.
- Destructive actions: require confirmation.
- Sends/posts/messages: require confirmation.
- Infrastructure creation/deletion/deployment: require confirmation.
- Paid actions or cost-increasing actions: require confirmation.
- Secrets and credentials: never expose in chat; place in provider secret stores or GitHub Secrets.

## Current App Matrix

| App | Role In Jarvis | Current Capability | Risk Level | Recommended Approval | Notes |
|---|---|---|---|---|---|
| GitHub | Primary repo/build spine | Read/write repo actions | High | Require confirmation for merge/delete/update main/create PR unless explicitly approved | Use branches and PRs by default |
| Google Drive | Docs/sheets/slides/file artifacts | Read/write/share/delete | High | Require confirmation for share/delete/large edits; allow draft docs when requested | Use as artifact route |
| Gmail | Source intake and email drafts/sends | Read/write/send/delete | High | Require confirmation for sends, forwards, deletes, bulk labels | Prefer drafts before sends |
| Google Calendar | Scheduling and availability | Read/write events | Medium | Require confirmation for create/update/delete/respond | Reads can be automatic |
| Google Contacts | Contact lookup | Read only | Low | Automatic reads | No writes visible |
| Slack app | Slack read/write as connected user | Read/write/post/delete/edit | High | Require confirmation for posts, deletes, edits, DMs, invites | Separate from Slack channel deployment |
| Notion | Dashboard/task/docs database route | Read/write pages/databases | Medium/High | Require confirmation for database changes/moves/deletes; allow requested page drafts | Good structured operating record |
| DigitalOcean | Cloud deployment fallback | Provision/delete/resize/rebuild/power actions | Critical | Require confirmation for all writes and cost-impacting actions | Never auto-create paid infra without approval |
| Hostinger | Website/app fallback | Create websites | High | Require confirmation for create/publish actions | Use for fast site fallback |
| Hercules | App/site build route | Build apps/websites | High | Require confirmation for external publishes or cost-impacting actions | Useful for rapid app surfaces |
| Alchemy | On-chain data | Mostly read/simulate | Medium | Automatic reads; confirmation for simulations if externally consequential | Good crypto/on-chain source |
| Binance | Market data | Read market data | Low/Medium | Automatic reads | Research-only unless trading actions ever appear |
| CoinGecko | Crypto market data | Read market data | Low | Automatic reads | Good free/source route |
| Kraken | Crypto news/data | Read | Low | Automatic reads | Research-only |
| Financial Datasets | Market data | Read | Low/Medium | Automatic reads | Watch API cost/limits |
| Fiscal.ai | Financial data | Read | Low/Medium | Automatic reads | Watch API cost/limits |
| Bigdata.com | Finance/news/data | Read | Low/Medium | Automatic reads | Watch API cost/limits |
| AlphaStocks | Stock analysis | Read | Low/Medium | Automatic reads | Research-only |
| Context7 | Up-to-date docs | Read | Low | Automatic reads | Use for library/API docs |
| HAPI MCP Registry | MCP discovery | Read | Low | Automatic reads | Use for MCP discovery, not blind install |
| Hugging Face | Models/datasets/Spaces | Read | Low | Automatic reads | Good for model discovery |
| Canva | Designs | Read/write design actions | Medium/High | Confirmation already recommended for writes | Use for visual artifacts when requested |
| Adobe Acrobat | PDF work | Connected but no visible enabled actions | Low currently | Defer until actions needed | Confirm capabilities before relying on it |

## Required Changes To Consider

The current editor setup shows many write-capable apps configured with low/no confirmation. For production Jarvis, recommended next action is to reconfigure key write-capable apps to require confirmation for consequential writes.

Priority apps for approval tightening:

1. GitHub
2. Gmail
3. Slack app
4. Google Drive
5. DigitalOcean
6. Hostinger
7. Hercules
8. Notion
9. Google Calendar

## GitHub Safe Execution Pattern

- Prefer branch creation over direct default-branch updates.
- Prefer PR creation over direct merge.
- Require confirmation before merge, branch deletion, file deletion, or workflow reruns that may deploy.
- Use commit messages that reference the Jarvis module and registry update.
- Include rollback notes in PR body.

## Deployment Safe Execution Pattern

- Never create, resize, rebuild, delete, or power-cycle cloud resources without confirmation.
- Use GitHub Secrets or provider secret stores for API keys.
- Use `.env.example` for names only, never values.
- Run CI/smoke tests before deployment where possible.
- Prefer free-first Oracle path when externally prepared.
- Use DigitalOcean/Hostinger/Hercules only when approved or when the user prioritizes speed over lowest cost.

## Secrets Policy

Use GitHub Secrets or provider-managed secrets for:

- OPENROUTER_API_KEY
- DEEPSEEK_API_KEY
- KIMI_API_KEY
- QWEN_API_KEY or DASHSCOPE_API_KEY
- ORACLE credentials or deploy tokens
- DIGITALOCEAN_ACCESS_TOKEN
- HOSTINGER tokens or project credentials
- HERCULES credentials
- DATABASE_URL
- REDIS_URL
- JWT_SECRET or app secret keys

Never paste secret values into chat, instructions, files, commits, or logs.

## Open Gaps

- Need explicit user decision on whether to change app approval policy from current high-autonomy mode to safer confirmation mode.
- Target GitHub repo/branch verified for this pass: `rafsof22-lgtm/jarvis-build`, base `main`, work branch `jarvis/control-registry-model-router-plan`.
- Need actual secret placement outside chat before live deployment.

## Update Log

- Initial app risk and approval matrix created from the Jarvis setup audit.
- 2026-07-17: Confirmed GitHub branch/PR workflow for control-registry updates; live deployment remains blocked until host configuration and secrets are proven outside chat.
