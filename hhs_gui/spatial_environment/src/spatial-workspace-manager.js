const MIN_WIDTH = 260;
const MIN_HEIGHT = 180;
const MAX_SURFACES = 24;

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function makeSurfaceId(applicationId) {
  return `${applicationId}-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function defaultPosition(anchor, viewport, width, height, offset = 0) {
  const vw = Math.max(800, viewport?.width ?? 1280);
  const vh = Math.max(600, viewport?.height ?? 800);
  const margin = 28 + offset * 22;
  switch (anchor) {
    case "left":
      return { x: margin, y: 90 + offset * 18 };
    case "right":
      return { x: vw - width - margin, y: 90 + offset * 18 };
    case "bottom":
      return { x: (vw - width) / 2, y: vh - height - 105 };
    default:
      return { x: (vw - width) / 2 + offset * 18, y: (vh - height) / 2 + offset * 14 };
  }
}

export class SpatialWorkspaceManager extends EventTarget {
  constructor({ viewportProvider = () => ({ width: globalThis.innerWidth, height: globalThis.innerHeight }) } = {}) {
    super();
    this.viewportProvider = viewportProvider;
    this.surfaces = [];
    this.focusedSurfaceId = null;
    this.zCounter = 100;
  }

  open(application, options = {}) {
    if (!application?.id) {
      throw new Error("APPLICATION_REQUIRED");
    }
    if (this.surfaces.length >= MAX_SURFACES) {
      throw new Error("SURFACE_LIMIT_REACHED");
    }

    const existing = options.singleton !== false
      ? this.surfaces.find((surface) => surface.applicationId === application.id)
      : null;
    if (existing) {
      this.focus(existing.id);
      return clone(existing);
    }

    const preset = application.defaultSurface ?? {};
    const width = clamp(Number(options.width ?? preset.width ?? 460), MIN_WIDTH, 1200);
    const height = clamp(Number(options.height ?? preset.height ?? 340), MIN_HEIGHT, 900);
    const position = defaultPosition(
      options.anchor ?? preset.anchor ?? "center",
      this.viewportProvider(),
      width,
      height,
      this.surfaces.length % 5
    );
    const surface = {
      id: options.id ?? makeSurfaceId(application.id),
      applicationId: application.id,
      title: options.title ?? application.label,
      glyph: application.glyph ?? "◇",
      authority: application.authority ?? "PRESENTATION_ONLY",
      feature: application.feature ?? "dashboard",
      x: Number(options.x ?? position.x),
      y: Number(options.y ?? position.y),
      width,
      height,
      z: ++this.zCounter,
      minimized: Boolean(options.minimized),
      maximized: false,
      dock: options.dock ?? null,
      pinned: Boolean(options.pinned),
      createdAt: options.createdAt ?? new Date().toISOString(),
      state: clone(options.state ?? {})
    };
    this.surfaces.push(surface);
    this.focusedSurfaceId = surface.id;
    this.emit("surface-opened", clone(surface));
    this.emit("changed", this.snapshot());
    return clone(surface);
  }

  close(id) {
    const index = this.surfaces.findIndex((surface) => surface.id === id);
    if (index < 0) {
      return false;
    }
    const [surface] = this.surfaces.splice(index, 1);
    if (this.focusedSurfaceId === id) {
      this.focusedSurfaceId = this.surfaces.at(-1)?.id ?? null;
    }
    this.emit("surface-closed", clone(surface));
    this.emit("changed", this.snapshot());
    return true;
  }

  focus(id) {
    const surface = this.get(id);
    if (!surface) {
      return null;
    }
    surface.z = ++this.zCounter;
    surface.minimized = false;
    this.focusedSurfaceId = id;
    this.emit("surface-focused", clone(surface));
    this.emit("changed", this.snapshot());
    return clone(surface);
  }

  move(id, x, y) {
    const surface = this.get(id);
    if (!surface || surface.maximized || surface.pinned) {
      return null;
    }
    const viewport = this.viewportProvider();
    surface.x = clamp(Number(x), -surface.width + 80, Math.max(80, viewport.width - 80));
    surface.y = clamp(Number(y), 60, Math.max(80, viewport.height - 80));
    surface.dock = null;
    this.emit("surface-updated", clone(surface));
    return clone(surface);
  }

  resize(id, width, height) {
    const surface = this.get(id);
    if (!surface || surface.maximized || surface.pinned) {
      return null;
    }
    const viewport = this.viewportProvider();
    surface.width = clamp(Number(width), MIN_WIDTH, Math.max(MIN_WIDTH, viewport.width - 24));
    surface.height = clamp(Number(height), MIN_HEIGHT, Math.max(MIN_HEIGHT, viewport.height - 100));
    surface.dock = null;
    this.emit("surface-updated", clone(surface));
    return clone(surface);
  }

  minimize(id) {
    const surface = this.get(id);
    if (!surface) {
      return null;
    }
    surface.minimized = !surface.minimized;
    surface.maximized = false;
    this.emit("surface-updated", clone(surface));
    this.emit("changed", this.snapshot());
    return clone(surface);
  }

  maximize(id) {
    const surface = this.get(id);
    if (!surface) {
      return null;
    }
    if (!surface.maximized) {
      surface.restoreBounds = {
        x: surface.x,
        y: surface.y,
        width: surface.width,
        height: surface.height,
        dock: surface.dock
      };
      surface.x = 16;
      surface.y = 76;
      surface.width = Math.max(MIN_WIDTH, this.viewportProvider().width - 32);
      surface.height = Math.max(MIN_HEIGHT, this.viewportProvider().height - 166);
      surface.maximized = true;
      surface.minimized = false;
      surface.dock = null;
    } else {
      Object.assign(surface, surface.restoreBounds ?? {});
      surface.maximized = false;
      delete surface.restoreBounds;
    }
    this.focus(id);
    this.emit("surface-updated", clone(surface));
    this.emit("changed", this.snapshot());
    return clone(surface);
  }

  pin(id) {
    const surface = this.get(id);
    if (!surface) {
      return null;
    }
    surface.pinned = !surface.pinned;
    this.emit("surface-updated", clone(surface));
    this.emit("changed", this.snapshot());
    return clone(surface);
  }

  dock(id, dock) {
    const surface = this.get(id);
    if (!surface) {
      return null;
    }
    const viewport = this.viewportProvider();
    const margin = 18;
    const usableHeight = Math.max(MIN_HEIGHT, viewport.height - 170);
    surface.maximized = false;
    surface.minimized = false;
    surface.dock = dock;
    if (dock === "left") {
      Object.assign(surface, { x: margin, y: 78, width: Math.max(MIN_WIDTH, viewport.width * 0.34), height: usableHeight });
    } else if (dock === "right") {
      const width = Math.max(MIN_WIDTH, viewport.width * 0.34);
      Object.assign(surface, { x: viewport.width - width - margin, y: 78, width, height: usableHeight });
    } else if (dock === "bottom") {
      Object.assign(surface, { x: margin, y: viewport.height - Math.max(MIN_HEIGHT, viewport.height * 0.36) - 84, width: viewport.width - margin * 2, height: Math.max(MIN_HEIGHT, viewport.height * 0.36) });
    } else {
      surface.dock = null;
    }
    this.focus(id);
    this.emit("surface-updated", clone(surface));
    this.emit("changed", this.snapshot());
    return clone(surface);
  }

  arrange(layout = "cascade") {
    const viewport = this.viewportProvider();
    const visible = this.surfaces.filter((surface) => !surface.minimized);
    if (!visible.length) {
      return this.snapshot();
    }

    if (layout === "grid") {
      const columns = Math.ceil(Math.sqrt(visible.length));
      const rows = Math.ceil(visible.length / columns);
      const gap = 12;
      const top = 78;
      const bottom = 86;
      const width = (viewport.width - gap * (columns + 1)) / columns;
      const height = (viewport.height - top - bottom - gap * (rows + 1)) / rows;
      visible.forEach((surface, index) => {
        const column = index % columns;
        const row = Math.floor(index / columns);
        Object.assign(surface, {
          x: gap + column * (width + gap),
          y: top + gap + row * (height + gap),
          width: Math.max(MIN_WIDTH, width),
          height: Math.max(MIN_HEIGHT, height),
          dock: null,
          maximized: false,
          z: ++this.zCounter
        });
      });
    } else if (layout === "focus") {
      const focused = this.get(this.focusedSurfaceId) ?? visible.at(-1);
      visible.forEach((surface) => {
        surface.minimized = surface.id !== focused.id;
      });
      this.maximize(focused.id);
    } else {
      visible.forEach((surface, index) => {
        surface.x = 80 + index * 34;
        surface.y = 100 + index * 28;
        surface.width = clamp(surface.width, MIN_WIDTH, Math.min(620, viewport.width - 160));
        surface.height = clamp(surface.height, MIN_HEIGHT, Math.min(430, viewport.height - 190));
        surface.dock = null;
        surface.maximized = false;
        surface.z = ++this.zCounter;
      });
    }
    this.emit("arranged", { layout, snapshot: this.snapshot() });
    this.emit("changed", this.snapshot());
    return this.snapshot();
  }

  updateState(id, patch = {}) {
    const surface = this.get(id);
    if (!surface) {
      return null;
    }
    surface.state = { ...surface.state, ...clone(patch) };
    this.emit("surface-updated", clone(surface));
    return clone(surface);
  }

  get(id) {
    return this.surfaces.find((surface) => surface.id === id) ?? null;
  }

  load(snapshot = []) {
    const surfaces = Array.isArray(snapshot) ? snapshot : snapshot.surfaces;
    this.surfaces = Array.isArray(surfaces)
      ? surfaces.slice(0, MAX_SURFACES).map((surface) => ({
          ...clone(surface),
          width: clamp(Number(surface.width ?? 460), MIN_WIDTH, 1200),
          height: clamp(Number(surface.height ?? 340), MIN_HEIGHT, 900),
          z: ++this.zCounter
        }))
      : [];
    this.focusedSurfaceId = this.surfaces.at(-1)?.id ?? null;
    this.emit("loaded", this.snapshot());
    this.emit("changed", this.snapshot());
    return this.snapshot();
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_SURFACE_LAYOUT_V3",
      focusedSurfaceId: this.focusedSurfaceId,
      surfaceCount: this.surfaces.length,
      surfaces: clone(this.surfaces)
    };
  }

  emit(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }
}
