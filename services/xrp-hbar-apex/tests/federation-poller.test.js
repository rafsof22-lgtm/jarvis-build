import assert from "node:assert/strict";
import { mkdtemp, readFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import {
  JsonFileFederationStateStore,
  createFederationPoller,
  federationTargetsFromConfig
} from "../src/federation/poller.js";

function response(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
}

test("polls the two read-only Jarvis contract endpoints and records state", async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), "jarvis-poller-"));
  const statePath = path.join(dir, "state.json");
  const urls = [];
  const fetchImpl = async (url, options) => {
    urls.push([url, options.method]);
    if (url.endsWith("/health")) return response({ ok: true, service: "hub", status: "healthy", secret: "redact" });
    return response({ contract_version: "1.0.0", capabilities: ["health", "research"] });
  };
  const store = new JsonFileFederationStateStore(statePath);
  const poller = createFederationPoller({ fetchImpl, store, now: () => Date.parse("2026-07-19T12:00:00Z") });
  const result = await poller.pollService({ serviceId: "xrp-hbar-hub-runtime", baseUrl: "https://hub.example" });

  assert.equal(result.status, "DONE_VERIFIED");
  assert.equal(result.retry_count, 0);
  assert.equal(result.dead_letter, false);
  assert.equal(result.duplicate, false);
  assert.deepEqual(urls, [
    ["https://hub.example/.well-known/jarvis/health", "GET"],
    ["https://hub.example/.well-known/jarvis/capabilities", "GET"]
  ]);
  assert.equal(Object.hasOwn(result.endpoints[0].summary, "secret"), false);
  const saved = JSON.parse(await readFile(statePath, "utf8"));
  assert.equal(saved.services["xrp-hbar-hub-runtime"].status, "DONE_VERIFIED");
});

test("suppresses duplicate response identities through the idempotency ledger", async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), "jarvis-poller-"));
  const store = new JsonFileFederationStateStore(path.join(dir, "state.json"));
  const fetchImpl = async (url) =>
    response(url.endsWith("/health") ? { status: "healthy" } : { capabilities: ["health"] });
  const poller = createFederationPoller({ fetchImpl, store });
  const target = { serviceId: "vti-evidence-service", baseUrl: "https://vti.example" };

  assert.equal((await poller.pollService(target)).duplicate, false);
  assert.equal((await poller.pollService(target)).duplicate, true);
});

test("retries transient failures and succeeds within the bounded attempt budget", async () => {
  let calls = 0;
  const fetchImpl = async (url) => {
    calls += 1;
    if (calls === 1) throw Object.assign(new Error("network"), { code: "ECONNRESET" });
    return response(url.endsWith("/health") ? { status: "healthy" } : { capabilities: [] });
  };
  const poller = createFederationPoller({ fetchImpl, maxAttempts: 3, delay: async () => {} });
  const result = await poller.pollService({ serviceId: "xrp-hbar-hub-runtime", baseUrl: "https://hub.example" });

  assert.equal(result.status, "DONE_VERIFIED");
  assert.equal(result.retry_count, 1);
  assert.equal(result.attempts, 2);
});

test("dead-letters a service after the bounded retry budget is exhausted", async () => {
  const dir = await mkdtemp(path.join(os.tmpdir(), "jarvis-poller-"));
  const statePath = path.join(dir, "state.json");
  const store = new JsonFileFederationStateStore(statePath);
  const fetchImpl = async () => {
    throw Object.assign(new Error("offline"), { code: "ENETUNREACH" });
  };
  const poller = createFederationPoller({ fetchImpl, store, maxAttempts: 2, delay: async () => {} });
  const result = await poller.pollService({ serviceId: "xrp-hbar-hub-runtime", baseUrl: "https://hub.example" });

  assert.equal(result.status, "BLOCKED");
  assert.equal(result.attempts, 2);
  assert.equal(result.retry_count, 1);
  assert.equal(result.dead_letter, true);
  const saved = JSON.parse(await readFile(statePath, "utf8"));
  assert.equal(saved.dead_letters.length, 1);
  assert.equal(saved.dead_letters[0].error_code, "ENETUNREACH");
});

test("blocks embedded URL credentials without making a network request", async () => {
  let called = false;
  const poller = createFederationPoller({ fetchImpl: async () => { called = true; } });
  const result = await poller.pollService({ serviceId: "hub", baseUrl: "https://user:pass@example.com" });

  assert.equal(result.status, "BLOCKED");
  assert.equal(result.error_code, "URL_CREDENTIALS_FORBIDDEN");
  assert.equal(result.attempts, 0);
  assert.equal(called, false);
});

test("builds Hub and VTI targets from secret-free runtime configuration", () => {
  assert.deepEqual(
    federationTargetsFromConfig({ federation: { hubBaseUrl: "https://hub", vtiBaseUrl: "https://vti" } }),
    [
      { serviceId: "xrp-hbar-hub-runtime", baseUrl: "https://hub" },
      { serviceId: "vti-evidence-service", baseUrl: "https://vti" }
    ]
  );
});
