import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(new URL('..', import.meta.url).pathname);
const read = (path) => readFileSync(resolve(root, path), 'utf8');

test('public boot awaits the complete application experience before lower hydration', () => {
  const boot = read('src/public-boot.mjs');
  const experience = boot.indexOf('const applicationExperience = launch(');
  const browser = boot.indexOf('const browser = applicationExperience.then');
  const integration = boot.indexOf('const productionIntegration = applicationExperience.then');
  const visual = boot.indexOf('const visualIDE = applicationExperience.then');
  const workflow = boot.indexOf('const workflowDefault = browser.then');

  assert.ok(experience >= 0);
  assert.ok(experience < browser);
  assert.ok(experience < integration);
  assert.ok(experience < visual);
  assert.ok(browser < workflow);
  assert.match(boot, /async \(module\) => \{\s*const result = await module\.startApplicationExperience\(\)/);
  assert.match(boot, /HHS_APPLICATION_EXPERIENCE_NOT_INTERACTIVE/);
  assert.match(boot, /application_experience_awaited_before_hydration: true/);
  assert.match(boot, /critical_surface_reasserted_after_settlement: true/);
  assert.match(boot, /await experienceModule\.startApplicationExperience\(\)/);
});

test('production startup awaits and reasserts the critical application surface', () => {
  const coordinator = read('src/production-startup-coordinator.mjs');
  assert.match(coordinator, /async function startProductionSurface\(\)/);
  assert.match(coordinator, /const applicationExperience = await startApplicationExperience\(\)/);
  assert.match(coordinator, /await publicBoot\.applicationExperience/);
  assert.match(coordinator, /await publicBoot\.allSettled/);
  assert.match(coordinator, /await startApplicationExperience\(\)/);
  assert.match(coordinator, /window\.HHSProductionStartupReady = startupReady/);
  assert.match(coordinator, /HHS_PRODUCTION_SURFACE_FAILED/);
});

test('preview readiness is bound before hydration and accepts only the active frame source', () => {
  const coordinator = read('src/production-startup-coordinator.mjs');
  const readiness = read('src/preview-readiness.mjs');
  const smoke = read('ux_lab/full_application_smoke.py');

  assert.match(coordinator, /import \{ initPreviewReadiness \} from '\.\/preview-readiness\.mjs'/);
  assert.ok(coordinator.indexOf('initPreviewReadiness();') < coordinator.indexOf('startProductionSurface()'));
  assert.match(coordinator, /application_preview_readiness_bound_before_hydration: true/);
  assert.match(readiness, /event\.source !== frame\.contentWindow/);
  assert.match(readiness, /payload\.source !== 'hhs-application-preview'/);
  assert.match(readiness, /frame\.dataset\.previewState = state/);
  assert.match(readiness, /frame\.dataset\.previewReady = state === 'READY' \? 'true' : 'false'/);
  assert.match(readiness, /payload\.kind === 'ready'/);
  assert.match(readiness, /payload\.kind === 'error'/);
  assert.match(smoke, /data-preview-state/);
  assert.match(smoke, /data-preview-ready/);
  assert.match(smoke, /APPLICATION_PREVIEW_FRAME_READY/);
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
