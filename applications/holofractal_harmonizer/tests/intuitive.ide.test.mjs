import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const root = new URL('../', import.meta.url);
const read = (path) => readFile(new URL(path, root), 'utf8');

test('primary IDE boots intuitive workflow, integrated assistant, and workbench', async () => {
  const source = await read('src/visual-ide.mjs');
  assert.match(source, /import \{ initProjectLifecycle \} from '\.\/project-lifecycle\.mjs'/);
  assert.match(source, /import \{ initIntegratedWorkbench \} from '\.\/integrated-workbench\.mjs'/);
  assert.match(source, /import \{ initIntegratedAssistant \} from '\.\/integrated-assistant\.mjs'/);
  assert.match(source, /import \{ initIntuitiveIDE \} from '\.\/intuitive-ide\.mjs'/);
  assert.match(source, /safeInit\('project-lifecycle', initProjectLifecycle\)/);
  assert.match(source, /safeInit\('integrated-assistant', initIntegratedAssistant, \{ optional: true \}\)/);
  assert.match(source, /function scheduleOptionalProjectionHydration\(\)/);
  assert.match(source, /\['integrated-workbench', initIntegratedWorkbench\]/);
  assert.match(source, /\['intuitive-ide', initIntuitiveIDE\]/);
  assert.match(source, /void safeInit\(name, initializer, \{ optional: true \}\)/);
  assert.match(source, /window\.setTimeout\(\(\) => \{/);
  assert.match(source, /async function bootVisualIDE\(\)/);
  assert.match(source, /return stability\.boot\(\[/);
  assert.match(source, /const visualIdeBootPromise = bootVisualIDE\(\)/);
  assert.match(source, /window\.HHSVisualIDEBoot = visualIdeBootPromise/);
  assert.doesNotMatch(source, /^await stability\.boot\(\[/m);
  assert.match(source, /stage: 'EDITOR_READY'/);
  assert.match(source, /stage: 'INTERACTIVE'/);
});

test('beginner workflow is application-oriented and non-destructive', async () => {
  const source = await read('src/intuitive-ide.mjs');
  for (const label of ['New App', 'Add Files', 'Add Folder', 'Build & Preview', 'Test', 'Export', 'Ask Assistant']) {
    assert.ok(source.includes(label), `missing primary workflow label: ${label}`);
  }
  assert.match(source, /collisionSafePath/);
  assert.match(source, /Existing project files will never be replaced/);
  assert.match(source, /existing_files_are_never_silently_replaced:\s*true/);
  assert.match(source, /system_knowledge_required:\s*false/);
  assert.match(source, /checkpoint\(/);
  assert.match(source, /undoSafeChange/);
  assert.match(source, /event\.stopImmediatePropagation\(\)/);
});

test('application output and multimodal preview remain real IDE panes', async () => {
  const workbench = await read('src/integrated-workbench.mjs');
  assert.match(workbench, /Application Preview/);
  assert.match(workbench, /iframe/);
  assert.match(workbench, /audio/);
  assert.match(workbench, /video/);
  assert.match(workbench, /application\/pdf/);
  assert.match(workbench, /project-local CSS and JavaScript/);
});

test('natural-language assistant is persistently reachable from desktop and mobile IDE', async () => {
  const assistant = await read('src/integrated-assistant.mjs');
  assert.match(assistant, /ide-menu-assistant/);
  assert.match(assistant, /ide-mobile-assistant/);
  assert.match(assistant, /ide-assistant-fab/);
  assert.match(assistant, /HHSAssistant\?\.refreshStatus/);
  assert.match(assistant, /ide_remains_primary_surface:\s*true/);
});

test('warm theme and all integrated IDE layers bootstrap independently', async () => {
  const source = await read('src/theme-bootstrap.mjs');
  for (const stylesheet of [
    'harmonic-studio-theme.css',
    'integrated-workbench.css',
    'integrated-assistant.css',
    'intuitive-ide.css',
  ]) assert.ok(source.includes(stylesheet), `missing stylesheet bootstrap: ${stylesheet}`);
});
