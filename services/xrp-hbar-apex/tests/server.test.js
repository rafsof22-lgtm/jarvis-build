import assert from "node:assert/strict";
import { mkdtemp } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { after, before, test } from "node:test";
import { getConfig } from "../src/config.js";
import { createServer } from "../src/server.js";

const runtimeDir = await mkdtemp(path.join(os.tmpdir(), "xrp-hbar-apex-server-"));
const runtimeConfig = getConfig({
  APP_ENV: "test",
  BASE_URL: "http://127.0.0.1",
  LOG_LEVEL: "silent",
  PORT: "0",
  MCP_AUTH_MODE: "none",
  FEDERATION_STATE_FILE: path.join(runtimeDir, "federation-state.json")
});

const server = createServer(runtimeConfig);
let baseUrl;

before(async () => {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  baseUrl = `http://${address.address}:${address.port}`;
});

after(async () => {
  await new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
});

test("health endpoint reports healthy", async () => {
  const response = await fetch(`${baseUrl}/health`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.service, "xrp-hbar-apex");
  assert.equal(body.status, "healthy");
});

test("namespaced health endpoint reports healthy", async () => {
  const response = await fetch(`${baseUrl}/xrp-hbar-apex/health`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.service, "xrp-hbar-apex");
  assert.equal(body.status, "healthy");
});

test("ready endpoint reports required config honestly", async () => {
  const response = await fetch(`${baseUrl}/ready`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.status, "ready");
  assert.deepEqual(body.checks.missingRequiredEnv, []);
  assert.equal(body.checks.mcpPostImplemented, true);
  assert.equal(body.checks.toolsExposed, true);
  assert.equal(body.checks.federationPollingImplemented, true);
  assert.equal(body.checks.federationTargetsConfigured.hub, false);
  assert.equal(body.checks.federationTargetsConfigured.vti, false);
});

test("namespaced ready endpoint uses the same readiness contract", async () => {
  const response = await fetch(`${baseUrl}/xrp-hbar-apex/ready`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.status, "ready");
  assert.deepEqual(body.checks.missingRequiredEnv, []);
});

test("deployment status reports implemented MCP and federation polling truth", async () => {
  const response = await fetch(`${baseUrl}/deployment/status`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.version, "0.4.0");
  assert.equal(body.railwayRootDirectory, "services/xrp-hbar-apex");
  assert.equal(body.deployBranch, "main");
  assert.equal(body.capabilities.health, "implemented");
  assert.equal(body.capabilities.mcp, "implemented_metadata_first");
  assert.equal(body.capabilities.federationPolling, "implemented_not_configured");
  assert.ok(body.implementedNow.includes("POST /mcp"));
  assert.ok(body.implementedNow.includes("POST /federation/poll"));
  assert.ok(body.notImplementedYet.includes("full XRP/HBAR tracker execution inside this service"));
});

test("namespaced deployment status uses the same route contract", async () => {
  const response = await fetch(`${baseUrl}/xrp-hbar-apex/deployment/status`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.routeNamespace, "/xrp-hbar-apex");
  assert.ok(body.implementedNow.includes("GET /xrp-hbar-apex/deployment/status"));
});

test("mcp tools endpoint exposes the implemented metadata-first tools", async () => {
  const response = await fetch(`${baseUrl}/mcp/tools`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.status, "implemented");
  assert.equal(body.tools.length, 5);
  assert.ok(body.tools.some((tool) => tool.name === "extract_metadata"));
  assert.ok(body.tools.some((tool) => tool.name === "reprocess_transcript"));
});

test("mcp endpoint dispatches an implemented metadata tool", async () => {
  const response = await fetch(`${baseUrl}/mcp`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ tool: "extract_metadata", input: { url: "https://example.com/video" } })
  });
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.tool, "extract_metadata");
  assert.equal(body.output.proof_label, "METADATA_ONLY");
  assert.equal(body.output.canonical_url, "https://example.com/video");
});

test("federation status is readable without exposing state-file paths", async () => {
  const response = await fetch(`${baseUrl}/federation/status`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.status, "implemented");
  assert.equal(body.configuration.hub, false);
  assert.equal(body.configuration.vti, false);
  assert.equal(body.dead_letter_count, 0);
  assert.equal(Object.hasOwn(body, "stateFile"), false);
});

test("federation poll blocks safely when targets are not configured", async () => {
  const response = await fetch(`${baseUrl}/federation/poll`, { method: "POST" });
  const body = await response.json();

  assert.equal(response.status, 503);
  assert.equal(body.ok, false);
  assert.equal(body.integration_status, "BLOCKED");
  assert.equal(body.service_count, 2);
  assert.equal(body.blocked_services, 2);
  assert.ok(body.results.every((result) => result.error_code === "BASE_URL_NOT_CONFIGURED"));
  assert.ok(body.results.every((result) => result.attempts === 0));
});
