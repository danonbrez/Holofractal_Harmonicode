import { MOVE_DEFINITIONS } from './model.js';

export class SoundEngine {
  constructor() { this.enabled = true; this.context = null; }
  ensureContext() {
    if (!this.context) this.context = new AudioContext();
    if (this.context.state === 'suspended') void this.context.resume();
    return this.context;
  }
  tone(frequency, duration = .12, volume = .08, type = 'sine') {
    if (!this.enabled) return;
    try {
      const context = this.ensureContext();
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = type;
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(.0001, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(volume, context.currentTime + .012);
      gain.gain.exponentialRampToValueAtTime(.0001, context.currentTime + duration);
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start();
      oscillator.stop(context.currentTime + duration + .03);
    } catch { /* Audio is optional in sandboxed previews. */ }
  }
  move(direction, score) { this.tone(210 + (score * 1.7) + (direction > 0 ? 38 : 0), .1, .055, 'triangle'); }
  hint() { this.tone(523.25, .16, .05, 'sine'); }
  win() {
    [392, 523.25, 659.25, 783.99].forEach((frequency, index) => setTimeout(() => this.tone(frequency, .28, .07, 'sine'), index * 95));
  }
}

export class GameInput {
  constructor(canvas, model) {
    this.canvas = canvas;
    this.model = model;
    this.start = null;
    canvas.addEventListener('pointerdown', (event) => this.pointerDown(event));
    canvas.addEventListener('pointerup', (event) => this.pointerUp(event));
    canvas.addEventListener('pointercancel', () => { this.start = null; });
    addEventListener('keydown', (event) => this.keyDown(event));
  }

  normalized(event) {
    const rect = this.canvas.getBoundingClientRect();
    return { x: (event.clientX - rect.left) / rect.width, y: (event.clientY - rect.top) / rect.height };
  }

  pointerDown(event) {
    this.canvas.setPointerCapture?.(event.pointerId);
    this.start = this.normalized(event);
  }

  pointerUp(event) {
    if (!this.start) return;
    const end = this.normalized(event);
    const dx = end.x - this.start.x;
    const dy = end.y - this.start.y;
    const magnitude = Math.hypot(dx, dy);
    const start = this.start;
    this.start = null;
    if (magnitude < .08) return;

    let moveId;
    let direction;
    if (Math.abs(dx) > Math.abs(dy) * 1.35) {
      const row = Math.max(0, Math.min(2, Math.floor(start.y * 3)));
      moveId = `row-${row + 1}`;
      direction = dx > 0 ? 1 : -1;
    } else if (Math.abs(dy) > Math.abs(dx) * 1.35) {
      const column = Math.max(0, Math.min(2, Math.floor(start.x * 3)));
      moveId = `col-${column + 1}`;
      direction = dy > 0 ? 1 : -1;
    } else if (Math.sign(dx) === Math.sign(dy)) {
      moveId = 'diag-main';
      direction = dx > 0 ? 1 : -1;
    } else {
      moveId = 'diag-anti';
      direction = dx > 0 ? 1 : -1;
    }
    this.model.applyMove(moveId, direction);
  }

  keyDown(event) {
    const active = document.activeElement;
    if (active && /^(INPUT|SELECT|TEXTAREA)$/.test(active.tagName)) return;
    const number = Number(event.key);
    if (Number.isInteger(number) && number >= 1 && number <= MOVE_DEFINITIONS.length) {
      event.preventDefault();
      this.model.selectMove(MOVE_DEFINITIONS[number - 1].id);
      return;
    }
    if (event.key === 'ArrowLeft' || event.key.toLowerCase() === 'q') {
      event.preventDefault();
      this.model.applyMove(this.model.selectedMoveId, -1);
    } else if (event.key === 'ArrowRight' || event.key.toLowerCase() === 'e') {
      event.preventDefault();
      this.model.applyMove(this.model.selectedMoveId, 1);
    } else if (event.key.toLowerCase() === 'u') {
      event.preventDefault();
      this.model.undo();
    } else if (event.key.toLowerCase() === 'h') {
      event.preventDefault();
      this.model.hint();
    } else if (event.key.toLowerCase() === 'r') {
      event.preventDefault();
      this.model.reset();
    }
  }
}
