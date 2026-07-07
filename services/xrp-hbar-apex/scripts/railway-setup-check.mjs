const expected = {
  serviceRoot: "services/xrp-hbar-apex",
  branch: "main",
  appEnv: "production",
  logLevel: "info",
  healthPath: "/health",
  readyPath: "/ready",
  deploymentStatusPath: "/deployment/status",
  mcpToolsPath: "/mcp/tools",
  mcpPath: "/mcp"
};

function hasValue(value) {
  return typeof value === "string" && value.trim().length > 0;
}

const observed = {
  APP_ENV: process.env.APP_ENV || "",
  BASE_URL: process.env.BASE_URL || process.env.RAILWAY_PUBLIC_DOMAIN || process.env.RAILWAY_STATIC_URL || "",
  LOG_LEVEL: process.env.LOG_LEVEL || "",
  PORT: process.env.PORT || ""
};

const mismatches = [];

if (hasValue(observed.APP_ENV) && observed.APP_ENV !== expected.appEnv) {
  mismatches.push({ name: "APP_ENV", expected: expected.appEnv, actual: observed.APP_ENV });
}

if (hasValue(observed.LOG_LEVEL) && observed.LOG_LEVEL !== expected.logLevel) {
  mismatches.push({ name: "LOG_LEVEL", expected: expected.logLevel, actual: observed.LOG_LEVEL });
}

if (hasValue(observed.PORT)) {
  const parsedPort = Number.parseInt(observed.PORT, 10);
  if (!Number.isFinite(parsedPort) || parsedPort <= 0) {
    mismatches.push({ name: "PORT", expected: "positive integer", actual: observed.PORT });
  }
}

const summary = {
  ok: mismatches.length === 0,
  module: "xrp-hbar-apex",
  classification: "repo-side setup check",
  sharedMonorepoSafety: "Deploy as a separate Railway service from services/xrp-hbar-apex. Do not deploy from the monorepo root or reuse another module's service/env/runtime.",
  expectedRailway: expected,
  safeMinimumVars: {
    APP_ENV: expected.appEnv,
    BASE_URL: "https://jarvis-build-production.up.railway.app",
    LOG_LEVEL: expected.logLevel
  },
  requiredSecretsForCurrentShell: [],
  observedVars: Object.fromEntries(Object.entries(observed).map(([key, value]) => [key, hasValue(value) ? "set" : "not_set"])),
  mismatches
};

console.log(JSON.stringify(summary, null, 2));

if (mismatches.length > 0) {
  process.exitCode = 1;
}
