const MAX_ROUTES = 128;
const clone = (value) => JSON.parse(JSON.stringify(value));

export class WorldRouter extends EventTarget {
  constructor({ maxRoutes = MAX_ROUTES } = {}) {
    super();
    this.maxRoutes = maxRoutes;
    this.worlds = new Map();
    this.routes = new Map();
    this.currentWorldId = null;
    this.sequence = 0;
  }

  registerWorld(world) {
    if (!world?.id) throw new Error("WORLD_ID_REQUIRED");
    this.worlds.set(world.id, { id: world.id, name: world.name ?? world.id });
    if (!this.currentWorldId) this.currentWorldId = world.id;
    this.emit("changed", this.snapshot());
    return clone(this.worlds.get(world.id));
  }

  syncWorlds(worlds = []) {
    const prior = this.currentWorldId;
    this.worlds = new Map(worlds.map((world) => [world.id, { id: world.id, name: world.name ?? world.id }]));
    for (const [id, route] of this.routes) {
      if (!this.worlds.has(route.from) || !this.worlds.has(route.to)) this.routes.delete(id);
    }
    this.currentWorldId = this.worlds.has(prior) ? prior : worlds[0]?.id ?? null;
    this.emit("changed", this.snapshot());
    return this.snapshot();
  }

  addRoute({ from, to, label = "Spatial Portal", bidirectional = true, anchor = null } = {}) {
    if (this.routes.size >= this.maxRoutes) throw new Error("ROUTE_LIMIT_REACHED");
    if (!this.worlds.has(from) || !this.worlds.has(to)) throw new Error("ROUTE_WORLD_NOT_FOUND");
    if (from === to) throw new Error("SELF_ROUTE_REJECTED");
    const duplicate = [...this.routes.values()].find((route) => route.from === from && route.to === to && route.label === label);
    if (duplicate) return clone(duplicate);
    const id = `route-${String(++this.sequence).padStart(4, "0")}`;
    const route = { id, from, to, label, bidirectional: Boolean(bidirectional), anchor, createdAt: new Date().toISOString() };
    this.routes.set(id, route);
    this.emit("route-added", route);
    this.emit("changed", this.snapshot());
    return clone(route);
  }

  removeRoute(id) {
    const route = this.routes.get(id);
    if (!route) return false;
    this.routes.delete(id);
    this.emit("route-removed", route);
    this.emit("changed", this.snapshot());
    return true;
  }

  neighbors(worldId) {
    const result = [];
    for (const route of this.routes.values()) {
      if (route.from === worldId) result.push({ worldId: route.to, routeId: route.id });
      if (route.bidirectional && route.to === worldId) result.push({ worldId: route.from, routeId: route.id });
    }
    return result;
  }

  resolve(from, to) {
    if (!this.worlds.has(from) || !this.worlds.has(to)) throw new Error("ROUTE_WORLD_NOT_FOUND");
    const queue = [[from]];
    const visited = new Set([from]);
    while (queue.length) {
      const path = queue.shift();
      const tail = path[path.length - 1];
      if (tail === to) return path;
      for (const neighbor of this.neighbors(tail)) {
        if (!visited.has(neighbor.worldId)) {
          visited.add(neighbor.worldId);
          queue.push([...path, neighbor.worldId]);
        }
      }
    }
    return null;
  }

  navigate(to) {
    if (!this.currentWorldId) throw new Error("CURRENT_WORLD_UNAVAILABLE");
    const path = this.resolve(this.currentWorldId, to);
    if (!path) throw new Error("WORLD_ROUTE_UNREACHABLE");
    const from = this.currentWorldId;
    this.currentWorldId = to;
    const detail = { from, to, path, classification: "PRESENTATION_WORLD_NAVIGATION" };
    this.emit("navigation", detail);
    this.emit("changed", this.snapshot());
    return clone(detail);
  }

  load(snapshot = {}) {
    this.worlds = new Map((snapshot.worlds ?? []).map((world) => [world.id, clone(world)]));
    this.routes = new Map((snapshot.routes ?? []).map((route) => [route.id, clone(route)]));
    for (const route of this.routes.values()) {
      if (!this.worlds.has(route.from) || !this.worlds.has(route.to)) throw new Error("DANGLING_WORLD_ROUTE");
    }
    this.sequence = Math.max(0, ...[...this.routes.keys()].map((id) => Number(id.match(/(\d+)$/)?.[1] ?? 0)));
    this.currentWorldId = this.worlds.has(snapshot.currentWorldId) ? snapshot.currentWorldId : [...this.worlds.keys()][0] ?? null;
    this.emit("changed", this.snapshot());
    return this.snapshot();
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_WORLD_ROUTER_V4",
      classification: "PRESENTATION_NAVIGATION_ONLY",
      currentWorldId: this.currentWorldId,
      worlds: [...this.worlds.values()].map(clone),
      routes: [...this.routes.values()].map(clone)
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail: clone(detail) }));
  }
}

export { MAX_ROUTES };
