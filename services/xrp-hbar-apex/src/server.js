import http from "node:http";
import { authenticateRequest } from "./auth.js";
import { getCapabilityStatus, getConfig } from "./config.js";
import {
  JsonFileFederationStateStore,
  createFederationPoller,
  federationTargetsFromConfig
} from "./federation/poller.js";
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

function federationConfiguration(runtimeConfig) {
  return {
    hub: Boolean(runtimeConfig.federation?.hubBaseUrl),
    vti: Boolean(runtimeConfig.federation?.vtiBaseUrl),
    timeout_ms: runtimeConfig.federation?.timeoutMs,
    max_attempts: runtimeConfig.federation?.maxAttempts,
    backoff_ms: runtimeConfig.federation?.backoffMs
  };
}

export function createServer(runtimeConfig = config, dependencies = {}) {
  const federationStore =
    dependencies.federationStore ?? new JsonFileFederationStateStore(runtimeConfig.federation.stateFile);
  const federationPoller =
    dependencies.federationPoller ??
    createFederationPoller({
      fetchImpl: dependencies.fetchImpl ?? globalThis.fetch,
      store: federationStore,
      timeoutMs: runtimeConfig.federation.timeoutMs,
      maxAttempts: runtimeConfig.federation.maxAttempts,
      backoffMs: runtimeConfig.federation.backoffMs
    });

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
          authMode: runtimeConfig.auth.mode,
          federationPollingImplemented: true,
          federationTargetsConfigured: federationConfiguration(runtimeConfig)
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
        federation: federationConfiguration(runtimeConfig),
        implementedNow: [
          "GET /health",
          "GET /ready",
          "GET /deployment/status",
          "GET /xrp-hbar-apex/health",
          "GET /xrp-hbar-apex/ready",
          "GET /xrp-hbar-apex/deployment/status",
          "GET /federation/status",
          "POST /federation/poll",
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
          "provider-backed external integrations",
          "archive ingestion",
          "live Hub/VTI federation proof until endpoints are configured and reachable"
        ],
        truthBoundary:
          "This service can authenticate and dispatch MCP calls and can perform authenticated read-only polling of configured Jarvis health and capability contracts with bounded retries, idempotency records, and dead-letter classification. It does not prove that external endpoints are configured, reachable, fresh, or production-verified."
      });
    }

    if (req.method === "GET" && path === "/federation/status") {
      try {
        const state = await federationStore.load();
        return sendJson(res, 200, {
          ok: true,
          status: "implemented",
          configuration: federationConfiguration(runtimeConfig),
          services: state.services ?? {},
          dead_letter_count: Array.isArray(state.dead_letters) ? state.dead_letters.length : 0,
          truth_boundary:
            "Stored results are read-only observations. DONE_VERIFIED applies only to the two contract responses captured in that observation, not to the complete external service or deployment."
        });
      } catch {
        return sendJson(res, 500, {
          ok: false,
          error: { code: "FEDERATION_STATE_READ_FAILED", message: "Federation state could not be read." }
        });
      }
    }

    if (req.method === "POST" && path === "/federation/poll") {
      const auth = authenticateRequest(req, runtimeConfig);
      if (!auth.ok) {
        return sendJson(res, auth.statusCode, { ok: false, error: auth.error });
      }
      try {
        const result = await federationPoller.pollAll(federationTargetsFromConfig(runtimeConfig));
        return sendJson(res, result.integration_status === "INTEGRATED_STAGING" ? 200 : 503, {
          ok: result.integration_status === "INTEGRATED_STAGING",
          ...result
        });
      } catch {
        return sendJson(res, 500, {
          ok: false,
          error: { code: "FEDERATION_POLL_FAILED", message: "Federation polling failed safely." }
        });
      }
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
        status: "mcp_metadata_first_with_federation_polling",
        endpoints: [
          "/health",
          "/ready",
          "/deployment/status",
          "/xrp-hbar-apex/health",
          "/xrp-hbar-apex/ready",
          "/xrp-hbar-apex/deployment/status",
          "/federation/status",
          "/federation/poll",
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
