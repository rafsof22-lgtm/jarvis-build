# XRP/HBAR Apex Railway Variable Manifest

Last updated: 2026-07-07

## Purpose

Use this as the Railway Variables tab checklist for the dedicated XRP/HBAR Apex service.

Repository: `rafsof22-lgtm/jarvis-build`
Branch: `main`
Root directory: `services/xrp-hbar-apex`
Service name target: `xrp-hbar-intelligence`

Never commit real secrets. Never paste secret values into chat.

## Required now for service readiness

Set these before redeploying:

```text
APP_ENV=production
BASE_URL=<public XRP/HBAR Railway URL>
LOG_LEVEL=info
MCP_AUTH_MODE=bearer
MCP_BEARER_TOKEN=<Railway secret only>
```

`PORT` is injected by Railway. Do not force it unless Railway support asks for it.

## Recommended safe defaults

These keep the service read-only/paper-mode until source handlers and workers are explicitly wired and tested:

```text
READ_ONLY_MODE=true
TRADING_MODE=paper
LIVE_TRADING_ENABLED=false
APPROVAL_REQUIRED=true
ENABLE_SCHEDULED_SCANS=false
ENABLE_PROVIDER_TRANSCRIPTION=false
ENABLE_PROVIDER_OCR=false
ENABLE_PROVIDER_MARKET_DATA=false
ENABLE_PROVIDER_ONCHAIN_DATA=false
ENABLE_PROVIDER_SOCIAL_DATA=false
ENABLE_PROVIDER_NEWS_DATA=false
ENABLE_DATABASE_WRITES=false
ENABLE_GOOGLE_SHEETS_WRITES=false
ENABLE_GITHUB_WRITES=false
ENABLE_RAILWAY_MUTATIONS=false
```

## Free/public source defaults

These can be set without secrets and support future source routing:

```text
XRPL_RPC_URL=https://s1.ripple.com:51234
XRPL_RPC_FALLBACK_URL=https://xrplcluster.com
XRPL_WS_URL=wss://s1.ripple.com
XRPL_WS_FALLBACK_URL=wss://xrplcluster.com
XRPL_EXPLORER_BASE_URL=https://livenet.xrpl.org
XRPSCAN_BASE_URL=https://xrpscan.com
BITHOMP_BASE_URL=https://bithomp.com
XRPL_TO_BASE_URL=https://xrpl.to
XRPL_ORG_BASE_URL=https://xrpl.org
RIPPLE_BASE_URL=https://ripple.com
RIPPLE_INSIGHTS_RSS_URL=https://ripple.com/insights/feed/
HEDERA_MIRROR_NODE_URL=https://mainnet-public.mirrornode.hedera.com
HEDERA_HASHSCAN_BASE_URL=https://hashscan.io/mainnet
HEDERA_DOCS_BASE_URL=https://docs.hedera.com
HEDERA_BASE_URL=https://hedera.com
COINGECKO_API_BASE_URL=https://api.coingecko.com/api/v3
COINPAPRIKA_API_BASE_URL=https://api.coinpaprika.com/v1
DEFILLAMA_API_BASE_URL=https://api.llama.fi
DEFILLAMA_STABLECOINS_API_BASE_URL=https://stablecoins.llama.fi
YAHOO_FINANCE_BASE_URL=https://query1.finance.yahoo.com
GDELT_API_BASE_URL=https://api.gdeltproject.org/api/v2
NEWSAPI_BASE_URL=https://newsapi.org/v2
YOUTUBE_API_BASE_URL=https://www.googleapis.com/youtube/v3
X_API_BASE_URL=https://api.x.com/2
```

## Optional API keys to add only when available

### Crypto market and DeFi

```text
COINGECKO_API_KEY=
COINMARKETCAP_API_KEY=
CRYPTOCOMPARE_API_KEY=
COINGLASS_API_KEY=
MESSARI_API_KEY=
COINMETRICS_API_KEY=
GLASSNODE_API_KEY=
SANTIMENT_API_KEY=
CRYPTOQUANT_API_KEY=
TOKEN_TERMINAL_API_KEY=
DUNE_API_KEY=
NANSEN_API_KEY=
ARKHAM_API_KEY=
```

### News and search

```text
NEWSAPI_KEY=
BRAVE_SEARCH_API_KEY=
SERPAPI_API_KEY=
GOOGLE_CUSTOM_SEARCH_API_KEY=
GOOGLE_CUSTOM_SEARCH_CX=
CRYPTOPANIC_API_KEY=
COINDESK_API_KEY=
THE_TIE_API_KEY=
```

### Finance news and equities data

```text
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
FMP_API_KEY=
POLYGON_API_KEY=
MARKETAUX_API_KEY=
EODHD_API_KEY=
BENZINGA_API_KEY=
IEX_CLOUD_API_KEY=
TWELVE_DATA_API_KEY=
TIINGO_API_KEY=
```

### Social/video

```text
YOUTUBE_API_KEY=
X_BEARER_TOKEN=
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=xrp-hbar-apex
TELEGRAM_API_ID=
TELEGRAM_API_HASH=
DISCORD_BOT_TOKEN=
MASTODON_ACCESS_TOKEN=
BLUESKY_IDENTIFIER=
BLUESKY_APP_PASSWORD=
```

### Optional infrastructure

```text
OPENAI_API_KEY=
POSTGRES_URL=
REDIS_URL=
GOOGLE_SERVICE_ACCOUNT_JSON=
GOOGLE_SHEET_ID=
N8N_WEBHOOK_BASE_URL=
N8N_WEBHOOK_SECRET=
JOB_SIGNING_SECRET=
WEBHOOK_SIGNING_SECRET=
```

## Verification after redeploy

Run these against the live URL:

```bash
npm run live:verify
```

or manually verify:

```text
GET /ready
GET /deployment/status
GET /xrp-hbar-apex/health
GET /xrp-hbar-apex/ready
GET /xrp-hbar-apex/deployment/status
POST /mcp
```

`/deployment/status` should show optional integration flags for CoinGecko, NewsAPI, finance news, YouTube, social media, and free public sources.

## Blocker truth

This manifest is deployment-ready repo guidance. It does not set Railway variables by itself. Variable mutation still requires Railway UI, Railway CLI with a valid token, or a Railway connector/control surface.
