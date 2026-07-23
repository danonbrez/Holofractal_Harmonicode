const MAX_ENTITIES = 2048;
const TRANSFORM_COMPONENT = "Transform";

const clone = (value) => JSON.parse(JSON.stringify(value));
const now = () => new Date().toISOString();

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonical(value[key])]));
  }
  return value;
}

async function sha256Text(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function defaultTransform(seed = {}) {
  return {
    position: [0, 0, 0],
    rotation: [0, 0, 0],
    scale: [1, 1, 1],
    ...clone(seed)
  };
}

function rootEntity() {
  const time = now();
  return {
    id: "world-root",
    name: "World Root",
    parentId: null,
    children: [],
    components: {
      [TRANSFORM_COMPONENT]: defaultTransform(),
      Metadata: { classification: "PRESENTATION_WORLD_ROOT" }
    },
    createdAt: time,
    modifiedAt: time
  };
}

export class EntitySceneGraph extends EventTarget {
  constructor({ maxEntities = MAX_ENTITIES } = {}) {
    super();
    this.maxEntities = maxEntities;
    this.entities = new Map();
    this.sequence = 0;
    this.selectedEntityId = "world-root";
    this.reset();
  }

  reset() {
    this.entities.clear();
    const root = rootEntity();
    this.entities.set(root.id, root);
    this.sequence = 0;
    this.selectedEntityId = root.id;
    this.emit("changed", this.snapshot());
    return root;
  }

  makeId() {
    this.sequence += 1;
    return `entity-${String(this.sequence).padStart(4, "0")}`;
  }

  addEntity({ id, name = "Spatial Entity", parentId = "world-root", components = {} } = {}) {
    if (this.entities.size >= this.maxEntities) throw new Error("ENTITY_LIMIT_REACHED");
    if (!this.entities.has(parentId)) throw new Error("PARENT_ENTITY_NOT_FOUND");
    const entityId = id ?? this.makeId();
    if (this.entities.has(entityId)) throw new Error("ENTITY_ID_CONFLICT");
    const time = now();
    const entity = {
      id: entityId,
      name: String(name).trim() || "Spatial Entity",
      parentId,
      children: [],
      components: {
        [TRANSFORM_COMPONENT]: defaultTransform(components[TRANSFORM_COMPONENT]),
        ...clone(components)
      },
      createdAt: time,
      modifiedAt: time
    };
    this.entities.set(entityId, entity);
    this.entities.get(parentId).children.push(entityId);
    this.select(entityId);
    this.emit("entity-added", clone(entity));
    this.emit("changed", this.snapshot());
    return clone(entity);
  }

  createPrimitive(kind = "orb", options = {}) {
    const palette = {
      orb: { geometry: "sphere", emissive: true },
      membrane: { geometry: "torus", transmissive: true },
      portal: { geometry: "ring", emissive: true },
      panel: { geometry: "plane", transmissive: true },
      light: { geometry: "point", emissive: true }
    };
    const primitive = palette[kind] ?? palette.orb;
    return this.addEntity({
      name: options.name ?? `${kind[0].toUpperCase()}${kind.slice(1)} ${this.sequence + 1}`,
      parentId: options.parentId ?? "world-root",
      components: {
        Transform: defaultTransform(options.transform),
        Renderable: { primitive: kind, ...primitive, material: options.material ?? "holographic" },
        Interaction: { selectable: true, draggable: true },
        Metadata: { classification: "PRESENTATION_SCENE_ENTITY", source: options.source ?? "creator" }
      }
    });
  }

  get(id) {
    const entity = this.entities.get(id);
    return entity ? clone(entity) : null;
  }

  list() {
    return [...this.entities.values()].map(clone);
  }

  select(id) {
    if (!this.entities.has(id)) throw new Error("ENTITY_NOT_FOUND");
    this.selectedEntityId = id;
    const entity = this.get(id);
    this.emit("selection", entity);
    return entity;
  }

  rename(id, name) {
    const entity = this.require(id);
    const normalized = String(name ?? "").trim();
    if (!normalized) throw new Error("ENTITY_NAME_REQUIRED");
    entity.name = normalized;
    entity.modifiedAt = now();
    this.emit("changed", this.snapshot());
    return this.get(id);
  }

  setComponent(id, type, value) {
    const entity = this.require(id);
    if (!type) throw new Error("COMPONENT_TYPE_REQUIRED");
    entity.components[type] = clone(value ?? {});
    if (type === TRANSFORM_COMPONENT) entity.components[type] = defaultTransform(entity.components[type]);
    entity.modifiedAt = now();
    this.emit("component-updated", { entityId: id, type, value: clone(entity.components[type]) });
    this.emit("changed", this.snapshot());
    return clone(entity.components[type]);
  }

  patchComponent(id, type, patch = {}) {
    const entity = this.require(id);
    const existing = entity.components[type] ?? {};
    return this.setComponent(id, type, { ...clone(existing), ...clone(patch) });
  }

  translate(id, delta = [0, 0, 0]) {
    const entity = this.require(id);
    const transform = defaultTransform(entity.components.Transform);
    transform.position = transform.position.map((value, index) => Number(value) + Number(delta[index] ?? 0));
    return this.setComponent(id, TRANSFORM_COMPONENT, transform);
  }

  removeComponent(id, type) {
    if (type === TRANSFORM_COMPONENT) throw new Error("TRANSFORM_COMPONENT_REQUIRED");
    const entity = this.require(id);
    const existed = Object.prototype.hasOwnProperty.call(entity.components, type);
    delete entity.components[type];
    entity.modifiedAt = now();
    if (existed) this.emit("changed", this.snapshot());
    return existed;
  }

  reparent(id, parentId) {
    if (id === "world-root") throw new Error("WORLD_ROOT_IMMUTABLE");
    const entity = this.require(id);
    const parent = this.require(parentId);
    if (id === parentId || this.descendants(id).includes(parentId)) throw new Error("SCENE_GRAPH_CYCLE");
    const previous = this.require(entity.parentId);
    previous.children = previous.children.filter((childId) => childId !== id);
    parent.children.push(id);
    entity.parentId = parentId;
    entity.modifiedAt = now();
    this.emit("changed", this.snapshot());
    return this.get(id);
  }

  removeEntity(id) {
    if (id === "world-root") throw new Error("WORLD_ROOT_IMMUTABLE");
    const entity = this.require(id);
    const ids = [id, ...this.descendants(id)];
    const parent = this.require(entity.parentId);
    parent.children = parent.children.filter((childId) => childId !== id);
    for (const entityId of ids) this.entities.delete(entityId);
    if (ids.includes(this.selectedEntityId)) this.selectedEntityId = "world-root";
    this.emit("entity-removed", { id, removed: ids });
    this.emit("changed", this.snapshot());
    return ids;
  }

  descendants(id) {
    const result = [];
    const stack = [...this.require(id).children];
    while (stack.length) {
      const childId = stack.shift();
      result.push(childId);
      stack.push(...this.require(childId).children);
    }
    return result;
  }

  require(id) {
    const entity = this.entities.get(id);
    if (!entity) throw new Error("ENTITY_NOT_FOUND");
    return entity;
  }

  load(snapshot = {}) {
    const entities = Array.isArray(snapshot.entities) ? snapshot.entities : [];
    if (!entities.length) return this.reset();
    if (entities.length > this.maxEntities) throw new Error("ENTITY_LIMIT_REACHED");
    const map = new Map(entities.map((entity) => [entity.id, clone(entity)]));
    if (!map.has("world-root")) throw new Error("WORLD_ROOT_REQUIRED");
    for (const entity of map.values()) {
      if (entity.parentId !== null && !map.has(entity.parentId)) throw new Error("DANGLING_SCENE_PARENT");
      entity.components = entity.components ?? {};
      entity.components.Transform = defaultTransform(entity.components.Transform);
      entity.children = Array.isArray(entity.children) ? entity.children : [];
    }
    this.entities = map;
    this.sequence = Math.max(0, ...entities.map((entity) => Number(String(entity.id).match(/(\d+)$/)?.[1] ?? 0)));
    this.selectedEntityId = map.has(snapshot.selectedEntityId) ? snapshot.selectedEntityId : "world-root";
    this.emit("changed", this.snapshot());
    this.emit("selection", this.get(this.selectedEntityId));
    return this.snapshot();
  }

  snapshot() {
    return {
      schema: "HHS_ENTITY_SCENE_GRAPH_V4",
      classification: "PRESENTATION_AND_SIMULATION_STATE_ONLY",
      selectedEntityId: this.selectedEntityId,
      entities: [...this.entities.values()].map(clone).sort((a, b) => a.id.localeCompare(b.id))
    };
  }

  async digest() {
    return sha256Text(JSON.stringify(canonical(this.snapshot())));
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail: clone(detail) }));
  }
}

export { MAX_ENTITIES, TRANSFORM_COMPONENT, canonical, sha256Text };
