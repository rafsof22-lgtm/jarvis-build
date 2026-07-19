import { createHash } from "node:crypto";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import path from "node:path";

const CONTRACT_PATHS = Object.freeze([
  "/.well-known/jarvis/health",
  "/.well-known/jarvis/capabilities"
]);
const SECRET_FIELD_PATTERN = /(api[_-]?key|secret|password|private[_-]?key|refresh[_-]?token|access[_-]?token|authorization|cookie)/i;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function hashText(value) {
  return createHash("sha256").update(value).digest("hex");
}

function isoNow(now) {
  return new Date(now()).toISOString();
}

function parsePositiveInteger(value, fallback) {
  const parsed = Number.parseInt(String(value ?? ""), 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function safeSummary(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return {};
  const summary = {};
  const allowed = [
    "ok",
    "status",
    "service",
    "service_id",
    "schema_version",
    "contract_version",
    "version",
    "observed_at",
    "updated_at"
  ];
  for (const key of allowed) {
    if (Object.hasOwn(payload, key) && !SECRET_FIELD_PATTERN.test(key)) {
      const value = payload[key];
      if (["string", "number", "boolean"].includes(typeof value) || value === null) summary[key] = value;
    }
  }
  if (Array.isArray(payload.capabilities)) {
    summary.capabilities = payload.capabilities
      .filter((value) => typeof value === "string")
      .slice(0, 100);
  } else if (payload.capabilities && typeof payload.capabilities === "object") {
    summary.capabilities = Object.keys(payload.capabilities)
      .filter((key) => !SECRET_FIELD_PATTERN.test(key))
      .slice(0, 100)
      .sort();
  }
  return summary;
}

function validateBaseUrl(rawUrl) {
  if (typeof rawUrl !== "string" || !rawUrl.trim()) {
    return { ok: false, code: "BASE_URL_NOT_CONFIGURED" };
  }
  let parsed;
  try {
    parsed = new URL(rawUrl);
  } catch {
    return { ok: false, code: "INVALID_BASE_URL" };
  }
  if (!new Set(["http:", "https:"]).has(parsed.protocol)) {
    return { ok: false, code: "UNSUPPORTED_URL_SCHEME" };
  }
  if (parsed.username || parsed.password) {
    return { ok: false, code: "URL_CREDENTIALS_FORBIDDEN" };
  }
  parsed.hash = "";
  parsed.search = "";
  parsed.pathname = parsed.pathname.replace(/\/$/, "");
  return { ok: true, baseUrl: parsed.toString().replace(/\/$/, "") };
}

export class JsonFileFederationStateStore {
  constructor(filePath) {
    this.filePath = filePath;
  }

  async load() {
    try {
      return JSON.parse(await readFile(this.filePath, "utf8"));
    } catch (error) {
      if (error?.code === "ENOENT") {
        return { schema_version: "1.0.0", services: {}, seen_idempotency_keys: {}, dead_letters: [] };
      }
      throw error;
    }
  }

  async save(state) {
    await mkdir(path.dirname(this.filePath), { recursive: true });
    const tempPath = `${this.filePath}.${process.pid}.${Date.now()}.tmp`;
    await writeFile(tempPath, `${JSON.stringify(state, null, 2)}\n`, { encoding: "utf8", mode: 0o600 });
    await rename(tempPath, this.filePath);
  }

  async record(result) {
    const state = await this.load();
    const duplicate = Boolean(state.seen_idempotency_keys[result.idempotency_key]);
    state.seen_idempotency_keys[result.idempotency_key] = result.observed_at;
    state.services[result.service_id] = result;
    if (result.dead_letter) {
      const exists = state.dead_letters.some((row) => row.idempotency_key === result.idempotency_key);
      if (!exists) state.dead_letters.push(result);
    }
    await this.save(state);
    return { duplicate, state };
  }
}

async function fetchJsonEndpoint({ fetchImpl, url, timeoutMs }) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetchImpl(url, {
      method: "GET",
      redirect: "manual",
      headers: { accept: "application/json" },
      signal: controller.signal
    });
    const rawBody = await response.text();
    if (!response.ok) {
      const error = new Error(`HTTP_${response.status}`);
      error.code = `HTTP_${response.status}`;
      error.response_hash = hashText(rawBody);
      throw error;
    }
    let payload;
    try {
      payload = JSON.parse(rawBody);
    } catch {
      const error = new Error("MALFORMED_JSON");
      error.code = "MALFORMED_JSON";
      error.response_hash = hashText(rawBody);
      throw error;
    }
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      const error = new Error("INVALID_JSON_OBJECT");
      error.code = "INVALID_JSON_OBJECT";
      throw error;
    }
    return {
      url,
      http_status: response.status,
      body_hash: hashText(rawBody),
      summary: safeSummary(payload)
    };
  } finally {
    clearTimeout(timeout);
  }
}

