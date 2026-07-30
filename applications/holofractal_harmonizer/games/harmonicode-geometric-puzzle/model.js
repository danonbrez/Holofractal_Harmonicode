export const LO_SHU_TARGET = Object.freeze([4, 9, 2, 3, 5, 7, 8, 1, 6]);

export const RESONANCE_LINES = Object.freeze([
  Object.freeze({ id: 'row-1', label: 'Upper triad', short: 'R1', indices: Object.freeze([0, 1, 2]) }),
  Object.freeze({ id: 'row-2', label: 'Middle triad', short: 'R2', indices: Object.freeze([3, 4, 5]) }),
  Object.freeze({ id: 'row-3', label: 'Lower triad', short: 'R3', indices: Object.freeze([6, 7, 8]) }),
  Object.freeze({ id: 'col-1', label: 'Left pillar', short: 'C1', indices: Object.freeze([0, 3, 6]) }),
  Object.freeze({ id: 'col-2', label: 'Center pillar', short: 'C2', indices: Object.freeze([1, 4, 7]) }),
  Object.freeze({ id: 'col-3', label: 'Right pillar', short: 'C3', indices: Object.freeze([2, 5, 8]) }),
  Object.freeze({ id: 'diag-main', label: 'Falling diagonal', short: 'D↘', indices: Object.freeze([0, 4, 8]) }),
  Object.freeze({ id: 'diag-anti', label: 'Rising diagonal', short: 'D↙', indices: Object.freeze([2, 4, 6]) }),
]);

export const MOVE_DEFINITIONS = Object.freeze([
  ...RESONANCE_LINES,
  Object.freeze({ id: 'orbit', label: 'Outer orbit', short: 'O', indices: Object.freeze([0, 1, 2, 5, 8, 7, 6, 3]) }),
]);

export const LEVELS = Object.freeze([
  Object.freeze({ id: 1, name: 'Triad Opening', scramble: 4, par: 4, seed: 4092 }),
  Object.freeze({ id: 2, name: 'Reciprocal Paths', scramble: 6, par: 6, seed: 3571 }),
  Object.freeze({ id: 3, name: 'Lo Shu Manifold', scramble: 8, par: 8, seed: 8164 }),
  Object.freeze({ id: 4, name: 'Hash72 Lattice', scramble: 10, par: 10, seed: 7292 }),
  Object.freeze({ id: 5, name: 'VM81 Phase Field', scramble: 12, par: 12, seed: 5184 }),
  Object.freeze({ id: 6, name: 'Recursion Closure', scramble: 15, par: 15, seed: 8172 }),
]);

const MOVE_BY_ID = new Map(MOVE_DEFINITIONS.map((move) => [move.id, move]));
export const STORAGE_KEY = 'hhs:harmonicode-geometric-puzzle:v1';

function cloneBoard(board) {
  return [...board];
}

export function boardKey(board) {
  return board.join('');
}

export function isPermutation(board) {
  return Array.isArray(board)
    && board.length === 9
    && [...board].sort((a, b) => a - b).every((value, index) => value === index + 1);
}

export function rotateIndices(board, indices, direction = 1) {
  if (!isPermutation(board)) throw new TypeError('board must be a permutation of 1..9');
  if (!Array.isArray(indices) || indices.length < 2) throw new TypeError('indices must define a rotatable path');
  const next = cloneBoard(board);
  const normalizedDirection = direction >= 0 ? 1 : -1;
  for (let offset = 0; offset < indices.length; offset += 1) {
    const source = indices[offset];
    const target = indices[(offset + normalizedDirection + indices.length) % indices.length];
    next[target] = board[source];
  }
  return next;
}

export function getMoveDefinition(moveId) {
  return MOVE_BY_ID.get(moveId) ?? null;
}

export function applyNamedMove(board, moveId, direction = 1) {
  const move = MOVE_BY_ID.get(moveId);
  if (!move) throw new RangeError(`unknown move: ${moveId}`);
  return rotateIndices(board, move.indices, direction);
}

