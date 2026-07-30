import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { APPLICATION_TEMPLATES, materializeApplicationTemplate } from '../src/application-templates.mjs';

const root = new URL('../', import.meta.url);
const source = async (path) => readFile(new URL(path, root), 'utf8');

const required = ['web', 'pong', 'calculator', 'puzzle', 'document', 'audio', 'video', 'automation'];

test('application gallery contains real representative project classes', () => {
  assert.deepEqual(Object.keys(APPLICATION_TEMPLATES), required);
  for (const id of required) {
    const project = materializeApplicationTemplate(id);
    assert.equal(project.id, id);
    assert.ok(project.files.length >= 3);
    assert.ok(project.files.some((file) => file.path === project.entrypoint));
    assert.ok(project.files.every((file) => typeof file.content === 'string' && file.content.length > 0));
  }
});

test('game, calculator, document, audio and video starters contain executable behavior', () => {
  const pong = JSON.stringify(materializeApplicationTemplate('pong'));
  const calculator = JSON.stringify(materializeApplicationTemplate('calculator'));
  const puzzle = JSON.stringify(materializeApplicationTemplate('puzzle'));
  const documentProject = JSON.stringify(materializeApplicationTemplate('document'));
  const audio = JSON.stringify(materializeApplicationTemplate('audio'));
  const video = JSON.stringify(materializeApplicationTemplate('video'));
  assert.match(pong, /requestAnimationFrame/);
  assert.match(pong, /pointermove/);
  assert.match(calculator, /evaluate/);
  assert.match(puzzle, /solvableShuffle/);
  assert.match(documentProject, /contenteditable/);
  assert.match(documentProject, /Download TXT/);
  assert.match(audio, /AudioContext/);
  assert.match(audio, /MediaRecorder/);
  assert.match(video, /captureStream/);
  assert.match(video, /MediaRecorder/);
});

test('full IDE initializes application studio and deployable browser compiler', async () => {
  const ide = await source('src/visual-ide.mjs');
  const studio = await source('src/application-studio.mjs');
  const compiler = await source('src/deployable-app-compiler.mjs');
  const index = await source('index.html');
  assert.match(ide, /initApplicationStudio/);
  assert.match(ide, /initDeployableAppCompiler/);
  assert.match(studio, /Pong, calculator, puzzle, document, audio, video/);
  assert.match(compiler, /HHS_DEPLOYABLE_BROWSER_APPLICATION_V1/);
  assert.match(compiler, /Download App ZIP/);
  assert.match(index, /application-studio\.css/);
  assert.match(index, /Full Multimodal Application IDE/);
});
