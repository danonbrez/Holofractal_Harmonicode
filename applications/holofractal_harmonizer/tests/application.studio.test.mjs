import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { APPLICATION_TEMPLATES, materializeApplicationTemplate } from '../src/application-templates-runtime.mjs';

const root = new URL('../', import.meta.url);
const source = async (path) => readFile(new URL(path, root), 'utf8');

const required = ['web', 'pong', 'calculator', 'puzzle', 'document', 'audio', 'video', 'automation', 'harmonic-puzzle', 'platformer'];
const pass177Required = ['modular-web-application', 'offline-pwa', 'csv-data-explorer', 'canvas-simulation', 'local-media-studio'];

test('application gallery contains real representative project classes', () => {
  const templateIds = Object.keys(APPLICATION_TEMPLATES);
  assert.deepEqual(templateIds.slice(0, required.length), required);
  assert.deepEqual(templateIds.slice(required.length), pass177Required);
  for (const id of [...required, ...pass177Required]) {
    const project = materializeApplicationTemplate(id);
    assert.equal(project.id, id);
    assert.ok(project.files.length >= 3);
    assert.ok(project.files.some((file) => file.path === project.entrypoint));
    assert.ok(project.files.every((file) => typeof file.content === 'string' && file.content.length > 0));
  }
});

test('game, calculator, document, audio and video starters contain executable behavior', () => {
  const pong = JSON.stringify(materializeApplicationTemplate('pong'));
  const calculatorProject = materializeApplicationTemplate('calculator');
  const calculator = JSON.stringify(calculatorProject);
  const puzzle = JSON.stringify(materializeApplicationTemplate('puzzle'));
  const harmonicProject = materializeApplicationTemplate('harmonic-puzzle');
  const harmonic = JSON.stringify(harmonicProject);
  const platformerProject = materializeApplicationTemplate('platformer');
  const platformer = JSON.stringify(platformerProject);
  const documentProjectObject = materializeApplicationTemplate('document');
  const documentProject = JSON.stringify(documentProjectObject);
  const audio = JSON.stringify(materializeApplicationTemplate('audio'));
  const video = JSON.stringify(materializeApplicationTemplate('video'));
  assert.match(pong, /requestAnimationFrame/);
  assert.match(pong, /pointermove/);
  assert.match(calculator, /evaluate/);
  assert.match(puzzle, /solvableShuffle/);
  assert.match(harmonic, /HarmonicPuzzleModel/);
  assert.match(harmonic, /HarmonicRenderer/);
  assert.match(platformer, /__HHS_CAPTURE_STEP__/);
  assert.match(platformer, /Checkpoint synchronized/);
  assert.match(platformer, /data-action/);
  assert.match(platformer, /JUMP/);
  assert.match(documentProject, /contenteditable/);
  assert.match(documentProject, /Download TXT/);
  assert.match(documentProject, /autosave available after export/);
  assert.match(audio, /AudioContext/);
  assert.match(audio, /MediaRecorder/);
  assert.match(video, /captureStream/);
  assert.match(video, /MediaRecorder/);
  const calculatorSource = calculatorProject.files.find((file) => file.path.endsWith('/app.js')).content;
  const harmonicSource = harmonicProject.files.find((file) => file.path.endsWith('/app.js')).content;
  const platformerSource = platformerProject.files.find((file) => file.path.endsWith('/app.js')).content;
  const documentSource = documentProjectObject.files.find((file) => file.path.endsWith('/app.js')).content;
  assert.doesNotThrow(() => new Function(calculatorSource));
  assert.doesNotThrow(() => new Function(harmonicSource));
  assert.doesNotThrow(() => new Function(platformerSource));
  assert.doesNotThrow(() => new Function(documentSource));
});

test('full IDE initializes application studio and deployable browser compiler', async () => {
  const ide = await source('src/visual-ide.mjs');
  const studio = await source('src/application-studio.mjs');
  const compiler = await source('src/deployable-app-compiler.mjs');
  const index = await source('index.html');
  assert.match(ide, /initApplicationStudio/);
  assert.match(ide, /initDeployableAppCompiler/);
  assert.match(studio, /Pong, calculator, puzzle, document, audio, video/);
  assert.match(studio, /application-templates-runtime/);
  assert.match(studio, /function schedulePreviewHydration\(\)/);
  assert.match(studio, /window\.setTimeout\(\(\) =>/);
  assert.match(studio, /preview_hydration_deferred:\s*true/);
  assert.match(studio, /preview_hydration_is_deferred:\s*true/);
  assert.doesNotMatch(studio, /openBottomTab\('preview'\);\s*window\.HHSIntegratedWorkbench\?\.preview\?\.\(\)/);
  assert.match(compiler, /HHS_DEPLOYABLE_BROWSER_APPLICATION_V1/);
  assert.match(compiler, /Download App ZIP/);
  assert.match(index, /application-studio\.css/);
  assert.match(index, /Full Multimodal Application IDE/);
});
