const expected = {
  serviceRoot: "services/xrp-hbar-apex",
  branch: "main",
  appEnv: "production",
  logLevel: "info",
  healthPath: "/health",
  readyPath: "/ready",
  deploymentStatusPath: "/deployment/status",
  mcpToolsPath: "/mcp/tools",
  mcpPath: "/mcp",
  authMode: "bearer"
};

function hasValue(value) {
  return typeof value === "string" && value.trim().length > 0;
}

const observed = {
  APP_ENV: process.env.APP_ENV || "",
  BASE_URL: process.env.BASE_URL || process.env.RAILWAY_PUBLIC_DOMAIN || process.env.RAILWAY_STATIC_URL || "",
  LOG_LEVEL: process.env.LOG_LEVEL || "",
  PORT: process.env.PORT || "",
  MCP_AUTH_MODE: process.env.MCP_AUTH_MODE || "",
  MCP_BEARER_TOKEN: process.env.MCP_BEARER_TOKEN || "",
  MCP_API_KEY: process.env.MCP_API_KEY || ""
};

const mismatches = [];
const missing = [];

if (!hasValue(observed.APP_ENV)) missing.push("APP_ENV");
if (!hasValue(observed.BASE_URL)) missing.push("BASE_URL or Railway public domain variable");
if (!hasValue(observed.MCP_AUTH_MODE)) missing.push("MCP_AUTH_MODE");
if ((observed.MCP_AUTH_MODE || "").toLowerCase() === "bearer" && !hasValue(observed.MCP_BEARER_TOKEN)) {
  missing.push("MCP_BEARER_TOKEN");
}

if (hasValue(observed.APP_ENV) && observed.APP_ENV !== expected.appEnv) {
  mismatches.push({ name: "APP_ENV", expected: expected.appEnv, actual: observed.APP_ENV });
}

if (hasValue(observed.LOG_LEVEL) && observed.LOG_LEVEL !== expected.logLevel) {
  mismatches.push({ name: "LOG_LEVEL", expected: expected.logLevel, actual: observed.LOG_LEVEL });
}

if (hasValue(observed.MCP_AUTH_MODE) && observed.MCP_AUTH_MODE.toLowerCase() !== expected.authMode) {
  mismatches.push({ name: "MCP_AUTH_MODE", expected: expected.authMode, actual: observed.MCP_AUTH_MODE });
}

if (hasValue(observed.PORT)) {
  const parsedPort = Number.parseInt(observed.PORT, 10);
  if (!Number.isFinite(parsedPort) || parsedPort <= 0) {
    mismatches.push({ name: "PORT", expected: "positive integer", actual: observed.PORT });
  }
}

const summary = {
  ok: mismatches.length === 0 && missing.length === 0,
  module: "xrp-hbar-apex",
  classification: "repo-side setup check",
  sharedMonorepoSafety: "Deploy as a separate Railway service from services/xrp-hbar-apex. Do not deploy from the monorepo root or reuse Bill-CFO's service/env/runtime.",
  expectedRailway: expected,
  safeMinimumVars: {
    APP_ENV: expected.appEnv,
    BASE_URL: "https://your-xrp-hbar-apex-service.up.railway.app",
    LOG_LEVEL: expected.logLevel,
    MCP_AUTH_MODE: expected.authMode,
    MCP_BEARER_TOKEN: "set as a Railway secret only"
  },
  requiredSecretsForCurrentMcp: ["MCP_BEARER_TOKEN"],
  observedVars: Object.fromEntries(Object.entries(observed).map(([key, value]) => [key, hasValue(value) ? "set" : "not_set"])),
  missing,
  mismatches
};

console.log(JSON.stringify(summary, null, 2));

if (!summary.ok) {
  process.exitCode = 1;
}
