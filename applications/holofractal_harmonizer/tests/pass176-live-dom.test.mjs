import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../', import.meta.url);
const read = (path) => readFile(new URL(path, root), 'utf8');

test('application-first switching preserves live advanced runtime DOM', async () => {
  const recovery = await read('src/production-recovery.mjs');
  const detachStart = recovery.indexOf('function detachAdvancedSurfaces()');
  const restoreStart = recovery.indexOf('function restoreAdvancedSurfaces()');
  const setWorkspaceStart = recovery.indexOf('function setWorkspace(');
  assert.ok(detachStart >= 0 && restoreStart > detachStart && setWorkspaceStart > restoreStart);
  const detach = recovery.slice(detachStart, restoreStart);
  const restore = recovery.slice(restoreStart, setWorkspaceStart);
  assert.match(detach, /node\.hidden = true/);
  assert.match(detach, /aria-hidden/);
  assert.doesNotMatch(detach, /node\.remove\(\)/);
  assert.match(restore, /node\.hidden = hidden/);
  assert.match(restore, /delete node\.dataset\.hhsPass176AdvancedHidden/);
});

test('legacy lifecycle button has one production recovery owner', async () => {
  const visual = await read('src/visual-ide.mjs');
  const recovery = await read('src/production-recovery.mjs');
  assert.doesNotMatch(visual, /\['#ide-run-lifecycle',\s*'lifecycle'\]/);
  assert.doesNotMatch(visual, /required\('#ide-run-lifecycle'\)\.onclick/);
  assert.match(recovery, /bind\('#ide-run-lifecycle',\s*\(\) => void runBoundedProjectTest/);
});
