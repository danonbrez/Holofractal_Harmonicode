import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const stateSource = readFileSync(resolve(root, 'src/visual-ide-state.mjs'), 'utf8');
const runtimeSource = readFileSync(resolve(root, 'src/visual-ide-runtime.mjs'), 'utf8');

test('lifecycle request remains bound to the canonical Pass 174 endpoint', () => {
  assert.match(runtimeSource, /\/api\/runtime\/development\/lifecycle/);
  assert.match(runtimeSource, /timeoutMs:\s*180000/);
});

test('non-JSON backend responses expose route, HTTP status, content type, and body preview', () => {
  assert.match(stateSource, /HHS_API_ROUTE_UNREACHABLE/);
  assert.match(stateSource, /response\.headers\.get\('content-type'\)/);
  assert.match(stateSource, /response\.status/);
  assert.match(stateSource, /responsePreview\(raw\)/);
  assert.match(stateSource, /await response\.text\(\)/);
});

test('the frontend does not accept an HTML static fallback as lifecycle evidence', () => {
  assert.doesNotMatch(stateSource, /response\.json\(\)\.catch\(\(\) => \(\{ error:/);
  assert.match(stateSource, /JSON\.parse\(raw\)/);
  assert.match(stateSource, /throw new Error\(/);
});
