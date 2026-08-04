import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const publicBootUrl = new URL('../src/public-boot.mjs', import.meta.url);
const criticalPathUrl = new URL('../src/application-critical-path.mjs', import.meta.url);

async function publicBootSource() {
  return readFile(publicBootUrl, 'utf8');
}

async function criticalPathSource() {
  return readFile(criticalPathUrl, 'utf8');
}

test('application controls and visual IDE commit before browser and production projections', async () => {
  const text = await publicBootSource();
  const applicationIndex = text.indexOf("const applicationExperience = launch('application-experience'");
  const controlsIndex = text.indexOf('const applicationControls = applicationExperience');
  const visualIndex = text.indexOf('const visualIDE = applicationControls');
  const browserIndex = text.indexOf('const browser = visualIDE');
  const productionIndex = text.indexOf('const productionIntegration = browser.then');

  assert.ok(applicationIndex >= 0);
  assert.ok(controlsIndex > applicationIndex);
  assert.ok(visualIndex > controlsIndex);
  assert.ok(browserIndex > visualIndex);
  assert.ok(productionIndex > browserIndex);
  assert.match(text, /launch\('application-controls', '\.\/application-critical-path\.mjs'\)/);
  assert.match(text, /awaitGlobalPromise\('HHSVisualIDEBoot', result\)/);
  assert.match(text, /awaitGlobalPromise\('HHSBrowserReady', result\)/);
  assert.match(text, /application_controls_closed_before_visual_ide: true/);
  assert.match(text, /visual_ide_interactive_before_browser_projection: true/);
  assert.match(text, /browser_registry_before_production_projection: true/);
});

test('critical path guarantees New Application and gallery controls', async () => {
  const text = await criticalPathSource();

  assert.match(text, /initIntuitiveIDE/);
  assert.match(text, /initApplicationStudio/);
  assert.match(text, /ensureControl\('HHSIntuitiveIDE', '#ide-new-app'/);
  assert.match(text, /ensureControl\('HHSApplicationStudio', '#ide-application-gallery'/);
  assert.match(text, /HHS_APPLICATION_CRITICAL_CONTROL_MISSING/);
  assert.match(text, /state: 'INTERACTIVE_CONTROLS_READY'/);
  assert.match(text, /frontend_is_authority: false/);
});

test('public boot retains every inherited user surface', async () => {
  const text = await publicBootSource();
  for (const moduleId of [
    'application-experience',
    'application-controls',
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