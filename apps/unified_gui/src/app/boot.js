import { HHSApplicationStore, ACTIONS } from "./state.js";
import { HHSParticleEngine } from "../physics/engine.js";
import { HHSRenderProjection } from "../render/scene.js";
import { HHSTraceChain } from "../trace/chain.js";
import { HHSExactBridge } from "../kernel/exact_bridge.js";
import { validateAddressTable } from "../physics/address_map.js";

function json(value) {
  return JSON.stringify(value, (_, item) => typeof item === "bigint" ? item.toString() : item, 2);
}

function detectCapabilities() {
  const probe = document.createElement("canvas");
  const webgl2 = Boolean(probe.getContext("webgl2"));
  const mobile = matchMedia("(max-width: 900px)").matches || /Android|iPhone|iPad/i.test(navigator.userAgent);
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const dpr = window.devicePixelRatio || 1;
  const screenPixels = Math.round((window.screen?.width ?? 0) * dpr * (window.screen?.height ?? 0) * dpr);
  const colorDepthBits = window.screen?.colorDepth ?? 0;
  const highRefreshCapable = webgl2 && !mobile && screenPixels >= 8_000_000;
  let profile;
  if (!webgl2 || mobile) {
    profile = "MOBILE_SAFE";
  } else if (highRefreshCapable) {
    profile = "HIGH_REFRESH";
  } else {
    profile = "BALANCED";
  }
  return Object.freeze({
    webgl2,
    workers: typeof Worker !== "undefined",
    indexeddb: typeof indexedDB !== "undefined",
    reduced_motion: reducedMotion,
    device_pixel_ratio: dpr,
    screen_pixels: screenPixels,
    color_depth_bits: colorDepthBits,
    high_refresh_capable: highRefreshCapable,
    profile,
  });
}

export class HHSUnifiedApplication {
  constructor() {
    this.store = new HHSApplicationStore();
    this.trace = new HHSTraceChain("HHS.gui");
    this.exact = new HHSExactBridge();
    this.physics = null;
    this.render = null;
    this.physicsTimer = null;
    this.unsubscribe = null;
    this.booted = false;
    this.capabilities = null;
    this.lastPhysicsReceipt = null;
    this.boundHandlers = [];
  }

  _listen(target, type, handler, options) {
    target.addEventListener(type, handler, options);
    this.boundHandlers.push(() => target.removeEventListener(type, handler, options));
  }

  _dispatch(action) {
    const prior = this.store.getState();
    const next = this.store.dispatch(action);
    const event = this.trace.append(action.type, action.payload ?? {}, {
      priorStateHash: prior.state_hash72,
      resultingStateHash: next.state_hash72,
    });
    document.querySelector("#trace-head").textContent = `TRACE: ${event.event_hash}`;
    return next;
  }

  _updateStatus(state) {
    document.querySelector("#boot-status").textContent = state.boot_state;
    document.querySelector("#profile-status").textContent = `PROFILE: ${state.render_projection_state.profile}`;
    document.querySelector("#step-status").textContent = `STEP: ${state.particle_state.step_count}`;
    document.querySelector("#hhs-app").dataset.bootState = state.boot_state;
  }

  _startPhysicsClock() {
    if (this.physicsTimer !== null) return;
    this.physics.start();
    this.physicsTimer = window.setInterval(() => {
      if (document.hidden || !this.physics.running) return;
      this.physics.stepSilent(1);
      this.render?.markDirty();
      if (this.physics.stepCount % 15 === 0) {
        const receipt = this.physics.serialize();
        this.lastPhysicsReceipt = receipt;
        this._dispatch({ type: ACTIONS.PARTICLE_FIELD_ADVANCED, payload: receipt });
        this.refreshDiagnostics();
      }
    }, 1000 / 60);
  }

  _stopPhysicsClock() {
    if (this.physicsTimer !== null) window.clearInterval(this.physicsTimer);
    this.physicsTimer = null;
    this.physics?.pause();
  }

