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

test('application controls close before projection modules are installed', async () => {
  const text = await publicBootSource();
  const applicationIndex = text.indexOf("const applicationExperience = launch('application-experience'");
  const controlsIndex = text.indexOf('const applicationControls = applicationExperience');
  const visualModuleIndex = text.indexOf('const visualModule = applicationControls');
  const browserModuleIndex = text.indexOf('const browserModule = visualModule');
  const productionIndex = text.indexOf('const productionIntegration = browserModule.then');

  assert.ok(applicationIndex >= 0);
  assert.ok(controlsIndex > applicationIndex);
  assert.ok(visualModuleIndex > controlsIndex);
  assert.ok(browserModuleIndex > visualModuleIndex);
  assert.ok(productionIndex > browserModuleIndex);
  assert.match(text, /launch\('application-controls', '\.\/application-critical-path\.mjs'\)/);
  assert.match(text, /requireReady\('application-controls', result\)/);
  assert.match(text, /requireReady\('visual-ide', result\)/);
  assert.match(text, /requireReady\('browser', result\)/);
  assert.match(text, /application_controls_closed_before_projection_modules: true/);
  assert.match(text, /visual_module_installed_before_browser_module: true/);
});

test('production integration is not blocked by browser projection completion', async () => {
  const text = await publicBootSource();
  const browserModuleIndex = text.indexOf('const browserModule = visualModule');
  const browserCompletionIndex = text.indexOf('const browser = browserModule');
  const productionIndex = text.indexOf('const productionIntegration = browserModule.then');

  assert.ok(browserModuleIndex >= 0);
  assert.ok(browserCompletionIndex > browserModuleIndex);
  assert.ok(productionIndex > browserCompletionIndex);
  assert.doesNotMatch(text, /const productionIntegration = browser\.then\(/);
  assert.match(text, /production_integration_installed_before_browser_projection_completion: true/);
  assert.match(text, /production_integration_owns_bounded_harmonizer_wait: true/);
  assert.match(text, /awaitGlobalPromise\('HHSVisualIDEBoot', result\)/);
  assert.match(text, /awaitGlobalPromise\('HHSBrowserReady', result\)/);
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