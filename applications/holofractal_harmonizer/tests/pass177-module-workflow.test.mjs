import test from 'node:test';
import assert from 'node:assert/strict';

import { applicationTemplateList, materializeApplicationTemplate } from '../src/application-templates-runtime.mjs';
import { hash216Identity } from '../src/pass177/hash216-browser.mjs';
import {
  BUILTIN_MODULES,
  ModuleRegistry,
  createBuiltinModuleRegistry,
  materializeModules,
} from '../src/pass177/module-library.mjs';
import {
  DEFAULT_STAGE_EXECUTORS,
  MemoryCheckpointStore,
  WorkflowRegistry,
  WorkflowRunner,
  createPass177WorkflowRegistry,
} from '../src/pass177/workflow-engine.mjs';
import {
  PASS177_IDE_TEMPLATE_SOURCES,
  PASS177_TEMPLATES,
  TemplateRegistry,
  createPass177Project,
} from '../src/pass177/project-factory.mjs';

test('browser Hash216 implementation matches the Pass 150 Python algorithm', async () => {
  const identity = await hash216Identity({ name: 'Demo', template: 'web-application' });
  assert.equal(identity.positions.length, 216);
  assert.equal(identity.payloadSha256, '125e0111e098afcaa150cd8eff54f53d9afb8bce33a4ebeb9d0ee60a6147d57d');
  assert.equal(identity.root, '9847a07faff38f71d9b7210e52c9defc1fa711f504a2d90fff64a3e183614a6c');
  assert.equal(identity.positions[0], '6b588b629d9c47a651d39b44af87a46abf4b28a7ba565f6fc556f7b89286f25c');
  assert.equal(identity.positions.at(-1), '3af5f137b271303bcbe7520676329d02c4fc80835b89611d62ec8548a686aeba');
  assert.equal(identity.vm81EchoRequired, true);
});

test('built-in module library exposes broad plug-and-play capabilities', () => {
  const registry = createBuiltinModuleRegistry();
  assert.equal(registry.list().length, BUILTIN_MODULES.length);
  assert.ok(registry.list({ category: 'media' }).length >= 2);
  assert.ok(registry.list({ capability: 'testing' }).length >= 2);
  assert.ok(registry.list({ target: 'pwa' }).some((module) => module.id === 'pwa.offline'));
});

test('module resolution is dependency ordered and detects cycles', () => {
  const registry = new ModuleRegistry([
    { id: 'core.base', version: '1.0.0', label: 'Base', category: 'core' },
    { id: 'feature.one', version: '1.0.0', label: 'Feature', category: 'feature', dependencies: ['core.base'] },
  ]);
  assert.deepEqual(registry.resolve(['feature.one']).map((module) => module.id), ['core.base', 'feature.one']);

  const cyclic = new ModuleRegistry([
    { id: 'cycle.a', version: '1.0.0', label: 'A', category: 'test', dependencies: ['cycle.b'] },
    { id: 'cycle.b', version: '1.0.0', label: 'B', category: 'test', dependencies: ['cycle.a'] },
  ]);
  assert.throws(() => cyclic.resolve(['cycle.a']), /dependency cycle/);
});

test('module materialization injects real files and workflow stages', () => {
  const output = materializeModules(
    createBuiltinModuleRegistry(),
    ['pwa.offline', 'test.browser-smoke', 'package.source-zip'],
    { projectName: 'Field Notes', projectSlug: 'field-notes' },
  );
  const paths = output.files.map((file) => file.path);
  assert.ok(paths.includes('manifest.webmanifest'));
  assert.ok(paths.includes('service-worker.js'));
  assert.ok(paths.includes('tests/smoke.mjs'));
  assert.match(output.files.find((file) => file.path === 'service-worker.js').content, /field-notes-v1/);
  assert.ok(output.workflowStages.includes('package-source-zip'));
});

