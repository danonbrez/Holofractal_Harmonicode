import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { createStoredZip, crc32 } from '../src/project-zip.mjs';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

function u32(bytes, offset) {
  return new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength).getUint32(offset, true);
}

test('stored ZIP writer preserves relative project paths and deterministic records', () => {
  const zip = createStoredZip([
    { path: 'source/src/main.hhs', data: 'a²=1\n' },
    { path: 'project.hhs-manifest.json', data: '{"ok":true}' },
  ]);
  assert.equal(u32(zip, 0), 0x04034b50);
  assert.equal(u32(zip, zip.length - 22), 0x06054b50);
  const decoded = Buffer.from(zip).toString('latin1');
  assert.match(decoded, /source\/src\/main\.hhs/);
  assert.match(decoded, /project\.hhs-manifest\.json/);
  assert.equal(crc32(new TextEncoder().encode('123456789')), 0xcbf43926);
});

test('project lifecycle is backend-grounded and packages multiple authorized targets', () => {
  const source = read('src/project-lifecycle.mjs');
  for (const endpoint of [
    '/api/runtime/development/lifecycle',
    '/api/runtime/workspace/command',
    '/api/runtime/multimodal-ingress/ingest',
    '/api/runtime/multimodal-ingress/snapshots/',
  ]) assert.match(source, new RegExp(endpoint.replaceAll('/', '\\/')));
  for (const target of ['HHS_IR', 'C_SOURCE', 'PYTHON_ADAPTER', 'JSON_EXECUTION_GRAPH', 'DOT_GRAPH', 'BYTECODE_OR_VM_PLAN']) {
    assert.match(source, new RegExp(target));
  }
  assert.match(source, /original_source_preserved: true/);
  assert.match(source, /backend_evidence_unmodified: true/);
  assert.match(source, /frontend_runtime_authority: false/);
  assert.match(source, /source\/\$\{file\.path\}/);
  assert.match(source, /build\/\$\{target\}/);
  assert.match(source, /receipts\/\$\{file\.path\}/);
});

test('deployed visual IDE gains the additive project lifecycle without replacing its existing boot path', () => {
  const ide = read('src/visual-ide.mjs');
  const theme = read('src/harmonic-studio-theme.css');
  assert.match(ide, /import \{ initProjectLifecycle \} from '\.\/project-lifecycle\.mjs'/);
  assert.match(ide, /showIde\(\); initProjectLifecycle\(\);/);
  assert.match(theme, /--background: #16110d/);
  assert.match(theme, /--active: #e0a63c/);
  assert.match(theme, /Additive Harmonicode Studio aesthetic layer/);
  assert.doesNotMatch(ide, /replaceChildren\(document\.body/);
});
