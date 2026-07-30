import {
  HarmonicPuzzleModel,
  LEVELS,
  MOVE_DEFINITIONS,
  STORAGE_KEY,
  getMoveDefinition,
} from './model.js';
import { HarmonicRenderer } from './renderer.js';
import { GameInput, SoundEngine } from './controls.js';

function safeLoad() {
  try { return localStorage.getItem(STORAGE_KEY); } catch { return null; }
}

function safeSave(value) {
  try { localStorage.setItem(STORAGE_KEY, value); return true; } catch { return false; }
}

function bootstrap() {
  const $ = (selector) => document.querySelector(selector);
  const model = new HarmonicPuzzleModel();
  const renderer = new HarmonicRenderer($('#game-canvas'), model);
  const sound = new SoundEngine();
  new GameInput($('#game-canvas'), model);

  const saved = safeLoad();
  if (saved) {
    try { model.restore(saved); } catch { /* Ignore incompatible or corrupted local state. */ }
  }

  for (const [index, level] of LEVELS.entries()) {
    const option = document.createElement('option');
    option.value = String(index);
    option.textContent = `${level.id}. ${level.name}`;
    $('#level-select').append(option);
  }

  MOVE_DEFINITIONS.forEach((move, index) => {
    const row = document.createElement('div');
    row.className = 'move-control';
    row.dataset.moveId = move.id;
    row.innerHTML = `<div class="move-label"><strong><span class="move-index">${index + 1}</span>${move.short} · ${move.label}</strong><small>${move.indices.map((cell) => cell + 1).join(' → ')}</small></div>`;
    const reverse = document.createElement('button');
    reverse.type = 'button';
    reverse.textContent = '↶';
    reverse.setAttribute('aria-label', `Rotate ${move.label} backward`);
    reverse.onclick = () => model.applyMove(move.id, -1);
    const forward = document.createElement('button');
    forward.type = 'button';
    forward.textContent = '↷';
    forward.setAttribute('aria-label', `Rotate ${move.label} forward`);
    forward.onclick = () => model.applyMove(move.id, 1);
    row.addEventListener('click', (event) => { if (event.target === row || event.target.closest('.move-label')) model.selectMove(move.id); });
    row.append(reverse, forward);
    $('#move-controls').append(row);
  });

  function renderUi(message) {
    const evaluation = model.evaluation;
    $('#score').textContent = `${evaluation.score} / 144`;
    $('#resonant-lines').textContent = `${evaluation.resonantLines} / 8`;
    $('#moves').textContent = `${model.moves} / ${model.level.par}`;
    $('#closure-state').textContent = evaluation.solved ? 'CLOSED' : 'OPEN';
    $('#closure-state').style.color = evaluation.solved ? 'var(--teal)' : 'var(--gold)';
    $('#level-select').value = String(model.levelIndex);
    $('#undo').disabled = !model.canUndo;
    $('#status').textContent = message || `${model.level.name}: ${evaluation.canonicalMatches}/9 cells canonical, ${evaluation.reciprocalPairs}/4 reciprocal pairs aligned.`;
    $('#game-canvas').setAttribute('aria-label', `Lo Shu lattice values ${model.board.join(', ')}. Resonance ${evaluation.score} of 144.`);
    document.querySelectorAll('.move-control').forEach((row) => row.classList.toggle('selected', row.dataset.moveId === model.selectedMoveId));
    renderer.draw();
    safeSave(model.serialize());
  }

  model.addEventListener('move', (event) => {
    const { moveId, direction, evaluation } = event.detail;
    renderer.animate(moveId);
    sound.move(direction, evaluation.score);
    const move = getMoveDefinition(moveId);
    renderUi(`${move.label} rotated ${direction > 0 ? 'forward' : 'backward'}. Resonance is ${evaluation.score}/144.`);
  });
  model.addEventListener('undo', () => renderUi('Previous phase rotation restored.'));
  model.addEventListener('reset', (event) => renderUi(event.detail.reason === 'restore' ? 'Saved lattice restored.' : 'Lattice reset to its initial pattern.'));
  model.addEventListener('selection', () => renderUi(`Selected ${getMoveDefinition(model.selectedMoveId).label}. Use ← or → to rotate.`));
  model.addEventListener('hint', (event) => {
    const suggestion = event.detail.suggestion;
    const move = getMoveDefinition(suggestion.moveId);
    sound.hint();
    renderUi(`Hint: rotate ${move.label} ${suggestion.direction > 0 ? 'forward ↷' : 'backward ↶'}.`);
  });
  model.addEventListener('solved', () => {
    sound.win();
    renderUi('Ω closure verified. Every harmonic path and canonical cell is aligned.');
    $('#win-title').textContent = `${model.level.name} stabilized`;
    const delta = model.moves - model.level.par;
    $('#win-summary').textContent = delta <= 0
      ? `Full 144-point closure in ${model.moves} moves — at or under the ${model.level.par}-move par.`
      : `Full 144-point closure in ${model.moves} moves. Par is ${model.level.par}; replay to compress the path.`;
    $('#next-level').hidden = model.levelIndex >= LEVELS.length - 1;
    if (!$('#win-dialog').open) $('#win-dialog').showModal();
  });

  $('#level-select').onchange = (event) => model.newPuzzle(Number(event.target.value));
  $('#undo').onclick = () => model.undo();
  $('#hint').onclick = () => model.hint();
  $('#reset').onclick = () => model.reset();
  $('#new-seed').onclick = () => model.randomizeSeed();
  $('#sound-toggle').onclick = (event) => {
    sound.enabled = !sound.enabled;
    event.currentTarget.setAttribute('aria-pressed', String(sound.enabled));
    event.currentTarget.textContent = sound.enabled ? 'Sound on' : 'Sound off';
    if (sound.enabled) sound.hint();
  };
  $('#next-level').onclick = () => {
    $('#win-dialog').close();
    model.newPuzzle(Math.min(LEVELS.length - 1, model.levelIndex + 1));
  };

  renderUi('Lattice initialized. Swipe the geometry or use a phase gate.');
  renderer.draw();

  window.HHSHarmonicPuzzle = Object.freeze({ model, renderer, levels: LEVELS, moves: MOVE_DEFINITIONS });
}

if (typeof document !== 'undefined') bootstrap();
