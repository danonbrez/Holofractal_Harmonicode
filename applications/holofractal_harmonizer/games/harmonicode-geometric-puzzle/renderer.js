import { LO_SHU_TARGET, RESONANCE_LINES, getMoveDefinition } from './model.js';

export class HarmonicRenderer {
  constructor(canvas, model) {
    this.canvas = canvas;
    this.context = canvas.getContext('2d');
    this.model = model;
    this.activeAnimation = null;
    this.lastSize = 0;
    this.reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.resizeObserver = new ResizeObserver(() => this.draw());
    this.resizeObserver.observe(canvas);
  }

  sizeCanvas() {
    const rect = this.canvas.getBoundingClientRect();
    const size = Math.max(320, Math.floor(Math.min(rect.width || 900, rect.height || rect.width || 900)));
    const ratio = Math.min(devicePixelRatio || 1, 2);
    const pixelSize = Math.round(size * ratio);
    if (this.canvas.width !== pixelSize || this.canvas.height !== pixelSize) {
      this.canvas.width = pixelSize;
      this.canvas.height = pixelSize;
    }
    this.context.setTransform(ratio, 0, 0, ratio, 0, 0);
    this.lastSize = size;
    return size;
  }

  coordinates(size) {
    const margin = size * 0.19;
    const gap = (size - (margin * 2)) / 2;
    return Array.from({ length: 9 }, (_, index) => ({
      x: margin + ((index % 3) * gap),
      y: margin + (Math.floor(index / 3) * gap),
    }));
  }

  animate(moveId) {
    if (this.reduceMotion) {
      this.activeAnimation = null;
      this.draw();
      return;
    }
    this.activeAnimation = { moveId, started: performance.now() };
    const frame = () => {
      this.draw();
      if (this.activeAnimation) requestAnimationFrame(frame);
    };
    requestAnimationFrame(frame);
  }

  draw() {
    const size = this.sizeCanvas();
    const ctx = this.context;
    const points = this.coordinates(size);
    const evaluation = this.model.evaluation;
    const now = performance.now();
    let pulse = 0;
    if (this.activeAnimation) {
      const elapsed = now - this.activeAnimation.started;
      pulse = Math.max(0, 1 - (elapsed / 520));
      if (elapsed >= 520) this.activeAnimation = null;
    }

    const background = ctx.createRadialGradient(size * .5, size * .44, size * .04, size * .5, size * .5, size * .72);
    background.addColorStop(0, '#241b35');
    background.addColorStop(.55, '#100c19');
    background.addColorStop(1, '#07060b');
    ctx.fillStyle = background;
    ctx.fillRect(0, 0, size, size);

    ctx.save();
    ctx.translate(size / 2, size / 2);
    for (let ring = 0; ring < 3; ring += 1) {
      ctx.beginPath();
      ctx.arc(0, 0, size * (.22 + (ring * .115)), 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(156,124,255,${.16 - (ring * .03)})`;
      ctx.lineWidth = 1.2;
      ctx.stroke();
    }
    ctx.restore();

    RESONANCE_LINES.forEach((line, lineIndex) => {
      const resonant = evaluation.lineSums[lineIndex] === 15;
      const selected = this.model.selectedMoveId === line.id;
      ctx.beginPath();
      line.indices.forEach((index, pointIndex) => {
        const point = points[index];
        if (pointIndex === 0) ctx.moveTo(point.x, point.y);
        else ctx.lineTo(point.x, point.y);
      });
      ctx.lineCap = 'round';
      ctx.lineWidth = resonant ? size * .009 : selected ? size * .006 : size * .0035;
      ctx.strokeStyle = resonant ? `rgba(98,216,199,${.76 + pulse * .2})` : selected ? 'rgba(242,189,99,.72)' : 'rgba(116,96,143,.42)';
      ctx.shadowColor = resonant ? '#62d8c7' : selected ? '#f2bd63' : 'transparent';
      ctx.shadowBlur = resonant ? size * .025 : selected ? size * .014 : 0;
      ctx.stroke();
      ctx.shadowBlur = 0;
    });

    const orbit = getMoveDefinition('orbit');
    ctx.beginPath();
    orbit.indices.forEach((index, pointIndex) => {
      const point = points[index];
      if (pointIndex === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.closePath();
    ctx.lineWidth = this.model.selectedMoveId === 'orbit' ? size * .006 : size * .0025;
    ctx.strokeStyle = this.model.selectedMoveId === 'orbit' ? 'rgba(242,189,99,.76)' : 'rgba(156,124,255,.28)';
    ctx.stroke();

    points.forEach((point, index) => {
      const value = this.model.board[index];
      const canonical = value === LO_SHU_TARGET[index];
      const radius = size * (index === 4 ? .079 : .068);
      const gradient = ctx.createRadialGradient(point.x - radius * .25, point.y - radius * .3, radius * .12, point.x, point.y, radius);
      gradient.addColorStop(0, canonical ? '#9ff6e8' : '#f8dda4');
      gradient.addColorStop(.2, canonical ? '#42ae9d' : '#8c6330');
      gradient.addColorStop(1, canonical ? '#173e3a' : '#25192f');
      ctx.beginPath();
      ctx.arc(point.x, point.y, radius + (canonical ? pulse * size * .006 : 0), 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.shadowColor = canonical ? '#62d8c7' : '#9c7cff';
      ctx.shadowBlur = canonical ? size * .026 : size * .012;
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.lineWidth = canonical ? 3 : 1.5;
      ctx.strokeStyle = canonical ? '#b8fff3' : '#a98bc8';
      ctx.stroke();

      ctx.fillStyle = canonical ? '#06100f' : '#fff4dc';
      ctx.font = `800 ${Math.round(size * .066)}px system-ui`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(String(value), point.x, point.y - size * .002);
      ctx.font = `700 ${Math.max(10, Math.round(size * .018))}px system-ui`;
      ctx.fillStyle = canonical ? '#08352f' : '#b8a4c9';
      ctx.fillText(`target ${LO_SHU_TARGET[index]}`, point.x, point.y + radius * .58);
    });

    ctx.textAlign = 'center';
    ctx.fillStyle = '#c5b8d6';
    ctx.font = `700 ${Math.max(11, Math.round(size * .02))}px system-ui`;
    ctx.fillText(`RESONANCE ${evaluation.score}/144`, size / 2, size * .075);
    ctx.fillStyle = evaluation.solved ? '#62d8c7' : '#f2bd63';
    ctx.font = `800 ${Math.max(12, Math.round(size * .024))}px system-ui`;
    ctx.fillText(evaluation.solved ? 'Ω CLOSED' : 'Ω OPEN', size / 2, size * .925);
  }
}
