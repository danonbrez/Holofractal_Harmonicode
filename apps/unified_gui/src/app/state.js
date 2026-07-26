import { hash72String } from "../physics/address_map.js";

export const ACTIONS = Object.freeze({
  APP_BOOT: "APP_BOOT",
  APP_CAPABILITIES_RESOLVED: "APP_CAPABILITIES_RESOLVED",
  PARTICLE_FIELD_ADVANCED: "PARTICLE_FIELD_ADVANCED",
  PARTICLE_SELECTED: "PARTICLE_SELECTED",
  LOD_PROFILE_CHANGED: "LOD_PROFILE_CHANGED",
  WORKSPACE_SELECTED: "WORKSPACE_SELECTED",
  TRACE_SEALED: "TRACE_SEALED",
  REPLAY_VERIFIED: "REPLAY_VERIFIED",
  WEBGL_CONTEXT_LOST: "WEBGL_CONTEXT_LOST",
  WEBGL_CONTEXT_RESTORED: "WEBGL_CONTEXT_RESTORED",
  RESOURCE_BOUND_REACHED: "RESOURCE_BOUND_REACHED",
});

function canonicalStateHash(state) {
  const projection = {
    schema_version: state.schema_version,
    pass_number: state.pass_number,
    boot_state: state.boot_state,
    capability_state: state.capability_state,
    exact_runtime_state: state.exact_runtime_state,
    symbolic_state: state.symbolic_state,
    equality_registry_state: state.equality_registry_state,
    particle_state: state.particle_state,
    gui_state: state.gui_state,
    trace_state: state.trace_state,
    receipt_state: state.receipt_state,
  };
  return hash72String(JSON.stringify(projection));
}

export function createInitialState() {
  const state = {
    schema_version: "HHS_APPLICATION_STATE_V1",
    pass_number: 157,
    boot_state: "UNINITIALIZED",
    capability_state: { profile: "UNRESOLVED", webgl2: false, workers: false },
    exact_runtime_state: {
      authority: "HHS_EXACT_TYPED_RUNTIME",
      render_float_is_authority: false,
      phase_tensor_contract: "HHS-P157-PPF-MPTC",
    },
    symbolic_state: { source: "", ast_hash72: null, classification: "EMPTY" },
    equality_registry_state: { links: [], mutation_owner: "HHS.symbolic" },
    particle_state: { step_count: 0, state_hash72: null, selected_index: null },
    render_projection_state: { profile: "MOBILE_SAFE", context: "UNINITIALIZED", frame: 0 },
    gui_state: { workspace: "Swarm", reduced_motion: false },
    persistence_state: { status: "MEMORY_ONLY", schema_version: 1 },
    trace_state: { event_count: 0, head: null, sealed: false },
    receipt_state: { latest: null, replay: "NOT_RUN" },
  };
  return Object.freeze({ ...state, state_hash72: canonicalStateHash(state) });
}

export function reduceApplicationState(state, action) {
  if (!action || typeof action.type !== "string") throw new TypeError("typed action required");
  let next;
  switch (action.type) {
    case ACTIONS.APP_BOOT:
      next = { ...state, boot_state: "BOOTING" };
      break;
    case ACTIONS.APP_CAPABILITIES_RESOLVED:
      next = {
        ...state,
        boot_state: "READY",
        capability_state: Object.freeze({ ...state.capability_state, ...action.payload }),
        render_projection_state: Object.freeze({
          ...state.render_projection_state,
          profile: action.payload.profile,
          context: action.payload.webgl2 ? "WEBGL2_READY" : "CAPABILITY_FALLBACK",
        }),
      };
      break;
    case ACTIONS.PARTICLE_FIELD_ADVANCED:
      next = {
        ...state,
        particle_state: Object.freeze({
          ...state.particle_state,
          step_count: action.payload.step_count,
          state_hash72: action.payload.state_hash72,
        }),
      };
      break;
    case ACTIONS.PARTICLE_SELECTED:
      next = {
        ...state,
        particle_state: Object.freeze({ ...state.particle_state, selected_index: action.payload.index }),
      };
      break;
    case ACTIONS.LOD_PROFILE_CHANGED:
      next = {
        ...state,
        render_projection_state: Object.freeze({ ...state.render_projection_state, profile: action.payload.profile }),
      };
      break;
    case ACTIONS.WORKSPACE_SELECTED:
      next = { ...state, gui_state: Object.freeze({ ...state.gui_state, workspace: action.payload.workspace }) };
      break;
    case ACTIONS.TRACE_SEALED:
      next = {
        ...state,
        trace_state: Object.freeze({
          event_count: action.payload.event_count,
          head: action.payload.head,
          sealed: true,
        }),
      };
      break;
    case ACTIONS.REPLAY_VERIFIED:
      next = {
        ...state,
        receipt_state: Object.freeze({ latest: action.payload.receipt ?? null, replay: action.payload.classification }),
      };
      break;
    case ACTIONS.WEBGL_CONTEXT_LOST:
      next = {
        ...state,
        render_projection_state: Object.freeze({ ...state.render_projection_state, context: "WEBGL_CONTEXT_LOST" }),
      };
      break;
    case ACTIONS.WEBGL_CONTEXT_RESTORED:
      next = {
        ...state,
        render_projection_state: Object.freeze({ ...state.render_projection_state, context: "WEBGL_CONTEXT_RESTORED" }),
      };
      break;
    case ACTIONS.RESOURCE_BOUND_REACHED:
      next = { ...state, boot_state: "RESOURCE_BOUNDED" };
      break;
    default:
      throw new Error(`UNKNOWN_TYPED_ACTION:${action.type}`);
  }
  return Object.freeze({ ...next, state_hash72: canonicalStateHash(next) });
}

export class HHSApplicationStore {
  constructor(initialState = createInitialState()) {
    this.state = initialState;
    this.listeners = new Set();
  }

  getState() {
    return this.state;
  }

  dispatch(action) {
    const previous = this.state;
    this.state = reduceApplicationState(previous, action);
    for (const listener of this.listeners) listener(this.state, previous, action);
    return this.state;
  }

  subscribe(listener) {
    if (typeof listener !== "function") throw new TypeError("listener must be a function");
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}