  _bindWorkspaceNavigation() {
    for (const button of document.querySelectorAll("[data-workspace]")) {
      this._listen(button, "click", () => {
        const workspace = button.dataset.workspace;
        for (const other of document.querySelectorAll("[data-workspace]")) {
          other.setAttribute("aria-current", other === button ? "page" : "false");
        }
        for (const panel of document.querySelectorAll("[data-panel]")) {
          panel.hidden = panel.dataset.panel !== workspace;
        }
        this._dispatch({ type: ACTIONS.WORKSPACE_SELECTED, payload: { workspace } });
        this.refreshDiagnostics();
      });
    }
  }

  _bindControls() {
    this._listen(document.querySelector("#physics-toggle"), "click", (event) => {
      if (this.physics.running) {
        this.physics.pause();
        event.currentTarget.textContent = "Resume";
      } else {
        this.physics.start();
        event.currentTarget.textContent = "Pause";
      }
    });
    this._listen(document.querySelector("#physics-step"), "click", () => {
      const receipt = this.physics.step(1);
      this.lastPhysicsReceipt = receipt;
      this._dispatch({ type: ACTIONS.PARTICLE_FIELD_ADVANCED, payload: receipt });
      this.render?.updateBuffers();
      this.refreshDiagnostics();
    });
    this._listen(document.querySelector("#physics-reset"), "click", () => {
      const receipt = this.physics.reset(0);
      this.physics.start();
      this.lastPhysicsReceipt = receipt;
      this._dispatch({ type: ACTIONS.PARTICLE_FIELD_ADVANCED, payload: receipt });
      this.render?.updateBuffers();
      this.refreshDiagnostics();
    });
    this._listen(document.querySelector("#profile-select"), "change", (event) => {
      const profile = event.currentTarget.value;
      this.render?.setProfile(profile);
      this._dispatch({ type: ACTIONS.LOD_PROFILE_CHANGED, payload: { profile } });
    });
    this._listen(document.querySelector("#constructor-parse"), "click", () => {
      const source = document.querySelector("#constructor-source").value;
      const result = this.exact.parse(source);
      document.querySelector("#constructor-output").textContent = json(result);
    });
    this._listen(document.querySelector("#symbolic-parse"), "click", () => {
      const source = document.querySelector("#symbolic-source").value;
      document.querySelector("#symbolic-output").textContent = json(this.exact.parse(source));
    });
    this._listen(document.querySelector("#calc-run"), "click", () => {
      try {
        const result = this.exact.evaluateExactBinary(
          document.querySelector("#calc-left").value,
          document.querySelector("#calc-op").value,
          document.querySelector("#calc-right").value,
        );
        document.querySelector("#calc-output").textContent = json({
          exact: result.toString(),
          display: this.exact.projectApproximate(result),
        });
      } catch (error) {
        document.querySelector("#calc-output").textContent = json({ classification: error.message });
      }
    });
    this._listen(document.querySelector("#equality-register"), "click", () => {
      try {
        const result = this.exact.registerEquality(
          document.querySelector("#equality-id").value,
          document.querySelector("#equality-left").value,
          document.querySelector("#equality-right").value,
        );
        document.querySelector("#equality-output").textContent = json(result);
      } catch (error) {
        document.querySelector("#equality-output").textContent = json({ classification: error.message });
      }
    });
    this._listen(document.querySelector("#focus-zero"), "click", () => {
      const particle = this.render?.focusParticle(0) ?? this.physics.getParticle(0);
      document.querySelector("#torus-output").textContent = json(particle);
      this._showParticle(particle);
    });
    this._listen(document.querySelector("#swarm-canvas"), "click", (event) => {
      const rect = event.currentTarget.getBoundingClientRect();
      const normalized = Math.max(0, Math.min(0.999999, (event.clientX - rect.left) / rect.width));
      const index = Math.floor(normalized * this.physics.addresses.length);
      const particle = this.physics.getParticle(index);
      this._showParticle(particle);
      this._dispatch({ type: ACTIONS.PARTICLE_SELECTED, payload: { index } });
    });
    this._listen(document.querySelector("#trace-seal"), "click", () => {
      try {
        const bundle = this.trace.seal();
        const state = this.store.dispatch({ type: ACTIONS.TRACE_SEALED, payload: bundle });
        this._updateStatus(state);
        this.trace = new HHSTraceChain("HHS.gui");
        this.trace.append("TRACE_CONTINUATION", { previous_bundle_hash72: bundle.bundle_hash72 });
        document.querySelector("#trace-output").textContent = json(bundle);
      } catch (error) {
        document.querySelector("#trace-output").textContent = json({ classification: error.message });
      }
    });
    this._listen(document.querySelector("#replay-run"), "click", () => {
      const receipt = this.lastPhysicsReceipt ?? this.physics.serialize();
      const replay = this.physics.replay(receipt);
      this._dispatch({ type: ACTIONS.REPLAY_VERIFIED, payload: replay });
      document.querySelector("#trace-output").textContent = json(replay);
    });
    this._listen(document.querySelector("#system-refresh"), "click", () => this.refreshDiagnostics());
    this._listen(window, "resize", () => this.render?.resize());
    this._listen(document, "visibilitychange", () => {
      if (document.hidden) this.physics.pause();
      else if (!this.capabilities.reduced_motion) this.physics.start();
    });
  }

