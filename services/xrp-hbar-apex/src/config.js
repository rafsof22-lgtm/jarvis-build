export function getConfig(env = process.env) {
  const port = Number.parseInt(env.PORT ?? "3000", 10);

  return {
    serviceName: "xrp-hbar-apex",
    version: "0.1.0",
    appEnv: env.APP_ENV || "development",
    logLevel: env.LOG_LEVEL || "info",
    port: Number.isFinite(port) && port > 0 ? port : 3000,
    optionalIntegrations: {
      openai: Boolean(env.OPENAI_API_KEY),
      postgres: Boolean(env.POSTGRES_URL),
      googleSheets: Boolean(env.GOOGLE_SERVICE_ACCOUNT_JSON && env.GOOGLE_SHEET_ID),
      github: Boolean(env.GITHUB_TOKEN),
      n8n: Boolean(env.N8N_WEBHOOK_BASE_URL && env.N8N_WEBHOOK_SECRET)
    }
  };
}

export function getCapabilityStatus(config) {
  return {
    health: "implemented",
    readiness: "implemented",
    mcp: "not_implemented",
    trackerExecution: "not_implemented",
    scheduledWorkers: "not_implemented",
    memoryAccess: "external_chatgpt_only",
    integrations: config.optionalIntegrations
  };
}
