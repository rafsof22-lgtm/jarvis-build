# XRP/HBAR Env And Source Stack Catalog

Last updated: 2026-07-07

This catalog keeps the XRP/HBAR service usable before every API is connected. The service must boot with required runtime variables only. Source, LLM, OCR, transcription, storage, alert, and trading providers stay disabled or metadata-only until their variables are filled and the matching feature gate is enabled.

## Safety Defaults

Keep these defaults unless the owner explicitly approves a narrower change:

```text
READ_ONLY_MODE=true
TRADING_MODE=paper
LIVE_TRADING_ENABLED=false
APPROVAL_REQUIRED=true
MAX_DAILY_API_SPEND_USD=0
MAX_DAILY_LLM_SPEND_USD=0
MAX_DAILY_TRADING_NOTIONAL_USD=0
```

Do not paste secrets into chat. Secrets belong in Railway variables, GitHub secrets, or a vault.

## Required Now

These are required for the Railway HTTP/MCP service to be production-ready:

| Variable | Purpose | Where | Secret |
|---|---|---|---|
| `APP_ENV=production` | Production mode label | Railway service variable | no |
| `BASE_URL` | Public XRP/HBAR Railway URL | Railway service variable | no |
| `LOG_LEVEL=info` | Runtime logging | Railway service variable | no |
| `MCP_AUTH_MODE=bearer` | MCP route protection | Railway service variable | no |
| `MCP_BEARER_TOKEN` | MCP auth secret | Railway service secret | yes |

Railway injects `PORT`; do not hardcode it in Railway unless debugging locally.

## Free/Public-First Sources

These should be filled first because they avoid paid API spend:

| Source family | Variables | Notes |
|---|---|---|
| XRPL public nodes | `XRPL_RPC_URL`, `XRPL_RPC_FALLBACK_URL`, `XRPL_WS_URL`, `XRPL_WS_FALLBACK_URL` | Use for ledger, amendments, transactions, AMM, and route proof where reachable. |
| XRPL explorers | `XRPL_EXPLORER_BASE_URL`, `XRPSCAN_BASE_URL`, `BITHOMP_BASE_URL`, `XRPL_TO_BASE_URL` | Evidence discovery and cross-checking. Treat explorer analytics as secondary until ledger-verified. |
| Ripple/XRPL official | `RIPPLE_BASE_URL`, `RIPPLE_INSIGHTS_RSS_URL`, `RIPPLE_STABLECOIN_URL`, `XRPL_ORG_BASE_URL` | Primary source class for Ripple/XRPL product, docs, and official updates. |
| Hedera public | `HEDERA_MIRROR_NODE_URL`, `HEDERA_HASHSCAN_BASE_URL`, `HEDERA_DOCS_BASE_URL`, `HEDERA_BASE_URL`, `HEDERA_BLOG_RSS_URL` | HBAR comparison and enterprise/DLT context. |
| Free market data | `COINGECKO_API_BASE_URL`, `COINPAPRIKA_API_BASE_URL`, `DEFILLAMA_API_BASE_URL`, `YAHOO_FINANCE_BASE_URL` | Use for baseline pricing, stablecoins, TVL, market caps, and watchlists. |
| Exchange public data | `BINANCE_API_BASE_URL`, `KRAKEN_API_BASE_URL`, `COINBASE_EXCHANGE_API_BASE_URL`, `BITSTAMP_API_BASE_URL`, `UPHOLD_API_BASE_URL` | Public market data only unless exchange keys are approved. |
| Official institutions | `SEC_BASE_URL`, `CFTC_BASE_URL`, `FEDERAL_RESERVE_BASE_URL`, `BIS_BASE_URL`, `IMF_BASE_URL`, `DTCC_BASE_URL`, `SWIFT_BASE_URL`, `ISDA_BASE_URL` | Regulatory, settlement, collateral, tokenization, and market-structure proof. |
| Public news/search | `GDELT_API_BASE_URL` | No-key public event/news discovery. |

## Optional Free-Key Or Low-Cost Add-Ons

These can improve coverage but should stay blank until the owner creates keys:

| Provider | Variables | Use |
|---|---|---|
| CoinGecko key | `COINGECKO_API_KEY` | Higher market-data limits. |
| CoinMarketCap | `COINMARKETCAP_API_KEY` | Market data fallback. |
| CryptoCompare | `CRYPTOCOMPARE_API_KEY` | Price/history fallback. |
| Brave Search | `BRAVE_SEARCH_API_KEY` | Web/source discovery. |
| SerpAPI or Google CSE | `SERPAPI_API_KEY`, `GOOGLE_CUSTOM_SEARCH_API_KEY`, `GOOGLE_CUSTOM_SEARCH_CX` | Search fallback when browser/search is unavailable. |
| YouTube Data API | `YOUTUBE_API_KEY` | Video discovery metadata. Transcripts still need public/manual or a transcription provider. |
| Reddit | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | Social lead discovery only, not proof. |
| OCR.space | `OCR_SPACE_API_KEY` | Low-cost OCR fallback. |
| CourtListener | `COURTLISTENER_API_KEY` | Public legal/court source discovery where relevant. |

