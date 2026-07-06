const baseUrl = process.env.XRP_HBAR_APEX_URL || process.env.RAILWAY_PUBLIC_DOMAIN || process.env.RAILWAY_STATIC_URL || "";

if (!baseUrl) {
  console.error(JSON.stringify({
    ok: false,
    classification: "blocked_external_manual",
    blocker: "No live URL supplied. Set XRP_HBAR_APEX_URL, RAILWAY_PUBLIC_DOMAIN, or RAILWAY_STATIC_URL after Railway creates the service domain."
  }, null, 2));
  process.exit(1);
}

const normalizedBaseUrl = baseUrl.startsWith("http") ? baseUrl.replace(/\/$/, "") : `https://${baseUrl.replace(/\/$/, "")}`;

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

const checks = [
  await readJson("/health"),
  await readJson("/ready"),
  await readJson("/deployment/status"),
  await readJson("/mcp/tools"),
  await readJson("/mcp", { method: "POST", body: "{}" })
];

const expected = {
  "/health": 200,
  "/ready": 200,
  "/deployment/status": 200,
  "/mcp/tools": 200,
  "/mcp": 501
};

const failures = checks.filter((check) => check.status !== expected[check.path]);
const summary = {
  ok: failures.length === 0,
  classification: failures.length === 0 ? "confirmed_live" : "partially_configured",
  baseUrl: normalizedBaseUrl,
  checks,
  failures
};

console.log(JSON.stringify(summary, null, 2));

if (failures.length > 0) {
  process.exit(1);
}
