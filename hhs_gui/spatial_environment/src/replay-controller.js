function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export class ReplayController extends EventTarget {
  constructor({ tickMs = 500 } = {}) {
    super();
    this.tickMs = tickMs;
    this.events = [];
    this.cursor = -1;
    this.playing = false;
    this.speed = 1;
    this.timer = null;
    this.classification = "NON_AUTHORITATIVE_PRESENTATION_REPLAY";
  }

  load(events = [], { source = "projection-journal" } = {}) {
    this.pause();
    this.events = [...events].map(clone).sort((a, b) => {
      const left = Number(a.sequence ?? 0);
      const right = Number(b.sequence ?? 0);
      return left - right;
    });
    this.cursor = this.events.length ? 0 : -1;
    this.source = source;
    this.emit("loaded", this.snapshot());
    if (this.cursor >= 0) {
      this.emitCurrent("load");
    }
    return this.snapshot();
  }

  append(event) {
    this.events.push(clone(event));
    this.emit("timeline-change", this.snapshot());
  }

  play() {
    if (!this.events.length || this.playing) {
      return this.snapshot();
    }
    if (this.cursor >= this.events.length - 1) {
      this.cursor = 0;
    }
    this.playing = true;
    this.schedule();
    this.emit("state", this.snapshot());
    return this.snapshot();
  }

  pause() {
    this.playing = false;
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    this.emit("state", this.snapshot());
    return this.snapshot();
  }

  toggle() {
    return this.playing ? this.pause() : this.play();
  }

  schedule() {
    if (!this.playing) {
      return;
    }
    const delay = Math.max(40, this.tickMs / this.speed);
    this.timer = setTimeout(() => {
      if (!this.playing) {
        return;
      }
      if (this.cursor < this.events.length - 1) {
        this.cursor += 1;
        this.emitCurrent("play");
        this.schedule();
      } else {
        this.pause();
        this.emit("complete", this.snapshot());
      }
    }, delay);
  }

  seek(index) {
    if (!this.events.length) {
      this.cursor = -1;
      return null;
    }
    this.cursor = Math.max(0, Math.min(this.events.length - 1, Number(index) || 0));
    this.emitCurrent("seek");
    this.emit("state", this.snapshot());
    return clone(this.events[this.cursor]);
  }

  step(delta = 1) {
    return this.seek(this.cursor + delta);
  }

  setSpeed(speed) {
    this.speed = Math.max(0.25, Math.min(8, Number(speed) || 1));
    if (this.playing) {
      clearTimeout(this.timer);
      this.schedule();
    }
    this.emit("state", this.snapshot());
    return this.speed;
  }

  emitCurrent(reason) {
    const event = this.events[this.cursor];
    if (!event) {
      return;
    }
    this.emit("frame", {
      classification: this.classification,
      reason,
      cursor: this.cursor,
      total: this.events.length,
      event: clone(event)
    });
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_REPLAY_STATE_V3",
      classification: this.classification,
      source: this.source ?? null,
      playing: this.playing,
      speed: this.speed,
      cursor: this.cursor,
      total: this.events.length,
      current: this.cursor >= 0 ? clone(this.events[this.cursor]) : null
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }
}
