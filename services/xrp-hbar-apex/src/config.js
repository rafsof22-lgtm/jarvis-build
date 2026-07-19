const AUTH_MODES = new Set(["bearer", "api_key", "none"]);

function hasValue(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function isEnabled(value) {
  return String(value || "").trim().toLowerCase() === "true";
}

function anyValue(env, names) {
  return names.some((name) => hasValue(env[name]));
}

function parsePositiveInteger(value, fallback) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function normalizeAuthMode(value) {
  const normalized = String(value || "none").trim().toLowerCase();
  return AUTH_MODES.has(normalized) ? normalized : "none";
}

function resolveBaseUrl(env) {
  if (hasValue(env.BASE_URL)) return env.BASE_URL;
  const railwayDomain = env.RAILWAY_PUBLIC_DOMAIN || env.RAILWAY_STATIC_URL || "";
  if (!hasValue(railwayDomain)) return "";
  return railwayDomain.startsWith("http") ? railwayDomain : `https://${railwayDomain}`;
}

export function getRequiredConfigStatus(env = process.env) {
  const baseUrl = resolveBaseUrl(env);
  const required = ["APP_ENV", "BASE_URL or Railway public domain"];
  const missing = [];
  const authMode = normalizeAuthMode(env.MCP_AUTH_MODE);

  if (!hasValue(env.APP_ENV)) missing.push("APP_ENV");
  if (!hasValue(baseUrl)) missing.push("BASE_URL or RAILWAY_PUBLIC_DOMAIN/RAILWAY_STATIC_URL");
  if (authMode === "bearer" && !hasValue(env.MCP_BEARER_TOKEN)) missing.push("MCP_BEARER_TOKEN");
  if (authMode === "api_key" && !hasValue(env.MCP_API_KEY)) missing.push("MCP_API_KEY");

  return {
    required,
    authMode,
    missing,
    ready: missing.length === 0,
    resolvedBaseUrl: baseUrl,
    note:
      "Ready means the HTTP runtime can serve health, readiness, deployment status, MCP discovery, authenticated MCP dispatch, and authenticated read-only federation polling. Provider-backed transcription, OCR, storage, market data, news, social, and full tracker execution remain limited unless separately configured."
  };
}

export function getConfig(env = process.env) {
  const port = Number.parseInt(env.PORT ?? "3000", 10);
  const authMode = normalizeAuthMode(env.MCP_AUTH_MODE);
  const requiredConfig = getRequiredConfigStatus(env);
  const transcriptionProviders = {
    openai: hasValue(env.OPENAI_API_KEY),
    deepgram: hasValue(env.DEEPGRAM_API_KEY),
    assemblyai: hasValue(env.ASSEMBLYAI_API_KEY),
    revai: hasValue(env.REVAI_API_KEY)
  };

  return {
    serviceName: "xrp-hbar-apex",
    version: "0.4.0",
    appEnv: env.APP_ENV || env.NODE_ENV || "development",
    baseUrl: requiredConfig.resolvedBaseUrl,
    logLevel: env.LOG_LEVEL || "info",
    port: Number.isFinite(port) && port > 0 ? port : 3000,
    auth: {
      mode: authMode,
      enabled: authMode !== "none",
      bearerToken: env.MCP_BEARER_TOKEN || "",
      apiKey: env.MCP_API_KEY || ""
    },
    federation: {
      hubBaseUrl: env.HUB_FEDERATION_BASE_URL || "",
      vtiBaseUrl: env.VTI_FEDERATION_BASE_URL || "",
      stateFile: env.FEDERATION_STATE_FILE || ".runtime/federation-state.json",
      timeoutMs: parsePositiveInteger(env.FEDERATION_TIMEOUT_MS, 5_000),
      maxAttempts: parsePositiveInteger(env.FEDERATION_MAX_ATTEMPTS, 3),
      backoffMs: parsePositiveInteger(env.FEDERATION_BACKOFF_MS, 100)
    },
    requiredConfig,
    optionalIntegrations: {
      openai: hasValue(env.OPENAI_API_KEY),
      transcriptProvider: hasValue(env.TRANSCRIPT_PROVIDER_API_KEY) || Object.values(transcriptionProviders).some(Boolean),
      ocrProvider: hasValue(env.OCR_PROVIDER_API_KEY),
      videoTranscription: {
        mode: env.VIDEO_TRANSCRIPTION_MODE || "metadata_first",
        captionFirst: isEnabled(env.ENABLE_CAPTION_EXTRACTION),
        localFfmpeg: isEnabled(env.ENABLE_LOCAL_FFMPEG_TRANSCRIPTION),
        ytDlp: isEnabled(env.ENABLE_YTDLP_EXTRACTION),
        frameOcr: isEnabled(env.ENABLE_VIDEO_FRAME_OCR),
        diarization: isEnabled(env.ENABLE_SPEAKER_DIARIZATION),
        providerFallback: isEnabled(env.ENABLE_PROVIDER_TRANSCRIPTION),
        providers: transcriptionProviders
      },
      postgres: hasValue(env.POSTGRES_URL),
      googleSheets: hasValue(env.GOOGLE_SERVICE_ACCOUNT_JSON) && hasValue(env.GOOGLE_SHEET_ID),
      github: hasValue(env.GITHUB_TOKEN),
      n8n: hasValue(env.N8N_WEBHOOK_BASE_URL) && hasValue(env.N8N_WEBHOOK_SECRET),
      coingecko: hasValue(env.COINGECKO_API_BASE_URL),
      coingeckoApiKey: hasValue(env.COINGECKO_API_KEY),
      newsApi: hasValue(env.NEWSAPI_KEY),
      cryptoNews: anyValue(env, ["CRYPTOPANIC_API_KEY", "COINDESK_API_KEY", "THE_TIE_API_KEY"]),
      financeNews: anyValue(env, [
        "ALPHA_VANTAGE_API_KEY",
        "FINNHUB_API_KEY",
        "FMP_API_KEY",
        "POLYGON_API_KEY",
        "MARKETAUX_API_KEY",
        "EODHD_API_KEY",
        "BENZINGA_API_KEY",
        "IEX_CLOUD_API_KEY",
        "TWELVE_DATA_API_KEY",
        "TIINGO_API_KEY"
      ]),
      youtube: hasValue(env.YOUTUBE_API_KEY),
      socialMedia: anyValue(env, [
        "X_BEARER_TOKEN",
        "REDDIT_CLIENT_ID",
        "TELEGRAM_API_ID",
        "DISCORD_BOT_TOKEN",
        "MASTODON_ACCESS_TOKEN",
        "BLUESKY_IDENTIFIER"
      ]),
      freePublicSources: anyValue(env, [
        "XRPL_RPC_URL",
        "HEDERA_MIRROR_NODE_URL",
        "DEFILLAMA_API_BASE_URL",
        "GDELT_API_BASE_URL",
        "YAHOO_FINANCE_BASE_URL"
      ])
    }
  };
}

export function getCapabilityStatus(config) {
  const federationConfigured = Boolean(config.federation?.hubBaseUrl && config.federation?.vtiBaseUrl);
  return {
    health: "implemented",
    readiness: config.requiredConfig.ready ? "implemented_ready" : "implemented_not_ready",
    deploymentStatus: "implemented",
    mcpTools: "implemented",
    mcp: "implemented_metadata_first",
    auth: config.auth.enabled ? `enabled_${config.auth.mode}` : "disabled",
    federationPolling: federationConfigured ? "implemented_configured" : "implemented_not_configured",
    trackerExecution: "external_chatgpt_agent_only",
    scheduledWorkers: "not_implemented",
    memoryAccess: "external_chatgpt_only",
    videoTranscription: config.optionalIntegrations.videoTranscription,
    integrations: config.optionalIntegrations
  };
}