  _showParticle(particle) {
    const summary = document.querySelector("#particle-summary");
    summary.innerHTML = `
      <dt>Particle</dt><dd>${particle.particle_id}</dd>
      <dt>Linear index</dt><dd>${particle.linear_index}</dd>
      <dt>Sector pair</dt><dd>${particle.sector_a}:${particle.sector_b}</dd>
      <dt>VM81</dt><dd>${particle.vm81_row},${particle.vm81_column} → ${particle.vm81_cell}</dd>
      <dt>Lo Shu</dt><dd>${particle.loshu_a}, ${particle.loshu_b}</dd>
      <dt>Phase72</dt><dd>${particle.phase72}</dd>
      <dt>Hash72</dt><dd>${particle.state_hash72}</dd>
    `;
  }

  refreshDiagnostics() {
    if (!this.physics) return;
    const physics = this.physics.getStatus();
    const render = this.render?.diagnostics() ?? { status: "CAPABILITY_FALLBACK" };
    const addressProof = validateAddressTable(this.physics.addresses);
    const trace = this.trace.verify();
    const state = this.store.getState();
    const diagnostics = { capabilities: this.capabilities, physics, render, addressProof, trace, state };
    document.querySelector("#system-output").textContent = json(diagnostics);
    document.querySelector("#physics-diagnostics").innerHTML = Object.entries({ ...physics, ...render })
      .map(([key, value]) => `<dt>${key}</dt><dd>${String(value)}</dd>`).join("");
    return diagnostics;
  }

  async boot(config = {}) {
    if (this.booted) return this.getStatus();
    this.booted = true;
    this._dispatch({ type: ACTIONS.APP_BOOT, payload: { config } });
    this.capabilities = detectCapabilities();
    this.physics = new HHSParticleEngine(config.physics ?? {});
    const canvas = document.querySelector("#swarm-canvas");
    const profile = config.profile ?? this.capabilities.profile;
    document.querySelector("#profile-select").value = profile;
    try {
      this.render = new HHSRenderProjection(canvas, this.physics, {
        profile,
        onContextLost: () => this._dispatch({ type: ACTIONS.WEBGL_CONTEXT_LOST }),
        onContextRestored: () => this._dispatch({ type: ACTIONS.WEBGL_CONTEXT_RESTORED }),
      });
      this.render.initialize();
      this.render.start();
    } catch (error) {
      this.render = null;
      this.trace.append("CAPABILITY_UNAVAILABLE", { module: "HHS.render", classification: error.message });
    }
    this.unsubscribe = this.store.subscribe((state) => this._updateStatus(state));
    this._bindWorkspaceNavigation();
    this._bindControls();
    this._dispatch({
      type: ACTIONS.APP_CAPABILITIES_RESOLVED,
      payload: { ...this.capabilities, profile },
    });
    this.lastPhysicsReceipt = this.physics.serialize();
    if (!this.capabilities.reduced_motion) this._startPhysicsClock();
    this.refreshDiagnostics();
    return this.getStatus();
  }