export function evaluateBoard(board) {
  if (!isPermutation(board)) throw new TypeError('board must be a permutation of 1..9');
  const lineSums = RESONANCE_LINES.map((line) => line.indices.reduce((sum, index) => sum + board[index], 0));
  const resonantLines = lineSums.filter((sum) => sum === 15).length;
  const canonicalMatches = board.reduce((count, value, index) => count + Number(value === LO_SHU_TARGET[index]), 0);
  const reciprocalPairs = [[0, 8], [1, 7], [2, 6], [3, 5]]
    .filter(([left, right]) => board[left] + board[right] === 10).length;
  const score = (resonantLines * 9) + (canonicalMatches * 8);
  return Object.freeze({
    lineSums: Object.freeze(lineSums),
    resonantLines,
    canonicalMatches,
    reciprocalPairs,
    score,
    solved: score === 144,
  });
}

export function createRng(seed) {
  let value = Number(seed) >>> 0;
  return () => {
    value += 0x6D2B79F5;
    let t = value;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function createScramble(level, seedOverride) {
  const config = typeof level === 'number' ? LEVELS[level] : level;
  if (!config) throw new RangeError('level does not exist');
  const seed = Number(seedOverride ?? config.seed) >>> 0;
  const random = createRng(seed);
  let board = cloneBoard(LO_SHU_TARGET);
  const applied = [];
  let previous = null;
  for (let step = 0; step < config.scramble; step += 1) {
    let move;
    let direction;
    do {
      move = MOVE_DEFINITIONS[Math.floor(random() * MOVE_DEFINITIONS.length)];
      direction = random() >= 0.5 ? 1 : -1;
    } while (previous && previous.moveId === move.id && previous.direction === -direction);
    board = applyNamedMove(board, move.id, direction);
    applied.push(Object.freeze({ moveId: move.id, direction }));
    previous = applied.at(-1);
  }
  if (boardKey(board) === boardKey(LO_SHU_TARGET)) {
    board = applyNamedMove(board, 'orbit', 1);
    applied.push(Object.freeze({ moveId: 'orbit', direction: 1 }));
  }
  const solution = applied.toReversed().map((entry) => Object.freeze({ moveId: entry.moveId, direction: -entry.direction }));
  return Object.freeze({ board: Object.freeze(board), seed, applied: Object.freeze(applied), solution: Object.freeze(solution) });
}

function boardDistance(board) {
  const targetPosition = new Map(LO_SHU_TARGET.map((value, index) => [value, index]));
  return board.reduce((distance, value, index) => {
    const target = targetPosition.get(value);
    return distance + Math.abs(Math.floor(index / 3) - Math.floor(target / 3)) + Math.abs((index % 3) - (target % 3));
  }, 0);
}

export function suggestMove(board, previousMove = null) {
  const candidates = [];
  for (const move of MOVE_DEFINITIONS) {
    for (const direction of [-1, 1]) {
      if (previousMove && previousMove.moveId === move.id && previousMove.direction === -direction) continue;
      const next = applyNamedMove(board, move.id, direction);
      const evaluation = evaluateBoard(next);
      candidates.push({
        moveId: move.id,
        direction,
        score: evaluation.score,
        resonantLines: evaluation.resonantLines,
        reciprocalPairs: evaluation.reciprocalPairs,
        distance: boardDistance(next),
      });
    }
  }
  candidates.sort((left, right) => (
    right.score - left.score
    || right.resonantLines - left.resonantLines
    || right.reciprocalPairs - left.reciprocalPairs
    || left.distance - right.distance
    || left.moveId.localeCompare(right.moveId)
    || right.direction - left.direction
  ));
  return Object.freeze(candidates[0]);
}

export class HarmonicPuzzleModel extends EventTarget {
  constructor({ levelIndex = 0, seed } = {}) {
    super();
    this.levelIndex = Math.max(0, Math.min(LEVELS.length - 1, Number(levelIndex) || 0));
    this.seed = seed;
    this.board = cloneBoard(LO_SHU_TARGET);
    this.initialBoard = cloneBoard(LO_SHU_TARGET);
    this.moves = 0;
    this.history = [];
    this.selectedMoveId = 'row-1';
    this.completedLevels = new Set();
    this.newPuzzle(this.levelIndex, seed);
  }

  get level() { return LEVELS[this.levelIndex]; }
  get evaluation() { return evaluateBoard(this.board); }
  get canUndo() { return this.history.length > 0; }

  emit(type, detail = {}) {
    this.dispatchEvent(new CustomEvent(type, { detail: { ...detail, snapshot: this.snapshot() } }));
  }

  newPuzzle(levelIndex = this.levelIndex, seed = undefined) {
    this.levelIndex = Math.max(0, Math.min(LEVELS.length - 1, Number(levelIndex) || 0));
    const config = LEVELS[this.levelIndex];
    const scramble = createScramble(config, seed ?? config.seed);
    this.seed = scramble.seed;
    this.initialBoard = cloneBoard(scramble.board);
    this.board = cloneBoard(scramble.board);
    this.referenceSolution = scramble.solution.map((entry) => ({ ...entry }));
    this.moves = 0;
    this.history = [];
    this.selectedMoveId = 'row-1';
    this.emit('reset', { reason: 'new-puzzle' });
    return this.snapshot();
  }

  randomizeSeed() {
    const entropy = ((Date.now() & 0xffffffff) ^ Math.floor(Math.random() * 0xffffffff)) >>> 0;
    return this.newPuzzle(this.levelIndex, entropy || 1);
  }

  applyMove(moveId, direction = 1) {
    const normalizedDirection = direction >= 0 ? 1 : -1;
    const before = cloneBoard(this.board);
    this.board = applyNamedMove(this.board, moveId, normalizedDirection);
    this.history.push({ board: before, moveId, direction: normalizedDirection });
    this.moves += 1;
    this.selectedMoveId = moveId;
    const evaluation = this.evaluation;
    this.emit('move', { moveId, direction: normalizedDirection, evaluation });
    if (evaluation.solved) {
      this.completedLevels.add(this.levelIndex);
      this.emit('solved', { evaluation });
    }
    return evaluation;
  }

  undo() {
    const previous = this.history.pop();
    if (!previous) return false;
    this.board = previous.board;
    this.moves = Math.max(0, this.moves - 1);
    this.selectedMoveId = previous.moveId;
    this.emit('undo', { moveId: previous.moveId });
    return true;
  }

  reset() {
    this.board = cloneBoard(this.initialBoard);
    this.moves = 0;
    this.history = [];
    this.emit('reset', { reason: 'manual-reset' });
  }

  hint() {
    const previous = this.history.at(-1) ?? null;
    const suggestion = suggestMove(this.board, previous);
    this.selectedMoveId = suggestion.moveId;
    this.emit('hint', { suggestion });
    return suggestion;
  }

  selectMove(moveId) {
    if (!MOVE_BY_ID.has(moveId)) return false;
    this.selectedMoveId = moveId;
    this.emit('selection', { moveId });
    return true;
  }

  snapshot() {
    return Object.freeze({
      schema: 'HHS_HARMONICODE_GEOMETRIC_PUZZLE_STATE_V1',
      levelIndex: this.levelIndex,
      seed: this.seed,
      board: Object.freeze(cloneBoard(this.board)),
      initialBoard: Object.freeze(cloneBoard(this.initialBoard)),
      moves: this.moves,
      selectedMoveId: this.selectedMoveId,
      completedLevels: Object.freeze([...this.completedLevels].sort((a, b) => a - b)),
      evaluation: this.evaluation,
    });
  }

  serialize() {
    return JSON.stringify(this.snapshot());
  }

  restore(serialized) {
    const value = typeof serialized === 'string' ? JSON.parse(serialized) : serialized;
    if (!value || value.schema !== 'HHS_HARMONICODE_GEOMETRIC_PUZZLE_STATE_V1') throw new TypeError('unsupported save state');
    if (!isPermutation(value.board) || !isPermutation(value.initialBoard)) throw new TypeError('invalid save board');
    this.levelIndex = Math.max(0, Math.min(LEVELS.length - 1, Number(value.levelIndex) || 0));
    this.seed = Number(value.seed) >>> 0;
    this.board = cloneBoard(value.board);
    this.initialBoard = cloneBoard(value.initialBoard);
    this.moves = Math.max(0, Number(value.moves) || 0);
    this.selectedMoveId = MOVE_BY_ID.has(value.selectedMoveId) ? value.selectedMoveId : 'row-1';
    this.completedLevels = new Set((value.completedLevels || []).filter((index) => Number.isInteger(index) && index >= 0 && index < LEVELS.length));
    this.history = [];
    this.emit('reset', { reason: 'restore' });
    return this.snapshot();
  }
}