## Paid Or Pro Sources To Add Later

These are optional placeholders. Do not enable until cost and terms are approved:

| Provider class | Variables | Use |
|---|---|---|
| On-chain analytics | `GLASSNODE_API_KEY`, `SANTIMENT_API_KEY`, `CRYPTOQUANT_API_KEY`, `COINMETRICS_API_KEY`, `TOKEN_TERMINAL_API_KEY`, `ARKHAM_API_KEY`, `NANSEN_API_KEY` | Deeper flow, reserve, holder, and institutional-wallet analytics. |
| Market/pro data | `MESSARI_API_KEY`, `COINAPI_KEY`, `COINGLASS_API_KEY`, `TRADINGVIEW_USERNAME`, `TRADINGVIEW_PASSWORD` | Markets, derivatives, exchange balances, charts, alerts. |
| Professional terminals | `BLOOMBERG_API_KEY`, `REFINITIV_API_KEY`, `FACTSET_API_KEY`, `S_AND_P_CAPITAL_IQ_API_KEY` | Institutional-grade finance data. Use only if already subscribed. |
| Legal/pro research | `LEXISNEXIS_API_KEY`, `PACER_API_KEY` | Legal record expansion. |

## LLM Order

Use this order to control cost:

1. `LLM_PROVIDER=none` for metadata-only runtime.
2. `OLLAMA_BASE_URL` for local/free private inference where available.
3. Low-cost hosted model providers only after approval: `OPENROUTER_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `TOGETHER_API_KEY`, `FIREWORKS_API_KEY`.
4. Premium providers only where needed: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_GEMINI_API_KEY`.

If no LLM key is present, the service should still run health, readiness, status, MCP discovery, metadata extraction, and supplied-transcript reprocessing.

## Transcription And OCR Order

1. Manual/public transcript input first.
2. Local OCR mode first where possible.
3. Low-cost OCR/transcription keys only after approval: `OCR_SPACE_API_KEY`, `DEEPGRAM_API_KEY`, `ASSEMBLYAI_API_KEY`.
4. Premium cloud OCR only when needed: Google Vision, Azure Vision, AWS Textract.

## Persistence And Exports

Start without writes. Add persistence only when needed:

| Stage | Variables | Notes |
|---|---|---|
| Local/export only | `LOCAL_EXPORT_DIR` | Temporary runtime exports. |
| Database | `POSTGRES_URL` or `DATABASE_URL` | Enable only with `ENABLE_DATABASE_WRITES=true`. |
| Queue/cache | `REDIS_URL` or Upstash variables | For scheduled scans and jobs. |
| Object storage | S3 or R2 variables | For transcripts, PDFs, images, archives, and evidence packs. |
| Google Sheets | `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEET_ID` | Enable only with `ENABLE_GOOGLE_SHEETS_WRITES=true`. |

## Alerts And Approval Bridges

Keep disabled until the channels are confirmed:

| Channel | Variables |
|---|---|
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Slack | `SLACK_WEBHOOK_URL` |
| Discord | `DISCORD_WEBHOOK_URL` |
| Email | `EMAIL_SMTP_*` |
| n8n/Make/Zapier | `N8N_WEBHOOK_BASE_URL`, `N8N_WEBHOOK_SECRET`, `MAKE_WEBHOOK_URL`, `ZAPIER_WEBHOOK_URL` |

## Exchange And Broker Keys

These are intentionally present but disabled by default. Do not enable live trading from this service without separate owner approval and risk controls:

```text
EXCHANGE_PROVIDER=none
LIVE_TRADING_ENABLED=false
TRADING_MODE=paper
APPROVAL_REQUIRED=true
```

Only paper endpoints should be used by default, such as `ALPACA_BASE_URL=https://paper-api.alpaca.markets`.

## Railway Fill Order

Fill Railway variables in this order to avoid wasting deploys:

1. Required runtime and MCP auth.
2. `BASE_URL` after Railway public domain exists.
3. Free/public source URLs from `.env.example`.
4. Safety gates and feature flags.
5. Optional free-key providers.
6. Paid providers only after approval.
7. Persistence/alerts only after the route they support exists.

## Verification

After variables are set, verify:

```text
GET /health
GET /ready
GET /deployment/status
GET /mcp/tools
POST /mcp with extract_metadata and bearer auth
```

Do not claim provider-backed transcription, OCR, market scans, on-chain scans, social monitoring, database writes, or live alerts until the matching provider variable is set, feature gate is enabled, and a route-level smoke test passes.
