const baseUrl = process.env.XRP_HBAR_APEX_URL || process.env.BASE_URL || process.env.RAILWAY_PUBLIC_DOMAIN || process.env.RAILWAY_STATIC_URL || "";
const authMode = (process.env.MCP_AUTH_MODE || "none").trim().toLowerCase();
const bearerToken = process.env.MCP_BEARER_TOKEN || "";
const apiKey = process.env.MCP_API_KEY || "";

if (!baseUrl) {
  console.error(JSON.stringify({
    ok: false,
    classification: "blocked_external_manual",
    blocker: "No live URL supplied. Set XRP_HBAR_APEX_URL, BASE_URL, RAILWAY_PUBLIC_DOMAIN, or RAILWAY_STATIC_URL after Railway creates the service domain."
  }, null, 2));
  process.exit(1);
}

const normalizedBaseUrl = baseUrl.startsWith("http") ? baseUrl.replace(/\/$/, "") : `https://${baseUrl.replace(/\/$/, "")}`;

function mcpAuthHeaders() {
  if (authMode === "bearer") {
    if (!bearerToken) {
      throw new Error("MCP_BEARER_TOKEN is required when MCP_AUTH_MODE=bearer");
    }
    return { authorization: `Bearer ${bearerToken}` };
  }

  if (authMode === "api_key") {
    if (!apiKey) {
      throw new Error("MCP_API_KEY is required when MCP_AUTH_MODE=api_key");
    }
    return { "x-api-key": apiKey };
  }

  return {};
}

async function readJson(path, options = {}) {
  const response = await fetch(`${normalizedBaseUrl}${path}`, options);
  const text = await response.text();
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    body = { raw: text };
  }
  return { path, status: response.status, body };
}

let authHeaders;
try {
  authHeaders = mcpAuthHeaders();
} catch (error) {
  console.error(JSON.stringify({
    ok: false,
    classification: "missing_env_var",
    blocker: error.message
  }, null, 2));
  process.exit(1);
}

const checks = [
  await readJson("/health"),
  await readJson("/ready"),
  await readJson("/deployment/status"),
  await readJson("/xrp-hbar-apex/health"),
  await readJson("/mcp"),
  await readJson("/mcp/tools"),
  await readJson("/mcp", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...authHeaders
    },
    body: JSON.stringify({
      tool: "extract_metadata",
      input: {
        url: "https://ripple.com/insights/the-xrpl-lending-protocol-bringing-credit-infrastructure-onchain/",
        platform_hint: "web"
      }
    })
  })
];

const expected = {
  "/health": 200,
  "/ready": 200,
  "/deployment/status": 200,
  "/xrp-hbar-apex/health": 200,
  "/mcp": 200,
  "/mcp/tools": 200
};

const failures = checks.filter((check) => check.status !== expected[check.path]);
const postMcp = checks[checks.length - 1];
if (!postMcp.body?.ok || postMcp.body?.tool !== "extract_metadata") {
  failures.push({
    path: "POST /mcp extract_metadata",
    status: postMcp.status,
    body: postMcp.body,
    expected: "HTTP 200 with ok:true and tool:extract_metadata"
  });
}

const summary = {
  ok: failures.length === 0,
  classification: failures.length === 0 ? "confirmed_live_mcp" : "partially_configured",
  baseUrl: normalizedBaseUrl,
  authMode,
  checks,
  failures
};

console.log(JSON.stringify(summary, null, 2));

if (failures.length > 0) {
  process.exit(1);
}
