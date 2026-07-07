import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { getConfig } from "../src/config.js";
import { createServer } from "../src/server.js";

const runtimeConfig = getConfig({
  APP_ENV: "test",
  LOG_LEVEL: "silent",
  PORT: "0"
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
  assert.deepEqual(body.checks.requiredEnv, []);
  assert.deepEqual(body.checks.missingRequiredEnv, []);
  assert.equal(body.checks.noRequiredSecretsForShell, true);
});

test("namespaced ready endpoint reports required config honestly", async () => {
  const response = await fetch(`${baseUrl}/xrp-hbar-apex/ready`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.ok, true);
  assert.equal(body.status, "ready");
  assert.deepEqual(body.checks.requiredEnv, []);
  assert.deepEqual(body.checks.missingRequiredEnv, []);
  assert.equal(body.checks.noRequiredSecretsForShell, true);
});

test("deployment status separates implemented and unimplemented capabilities", async () => {
  const response = await fetch(`${baseUrl}/deployment/status`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.railwayRootDirectory, "services/xrp-hbar-apex");
  assert.equal(body.deployBranch, "main");
  assert.equal(body.capabilities.health, "implemented");
  assert.equal(body.capabilities.mcp, "not_implemented");
  assert.ok(body.implementedNow.includes("GET /health"));
  assert.ok(body.notImplementedYet.includes("full XRP/HBAR tracker execution"));
});

test("namespaced deployment status uses the same route contract", async () => {
  const response = await fetch(`${baseUrl}/xrp-hbar-apex/deployment/status`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.railwayRootDirectory, "services/xrp-hbar-apex");
  assert.equal(body.deployBranch, "main");
  assert.equal(body.routeNamespace, "/xrp-hbar-apex");
  assert.ok(body.implementedNow.includes("GET /xrp-hbar-apex/deployment/status"));
});

test("mcp tools endpoint exposes no fake tools", async () => {
  const response = await fetch(`${baseUrl}/mcp/tools`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.deepEqual(body.tools, []);
  assert.equal(body.status, "not_implemented");
});

test("mcp endpoint does not fake implementation", async () => {
  const response = await fetch(`${baseUrl}/mcp`, { method: "POST", body: "{}" });
  const body = await response.json();

  assert.equal(response.status, 501);
  assert.equal(body.ok, false);
  assert.equal(body.error, "not_implemented");
});
