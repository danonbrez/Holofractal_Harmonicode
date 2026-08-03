import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const publicBootUrl = new URL('../src/public-boot.mjs', import.meta.url);

async function source() {
  return readFile(publicBootUrl, 'utf8');
}

test('visual IDE commits interaction before browser and production projections', async () => {
  const text = await source();
  const applicationIndex = text.indexOf("launch('application-experience'");
  const visualIndex = text.indexOf("launch('visual-ide'");
  const browserIndex = text.indexOf("launch('browser'");
  const productionIndex = text.indexOf("launch('production-integration'");

  assert.ok(applicationIndex >= 0);
  assert.ok(visualIndex > applicationIndex);
  assert.ok(browserIndex > visualIndex);
  assert.ok(productionIndex > browserIndex);
  assert.match(text, /awaitGlobalPromise\('HHSVisualIDEBoot', result\)/);
  assert.match(text, /awaitGlobalPromise\('HHSBrowserReady', result\)/);
  assert.match(text, /visual_ide_interactive_before_browser_projection: true/);
  assert.match(text, /browser_registry_before_production_projection: true/);
});

test('public boot retains every inherited user surface', async () => {
  const text = await source();
  for (const moduleId of [
    'application-experience',
    'visual-ide',
    'browser',
    'production-integration',
    'ux-default',
  ]) {
    assert.match(text, new RegExp(`launch\\('${moduleId}'`));
  }
  assert.match(text, /Promise\.allSettled\(\[/);
  assert.match(text, /frontend_is_authority: false/);
});
