import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const sourceUrl = new URL('../src/visual-ide.mjs', import.meta.url);

test('optional workspace authority binding cannot hold Pass 176 user-action quiescence', async () => {
  const source = await readFile(sourceUrl, 'utf8');
  assert.match(source, /const WORKSPACE_AUTHORITY_BIND_TIMEOUT_MS = 15_000;/);
  assert.match(source, /function scheduleWorkspaceAuthorityBind\(\)/);
  assert.match(source, /new AbortController\(\)/);
  assert.match(source, /HHS_P176_OPTIONAL_WORKSPACE_BIND_TIMEOUT/);
  assert.match(source, /ensureProject\(\{ signal: controller\.signal \}\)/);
  assert.match(source, /blocks_pass176_quiescence:\s*false/);
  assert.match(source, /project_files_preserved:\s*true/);
  assert.match(source, /void scheduleWorkspaceAuthorityBind\(\);/);
  assert.match(source, /optionalWorkspaceBindBlocksQuiescence:\s*false/);
  assert.doesNotMatch(source, /runAction\(['"]workspace-authority-bind/);
  assert.doesNotMatch(source, /recordError\([^)]*workspace-authority-bind/);
});