test('template catalog covers browser, PWA, data, simulation, media, service, and CLI modalities', () => {
  const registry = new TemplateRegistry();
  assert.equal(registry.list().length, PASS177_TEMPLATES.length);
  for (const family of ['web-application', 'progressive-web-application', 'dashboard', 'game-and-simulation', 'multimodal-media', 'service', 'command-line']) {
    assert.ok(registry.list({ family }).length >= 1, `missing ${family}`);
  }
  assert.equal(Object.keys(PASS177_IDE_TEMPLATE_SOURCES).length, 5);
});

test('project generation is deterministic and emits an editable, Hash216-bound project', async () => {
  const first = await createPass177Project({ templateId: 'offline-pwa', name: 'Field Notes' });
  const second = await createPass177Project({ templateId: 'offline-pwa', name: 'Field Notes' });
  assert.equal(first.identity.root, second.identity.root);
  assert.equal(first.manifest.identity.root, first.identity.root);
  assert.equal(first.manifest.entrypoint, 'index.html');
  assert.ok(first.files.some((file) => file.path === 'hhs.project.json'));
  assert.ok(first.files.some((file) => file.path === 'manifest.webmanifest'));
  assert.ok(first.files.some((file) => file.path === 'tests/smoke.mjs'));
  assert.ok(first.files.every((file) => file.dirty === false));

  const changed = await createPass177Project({ templateId: 'offline-pwa', name: 'Different Notes' });
  assert.notEqual(first.identity.root, changed.identity.root);
});

test('workflow engine validates, tests, builds, and packages a generated project', async () => {
  const project = await createPass177Project({ templateId: 'modular-web-application', name: 'Workflow Demo' });
  const runner = new WorkflowRunner({
    registry: createPass177WorkflowRegistry(),
    executors: DEFAULT_STAGE_EXECUTORS,
    checkpointStore: new MemoryCheckpointStore(),
    now: (() => { let tick = 0; return () => `2026-07-31T12:00:${String(tick++).padStart(2, '0')}Z`; })(),
  });
  const result = await runner.run(project.manifest.workflow.id, { project }, { runId: 'workflow-demo' });
  assert.equal(result.status, 'succeeded');
  assert.equal(result.stageStates['package-source-zip'].output.format, 'zip');
  assert.equal(result.stageStates['package-source-zip'].output.independentOfCompilation, true);
  assert.ok(result.checkpoint >= 6);
});

test('failed workflows can resume from repository-visible checkpoint state', async () => {
  const registry = new WorkflowRegistry([{
    id: 'resume.workflow', version: '1.0.0', stages: [
      { id: 'prepare', uses: 'prepare' },
      { id: 'finish', uses: 'finish' },
    ],
  }]);
  const checkpointStore = new MemoryCheckpointStore();
  const first = new WorkflowRunner({ registry, checkpointStore, executors: {
    prepare: async () => ({ prepared: true }),
    finish: async () => { throw new Error('temporary failure'); },
  } });
  const failed = await first.run('resume.workflow', {}, { runId: 'resume-1' });
  assert.equal(failed.status, 'failed');
  assert.equal(failed.stageStates.prepare.status, 'succeeded');

  const second = new WorkflowRunner({ registry, checkpointStore, executors: {
    prepare: async () => { throw new Error('completed stages must not rerun'); },
    finish: async () => ({ complete: true }),
  } });
  const resumed = await second.run('resume.workflow', {}, { runId: 'resume-1', resume: true });
  assert.equal(resumed.status, 'succeeded');
  assert.equal(resumed.stageStates.prepare.attempts, 1);
  assert.deepEqual(resumed.stageStates.finish.output, { complete: true });
});

test('Pass 177 browser templates are wired into the existing IDE template runtime', () => {
  const ids = new Set(applicationTemplateList().map((template) => template.id));
  for (const id of Object.keys(PASS177_IDE_TEMPLATE_SOURCES)) assert.ok(ids.has(id), `IDE catalog missing ${id}`);
  const pwa = materializeApplicationTemplate('offline-pwa');
  assert.ok(pwa.files.some((file) => file.path === 'manifest.webmanifest'));
  assert.ok(pwa.files.some((file) => file.path === 'service-worker.js'));
  assert.ok(pwa.files.every((file) => file.dirty === false));
});
