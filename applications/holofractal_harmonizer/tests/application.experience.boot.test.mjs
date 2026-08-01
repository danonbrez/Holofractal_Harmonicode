import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('public boot launches the complete application experience independently', () => {
  const boot = read('src/public-boot.mjs');
  assert.match(
    boot,
    /const applicationExperience = launch\('application-experience', '\.\/application-experience\.mjs'\)/,
  );
  assert.match(boot, /applicationExperience,/);
  assert.ok(
    boot.indexOf("const applicationExperience = launch('application-experience'")
      < boot.indexOf('const workflowDefault = browser.then'),
  );
});

test('New Application and Assistant are synchronous fail-closed critical surfaces', () => {
  const source = read('src/application-experience.mjs');
  const intuitive = source.indexOf("initialize('HHSIntuitiveIDE'");
  const studio = source.indexOf("initialize('HHSApplicationStudio'");
  const assistant = source.indexOf("initialize('HHSIntegratedAssistant'");
  const postcondition = source.indexOf('const criticalSurface = enforceCriticalSurfacePostconditions()');
  const support = source.indexOf('const supportReady = Promise.allSettled');

  assert.match(source, /import \{ initIntegratedAssistant \} from '\.\/integrated-assistant\.mjs'/);
  assert.ok(intuitive >= 0);
  assert.ok(intuitive < studio);
  assert.ok(studio < assistant);
  assert.ok(assistant < postcondition);
  assert.ok(postcondition < support);
  assert.doesNotMatch(source.slice(0, intuitive), /project-lifecycle|integrated-workbench|deployable-app-compiler/);
  assert.match(source, /retireLegacyApplicationLauncher\(\)/);
  assert.match(source, /window\.HHSApplicationStudio\?\.ensurePrimaryControl\?\.\(\)/);
  assert.match(source, /window\.HHSIntegratedAssistant\?\.open\?\.\(\)/);
  assert.match(source, /HHS_APPLICATION_LAUNCHER_CARDINALITY_INVALID/);
  assert.match(source, /HHS_APPLICATION_LAUNCHER_NOT_ACTIONABLE/);
  assert.match(source, /HHS_INTEGRATED_ASSISTANT_NOT_VISIBLE/);
  assert.match(source, /HHS_INTEGRATED_ASSISTANT_PROMPT_NOT_VISIBLE/);
  assert.match(source, /loadSupport\('project-lifecycle', '\.\/project-lifecycle\.mjs'/);
  assert.match(source, /loadSupport\('integrated-workbench', '\.\/integrated-workbench\.mjs'/);
  assert.match(source, /loadSupport\('deployable-app-compiler', '\.\/deployable-app-compiler\.mjs'/);
  assert.match(source, /state: 'INTERACTIVE'/);
  assert.match(source, /public_application_launcher_count:/);
  assert.match(source, /integrated_assistant_visible:/);
  assert.match(source, /creates_real_runnable_projects:/);
  assert.match(source, /if \(bootRecord\) \{\s*enforceCriticalSurfacePostconditions\(\);\s*return bootRecord;/);
  assert.match(source, /supportReady = Promise\.allSettled[\s\S]*enforceCriticalSurfacePostconditions\(\)/);
  assert.match(source, /frontend_is_authority: false/);
});
