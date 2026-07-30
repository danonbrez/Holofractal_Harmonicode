import test from 'node:test';
import assert from 'node:assert/strict';
import {
  LO_SHU_TARGET,
  LEVELS,
  MOVE_DEFINITIONS,
  HarmonicPuzzleModel,
  applyNamedMove,
  boardKey,
  createScramble,
  evaluateBoard,
  isPermutation,
  suggestMove,
} from '../model.js';

test('canonical Lo Shu board reaches exact 144-point closure', () => {
  const result = evaluateBoard([...LO_SHU_TARGET]);
  assert.equal(result.score, 144);
  assert.equal(result.resonantLines, 8);
  assert.equal(result.canonicalMatches, 9);
  assert.equal(result.reciprocalPairs, 4);
  assert.equal(result.solved, true);
});

test('every legal move preserves the 1..9 permutation and has an exact inverse', () => {
  for (const move of MOVE_DEFINITIONS) {
    const moved = applyNamedMove([...LO_SHU_TARGET], move.id, 1);
    assert.equal(isPermutation(moved), true, move.id);
    const restored = applyNamedMove(moved, move.id, -1);
    assert.equal(boardKey(restored), boardKey(LO_SHU_TARGET), move.id);
  }
});

test('scrambles are deterministic and the recorded inverse sequence closes them', () => {
  for (const level of LEVELS) {
    const left = createScramble(level, level.seed);
    const right = createScramble(level, level.seed);
    assert.deepEqual(left.board, right.board);
    assert.notEqual(boardKey(left.board), boardKey(LO_SHU_TARGET));
    let board = [...left.board];
    for (const step of left.solution) board = applyNamedMove(board, step.moveId, step.direction);
    assert.equal(boardKey(board), boardKey(LO_SHU_TARGET), level.name);
  }
});

test('model supports move, undo, reset, and serialization without renderer state', () => {
  const model = new HarmonicPuzzleModel({ levelIndex: 2, seed: 12345 });
  const initial = boardKey(model.board);
  model.applyMove('orbit', 1);
  assert.notEqual(boardKey(model.board), initial);
  assert.equal(model.moves, 1);
  assert.equal(model.undo(), true);
  assert.equal(boardKey(model.board), initial);
  assert.equal(model.moves, 0);
  model.applyMove('row-1', 1);
  const serialized = model.serialize();
  const restored = new HarmonicPuzzleModel();
  restored.restore(serialized);
  assert.deepEqual(restored.board, model.board);
  assert.equal(restored.levelIndex, model.levelIndex);
  assert.equal(restored.moves, model.moves);
});

test('hint always returns a valid deterministic move', () => {
  const scramble = createScramble(LEVELS[4], 5184);
  const first = suggestMove([...scramble.board]);
  const second = suggestMove([...scramble.board]);
  assert.deepEqual(first, second);
  assert.ok(MOVE_DEFINITIONS.some((move) => move.id === first.moveId));
  assert.ok(first.direction === -1 || first.direction === 1);
});
