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
  const browserModuleIndex = text.indexOf('const browserModule = applicationControls');
  const productionIndex = text.indexOf('const productionIntegration = applicationControls.then');
  const workflowIndex = text.indexOf('const workflowDefault = applicationControls.then');

  assert.ok(applicationIndex >= 0);
  assert.ok(controlsIndex > applicationIndex);
  assert.ok(visualModuleIndex > controlsIndex);
  assert.ok(browserModuleIndex > controlsIndex);
  assert.ok(productionIndex > controlsIndex);
  assert.ok(workflowIndex > controlsIndex);
  assert.match(text, /launch\('application-controls', '\.\/application-critical-path\.mjs'\)/);
  assert.match(text, /requireReady\('application-controls', result\)/);
  assert.match(text, /requireReady\('visual-ide', result\)/);
  assert.match(text, /requireReady\('browser', result\)/);
  assert.match(text, /application_controls_closed_before_projection_modules: true/);
});

test('projection modules cannot block each other from being installed', async () => {
  const text = await publicBootSource();

  assert.match(text, /const visualModule = applicationControls\s*\.then/);
  assert.match(text, /const browserModule = applicationControls\s*\.then/);
  assert.match(text, /const productionIntegration = applicationControls\.then/);
  assert.match(text, /const workflowDefault = applicationControls\.then/);
  assert.doesNotMatch(text, /const browserModule = visualModule\s*\.then/);
  assert.doesNotMatch(text, /const productionIntegration = browserModule\.then/);
  assert.doesNotMatch(text, /const productionIntegration = browser\.then\(/);
  assert.match(text, /projection_modules_start_independently_after_controls: true/);
  assert.match(text, /production_integration_independent_of_visual_browser_completion: true/);
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
