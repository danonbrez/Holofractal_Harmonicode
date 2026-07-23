const clone = (value) => JSON.parse(JSON.stringify(value));
const round = (value) => Math.round(Number(value) * 1e9) / 1e9;

export class SimulationEngine extends EventTarget {
  constructor({ scene, fixedDt = 1 / 60, maximumBatchSteps = 240 } = {}) {
    super();
    if (!scene) throw new Error("SCENE_GRAPH_REQUIRED");
    this.scene = scene;
    this.fixedDt = fixedDt;
    this.maximumBatchSteps = maximumBatchSteps;
    this.tick = 0;
    this.elapsed = 0;
    this.running = false;
    this.timer = null;
    this.lastEnergy = 0;
  }

  step(count = 1) {
    const steps = Math.max(1, Math.min(this.maximumBatchSteps, Math.floor(Number(count) || 1)));
    for (let index = 0; index < steps; index += 1) this.integrate();
    const state = this.snapshot();
    this.emit("step", state);
    return state;
  }

  integrate() {
    let energy = 0;
    for (const entity of this.scene.entities.values()) {
      const transform = entity.components?.Transform;
      const kinematics = entity.components?.Kinematics;
      if (!transform || !kinematics) continue;
      const velocity = [...(kinematics.velocity ?? [0, 0, 0])];
      const acceleration = [...(kinematics.acceleration ?? [0, 0, 0])];
      const damping = Math.max(0, Math.min(1, Number(kinematics.damping ?? 0)));
      for (let axis = 0; axis < 3; axis += 1) {
        velocity[axis] = round((Number(velocity[axis]) + Number(acceleration[axis] ?? 0) * this.fixedDt) * (1 - damping * this.fixedDt));
        transform.position[axis] = round(Number(transform.position[axis]) + velocity[axis] * this.fixedDt);
        energy += velocity[axis] * velocity[axis];
      }
      const bounds = entity.components?.WorldBounds;
      if (bounds?.min && bounds?.max) {
        for (let axis = 0; axis < 3; axis += 1) {
          const min = Number(bounds.min[axis]);
          const max = Number(bounds.max[axis]);
          if (transform.position[axis] < min || transform.position[axis] > max) {
            transform.position[axis] = Math.max(min, Math.min(max, transform.position[axis]));
            velocity[axis] = round(-velocity[axis] * Number(bounds.restitution ?? 1));
          }
        }
      }
      kinematics.velocity = velocity;
      entity.modifiedAt = new Date().toISOString();
    }
    this.tick += 1;
    this.elapsed = round(this.tick * this.fixedDt);
    this.lastEnergy = round(energy / 2);
  }

  start() {
    if (this.running) return this.snapshot();
    this.running = true;
    this.timer = setInterval(() => this.step(1), Math.max(4, Math.round(this.fixedDt * 1000)));
    this.emit("state", this.snapshot());
    return this.snapshot();
  }

  pause() {
    this.running = false;
    clearInterval(this.timer);
    this.timer = null;
    this.emit("state", this.snapshot());
    return this.snapshot();
  }

  reset() {
    this.pause();
    this.tick = 0;
    this.elapsed = 0;
    this.lastEnergy = 0;
    this.emit("state", this.snapshot());
    return this.snapshot();
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_SIMULATION_STATE_V4",
      classification: "NON_AUTHORITATIVE_PRESENTATION_SIMULATION",
      running: this.running,
      fixedDt: this.fixedDt,
      tick: this.tick,
      elapsed: this.elapsed,
      kineticEnergy: this.lastEnergy,
      dynamicEntities: [...this.scene.entities.values()].filter((entity) => Boolean(entity.components?.Kinematics)).length
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail: clone(detail) }));
  }
}
