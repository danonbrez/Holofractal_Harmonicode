import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('visual IDE is the front-and-center public surface', () => {
  const html = read('index.html');
  const ide = html.indexOf('id="ide-view"');
  const assistant = html.indexOf('id="assistant-view"');
  assert.ok(ide >= 0);
  assert.ok(assistant > ide);
  assert.doesNotMatch(html.slice(ide, html.indexOf('>', ide) + 1), /hidden/);
  assert.match(html, /id="ide-file-tree"/);
  assert.match(html, /id="ide-source-editor"/);
  assert.match(html, /id="ide-3d-viewport"/);
  assert.match(html, /class="ide-mobile-dock"/);
  assert.ok(html.indexOf('src/visual-ide.mjs') > html.indexOf('src/production-integration.mjs'));
});

test('IDE exposes a complete governed software lifecycle', () => {
  const source = [read('src/visual-ide-state.mjs'), read('src/visual-ide-ui.mjs'), read('src/visual-ide-runtime.mjs'), read('src/visual-ide.mjs')].join('\n');
  for (const endpoint of [
    '/api/runtime/multimodal-ingress/ingest',
    '/api/runtime/multimodal-ingress/snapshots/',
    '/api/runtime/workspace/command',
    '/api/runtime/development/lifecycle',
    '/api/runtime/development/replay',
  ]) {
    assert.match(source, new RegExp(endpoint.replaceAll('/', '\\/')));
  }
  for (const operation of ['interpret.execute', 'compile.execute', 'emulator.create', 'emulator.run', 'emulator.snapshot']) {
    assert.match(source, new RegExp(operation.replace('.', '\\.')));
  }
  assert.match(source, /new Uint8Array\(648\)/);
  assert.match(source, /for \(let cell = 0; cell < 81;/);
  assert.match(source, /laneIndex < 3/);
  assert.match(source, /laneIndex \* 72/);
  assert.match(source, /backend_evidence_unmodified: true/);
  assert.match(source, /projection_b64: state\.snapshot\.projection_b64/);
  assert.match(source, /ingestion_positions_hash216: state\.snapshot\.ingestion_positions_hash216/);
});

test('assistant initialization cannot freeze IDE or runtime calls', () => {
  const source = read('src/production-startup-coordinator.mjs');
  assert.match(source, /MAX_ASSISTANT_DEFERRAL_MS = 1_500/);
  assert.match(source, /pathname\.startsWith\('\/api\/assistant\/'\)/);
  assert.match(source, /visual_ide_requests_never_deferred: true/);
  assert.doesNotMatch(source, /pathname\.startsWith\('\/api\/runtime\/'\)/);
});
