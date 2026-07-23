import { canonical, sha256Text } from "./entity-scene-graph.js";

const STORAGE_KEY = "hhs-spatial-project-store-v4";
const MAX_PROJECTS = 16;
const MAX_WORLDS_PER_PROJECT = 32;
const MAX_SNAPSHOTS_PER_WORLD = 32;
const clone = (value) => JSON.parse(JSON.stringify(value));
const now = () => new Date().toISOString();

function id(prefix) {
  return `${prefix}-${globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`}`;
}

function defaultWorld(name = "Primary World") {
  const time = now();
  return {
    id: "world-main",
    name,
    createdAt: time,
    modifiedAt: time,
    scene: null,
    routes: [],
    snapshotHead: "GENESIS",
    snapshots: []
  };
}

function defaultProject() {
  const time = now();
  return {
    id: "default-project",
    name: "Harmonicode Spatial Project",
    createdAt: time,
    modifiedAt: time,
    activeWorldId: "world-main",
    manifest: {
      schema: "HHS_SPATIAL_PROJECT_MANIFEST_V4",
      classification: "PROJECT_AND_WORLD_DESCRIPTION",
      entryWorld: "world-main",
      runtimeAuthority: "VM81_BACKEND_AUTHORITATIVE",
      frontendAuthority: "PROJECTION_AND_ORCHESTRATION_ONLY",
      capabilities: ["scene.compose", "asset.import", "world.route", "simulation.presentation", "runtime.guarded-request"],
      assetPolicy: "IMPORTED_CODE_AND_SHADERS_INERT_UNTIL_VALIDATED"
    },
    worlds: [defaultWorld()],
    assets: []
  };
}

export class ProjectStore extends EventTarget {
  constructor({ storage = globalThis.localStorage } = {}) {
    super();
    this.storage = storage;
    this.projects = [];
    this.activeProjectId = null;
    this.load();
  }

  load() {
    try {
      const payload = JSON.parse(this.storage?.getItem(STORAGE_KEY) ?? "null");
      if (payload?.schema === "HHS_SPATIAL_PROJECT_STORE_V4" && Array.isArray(payload.projects) && payload.projects.length) {
        this.projects = payload.projects;
        this.activeProjectId = payload.projects.some((project) => project.id === payload.activeProjectId) ? payload.activeProjectId : payload.projects[0].id;
        return;
      }
    } catch {}
    const project = defaultProject();
    this.projects = [project];
    this.activeProjectId = project.id;
    this.persist();
  }

  persist() {
    try {
      this.storage?.setItem(STORAGE_KEY, JSON.stringify(this.snapshot()));
    } catch (error) {
      this.emit("storage-error", { error: String(error?.message ?? error) });
    }
  }

  get activeProject() {
    return this.projects.find((project) => project.id === this.activeProjectId) ?? null;
  }

  get activeWorld() {
    const project = this.activeProject;
    return project?.worlds.find((world) => world.id === project.activeWorldId) ?? project?.worlds[0] ?? null;
  }

  list() {
    return this.projects.map((project) => ({
      id: project.id,
      name: project.name,
      modifiedAt: project.modifiedAt,
      worlds: project.worlds.length,
      assets: project.assets.length
    }));
  }

  create(name = "Untitled Spatial Project") {
    if (this.projects.length >= MAX_PROJECTS) throw new Error("PROJECT_LIMIT_REACHED");
    const project = defaultProject();
    project.id = id("project");
    project.name = String(name).trim() || "Untitled Spatial Project";
    project.worlds[0].id = id("world");
    project.worlds[0].name = "Primary World";
    project.activeWorldId = project.worlds[0].id;
    project.manifest.entryWorld = project.activeWorldId;
    this.projects.push(project);
    this.activeProjectId = project.id;
    this.persist();
    this.emit("project-created", project);
    this.emit("project-selected", project);
    return clone(project);
  }

  select(projectId) {
    const project = this.requireProject(projectId);
    this.activeProjectId = project.id;
    this.persist();
    this.emit("project-selected", project);
    return clone(project);
  }

  rename(projectId, name) {
    const project = this.requireProject(projectId);
    const normalized = String(name ?? "").trim();
    if (!normalized) throw new Error("PROJECT_NAME_REQUIRED");
    project.name = normalized;
    project.modifiedAt = now();
    this.persist();
    this.emit("project-updated", project);
    return clone(project);
  }

  delete(projectId) {
    if (this.projects.length === 1) throw new Error("CANNOT_DELETE_LAST_PROJECT");
    const index = this.projects.findIndex((project) => project.id === projectId);
    if (index < 0) throw new Error("PROJECT_NOT_FOUND");
    const [removed] = this.projects.splice(index, 1);
    if (this.activeProjectId === projectId) this.activeProjectId = this.projects[0].id;
    this.persist();
    this.emit("project-deleted", removed);
    this.emit("project-selected", this.activeProject);
    return clone(removed);
  }

  addWorld(name = "Spatial World") {
    const project = this.requireProject(this.activeProjectId);
    if (project.worlds.length >= MAX_WORLDS_PER_PROJECT) throw new Error("WORLD_LIMIT_REACHED");
    const world = defaultWorld(String(name).trim() || "Spatial World");
    world.id = id("world");
    project.worlds.push(world);
    project.activeWorldId = world.id;
    project.modifiedAt = now();
    this.persist();
    this.emit("world-created", world);
    this.emit("world-selected", world);
    return clone(world);
  }

  selectWorld(worldId) {
    const project = this.requireProject(this.activeProjectId);
    const world = project.worlds.find((candidate) => candidate.id === worldId);
    if (!world) throw new Error("WORLD_NOT_FOUND");
    project.activeWorldId = world.id;
    project.modifiedAt = now();
    this.persist();
    this.emit("world-selected", world);
    return clone(world);
  }

  saveWorldState({ scene, routes } = {}) {
    const project = this.requireProject(this.activeProjectId);
    const world = project.worlds.find((candidate) => candidate.id === project.activeWorldId);
    if (!world) throw new Error("WORLD_NOT_FOUND");
    if (scene !== undefined) world.scene = clone(scene);
    if (routes !== undefined) world.routes = clone(routes);
    world.modifiedAt = now();
    project.modifiedAt = world.modifiedAt;
    this.persist();
    this.emit("world-updated", world);
    return clone(world);
  }

  saveAssets(assetManifest) {
    const project = this.requireProject(this.activeProjectId);
    project.assets = clone(assetManifest?.assets ?? assetManifest ?? []);
    project.modifiedAt = now();
    this.persist();
    this.emit("project-updated", project);
    return clone(project.assets);
  }

  async saveWorldSnapshot(label, state) {
    const project = this.requireProject(this.activeProjectId);
    const world = this.activeWorld;
    if (!world) throw new Error("WORLD_NOT_FOUND");
    const previous = world.snapshotHead ?? "GENESIS";
    const payload = clone(state);
    const createdAt = now();
    const digest = await sha256Text(JSON.stringify(canonical({ previous, label, createdAt, payload })));
    const snapshot = { id: id("world-snapshot"), label: String(label || "World snapshot"), createdAt, previous, digest, payload };
    world.snapshots.push(snapshot);
    world.snapshots = world.snapshots.slice(-MAX_SNAPSHOTS_PER_WORLD);
    world.snapshotHead = digest;
    world.modifiedAt = createdAt;
    project.modifiedAt = createdAt;
    this.persist();
    this.emit("world-snapshot", snapshot);
    return clone(snapshot);
  }

  async verifyWorldSnapshots(world = this.activeWorld) {
    if (!world) return { valid: false, failures: ["WORLD_NOT_FOUND"] };
    let previous = world.snapshots?.[0]?.previous ?? "GENESIS";
    const anchor = previous;
    const failures = [];
    for (const snapshot of world.snapshots ?? []) {
      const expected = await sha256Text(JSON.stringify(canonical({ previous, label: snapshot.label, createdAt: snapshot.createdAt, payload: snapshot.payload })));
      if (snapshot.previous !== previous || snapshot.digest !== expected) failures.push(snapshot.id);
      previous = snapshot.digest;
    }
    return { valid: failures.length === 0, checked: world.snapshots?.length ?? 0, failures, anchor, head: previous };
  }

  async restoreWorldSnapshot(snapshotId) {
    const world = this.activeWorld;
    const verification = await this.verifyWorldSnapshots(world);
    if (!verification.valid) throw new Error("WORLD_SNAPSHOT_CHAIN_INVALID");
    const snapshot = world.snapshots.find((candidate) => candidate.id === snapshotId);
    if (!snapshot) throw new Error("WORLD_SNAPSHOT_NOT_FOUND");
    this.emit("world-restore", snapshot);
    return clone(snapshot.payload);
  }

  requireProject(idValue) {
    const project = this.projects.find((candidate) => candidate.id === idValue);
    if (!project) throw new Error("PROJECT_NOT_FOUND");
    return project;
  }

  export() {
    return {
      schema: "HHS_SPATIAL_PROJECT_EXPORT_V4",
      classification: "PROJECT_PRESENTATION_AND_AUTHORING_STATE",
      exportedAt: now(),
      activeProjectId: this.activeProjectId,
      projects: clone(this.projects)
    };
  }

  import(payload, { merge = true } = {}) {
    if (payload?.schema !== "HHS_SPATIAL_PROJECT_EXPORT_V4" || !Array.isArray(payload.projects)) throw new Error("INVALID_PROJECT_EXPORT");
    if (!merge) this.projects = [];
    for (const project of payload.projects) {
      const copy = clone(project);
      if (this.projects.some((candidate) => candidate.id === copy.id)) copy.id = id("project");
      this.projects.push(copy);
    }
    this.projects = this.projects.slice(0, MAX_PROJECTS);
    if (!this.projects.length) throw new Error("PROJECT_IMPORT_EMPTY");
    this.activeProjectId = this.projects.some((project) => project.id === payload.activeProjectId) ? payload.activeProjectId : this.projects[0].id;
    this.persist();
    this.emit("project-selected", this.activeProject);
    return this.snapshot();
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_PROJECT_STORE_V4",
      activeProjectId: this.activeProjectId,
      projects: clone(this.projects)
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail: clone(detail) }));
  }
}

export { STORAGE_KEY, MAX_PROJECTS, MAX_WORLDS_PER_PROJECT, MAX_SNAPSHOTS_PER_WORLD };
