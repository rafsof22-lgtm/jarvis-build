import http from "node:http";
import { authenticateRequest } from "./auth.js";
import { getCapabilityStatus, getConfig } from "./config.js";
import { dispatchMcpRequest } from "./mcp/dispatcher.js";
import { publicTools } from "./mcp/tools.js";

const config = getConfig();
const ROUTE_NAMESPACE = "/xrp-hbar-apex";

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload, null, 2);
  res.writeHead(statusCode, {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store"
  });
  res.end(body);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.setEncoding("utf8");
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > 1_000_000) {
        reject(new Error("Request body too large"));
        req.destroy();
      }
    });
    req.on("end", () => resolve(body));
    req.on("error", reject);
  });
}

function normalizePath(pathname) {
  if (pathname === ROUTE_NAMESPACE) return "/";
  if (pathname.startsWith(`${ROUTE_NAMESPACE}/`)) return pathname.slice(ROUTE_NAMESPACE.length) || "/";
  return pathname;
}

function parseJsonBody(rawBody) {
  if (!rawBody.trim()) return {};
  return JSON.parse(rawBody);
}

export function createServer(runtimeConfig = config) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const path = normalizePath(url.pathname);
    const capabilities = getCapabilityStatus(runtimeConfig);

    if (req.method === "GET" && path === "/health") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        status: "healthy",
        routeNamespace: ROUTE_NAMESPACE
      });
    }

    if (req.method === "GET" && path === "/ready") {
      const ready = runtimeConfig.requiredConfig.ready;
      return sendJson(res, ready ? 200 : 503, {
        ok: ready,
        service: runtimeConfig.serviceName,
        status: ready ? "ready" : "not_ready",
        routeNamespace: ROUTE_NAMESPACE,
        checks: {
          configLoaded: true,
          portConfigured: true,
          requiredEnv: runtimeConfig.requiredConfig.required,
          missingRequiredEnv: runtimeConfig.requiredConfig.missing,
          mcpPostImplemented: true,
          toolsExposed: publicTools().length > 0,
          authMode: runtimeConfig.auth.mode
        },
        note: runtimeConfig.requiredConfig.note
      });
    }

    if (req.method === "GET" && path === "/deployment/status") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        version: runtimeConfig.version,
        appEnv: runtimeConfig.appEnv,
        baseUrlConfigured: Boolean(runtimeConfig.baseUrl),
        railwayRootDirectory: "services/xrp-hbar-apex",
        deployBranch: "main",
        routeNamespace: ROUTE_NAMESPACE,
        envNamespacePrefix: "XRP_HBAR_APEX_",
        queueJobPrefix: "xrp_hbar_apex_",
        databasePrefix: "xrp_hbar_apex_",
        webhookPrefix: "xrp-hbar-apex-",
        capabilities,
        implementedNow: [
          "GET /health",
          "GET /ready",
          "GET /deployment/status",
          "GET /xrp-hbar-apex/health",
          "GET /xrp-hbar-apex/ready",
          "GET /xrp-hbar-apex/deployment/status",
          "GET /",
          "GET /mcp",
          "GET /mcp/tools",
          "POST /mcp"
        ],
        mcp: {
          implemented: true,
          endpoint: "/mcp",
          authMode: runtimeConfig.auth.mode,
          tools: publicTools().map((tool) => tool.name)
        },
        notImplementedYet: [
          "provider-backed URL transcription",
          "provider-backed file transcription",
          "provider-backed OCR extraction",
          "full XRP/HBAR tracker execution inside this service",
          "scheduled workers",
          "ChatGPT Memory access from this service",
          "external integrations",
          "archive ingestion"
        ],
        truthBoundary:
          "This service can now authenticate and dispatch MCP tool calls. Metadata-only and supplied-transcript tools are live; provider-backed transcription, OCR, full tracker execution, schedules, Memory, and external integrations are not proven by this endpoint."
      });
    }

    if (req.method === "GET" && path === "/mcp/tools") {
      return sendJson(res, 200, {
        ok: true,
        status: "implemented",
        tools: publicTools()
      });
    }

    if (req.method === "GET" && path === "/mcp") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        endpoint: "/mcp",
        method: "POST",
        tools: publicTools().map((tool) => tool.name),
        request_shape: {
          tool: "extract_metadata",
          input: { url: "https://example.com/video" }
        }
      });
    }

    if (req.method === "POST" && path === "/mcp") {
      const auth = authenticateRequest(req, runtimeConfig);
      if (!auth.ok) {
        return sendJson(res, auth.statusCode, { ok: false, error: auth.error });
      }

      let body;
      try {
        body = parseJsonBody(await readBody(req));
      } catch {
        return sendJson(res, 400, {
          ok: false,
          error: { code: "MALFORMED_JSON", message: "Request body must be valid JSON." }
        });
      }

      try {
        const result = await dispatchMcpRequest(body);
        return sendJson(res, result.statusCode, result.payload);
      } catch {
        return sendJson(res, 500, {
          ok: false,
          error: { code: "INTERNAL_ERROR", message: "MCP request failed during dispatch." }
        });
      }
    }

    if (req.method === "GET" && path === "/") {
      return sendJson(res, 200, {
        service: runtimeConfig.serviceName,
        status: "mcp_metadata_first",
        endpoints: [
          "/health",
          "/ready",
          "/deployment/status",
          "/xrp-hbar-apex/health",
          "/xrp-hbar-apex/ready",
          "/xrp-hbar-apex/deployment/status",
          "/mcp",
          "/mcp/tools"
        ],
        railwayRootDirectory: "services/xrp-hbar-apex",
        routeNamespace: ROUTE_NAMESPACE
      });
    }

    return sendJson(res, 404, { ok: false, error: "not_found" });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const server = createServer(config);
  server.listen(config.port, () => {
    console.log(`${config.serviceName} listening on port ${config.port}`);
  });
}
