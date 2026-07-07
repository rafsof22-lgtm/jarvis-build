const baseUrl = process.env.BILL_CFO_OCR_MCP_URL || process.env.BASE_URL || process.env.RAILWAY_PUBLIC_DOMAIN || process.env.RAILWAY_STATIC_URL || "";

if (!baseUrl) {
  console.error(JSON.stringify({
    ok: false,
    classification: "blocked_external_manual",
    blocker: "No live URL supplied. Set BILL_CFO_OCR_MCP_URL, BASE_URL, RAILWAY_PUBLIC_DOMAIN, or RAILWAY_STATIC_URL after Railway creates the service domain."
  }, null, 2));
  process.exit(1);
}

const normalizedBaseUrl = baseUrl.startsWith("http") ? baseUrl.replace(/\/$/, "") : `https://${baseUrl.replace(/\/$/, "")}`;

async function readJson(path) {
  const response = await fetch(`${normalizedBaseUrl}${path}`);
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
  await readJson("/bill-cfo-ocr-mcp/health"),
  await readJson("/bill-cfo-ocr-mcp/ready"),
  await readJson("/bill-cfo-ocr-mcp/deployment/status")
];

const expected = Object.fromEntries(checks.map((check) => [check.path, 200]));
const failures = checks.filter((check) => check.status !== expected[check.path]);
const statusBody = checks.find((check) => check.path === "/deployment/status")?.body || {};

if (statusBody.railwayRootDirectory && statusBody.railwayRootDirectory !== "services/bill-cfo-ocr-mcp") {
  failures.push({
    path: "/deployment/status",
    status: 200,
    body: statusBody,
    expected: "railwayRootDirectory services/bill-cfo-ocr-mcp"
  });
}

const summary = {
  ok: failures.length === 0,
  classification: failures.length === 0 ? "confirmed_live_shell" : "partially_configured",
  baseUrl: normalizedBaseUrl,
  checks,
  failures,
  proofBoundary: "This verifies only the Bill CFO service shell routes. OCR provider auth, workbook writes, queue jobs, and finance workflows require separate route-level smoke tests after implementation."
};

console.log(JSON.stringify(summary, null, 2));

if (failures.length > 0) {
  process.exit(1);
}
