const REQUIRED_ENV = ["APP_ENV", "BASE_URL"];
const AUTH_MODES = new Set(["bearer", "api_key", "none"]);

function hasValue(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function normalizeAuthMode(value) {
  const normalized = String(value || "bearer").trim().toLowerCase();
  return AUTH_MODES.has(normalized) ? normalized : "bearer";
}

export function getRequiredConfigStatus(env = process.env) {
  const missing = REQUIRED_ENV.filter((name) => !hasValue(env[name]));
  const authMode = normalizeAuthMode(env.MCP_AUTH_MODE);

  if (authMode === "bearer" && !hasValue(env.MCP_BEARER_TOKEN)) {
    missing.push("MCP_BEARER_TOKEN");
  }

  if (authMode === "api_key" && !hasValue(env.MCP_API_KEY)) {
    missing.push("MCP_API_KEY");
  }

  return {
    required: REQUIRED_ENV,
    authMode,
    missing,
    ready: missing.length === 0,
    note:
      "Ready means the minimum MCP HTTP boundary can accept authenticated tool calls. Provider-backed transcription/OCR may still return structured limitation responses until provider credentials are added."
  };
}

export function getConfig(env = process.env) {
  const port = Number.parseInt(env.PORT ?? "3000", 10);
  const authMode = normalizeAuthMode(env.MCP_AUTH_MODE);
  const requiredConfig = getRequiredConfigStatus(env);

  return {
    serviceName: "xrp-hbar-apex",
    version: "0.2.0",
    appEnv: env.APP_ENV || "development",
    baseUrl: env.BASE_URL || "",
    logLevel: env.LOG_LEVEL || "info",
    port: Number.isFinite(port) && port > 0 ? port : 3000,
    auth: {
      mode: authMode,
      enabled: authMode !== "none",
      bearerToken: env.MCP_BEARER_TOKEN || "",
      apiKey: env.MCP_API_KEY || ""
    },
    requiredConfig,
    optionalIntegrations: {
      openai: hasValue(env.OPENAI_API_KEY),
      transcriptProvider: hasValue(env.TRANSCRIPT_PROVIDER_API_KEY),
      ocrProvider: hasValue(env.OCR_PROVIDER_API_KEY),
      postgres: hasValue(env.POSTGRES_URL),
      googleSheets: hasValue(env.GOOGLE_SERVICE_ACCOUNT_JSON) && hasValue(env.GOOGLE_SHEET_ID),
      github: hasValue(env.GITHUB_TOKEN),
      n8n: hasValue(env.N8N_WEBHOOK_BASE_URL) && hasValue(env.N8N_WEBHOOK_SECRET)
    }
  };
}

export function getCapabilityStatus(config) {
  return {
    health: "implemented",
    readiness: config.requiredConfig.ready ? "implemented_ready" : "implemented_not_ready",
    deploymentStatus: "implemented",
    mcpTools: "implemented",
    mcp: "implemented",
    auth: config.auth.enabled ? `enabled_${config.auth.mode}` : "disabled",
    trackerExecution: "external_chatgpt_agent_only",
    scheduledWorkers: "not_implemented",
    memoryAccess: "external_chatgpt_only",
    integrations: config.optionalIntegrations
  };
}
