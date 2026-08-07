import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const coordinatorUrl = new URL('../src/production-startup-coordinator.mjs', import.meta.url);

async function coordinatorSource() {
  return readFile(coordinatorUrl, 'utf8');
}

test('canonical public boot precedes legacy projection imports', async () => {
  const source = await coordinatorSource();
  const publicBootIndex = source.indexOf("void import('./public-boot.mjs')");
  const deferredBootIndex = source.indexOf('void loadDeferredProjectionModules();');

  assert.ok(publicBootIndex >= 0, 'public boot must be launched');
  assert.ok(deferredBootIndex > publicBootIndex, 'deferred projections must be scheduled from the public boot continuation');
  assert.doesNotMatch(source, /^import '\.\/pass(?:196|197|198|199|200a|200b|200c|201|203)[^']*';$/m);
  assert.match(source, /const DEFERRED_PROJECTION_MODULES = Object\.freeze\(\[/);
  assert.match(source, /'\.\/pass196-integration\.mjs'/);
  assert.match(source, /'\.\/pass203-mainframe\.mjs'/);
});

test('deferred projections require a closed runtime receipt and service registry', async () => {
  const source = await coordinatorSource();

  assert.match(source, /integration\.phase === 'READY'/);
  assert.match(source, /integration\.runtimeAuthority\?\.ok/);
  assert.match(source, /Number\(integration\.serviceCount \|\| 0\) > 0/);
  assert.match(source, /const ready = await waitForReceiptClosedRegistry\(\);/);
  assert.match(source, /if \(!ready\) \{/);
  assert.match(source, /DEFERRED_RUNTIME_NOT_READY/);
  assert.match(source, /deferred_projections_require_receipt_closure: true/);
});

test('legacy projections retain deterministic dependency order without request bursts', async () => {
  const source = await coordinatorSource();
  const expectedOrder = [
    './pass196-integration.mjs',
    './pass197-calibration.mjs',
    './pass198-calibration-registry.mjs',
    './pass199-distributed-calibration.mjs',
    './pass200a-proof-carrying-optimization.mjs',
    './pass200b-governed-canary.mjs',
    './pass200c-guarded-active.mjs',
    './pass201-public-api-federation.mjs',
    './pass203-mainframe.mjs',
  ];

  let previousIndex = -1;
  for (const path of expectedOrder) {
    const index = source.indexOf(`'${path}'`);
    assert.ok(index > previousIndex, `${path} must retain inherited projection order`);
    previousIndex = index;
  }
  assert.match(source, /for \(const path of DEFERRED_PROJECTION_MODULES\) \{/);
  assert.match(source, /await import\(path\);/);
  assert.match(source, /await sleep\(PRODUCTION_REGISTRY_POLL_MS\);/);
});
