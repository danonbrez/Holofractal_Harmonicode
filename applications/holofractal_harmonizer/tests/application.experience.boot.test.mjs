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

test('application experience initializes real project creation in dependency order', () => {
  const source = read('src/application-experience.mjs');
  const lifecycle = source.indexOf("initialize('HHSProjectLifecycle'");
  const workbench = source.indexOf("initialize('HHSIntegratedWorkbench'");
  const intuitive = source.indexOf("initialize('HHSIntuitiveIDE'");
  const studio = source.indexOf("initialize('HHSApplicationStudio'");
  const compiler = source.indexOf("initialize('HHSDeployableAppCompiler'");
  assert.ok(lifecycle >= 0);
  assert.ok(lifecycle < workbench);
  assert.ok(workbench < intuitive);
  assert.ok(intuitive < studio);
  assert.ok(studio < compiler);
  assert.match(source, /new_application_control: Boolean\(document\.querySelector\('#ide-new-app'\)\)/);
  assert.match(source, /creates_real_runnable_projects:/);
  assert.match(source, /if \(bootRecord\) return bootRecord/);
  assert.match(source, /frontend_is_authority: false/);
});
