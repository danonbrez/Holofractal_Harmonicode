import {
  PARTICLE_COUNT,
  createAddressTable,
  hash72String,
  validateAddressTable,
} from "./address_map.js";

const TWO_PI = Math.PI * 2;

function finiteOrThrow(value, label) {
  if (!Number.isFinite(value)) throw new Error(`NONFINITE_PHYSICS_STATE:${label}`);
  return value;
}

function clampMagnitude(x, y, z, maximum) {
  const magnitude = Math.hypot(x, y, z);
  if (magnitude === 0 || magnitude <= maximum) return [x, y, z];
  const scale = maximum / magnitude;
  return [x * scale, y * scale, z * scale];
}

export const DEFAULT_PHYSICS_CONFIG = Object.freeze({
  fixedStep: 1 / 60,
  damping: 0.985,
  maxForce: 4,
  maxCatchUpSteps: 8,
  torusWeight: 0.7,
  reciprocalWeight: 0.025,
  loShuWeight: 0.018,
  neighborWeight: 0.012,
  closureWeight: 0.02,
  majorRadius: 10,
  minorRadius: 3,
  loShuRadiusScale: 1.6,
  vm81RadiusScale: 0.8,
});

export class HHSParticleEngine {
  constructor(config = {}) {
    this.config = Object.freeze({ ...DEFAULT_PHYSICS_CONFIG, ...config });
    if (!(this.config.fixedStep > 0 && this.config.fixedStep <= 0.25)) {
      throw new RangeError("INVALID_FIXED_TIMESTEP");
    }
    if (!(this.config.maxForce > 0)) throw new RangeError("INVALID_FORCE_BOUND");
    this.addresses = createAddressTable();
    const proof = validateAddressTable(this.addresses);
    if (!proof.valid) throw new Error(proof.classification);
    this.positions = new Float64Array(PARTICLE_COUNT * 3);
    this.velocities = new Float64Array(PARTICLE_COUNT * 3);
    this.accelerations = new Float64Array(PARTICLE_COUNT * 3);
    this.running = false;
    this.stepCount = 0;
    this.seed = 0;
    this._addressRootHash72 = hash72String(this.addresses.map((particle) => particle.state_hash72).join(""));
    this.reset(0);
  }

  _torusTarget(particle, phaseOffset = 0) {
    const thetaA = TWO_PI * ((particle.hash_state_a + phaseOffset) % 72) / 72;
    const thetaB = TWO_PI * ((particle.hash_state_b + phaseOffset) % 72) / 72;
    const major = this.config.majorRadius
      + this.config.loShuRadiusScale * (particle.loshu_a + particle.loshu_b) / 30;
    const minor = this.config.minorRadius
      + this.config.vm81RadiusScale * particle.vm81_cell / 80;
    return [
      (major + minor * Math.cos(thetaB)) * Math.cos(thetaA),
      (major + minor * Math.cos(thetaB)) * Math.sin(thetaA),
      minor * Math.sin(thetaB),
    ];
  }

  reset(seed = 0) {
    if (!Number.isInteger(seed)) throw new TypeError("seed must be an integer");
    this.seed = seed;
    this.stepCount = 0;
    this.running = false;
    this.velocities.fill(0);
    this.accelerations.fill(0);
    const offset = ((seed % 72) + 72) % 72;
    for (let index = 0; index < PARTICLE_COUNT; index += 1) {
      const target = this._torusTarget(this.addresses[index], offset);
      const base = index * 3;
      this.positions[base] = target[0];
      this.positions[base + 1] = target[1];
      this.positions[base + 2] = target[2];
    }
    return this.serialize();
  }

  start() {
    this.running = true;
    return this.getStatus();
  }

  pause() {
    this.running = false;
    return this.getStatus();
  }

  getStatus() {
    return Object.freeze({
      running: this.running,
      step_count: this.stepCount,
      seed: this.seed,
      particle_count: PARTICLE_COUNT,
      fixed_step: this.config.fixedStep,
    });
  }