export function createFederationPoller(options = {}) {
  const fetchImpl = options.fetchImpl ?? globalThis.fetch;
  if (typeof fetchImpl !== "function") throw new TypeError("fetchImpl must be a function");
  const now = options.now ?? Date.now;
  const delay = options.delay ?? sleep;
  const timeoutMs = parsePositiveInteger(options.timeoutMs, 5_000);
  const maxAttempts = parsePositiveInteger(options.maxAttempts, 3);
  const backoffMs = parsePositiveInteger(options.backoffMs, 100);
  const store = options.store ?? null;

  async function pollService(target) {
    const observedAt = isoNow(now);
    const serviceId = String(target?.serviceId || "").trim();
    if (!serviceId) throw new TypeError("serviceId is required");

    const validated = validateBaseUrl(target?.baseUrl);
    if (!validated.ok) {
      const result = {
        schema_version: "1.0.0",
        service_id: serviceId,
        observed_at: observedAt,
        status: "BLOCKED",
        health_state: "unknown",
        retry_count: 0,
        attempts: 0,
        dead_letter: false,
        error_code: validated.code,
        endpoints: [],
        idempotency_key: hashText(`${serviceId}:${validated.code}`)
      };
      const recorded = store ? await store.record(result) : { duplicate: false };
      return { ...result, duplicate: recorded.duplicate };
    }

    const endpointResults = [];
    let finalError = null;
    let attempts = 0;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      attempts = attempt;
      endpointResults.length = 0;
      finalError = null;
      try {
        for (const contractPath of CONTRACT_PATHS) {
          endpointResults.push(
            await fetchJsonEndpoint({
              fetchImpl,
              url: `${validated.baseUrl}${contractPath}`,
              timeoutMs
            })
          );
        }
        break;
      } catch (error) {
        finalError = error;
        if (attempt < maxAttempts) await delay(backoffMs * 2 ** (attempt - 1));
      }
    }

    const succeeded = finalError === null && endpointResults.length === CONTRACT_PATHS.length;
    const bodyIdentity = endpointResults.map((row) => row.body_hash).join(":");
    const errorCode = succeeded ? null : finalError?.code || finalError?.name || "FETCH_FAILED";
    const result = {
      schema_version: "1.0.0",
      service_id: serviceId,
      observed_at: observedAt,
      status: succeeded ? "DONE_VERIFIED" : "BLOCKED",
      health_state: succeeded ? "healthy" : "unreachable",
      retry_count: Math.max(0, attempts - 1),
      attempts,
      dead_letter: !succeeded && attempts >= maxAttempts,
      error_code: errorCode,
      endpoints: endpointResults,
      idempotency_key: hashText(`${serviceId}:${succeeded ? bodyIdentity : errorCode}`)
    };
    const recorded = store ? await store.record(result) : { duplicate: false };
    return { ...result, duplicate: recorded.duplicate };
  }

  async function pollAll(targets = []) {
    const results = [];
    for (const target of targets) results.push(await pollService(target));
    const verified = results.filter((row) => row.status === "DONE_VERIFIED").length;
    const blocked = results.length - verified;
    return {
      schema_version: "1.0.0",
      observed_at: isoNow(now),
      integration_status: results.length > 0 && blocked === 0 ? "INTEGRATED_STAGING" : "BLOCKED",
      service_count: results.length,
      verified_services: verified,
      blocked_services: blocked,
      results
    };
  }

  return { pollService, pollAll };
}

export function federationTargetsFromConfig(runtimeConfig) {
  return [
    { serviceId: "xrp-hbar-hub-runtime", baseUrl: runtimeConfig?.federation?.hubBaseUrl || "" },
    { serviceId: "vti-evidence-service", baseUrl: runtimeConfig?.federation?.vtiBaseUrl || "" }
  ];
}