  shutdown() {
    this._stopPhysicsClock();
    this.render?.dispose();
    for (const dispose of this.boundHandlers.splice(0)) dispose();
    this.unsubscribe?.();
    this.unsubscribe = null;
    this.booted = false;
    return { classification: "HHS_APP_SHUTDOWN_COMPLETE" };
  }

  getStatus() {
    return Object.freeze({
      booted: this.booted,
      state: this.store.getState(),
      physics: this.physics?.getStatus() ?? null,
      render: this.render?.diagnostics() ?? null,
      trace: this.trace.verify(),
    });
  }

  getCapabilities() {
    return this.capabilities;
  }

  dispatch(action) {
    return this._dispatch(action);
  }

  subscribe(eventType, handler) {
    return this.store.subscribe((state, previous, action) => {
      if (action.type === eventType) handler(state, previous, action);
    });
  }

  loadWorkspace(source) {
    const parsed = this.exact.parse(source);
    this.trace.append("WORKSPACE_LOADED", parsed);
    return parsed;
  }

  exportWorkspace() {
    return Object.freeze({
      schema: "HHS_PASS157_WORKSPACE_BUNDLE_V1",
      state: this.store.getState(),
      physics: this.physics.serialize(),
      trace: this.trace.getEvents(),
    });
  }
}

export const HHSApp = new HHSUnifiedApplication();

globalThis.HHSApp = HHSApp;
globalThis.HHSPhysics = {
  configure: (config) => new HHSParticleEngine(config),
  start: () => HHSApp.physics.start(),
  pause: () => HHSApp.physics.pause(),
  step: (count) => HHSApp.physics.step(count),
  reset: (seed) => HHSApp.physics.reset(seed),
  getParticle: (index) => HHSApp.physics.getParticle(index),
  getSector: (sectorA, sectorB) => HHSApp.physics.getSector(sectorA, sectorB),
  serialize: () => HHSApp.physics.serialize(),
  replay: (receipt) => HHSApp.physics.replay(receipt),
};
globalThis.HHSRender = {
  setProfile: (profile) => HHSApp.render.setProfile(profile),
  focusParticle: (index) => HHSApp.render.focusParticle(index),
  focusVM81: (cell) => HHSApp.physics.addresses.filter((particle) => particle.vm81_cell === cell),
  captureDiagnostics: () => HHSApp.render.diagnostics(),
};
globalThis.HHSSymbolic = {
  parse: (source) => HHSApp.exact.parse(source),
  registerEquality: (...args) => HHSApp.exact.registerEquality(...args),
  substitute: (...args) => HHSApp.exact.substitute(...args),
};
globalThis.HHSTrace = {
  getHead: () => HHSApp.trace.getHead(),
  getEvents: (...args) => HHSApp.trace.getEvents(...args),
  seal: () => HHSApp.trace.seal(),
  exportBundle: () => HHSApp.trace.seal(),
  verifyBundle: (bundle) => HHSTraceChain.verifyBundle(bundle),
};

HHSApp.boot().catch((error) => {
  document.querySelector("#boot-status").textContent = "BOOT_FAILED";
  document.querySelector("#system-output").textContent = json({
    classification: "BOOT_FAILED",
    error: error instanceof Error ? error.message : String(error),
  });
});
