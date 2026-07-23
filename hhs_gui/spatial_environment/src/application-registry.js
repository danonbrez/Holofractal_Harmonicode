export const APPLICATIONS = Object.freeze([
  {
    id: "system-overview",
    label: "System Overview",
    glyph: "⌂",
    category: "system",
    feature: "dashboard",
    description: "Measured renderer, channel, session, and runtime projection status.",
    authority: "READ_ONLY_PROJECTION",
    defaultSurface: { width: 460, height: 330, anchor: "left" }
  },
  {
    id: "vm81-lattice",
    label: "VM81 Lattice",
    glyph: "◇",
    category: "runtime",
    feature: "lattice",
    description: "Interactive 81-cell lattice explorer with semantic focus.",
    authority: "READ_ONLY_PROJECTION",
    defaultSurface: { width: 520, height: 420, anchor: "center" }
  },
  {
    id: "constraint-membranes",
    label: "Constraint Membranes",
    glyph: "△",
    category: "runtime",
    feature: "membranes",
    description: "Constraint, rigidity, invariant, and admissibility projections.",
    authority: "READ_ONLY_PROJECTION",
    defaultSurface: { width: 450, height: 350, anchor: "right" }
  },
  {
    id: "modular-fields",
    label: "Modular Fields",
    glyph: "✧",
    category: "simulation",
    feature: "fields",
    description: "Modulus, phase, transport, and 42nd-field controls.",
    authority: "PRESENTATION_ONLY",
    defaultSurface: { width: 430, height: 330, anchor: "right" }
  },
  {
    id: "opcode-trace",
    label: "Opcode Trace",
    glyph: "⌘",
    category: "runtime",
    feature: "opcodes",
    description: "Backend-derived opcode events and guarded command outcomes.",
    authority: "READ_ONLY_PROJECTION",
    defaultSurface: { width: 540, height: 360, anchor: "left" }
  },
  {
    id: "reciprocal-topology",
    label: "Reciprocal Topology",
    glyph: "↝",
    category: "runtime",
    feature: "drift",
    description: "Reciprocal topology, drift, and manifold revalidation controls.",
    authority: "GUARDED_ORCHESTRATION",
    defaultSurface: { width: 480, height: 340, anchor: "right" }
  },
  {
    id: "constraint-console",
    label: "Constraint Console",
    glyph: "⊗",
    category: "runtime",
    feature: "constraints",
    description: "Guarded state, halt, error, and zero-bypass status surface.",
    authority: "GUARDED_ORCHESTRATION",
    defaultSurface: { width: 500, height: 370, anchor: "center" }
  },
  {
    id: "telemetry",
    label: "Telemetry",
    glyph: "▥",
    category: "diagnostics",
    feature: "metrics",
    description: "Measured frame timing, channel status, and runtime telemetry.",
    authority: "READ_ONLY_PROJECTION",
    defaultSurface: { width: 520, height: 380, anchor: "left" }
  },
  {
    id: "knowledge-explorer",
    label: "Knowledge Explorer",
    glyph: "◎",
    category: "knowledge",
    feature: "knowledge",
    description: "Spatial source-linked knowledge and semantic resource surface.",
    authority: "READ_ONLY_PROJECTION",
    defaultSurface: { width: 560, height: 420, anchor: "center" }
  },
  {
    id: "document-canvas",
    label: "Document Canvas",
    glyph: "▤",
    category: "knowledge",
    feature: "documents",
    description: "Accessible document, evidence, and source-link workspace.",
    authority: "READ_ONLY_PROJECTION",
    defaultSurface: { width: 560, height: 420, anchor: "center" }
  },
  {
    id: "runtime-control",
    label: "Runtime Control",
    glyph: "Ω",
    category: "runtime",
    feature: "runtime",
    description: "Guarded runtime state, step, commit, halt, and service access.",
    authority: "GUARDED_ORCHESTRATION",
    defaultSurface: { width: 520, height: 400, anchor: "right" }
  },
  {
    id: "elastic-closure",
    label: "Elastic Closure",
    glyph: "∞",
    category: "runtime",
    feature: "runtime",
    description: "Pass 152 candidate propagation, recursive control, closure proof, VM81 commit, and replay evidence.",
    authority: "GUARDED_ORCHESTRATION_AND_READ_ONLY_PROJECTION",
    defaultSurface: { width: 590, height: 440, anchor: "center" }
  },
  {
    id: "workspace-settings",
    label: "Workspace Settings",
    glyph: "⚙",
    category: "system",
    feature: "settings",
    description: "Themes, templates, sessions, imports, exports, and accessibility.",
    authority: "PRESENTATION_ONLY",
    defaultSurface: { width: 520, height: 430, anchor: "center" }
  },
  {
    id: "session-manager",
    label: "Session Manager",
    glyph: "◫",
    category: "system",
    feature: "settings",
    description: "Create, rename, switch, snapshot, export, and restore sessions.",
    authority: "PRESENTATION_ONLY",
    defaultSurface: { width: 500, height: 370, anchor: "left" }
  },
  {
    id: "replay-timeline",
    label: "Replay Timeline",
    glyph: "⟲",
    category: "diagnostics",
    feature: "runtime",
    description: "Bounded presentation replay of received events and local projections.",
    authority: "NON_AUTHORITATIVE_REPLAY",
    defaultSurface: { width: 620, height: 300, anchor: "bottom" }
  },
  {
    id: "scene-composer",
    label: "Scene Composer",
    glyph: "⬡",
    category: "creator",
    feature: "settings",
    description: "Open, move, resize, dock, arrange, and persist spatial tool surfaces.",
    authority: "PRESENTATION_ONLY",
    defaultSurface: { width: 540, height: 410, anchor: "center" }
  },
  {
    id: "game-environment",
    label: "Game Environment",
    glyph: "◉",
    category: "simulation",
    feature: "fields",
    description: "Explore-mode entry surface for spatial simulation and game controls.",
    authority: "PRESENTATION_AND_SIMULATION",
    defaultSurface: { width: 440, height: 310, anchor: "center" }
  },
  {
    id: "project-manager",
    label: "Project Manager",
    glyph: "▣",
    category: "creator",
    feature: "settings",
    description: "Versioned project manifests, world selection, snapshots, imports, and exports.",
    authority: "PROJECT_AUTHORING_METADATA",
    defaultSurface: { width: 560, height: 430, anchor: "left" }
  },
  {
    id: "entity-inspector",
    label: "Entity Inspector",
    glyph: "⬢",
    category: "creator",
    feature: "settings",
    description: "Entity-component inspection, transform editing, hierarchy, and runtime bindings.",
    authority: "PRESENTATION_SCENE_AUTHORING",
    defaultSurface: { width: 500, height: 420, anchor: "right" }
  },
  {
    id: "asset-vault",
    label: "Asset Vault",
    glyph: "◈",
    category: "creator",
    feature: "documents",
    description: "Digest-verified local asset ingestion with inert code and shader policy.",
    authority: "ASSET_METADATA_AND_DIGESTS",
    defaultSurface: { width: 560, height: 420, anchor: "left" }
  },
  {
    id: "world-router",
    label: "World Router",
    glyph: "⇄",
    category: "simulation",
    feature: "fields",
    description: "Portal topology, route validation, path resolution, and world navigation.",
    authority: "PRESENTATION_NAVIGATION_ONLY",
    defaultSurface: { width: 520, height: 380, anchor: "center" }
  },
  {
    id: "simulation-console",
    label: "Simulation Console",
    glyph: "▶",
    category: "simulation",
    feature: "fields",
    description: "Fixed-step deterministic presentation simulation for authored scene entities.",
    authority: "NON_AUTHORITATIVE_PRESENTATION_SIMULATION",
    defaultSurface: { width: 480, height: 350, anchor: "right" }
  }
]);

export function applicationById(id) {
  return APPLICATIONS.find((application) => application.id === id) ?? APPLICATIONS[0];
}

export function applicationsForFeature(featureId) {
  return APPLICATIONS.filter((application) => application.feature === featureId);
}

export function applicationCategories() {
  return [...new Set(APPLICATIONS.map((application) => application.category))];
}
