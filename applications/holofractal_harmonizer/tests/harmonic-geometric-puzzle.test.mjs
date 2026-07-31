import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import {
  HarmonicPuzzleModel,
  LEVELS,
  LO_SHU_TARGET,
  MOVE_DEFINITIONS,
  applyNamedMove,
  boardKey,
  createScramble,
  evaluateBoard,
} from '../games/harmonicode-geometric-puzzle/model.js';
import { HARMONIC_PUZZLE_TEMPLATE } from '../src/harmonic-puzzle-template.mjs';
import { applicationTemplateList, materializeApplicationTemplate } from '../src/application-templates-runtime.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const gameRoot = resolve(here, '../games/harmonicode-geometric-puzzle');

test('Harmonicode geometry closes only at the exact Lo Shu target', () => {
  const closure = evaluateBoard([...LO_SHU_TARGET]);
  assert.equal(closure.score, 144);
  assert.equal(closure.solved, true);
  const moved = applyNamedMove([...LO_SHU_TARGET], 'orbit', 1);
  assert.equal(evaluateBoard(moved).solved, false);
});

test('all levels produce deterministic solvable states', () => {
  for (const level of LEVELS) {
    const scramble = createScramble(level, level.seed);
    let board = [...scramble.board];
    for (const step of scramble.solution) board = applyNamedMove(board, step.moveId, step.direction);
    assert.equal(boardKey(board), boardKey(LO_SHU_TARGET), level.name);
  }
});

test('model state remains independent from canvas and DOM rendering', () => {
  const model = new HarmonicPuzzleModel({ levelIndex: 1, seed: 72 });
  const before = model.serialize();
  model.applyMove(MOVE_DEFINITIONS[0].id, 1);
  assert.notEqual(model.serialize(), before);
  model.undo();
  assert.deepEqual(model.board, model.initialBoard);
});

test('generated IDE template is byte-aligned with the served standalone game', async () => {
  const expected = new Map([
    ['harmonic-puzzle/index.html', await readFile(resolve(gameRoot, 'index.html'), 'utf8')],
    ['harmonic-puzzle/style.css', await readFile(resolve(gameRoot, 'style.css'), 'utf8')],
    ['harmonic-puzzle/README.md', await readFile(resolve(gameRoot, 'README.md'), 'utf8')],
  ]);
  assert.equal(HARMONIC_PUZZLE_TEMPLATE.files.length, expected.size + 1);
  for (const [path, , content] of HARMONIC_PUZZLE_TEMPLATE.files) {
    if (path.endsWith('/app.js')) {
      assert.match(content, /class HarmonicPuzzleModel/);
      assert.match(content, /class HarmonicRenderer/);
      assert.doesNotMatch(content, /^import\s/m);
    } else assert.equal(content, expected.get(path), path);
  }
});

test('application gallery exposes an editable runnable Harmonicode puzzle project', () => {
  const template = applicationTemplateList().find((entry) => entry.id === 'harmonic-puzzle');
  assert.ok(template);
  assert.equal(template.entrypoint, 'harmonic-puzzle/index.html');
  const project = materializeApplicationTemplate('harmonic-puzzle');
  assert.equal(project.files.length, 4);
  assert.ok(project.files.every((file) => file.dirty === true));
  assert.ok(project.files.every((file) => file.checkpoint === `Created from ${template.label} starter`));
  assert.match(project.files.find((file) => file.path.endsWith('/app.js')).content, /class HarmonicPuzzleModel/);
  assert.match(project.files.find((file) => file.path.endsWith('/app.js')).content, /class HarmonicRenderer/);
});
