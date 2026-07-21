import fs from 'node:fs';

const matrixPath = 'registry/xrp-hbar-cross-asset-historical-reconciliation-matrix.json';
const schemaPath = 'registry/xrp-hbar-cross-asset-historical-reconciliation-matrix.schema.json';

for (const path of [matrixPath, schemaPath]) {
  if (!fs.existsSync(path)) throw new Error(`Missing required file: ${path}`);
}

const matrix = JSON.parse(fs.readFileSync(matrixPath, 'utf8'));
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

const allowedAssetClasses = new Set(['xrp', 'hbar', 'crypto', 'stock', 'etf', 'commodity', 'macro', 'property', 'cross_asset']);
const allowedRecordTypes = new Set(['request', 'assistant_response', 'table', 'prediction', 'probability', 'catalyst', 'trigger', 'ranking', 'candidate', 'rejection', 'discrepancy', 'workflow', 'instruction']);
const allowedAuthorityTiers = new Set(['user_correction', 'user_request', 'official_source', 'verified_external', 'assistant_proposal', 'unverified_claim']);
const allowedAdoptionStates = new Set(['adopted', 'partially_adopted', 'proposed', 'rejected', 'superseded', 'unknown']);
const allowedVerificationStates = new Set(['not_checked', 'source_verified', 'semantically_reconciled', 'implementation_mapped', 'independently_verified', 'blocked']);
const allowedGapStates = new Set(['PENDING_INGEST', 'BACKLOGGED', 'IN_PROGRESS', 'BLOCKED', 'WAIVED', 'DONE_VERIFIED']);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(schema.properties?.schema_version?.const === matrix.schema_version, 'Matrix schema_version does not match schema const');
assert(typeof matrix.generated_at === 'string' && !Number.isNaN(Date.parse(matrix.generated_at)), 'generated_at must be an ISO date-time');
assert(matrix.source_denominator && typeof matrix.source_denominator === 'object', 'source_denominator is required');

for (const key of ['inventoried', 'processed', 'pending', 'inaccessible']) {
  assert(Number.isInteger(matrix.source_denominator[key]) && matrix.source_denominator[key] >= 0, `source_denominator.${key} must be a non-negative integer`);
}
assert(matrix.source_denominator.processed + matrix.source_denominator.pending + matrix.source_denominator.inaccessible === matrix.source_denominator.inventoried,
  'Source denominator arithmetic must satisfy processed + pending + inaccessible = inventoried');

assert(Array.isArray(matrix.records) && matrix.records.length > 0, 'records must be a non-empty array');
assert(Array.isArray(matrix.gaps), 'gaps must be an array');

const recordIds = new Set();
for (const [index, record] of matrix.records.entries()) {
  const prefix = `records[${index}]`;
  for (const key of ['record_id', 'source_pointer', 'asset_class', 'assets', 'record_type', 'normalized_requirement', 'authority_tier', 'adoption_state', 'verification_state', 'canonical_placement']) {
    assert(record[key] !== undefined && record[key] !== null, `${prefix}.${key} is required`);
  }
  assert(typeof record.record_id === 'string' && record.record_id.length > 0, `${prefix}.record_id must be non-empty`);
  assert(!recordIds.has(record.record_id), `Duplicate record_id: ${record.record_id}`);
  recordIds.add(record.record_id);
  assert(typeof record.source_pointer === 'string' && record.source_pointer.length > 0, `${prefix}.source_pointer must be non-empty`);
  assert(allowedAssetClasses.has(record.asset_class), `${prefix}.asset_class is invalid: ${record.asset_class}`);
  assert(Array.isArray(record.assets) && record.assets.length > 0 && record.assets.every((value) => typeof value === 'string' && value.length > 0), `${prefix}.assets must contain non-empty strings`);
  assert(allowedRecordTypes.has(record.record_type), `${prefix}.record_type is invalid: ${record.record_type}`);
  assert(typeof record.normalized_requirement === 'string' && record.normalized_requirement.length > 0, `${prefix}.normalized_requirement must be non-empty`);
  assert(allowedAuthorityTiers.has(record.authority_tier), `${prefix}.authority_tier is invalid: ${record.authority_tier}`);
  assert(allowedAdoptionStates.has(record.adoption_state), `${prefix}.adoption_state is invalid: ${record.adoption_state}`);
  assert(allowedVerificationStates.has(record.verification_state), `${prefix}.verification_state is invalid: ${record.verification_state}`);
  assert(typeof record.canonical_placement === 'string' && record.canonical_placement.length > 0, `${prefix}.canonical_placement must be non-empty`);
  if (record.historical_values?.probability_percent !== null && record.historical_values?.probability_percent !== undefined) {
    assert(typeof record.historical_values.probability_percent === 'number' && record.historical_values.probability_percent >= 0 && record.historical_values.probability_percent <= 100,
      `${prefix}.historical_values.probability_percent must be between 0 and 100`);
  }
}

const gapIds = new Set();
for (const [index, gap] of matrix.gaps.entries()) {
  const prefix = `gaps[${index}]`;
  for (const key of ['gap_id', 'description', 'status', 'next_action']) {
    assert(typeof gap[key] === 'string' && gap[key].length > 0, `${prefix}.${key} must be non-empty`);
  }
  assert(!gapIds.has(gap.gap_id), `Duplicate gap_id: ${gap.gap_id}`);
  gapIds.add(gap.gap_id);
  assert(allowedGapStates.has(gap.status), `${prefix}.status is invalid: ${gap.status}`);
  if (gap.source_refs !== undefined) assert(Array.isArray(gap.source_refs) && gap.source_refs.every((value) => typeof value === 'string'), `${prefix}.source_refs must be strings`);
}

const unresolvedCrossReferences = [];
for (const record of matrix.records) {
  for (const field of ['supersedes', 'conflicts_with']) {
    for (const reference of record[field] || []) {
      if (/^XHR-/.test(reference) && !recordIds.has(reference)) unresolvedCrossReferences.push(`${record.record_id}.${field}:${reference}`);
    }
  }
}
assert(unresolvedCrossReferences.length === 0, `Unresolved matrix record references: ${unresolvedCrossReferences.join(', ')}`);

console.log(JSON.stringify({
  status: 'VALIDATION_PASSED',
  schemaVersion: matrix.schema_version,
  inventoriedSources: matrix.source_denominator.inventoried,
  processedSources: matrix.source_denominator.processed,
  records: matrix.records.length,
  gaps: matrix.gaps.length,
  uniqueRecordIds: recordIds.size,
  uniqueGapIds: gapIds.size
}, null, 2));
