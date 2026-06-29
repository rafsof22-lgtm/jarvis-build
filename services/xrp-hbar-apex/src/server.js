import http from "node:http";
import { getCapabilityStatus, getConfig } from "./config.js";

const config = getConfig();

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

export function createServer(runtimeConfig = config) {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");

    if (req.method === "GET" && url.pathname === "/health") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        status: "healthy"
      });
    }

    if (req.method === "GET" && url.pathname === "/ready") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        status: "ready",
        checks: {
          configLoaded: true,
          portConfigured: true,
          noRequiredSecretsForShell: true
        }
      });
    }

    if (req.method === "GET" && url.pathname === "/deployment/status") {
      return sendJson(res, 200, {
        ok: true,
        service: runtimeConfig.serviceName,
        version: runtimeConfig.version,
        appEnv: runtimeConfig.appEnv,
        capabilities: getCapabilityStatus(runtimeConfig),
        truthBoundary:
          "This service shell is running if this endpoint is reachable. Full XRP/HBAR intelligence execution, schedules, Memory, and external integrations are not proven by this endpoint."
      });
    }

    if (req.method === "GET" && url.pathname === "/mcp/tools") {
      return sendJson(res, 200, {
        ok: true,
        tools: [],
        status: "not_implemented",
        note: "No MCP tools are exposed until they are implemented and verified."
      });
    }

    if (req.method === "POST" && url.pathname === "/mcp") {
      await readBody(req).catch(() => "");
      return sendJson(res, 501, {
        ok: false,
        error: "not_implemented",
        note: "MCP handling is intentionally disabled in the starter shell."
      });
    }

    if (req.method === "GET" && url.pathname === "/") {
      return sendJson(res, 200, {
        service: runtimeConfig.serviceName,
        status: "starter_shell",
        endpoints: ["/health", "/ready", "/deployment/status", "/mcp/tools"],
        railwayRootDirectory: "services/xrp-hbar-apex"
      });
    }

    return sendJson(res, 404, {
      ok: false,
      error: "not_found"
    });
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const server = createServer(config);
  server.listen(config.port, () => {
    console.log(`${config.serviceName} listening on port ${config.port}`);
  });
}
