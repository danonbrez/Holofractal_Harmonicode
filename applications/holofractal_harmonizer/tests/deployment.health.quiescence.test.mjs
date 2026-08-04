import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const stateUrl = new URL('../src/visual-ide-state.mjs', import.meta.url);
const healthUrl = new URL('../src/deployment-health.mjs', import.meta.url);

test('unchanged IDE status text preserves DOM identity', async () => {
  const source = await readFile(stateUrl, 'utf8');
  assert.match(source, /const next = String\(value\);/);
  assert.match(source, /if \(node\.textContent === next\) return false;/);
  assert.match(source, /node\.textContent = next;/);
});

test('deployment health reconciliation is task-bounded and non-reentrant', async () => {
  const source = await readFile(healthUrl, 'utf8');
  const observer = source.match(
    /mutationObserver = new MutationObserver\(scheduleHealthReconciliation\);[\s\S]*?mutationObserver\.observe\(document\.body, \{([^}]*)\}\);/,
  );
  assert.ok(observer, 'body health observer contract is present');
  assert.match(observer[1], /childList:\s*true/);
  assert.match(observer[1], /subtree:\s*true/);
  assert.doesNotMatch(observer[1], /characterData:\s*true/);
  assert.match(source, /let healthReconcileTimer = null;/);
  assert.match(source, /let healthReconcileRunning = false;/);
  assert.match(source, /if \(healthReconcileTimer !== null\) return;/);
  assert.match(source, /healthReconcileTimer = window\.setTimeout/);
  assert.match(source, /if \(healthReconcileRunning\) return;/);
  assert.match(source, /reconciliation_task_bounded:\s*true/);
  assert.match(source, /setText\('#hhs-backend-health-title'/);
  assert.match(source, /setText\('#hhs-backend-health-message'/);
});

test('deployment health uses one bounded startup liveness projection', async () => {
  const source = await readFile(healthUrl, 'utf8');
  assert.match(source, /const LIVENESS_PATHS = \['\/api\/health'\];/);
  assert.match(source, /const REQUEST_TIMEOUT_MS = 30_000;/);
  assert.match(source, /const RUNTIME_AUTHORITY_PATH = '\/api\/runtime\/authority\/status';/);
  assert.match(source, /const ASSISTANT_STATUS_PATH = '\/api\/assistant\/status';/);
  assert.match(source, /Promise\.allSettled\(\[/);
  assert.match(source, /withTimeout\(RUNTIME_AUTHORITY_PATH\)/);
  assert.match(source, /withTimeout\(ASSISTANT_STATUS_PATH\)/);
  assert.doesNotMatch(source, /\/api\/product\/health/);
  assert.doesNotMatch(source, /['"]\/healthz['"]/);
  assert.match(source, /heavyweight_product_health_probe_duplicated:\s*false/);
  assert.match(source, /startup_health_timeout_ms:\s*REQUEST_TIMEOUT_MS/);
  assert.match(source, /healthz_startup_probe_disabled:\s*true/);
});

test('visual authority requests retain a 30 second startup floor without widening ordinary calls', async () => {
  const source = await readFile(stateUrl, 'utf8');
  assert.match(source, /const STARTUP_AUTHORITY_TIMEOUT_MS = 30_000;/);
  assert.match(source, /STARTUP_AUTHORITY_PATHS\.has\(path\)/);
  assert.match(source, /Math\.max\(STARTUP_AUTHORITY_TIMEOUT_MS, requestedTimeoutMs\)/);
  assert.match(source, /:\s*requestedTimeoutMs;/);
});
