import fs from "node:fs"

const files = {
  socket: "runtime_os/core/RuntimeSocketManager.ts",
  runtimeOS: "runtime_os/core/RuntimeOS.ts",
  windowManager: "runtime_os/core/RuntimeWindowManager.ts",
  projectionPanel: "runtime_os/core/LiveRuntimeProjectionPanel.tsx",
  canonicalIDE: "runtime_os/core/CanonicalRuntimeIDE.tsx",
  workspace: "runtime_os/workspace/HHSWorkspaceShell.tsx",
  assistant: "runtime_os/assistant/RuntimeAssistantPanel.tsx",
  commandClient: "runtime_os/workspace/WorkspaceCommandClient.ts",
  vite: "vite.config.ts",
}

const read = (path) => fs.readFileSync(new URL(`../${path}`, import.meta.url), "utf8")
const assert = (condition, message) => { if (!condition) throw new Error(message) }
const content = Object.fromEntries(Object.entries(files).map(([key, path]) => [key, read(path)]))

for (const token of ["runtime_state_hash72", "kernel_tick", "receipt_hash72", "getChannelHealth", "LIVE_KERNEL_CONNECTED"]) {
  assert(content.socket.includes(token), `RuntimeSocketManager missing ${token}`)
}

for (const channel of ["runtime", "replay", "graph", "transport"]) {
  assert(content.projectionPanel.includes(channel), `LiveRuntimeProjectionPanel missing ${channel}`)
}

assert(content.projectionPanel.includes("1500"), "live projection refresh is not production-bounded")
assert(content.projectionPanel.includes("Loaded only while the Runtime tab is active"), "runtime diagnostics are not deferred")
assert(content.canonicalIDE.includes("HHSWorkspaceShell"), "CanonicalRuntimeIDE does not mount HHSWorkspaceShell")
assert(!content.canonicalIDE.includes("RuntimeCommandPanel"), "isolated runtime command panel remains public")
assert(!content.canonicalIDE.includes("RuntimeMutationPanel"), "isolated runtime mutation panel remains public")

for (const endpoint of [
  "/api/runtime/workspace/session",
  "/api/runtime/workspace/command",
  "/api/runtime/live/tick",
]) {
  assert(`${content.workspace}\n${content.commandClient}`.includes(endpoint), `integrated workspace missing ${endpoint}`)
}

for (const operation of [
  "project.create",
  "ingress.register",
  "interpret.execute",
  "compile.execute",
  "emulator.create",
]) {
  assert(content.workspace.includes(operation), `integrated workspace missing ${operation}`)
}

for (const token of [
  "/api/assistant/health",
  "/api/assistant/chat",
  "workspace_surface",
  "source_object_id",
  "artifact_id",
]) {
  assert(content.assistant.includes(token), `assistant integration missing ${token}`)
}

assert(content.windowManager.includes("export class RuntimeWindowManager"), "RuntimeWindowManager is not a constructible state class")
assert(content.runtimeOS.includes("new RuntimeWindowManager"), "RuntimeOS does not instantiate the state manager")
assert(!fs.existsSync(new URL("../runtime_os/core/RuntimeWindowManager.tsx", import.meta.url)), "same-stem RuntimeWindowManager.tsx would shadow the state manager constructor")
assert(content.vite.indexOf('".ts"') < content.vite.indexOf('".tsx"'), "Vite must resolve .ts state modules before .tsx view modules")
assert(content.vite.includes('"/ws"') && content.vite.includes("ws: true"), "Vite websocket proxy missing")
assert(!content.socket.includes("NODE_DEMO_STUB"), "socket manager contains Node demo authority")

for (const forbidden of ["ProductionApp", "runtime_application_missing", "detached deployment mode"]) {
  const publicSources = `${content.canonicalIDE}\n${content.workspace}\n${content.assistant}`
  assert(!publicSources.includes(forbidden), `obsolete public behavior leaked: ${forbidden}`)
}

console.log("live-gui-e2e-source-verify: PASS")
