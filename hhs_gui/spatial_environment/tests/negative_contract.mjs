import assert from "node:assert/strict";
import { SessionStore } from "../src/session-store.js";
import { SpatialWorkspaceManager } from "../src/spatial-workspace-manager.js";
import { APPLICATIONS } from "../src/application-registry.js";
import { ProjectionJournal } from "../src/projection-journal.js";
import { RuntimeBridge } from "../src/runtime-bridge.js";
import { CommandRouter } from "../src/command-router.js";

class MemoryStorage {
  constructor() { this.map = new Map(); }
  getItem(key) { return this.map.get(key) ?? null; }
  setItem(key, value) { this.map.set(key, String(value)); }
}

const sessions = new SessionStore({ storage: new MemoryStorage() });
assert.throws(() => sessions.delete(sessions.activeSessionId), /CANNOT_DELETE_LAST_SESSION/);
assert.throws(() => sessions.import({ schema: "BAD", sessions: [] }), /INVALID_SESSION_EXPORT/);
assert.throws(() => sessions.rename(sessions.activeSessionId, ""), /SESSION_NAME_REQUIRED/);

const workspace = new SpatialWorkspaceManager({ viewportProvider: () => ({ width: 1000, height: 700 }) });
for (let index = 0; index < 24; index += 1) {
  workspace.open(APPLICATIONS[index % APPLICATIONS.length], { singleton: false });
}
assert.throws(() => workspace.open(APPLICATIONS[0], { singleton: false }), /SURFACE_LIMIT_REACHED/);
assert.equal(workspace.close("missing"), false);

const journal = new ProjectionJournal();
await journal.append("A", { x: 1 });
journal.entries[0].payload.x = 2;
assert.equal((await journal.verify()).valid, false);

const failingFetch = async () => { throw new Error("offline"); };
const bridge = new RuntimeBridge({ fetchImpl: failingFetch, WebSocketImpl: null });
await assert.rejects(() => bridge.execute("state", { timeoutMs: 50 }), /RUNTIME_UNAVAILABLE/);
await assert.rejects(() => bridge.execute("unknown"), /UNKNOWN_COMMAND/);

const router = new CommandRouter({ bridge, journal });
await assert.rejects(() => router.execute("missing"), /UNKNOWN_ROUTED_COMMAND/);

console.log("NEGATIVE_CONTRACT_PASSED");
console.log("session_guards=3");
console.log("surface_limit=24");
console.log("journal_tamper_detected=true");
console.log("runtime_unavailable_explicit=true");
