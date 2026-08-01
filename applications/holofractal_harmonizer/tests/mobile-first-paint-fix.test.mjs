import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../src/', import.meta.url);

async function source(name) {
  return readFile(new URL(name, root), 'utf8');
}

test('startup coordinator establishes mobile first paint before loading the public graph', async () => {
  const coordinator = await source('production-startup-coordinator.mjs');
  const firstPaintImport = coordinator.indexOf("import './mobile-first-paint-fix.mjs';");
  const themeImport = coordinator.indexOf("import './theme-bootstrap.mjs';");
  const publicDynamicImport = coordinator.indexOf("import('./public-boot.mjs')");

  assert.equal(firstPaintImport, 0);
  assert.ok(themeImport > firstPaintImport);
  assert.ok(publicDynamicImport > themeImport);
  assert.doesNotMatch(coordinator, /import\s+\{\s*startPublicBoot\s*\}\s+from\s+'\.\/public-boot\.mjs'/);
  assert.match(coordinator, /mobile_first_paint_precedes_public_module_graph:\s*true/);
});

test('mobile repair owns one dock, closes stale panels, and exposes editor first', async () => {
  const repair = await source('mobile-first-paint-fix.mjs');

  assert.match(repair, /body\.classList\.add\('visual-ide-active', 'hhs-mobile-first-paint'\)/);
  assert.match(repair, /ideLayout\.dataset\.mobilePane = 'editor'/);
  assert.match(repair, /workflow-mobile-tabs/);
  assert.match(repair, /tabs\.hidden = true/);
  assert.match(repair, /tabs\.inert = true/);
  assert.match(repair, /mobile-explorer-open/);
  assert.match(repair, /mobile-inspector-open/);
  assert.match(repair, /setExplorerOpen\(false\)/);
  assert.match(repair, /event\.stopImmediatePropagation\(\)/);
  assert.match(repair, /\.ide-file-item, \.ide-editor-tab, #ide-new-file/);
  assert.match(repair, /enforceVisualIdeSurface/);
});
