import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const sourceUrl = new URL('../src/gui-reliability.mjs', import.meta.url);

async function source() {
  return readFile(sourceUrl, 'utf8');
}

test('GUI mutation reconciliation is task-bounded and non-reentrant', async () => {
  const text = await source();

  assert.match(text, /let reconcileTimer = null;/);
  assert.match(text, /let reconciling = false;/);
  assert.match(text, /function scheduleReconcile\(preferred = null\)/);
  assert.match(text, /reconcileTimer = window\.setTimeout/);
  assert.match(text, /if \(reconcileTimer !== null\) return;/);
  assert.match(text, /if \(reconciling\) return;/);
  assert.match(text, /state\.activeSurface === selected && openNames\.length === 1/);
  assert.doesNotMatch(text, /queueMicrotask\(\(\) => reconcileSurfaceState/);
});

test('mutation observer schedules one bounded reconciliation task', async () => {
  const text = await source();
  const observerStart = text.indexOf('const observer = new MutationObserver');
  const observerBody = text.slice(observerStart, text.indexOf('for (const name', observerStart));

  assert.ok(observerStart >= 0);
  assert.match(observerBody, /scheduleReconcile\(\);/);
  assert.doesNotMatch(observerBody, /queueMicrotask/);
  assert.doesNotMatch(observerBody, /reconcileSurfaceState\(\)/);
});