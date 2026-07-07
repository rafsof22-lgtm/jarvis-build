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

async function readJson(check) {
  const response = await fetch(`${normalizedBaseUrl}${check.path}`, check.options || {});
  const text = await response.text();
  let body;
  try {
    body = JSON.parse(text);
  } catch {
    body = { raw: text };
  }
  return { ...check, status: response.status, body };
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

const checkPlan = [
  { id: "GET /health", path: "/health", expectedStatus: 200 },
  { id: "GET /ready", path: "/ready", expectedStatus: 200 },
  { id: "GET /deployment/status", path: "/deployment/status", expectedStatus: 200 },
  { id: "GET /xrp-hbar-apex/health", path: "/xrp-hbar-apex/health", expectedStatus: 200 },
  { id: "GET /xrp-hbar-apex/ready", path: "/xrp-hbar-apex/ready", expectedStatus: 200 },
  { id: "GET /xrp-hbar-apex/deployment/status", path: "/xrp-hbar-apex/deployment/status", expectedStatus: 200 },
  { id: "GET /mcp", path: "/mcp", expectedStatus: 200 },
  { id: "GET /mcp/tools", path: "/mcp/tools", expectedStatus: 200 },
  {
    id: "POST /mcp extract_metadata",
    path: "/mcp",
    expectedStatus: 200,
    options: {
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
    }
  }
];

const checks = [];
for (const check of checkPlan) {
  checks.push(await readJson(check));
}

const failures = checks.filter((check) => check.status !== check.expectedStatus);
const postMcp = checks.find((check) => check.id === "POST /mcp extract_metadata");
if (!postMcp?.body?.ok || postMcp.body?.tool !== "extract_metadata") {
  failures.push({
    id: "POST /mcp extract_metadata",
    path: "/mcp",
    status: postMcp?.status,
    body: postMcp?.body,
    expected: "HTTP 200 with ok:true and tool:extract_metadata"
  });
}

const deploymentStatus = checks.find((check) => check.id === "GET /deployment/status")?.body || {};
if (deploymentStatus.railwayRootDirectory && deploymentStatus.railwayRootDirectory !== "services/xrp-hbar-apex") {
  failures.push({
    id: "GET /deployment/status",
    path: "/deployment/status",
    status: 200,
    body: deploymentStatus,
    expected: "railwayRootDirectory services/xrp-hbar-apex"
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
