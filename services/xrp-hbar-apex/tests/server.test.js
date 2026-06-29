import assert from "node:assert/strict";
import { after, before, test } from "node:test";
import { createServer } from "../src/server.js";

const server = createServer({
  serviceName: "xrp-hbar-apex",
  version: "0.1.0",
  appEnv: "test",
  logLevel: "silent",
  port: 0,
  optionalIntegrations: {
    openai: false,
    postgres: false,
    googleSheets: false,
    github: false,
    n8n: false
  }
});

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
  assert.equal(body.status, "healthy");
});

test("ready endpoint reports shell readiness", async () => {
  const response = await fetch(`${baseUrl}/ready`);
  const body = await response.json();

  assert.equal(response.status, 200);
  assert.equal(body.status, "ready");
  assert.equal(body.checks.noRequiredSecretsForShell, true);
});

test("mcp endpoint does not fake implementation", async () => {
  const response = await fetch(`${baseUrl}/mcp`, { method: "POST", body: "{}" });
  const body = await response.json();

  assert.equal(response.status, 501);
  assert.equal(body.error, "not_implemented");
});
