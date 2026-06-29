const CURRENT_SHELL_REQUIRED_ENV = [];

function hasValue(value) {
  return typeof value === "string" && value.trim().length > 0;
}

export function getRequiredConfigStatus(env = process.env) {
  const missing = CURRENT_SHELL_REQUIRED_ENV.filter((name) => !hasValue(env[name]));

  return {
    required: CURRENT_SHELL_REQUIRED_ENV,
    missing,
    ready: missing.length === 0,
    note: "The current starter shell has no required secrets. Future integrations must add required env checks before reporting ready."
  };
}

export function getConfig(env = process.env) {
  const port = Number.parseInt(env.PORT ?? "3000", 10);
  const requiredConfig = getRequiredConfigStatus(env);

  return {
    serviceName: "xrp-hbar-apex",
    version: "0.1.0",
    appEnv: env.APP_ENV || "development",
    logLevel: env.LOG_LEVEL || "info",
    port: Number.isFinite(port) && port > 0 ? port : 3000,
    requiredConfig,
    optionalIntegrations: {
      openai: hasValue(env.OPENAI_API_KEY),
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
    mcpTools: "implemented_empty_until_tools_exist",
    mcp: "not_implemented",
    trackerExecution: "not_implemented",
    scheduledWorkers: "not_implemented",
    memoryAccess: "external_chatgpt_only",
    integrations: config.optionalIntegrations
  };
}