  _computeForces() {
    const phaseOffset = (this.seed + this.stepCount) % 72;
    for (let index = 0; index < PARTICLE_COUNT; index += 1) {
      const particle = this.addresses[index];
      const base = index * 3;
      const px = this.positions[base];
      const py = this.positions[base + 1];
      const pz = this.positions[base + 2];
      const target = this._torusTarget(particle, phaseOffset);
      let fx = (target[0] - px) * this.config.torusWeight;
      let fy = (target[1] - py) * this.config.torusWeight;
      let fz = (target[2] - pz) * this.config.torusWeight;

      const reciprocalBase = particle.reciprocal_index * 3;
      fx += (this.positions[reciprocalBase] + px) * -this.config.reciprocalWeight;
      fy += (this.positions[reciprocalBase + 1] + py) * -this.config.reciprocalWeight;
      fz += (this.positions[reciprocalBase + 2] + pz) * -this.config.reciprocalWeight;

      const previousBase = particle.previous_index * 3;
      const nextBase = particle.next_index * 3;
      fx += ((this.positions[previousBase] + this.positions[nextBase]) * 0.5 - px) * this.config.neighborWeight;
      fy += ((this.positions[previousBase + 1] + this.positions[nextBase + 1]) * 0.5 - py) * this.config.neighborWeight;
      fz += ((this.positions[previousBase + 2] + this.positions[nextBase + 2]) * 0.5 - pz) * this.config.neighborWeight;

      const loShuBalance = (particle.loshu_a + particle.loshu_b - 10) / 10;
      fz += loShuBalance * this.config.loShuWeight;
      const closure = Math.sin(TWO_PI * (particle.phase72 + phaseOffset) / 72);
      fx += closure * this.config.closureWeight;
      fy -= closure * this.config.closureWeight;

      [fx, fy, fz] = clampMagnitude(fx, fy, fz, this.config.maxForce);
      this.accelerations[base] = finiteOrThrow(fx, `${index}:x`);
      this.accelerations[base + 1] = finiteOrThrow(fy, `${index}:y`);
      this.accelerations[base + 2] = finiteOrThrow(fz, `${index}:z`);
    }
  }

  _integrateOneStep() {
    this._computeForces();
    const dt = this.config.fixedStep;
    for (let index = 0; index < PARTICLE_COUNT; index += 1) {
      const base = index * 3;
      for (let axis = 0; axis < 3; axis += 1) {
        const offset = base + axis;
        const velocity = (this.velocities[offset] + dt * this.accelerations[offset]) * this.config.damping;
        const position = this.positions[offset] + dt * velocity;
        this.velocities[offset] = finiteOrThrow(velocity, `${index}:velocity:${axis}`);
        this.positions[offset] = finiteOrThrow(position, `${index}:position:${axis}`);
      }
    }
    this.stepCount += 1;
  }

  step(count = 1) {
    if (!Number.isInteger(count) || count < 0 || count > 4096) {
      throw new RangeError("RESOURCE_BOUNDED:invalid_step_count");
    }
    for (let step = 0; step < count; step += 1) this._integrateOneStep();
    return this.serialize();
  }

  getParticle(index) {
    if (!Number.isInteger(index) || index < 0 || index >= PARTICLE_COUNT) {
      throw new RangeError("particle index out of range");
    }
    const base = index * 3;
    return Object.freeze({
      ...this.addresses[index],
      position: [this.positions[base], this.positions[base + 1], this.positions[base + 2]],
      velocity: [this.velocities[base], this.velocities[base + 1], this.velocities[base + 2]],
      acceleration: [this.accelerations[base], this.accelerations[base + 1], this.accelerations[base + 2]],
    });
  }

  getSector(sectorA, sectorB) {
    if (!Number.isInteger(sectorA) || !Number.isInteger(sectorB)
      || sectorA < 0 || sectorA > 7 || sectorB < 0 || sectorB > 7) {
      throw new RangeError("sector coordinates out of range");
    }
    return this.addresses.filter((particle) => particle.sector_a === sectorA && particle.sector_b === sectorB);
  }

  serialize() {
    const sample = [];
    for (let index = 0; index < PARTICLE_COUNT; index += 64) {
      const base = index * 3;
      sample.push([
        index,
        Number(this.positions[base].toFixed(12)),
        Number(this.positions[base + 1].toFixed(12)),
        Number(this.positions[base + 2].toFixed(12)),
      ]);
    }
    const payload = {
      schema: "HHS_PASS157_PARTICLE_STATE_V1",
      seed: this.seed,
      step_count: this.stepCount,
      fixed_step: this.config.fixedStep,
      particle_count: PARTICLE_COUNT,
      address_root_hash72: this._addressRootHash72,
      projection_sample: sample,
    };
    return Object.freeze({ ...payload, state_hash72: hash72String(JSON.stringify(payload)) });
  }

  stepSilent(count = 1) {
    if (!Number.isInteger(count) || count < 0 || count > 4096) {
      throw new RangeError("RESOURCE_BOUNDED:invalid_step_count");
    }
    for (let step = 0; step < count; step += 1) this._integrateOneStep();
  }

  replay(receipt) {
    if (!receipt || !Number.isInteger(receipt.seed) || !Number.isInteger(receipt.step_count)) {
      throw new TypeError("invalid replay receipt");
    }
    const replay = new HHSParticleEngine(this.config);
    replay.reset(receipt.seed);
    replay.step(receipt.step_count);
    const actual = replay.serialize();
    return Object.freeze({
      classification: actual.state_hash72 === receipt.state_hash72 ? "PASS157_REPLAY_MATCH" : "REPLAY_MISMATCH",
      match: actual.state_hash72 === receipt.state_hash72,
      expected: receipt.state_hash72,
      actual: actual.state_hash72,
    });
  }
}
