import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('public boot launches the complete application experience before heavy hydration', () => {
  const boot = read('src/public-boot.mjs');
  const application = boot.indexOf("const applicationExperience = launch('application-experience'");
  const browser = boot.indexOf('const browser = applicationExperience.then');
  const integration = boot.indexOf('const productionIntegration = applicationExperience.then');
  const visual = boot.indexOf('const visualIDE = applicationExperience.then');
  assert.match(
    boot,
    /const applicationExperience = launch\('application-experience', '\.\/application-experience\.mjs'\)/,
  );
  assert.match(boot, /applicationExperience,/);
  assert.ok(application >= 0);
  assert.ok(application < browser);
  assert.ok(application < integration);
  assert.ok(application < visual);
  assert.match(boot, /application_controls_first: true/);
  assert.ok(
    application < boot.indexOf('const workflowDefault = browser.then'),
  );
});

test('New Application is the non-blocking critical path', () => {
  const source = read('src/application-experience.mjs');
  const intuitive = source.indexOf("initialize('HHSIntuitiveIDE'");
  const studio = source.indexOf("initialize('HHSApplicationStudio'");
  const support = source.indexOf('const supportReady = Promise.allSettled');
  assert.ok(intuitive >= 0);
  assert.ok(intuitive < studio);
  assert.ok(studio < support);
  assert.doesNotMatch(source.slice(0, intuitive), /project-lifecycle|integrated-workbench|deployable-app-compiler/);
  assert.match(source, /loadSupport\('project-lifecycle', '\.\/project-lifecycle\.mjs'/);
  assert.match(source, /loadSupport\('integrated-workbench', '\.\/integrated-workbench\.mjs'/);
  assert.match(source, /loadSupport\('deployable-app-compiler', '\.\/deployable-app-compiler\.mjs'/);
  assert.match(source, /state: 'INTERACTIVE'/);
  assert.match(source, /new_application_control: Boolean\(document\.querySelector\('#ide-new-app'\)\)/);
  assert.match(source, /creates_real_runnable_projects:/);
  assert.match(source, /if \(bootRecord\) return bootRecord/);
  assert.match(source, /frontend_is_authority: false/);
});
