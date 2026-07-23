const LOSHU = [4, 9, 2, 3, 5, 7, 8, 1, 6];

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function neighborsFor(id) {
  const x = id % 9;
  const y = Math.floor(id / 9);
  const neighbors = [];
  for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
    const nx = x + dx;
    const ny = y + dy;
    if (nx >= 0 && nx < 9 && ny >= 0 && ny < 9) {
      neighbors.push(ny * 9 + nx);
    }
  }
  return neighbors;
}

export class SpatialWorldModel extends EventTarget {
  constructor() {
    super();
    this.selectedCell = null;
    this.activeCell = null;
    this.runtime = {};
    this.activationSequence = 0;
    this.cells = Array.from({ length: 81 }, (_, id) => {
      const x = id % 9;
      const y = Math.floor(id / 9);
      return {
        id,
        index: id + 1,
        x,
        y,
        blockX: Math.floor(x / 3),
        blockY: Math.floor(y / 3),
        localX: x % 3,
        localY: y % 3,
        loshu: LOSHU[(x % 3) + (y % 3) * 3],
        lane: id % 2 === 0 ? "A=xy" : "B=yx",
        reciprocalCell: id % 2 === 0 ? Math.min(80, id + 1) : id - 1,
        phase: (id % 9) / 9,
        binding: `VM81_CELL_${String(id + 1).padStart(2, "0")}`,
        runtimeState: "UNBOUND",
        opcode: null,
        receipt: null,
        activationCount: 0,
        lastActivatedAt: null,
        pinned: false,
        neighbors: neighborsFor(id),
        metadata: {}
      };
    });
  }

  getCell(id) {
    return Number.isInteger(id) ? this.cells[id] ?? null : null;
  }

  select(id, source = "pointer") {
    const cell = this.getCell(id);
    this.selectedCell = cell?.id ?? null;
    this.dispatchEvent(new CustomEvent("selection", { detail: { cell: cell ? clone(cell) : null, source } }));
    return cell ? clone(cell) : null;
  }

  clearSelection() {
    this.selectedCell = null;
    this.dispatchEvent(new CustomEvent("selection", { detail: { cell: null, source: "clear" } }));
  }

  togglePin(id) {
    const cell = this.getCell(id);
    if (!cell) {
      return null;
    }
    cell.pinned = !cell.pinned;
    this.dispatchEvent(new CustomEvent("cell-update", { detail: { cell: clone(cell), reason: "pin" } }));
    return clone(cell);
  }

  updateCell(id, patch = {}, reason = "local-metadata") {
    const cell = this.getCell(id);
    if (!cell) {
      return null;
    }
    const allowed = ["metadata", "pinned"];
    for (const key of allowed) {
      if (Object.prototype.hasOwnProperty.call(patch, key)) {
        cell[key] = clone(patch[key]);
      }
    }
    this.dispatchEvent(new CustomEvent("cell-update", { detail: { cell: clone(cell), reason } }));
    return clone(cell);
  }

  bindRuntime(summary = {}) {
    this.runtime = { ...this.runtime, ...summary };
    const step = Number(summary.step);
    if (Number.isFinite(step)) {
      this.activeCell = ((step % 81) + 81) % 81;
      const cell = this.cells[this.activeCell];
      cell.runtimeState = String(summary.state ?? "ACTIVE");
      cell.opcode = summary.opcode ?? cell.opcode;
      cell.receipt = summary.receipt ?? cell.receipt;
      cell.activationCount += 1;
      cell.lastActivatedAt = new Date().toISOString();
      cell.activationSequence = ++this.activationSequence;
    }
    this.dispatchEvent(new CustomEvent("runtime-binding", {
      detail: {
        summary: clone(this.runtime),
        activeCell: this.activeCell,
        cell: this.activeCell === null ? null : clone(this.getCell(this.activeCell))
      }
    }));
  }

  applyReplayFrame(frame = {}) {
    const payload = frame.event?.payload ?? frame.payload ?? {};
    const summary = payload.summary ?? payload;
    if (summary && typeof summary === "object") {
      this.bindRuntime(summary);
    }
    this.dispatchEvent(new CustomEvent("replay-frame", { detail: clone(frame) }));
  }

  activeNeighborhood(radius = 1) {
    if (this.activeCell === null) {
      return [];
    }
    let frontier = [this.activeCell];
    const seen = new Set(frontier);
    for (let depth = 0; depth < radius; depth += 1) {
      const next = [];
      for (const id of frontier) {
        for (const neighbor of this.cells[id].neighbors) {
          if (!seen.has(neighbor)) {
            seen.add(neighbor);
            next.push(neighbor);
          }
        }
      }
      frontier = next;
    }
    return [...seen].map((id) => clone(this.cells[id]));
  }

  loadSnapshot(snapshot = {}) {
    this.selectedCell = Number.isInteger(snapshot.selectedCell) ? snapshot.selectedCell : null;
    this.activeCell = Number.isInteger(snapshot.activeCell) ? snapshot.activeCell : null;
    this.runtime = snapshot.runtime && typeof snapshot.runtime === "object" ? clone(snapshot.runtime) : {};
    if (Array.isArray(snapshot.cells)) {
      for (const patch of snapshot.cells) {
        const cell = this.getCell(Number(patch.id));
        if (!cell) {
          continue;
        }
        for (const key of ["runtimeState", "opcode", "receipt", "activationCount", "lastActivatedAt", "pinned", "metadata"]) {
          if (Object.prototype.hasOwnProperty.call(patch, key)) {
            cell[key] = clone(patch[key]);
          }
        }
      }
    }
    this.dispatchEvent(new CustomEvent("snapshot-loaded", { detail: this.snapshot() }));
    if (this.selectedCell !== null) {
      this.select(this.selectedCell, "snapshot");
    }
    this.dispatchEvent(new CustomEvent("runtime-binding", {
      detail: {
        summary: clone(this.runtime),
        activeCell: this.activeCell,
        cell: this.activeCell === null ? null : clone(this.getCell(this.activeCell))
      }
    }));
    return this.snapshot();
  }

  snapshot() {
    return {
      schema: "HHS_SPATIAL_WORLD_SNAPSHOT_V2",
      selectedCell: this.selectedCell,
      activeCell: this.activeCell,
      runtime: clone(this.runtime),
      cells: this.cells.map(({ id, runtimeState, opcode, receipt, activationCount, lastActivatedAt, pinned, metadata }) => ({
        id,
        runtimeState,
        opcode,
        receipt,
        activationCount,
        lastActivatedAt,
        pinned,
        metadata: clone(metadata)
      }))
    };
  }
}

export const LOSHU_LAYOUT = Object.freeze([...LOSHU]);
