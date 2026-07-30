import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('verified workflow-first Harmonizer remains the public presentation authority', () => {
  const html = read('index.html');
  const coordinatorIndex = html.indexOf('src/production-startup-coordinator.mjs');
  const browserIndex = html.indexOf('src/browser.mjs');
  const uxIndex = html.indexOf('src/ux-default.mjs');
  const integrationIndex = html.indexOf('src/production-integration.mjs');
  assert.ok(coordinatorIndex >= 0);
  assert.ok(coordinatorIndex < browserIndex);
  assert.ok(browserIndex < uxIndex);
  assert.ok(uxIndex < integrationIndex);
  assert.match(html, /src\/production-integration\.css/);
  assert.match(html, /id="registry-tree"/);
  assert.match(html, /id="assistant-view"/);
  assert.match(html, /id="api-view"/);
  assert.match(html, /id="inspector"/);
});

test('Pass 161 browser imports and calls only verified core contracts', () => {
  const source = read('src/browser.mjs');
  assert.match(source, /HarmonizerRuntime,\s*OBJECT_TYPES,/s);
  assert.doesNotMatch(source, /REGISTERED_OBJECT_TYPES/);
  assert.match(source, /runtime\.authority\.grant\('human:owner'/);
  assert.match(source, /'api\.invoke'/);
  assert.match(source, /runtime\.apis\.register\(\s*'hhs:api:object-search',\s*\{/s);
  assert.match(source, /operation:\s*'OBJECT_SEARCH'/);
  assert.match(source, /authoritative_completion_evidence:\s*true/);
  assert.match(source, /runtime\.faces\.register/);
  assert.doesNotMatch(source, /runtime\.panels\.registerFace/);
  assert.match(source, /runtime\.panels\.open\(objectId, \{ allow_repeat: true, stateful: false \}\)/);
  assert.match(source, /runtime\.registry\.lookup\(objectId\)/);
  assert.match(source, /object\.receipts\?\.at\(-1\)/);
  for (const forbidden of [
    "authority_state: 'ADMITTED'",
    "authority_state: 'PROPOSAL_ONLY'",
    "authority_state: 'EXTERNAL_PROVIDER'",
    "authority_state: 'CANONICAL'",
    "authority_state: 'API_BOUND'",
    "authority_state: 'PROJECTION_ONLY'",
  ]) {
    assert.ok(!source.includes(forbidden), `browser uses invalid Pass 161 authority enum: ${forbidden}`);
  }
});

test('Pass 161 runtime is exposed before assistant cold-start work', () => {
  const source = read('src/browser.mjs');
  const runtimeExposure = source.indexOf('window.HHSHarmonizer = runtime');
  const assistantExposure = source.indexOf('window.HHSAssistant = Object.freeze');
  const assistantColdStart = source.indexOf('void Promise.allSettled([refreshAssistantStatus(), restoreOrCreateThread()])');
  assert.ok(runtimeExposure >= 0);
  assert.ok(assistantExposure > runtimeExposure);
  assert.ok(assistantColdStart > assistantExposure);
  assert.doesNotMatch(
    source,
    /await Promise\.allSettled\(\[refreshAssistantStatus\(\), restoreOrCreateThread\(\)\]\);\s*window\.HHSHarmonizer/,
  );
});

test('production startup gives live runtime registry priority over assistant cold start', () => {
  const source = read('src/production-startup-coordinator.mjs');
  assert.match(source, /pathname\.startsWith\('\/api\/assistant\/'\)/);
  assert.match(source, /HHSProductionIntegration/);
  assert.match(source, /serviceCount/);
  assert.match(source, /MAX_ASSISTANT_DEFERRAL_MS/);
  assert.match(source, /runtime_registry_has_priority:\s*true/);
  assert.match(source, /frontend_is_authority:\s*false/);
  assert.doesNotMatch(source, /\/api\/runtime\/services/);
  assert.doesNotMatch(source, /new\s+WebSocket/);
});

test('production integration hydrates existing Pass 161 objects from live backend registries', () => {
  const source = read('src/production-integration.mjs');
  for (const endpoint of [
    '/api/runtime/authority/status',
    '/api/runtime/services',
    '/api/runtime/workspace/session',
    '/api/runtime/installation/status',
  ]) {
    assert.match(source, new RegExp(endpoint.replaceAll('/', '\\/')));
  }
  assert.match(source, /runtime\.registry\.register/);
  assert.match(source, /runtime\.registry\.relate/);
  assert.match(source, /refreshRegistryProjection/);
  assert.match(source, /window\.HHSHarmonizer/);
  assert.match(source, /VALIDATED_PROJECTION/);
  assert.match(source, /frontend_is_authority:\s*false/);
  assert.doesNotMatch(source, /new\s+HarmonizerRuntime/);
  assert.doesNotMatch(source, /new\s+WebSocket/);
});

test('every live service remains executable through guarded backend dispatch', () => {
  const source = read('src/production-integration.mjs');
  assert.match(source, /serviceDescriptors/);
  assert.match(source, /serviceObjectIds/);
  assert.match(source, /schemaDefaults/);
  assert.match(source, /service-schema-fields/);
  assert.match(source, /\/api\/runtime\/services\/dispatch/);
  assert.match(source, /JSON\.stringify\(\{ service: descriptor\.name, payload \}\)/);
  assert.match(source, /Execute registered service/);
  assert.match(source, /extractReceiptHash/);
  assert.match(source, /BACKEND RESULT RETURNED/);
  assert.match(source, /frontend_result_fabricated:\s*false/);
  assert.doesNotMatch(source, /disabled registry item/);
  assert.doesNotMatch(source, /simulated_raw_result/);
});

test('runtime warming is disclosed without blocking the verified workflow interface', () => {
  const source = read('src/production-integration.mjs');
  assert.match(source, /RUNTIME AUTHORITY · WARMING/);
  assert.match(source, /Promise\.allSettled/);
  assert.match(source, /hydrateProductionRegistry\(\)\.catch/);
  assert.doesNotMatch(source, /document\.body\.replaceChildren/);
  assert.doesNotMatch(source, /window\.location\.replace/);
});
