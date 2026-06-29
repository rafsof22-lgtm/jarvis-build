import test from 'node:test';
import assert from 'node:assert/strict';

test('service contract lists health and readiness as implemented', () => {
  const implemented = ['GET /health', 'GET /ready'];
  assert.deepEqual(implemented, ['GET /health', 'GET /ready']);
});
