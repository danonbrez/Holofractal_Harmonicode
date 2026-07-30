import fs from "node:fs"

const files = {
  socket: "runtime_os/core/RuntimeSocketManager.ts",
  runtimeOS: "runtime_os/core/RuntimeOS.ts",
  integratedClient: "runtime_os/core/IntegratedRuntimeClient.ts",
  windowManager: "runtime_os/core/RuntimeWindowManager.ts",
  projectionPanel: "runtime_os/core/LiveRuntimeProjectionPanel.tsx",
  canonicalIDE: "runtime_os/core/CanonicalRuntimeIDE.tsx",
  product: "runtime_os/workspace/HHSProductWorkspace.tsx",
  programmer: "runtime_os/workspace/RegistryVisualProgrammer.tsx",
  workspace: "runtime_os/workspace/HHSWorkspaceShell.tsx",
  assistant: "runtime_os/assistant/RuntimeAssistantPanel.tsx",
  commandClient: "runtime_os/workspace/WorkspaceCommandClient.ts",
  applicationRegistry: "runtime_os/core/RuntimeApplicationRegistry.tsx",
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
assert(content.projectionPanel.includes("/api/runtime/authority/status"), "runtime surface does not verify backend authority")
assert(content.projectionPanel.includes("WebSockets are on-demand projection channels"), "runtime authority is still conflated with WebSocket projection")
assert(content.projectionPanel.includes("RUNTIME AUTHORITY ONLINE"), "runtime surface does not expose active authority")
assert(content.projectionPanel.includes("runtimeOS.initialize()"), "Runtime tab does not activate transport")
assert(content.projectionPanel.includes("runtimeOS.shutdown()"), "Runtime tab does not release transport")
assert(content.canonicalIDE.includes("HHSProductWorkspace"), "CanonicalRuntimeIDE does not mount the product workspace")
assert(content.product.includes("RegistryVisualProgrammer"), "product workspace does not expose registry visual programming")
assert(content.product.includes("HHSWorkspaceShell"), "product workspace removed the full conventional workspace")
assert(content.product.includes("/api/product/health"), "product does not verify runtime and assistant execution authorities")
assert(content.product.includes("runtime online"), "product does not expose runtime authority readiness")
assert(content.product.includes("assistantOnline"), "product does not expose assistant provider readiness")
assert(content.canonicalIDE.includes("IntegratedRuntimeClient"), "CanonicalRuntimeIDE does not use integrated client")
assert(!content.integratedClient.includes("RuntimeWindowManager"), "public client imports legacy window manager")
assert(!content.canonicalIDE.includes("RuntimeCommandPanel"), "isolated runtime command panel remains public")
assert(!content.canonicalIDE.includes("RuntimeMutationPanel"), "isolated runtime mutation panel remains public")

for (const token of [
  "/api/runtime/services",
  "/api/runtime/services/dispatch",
  "runtimeApplicationRegistry.all()",
  "topologicalOrder",
  "sourcePath",
  "targetPath",
  "executeNode",
  "runGraph",
  "HHS_REGISTRY_VISUAL_PROGRAM_V1",
]) {
  assert(content.programmer.includes(token), `registry visual programmer missing ${token}`)
}

for (const endpoint of [
  "/api/runtime/workspace/session",
  "/api/runtime/workspace/command",
  "/api/runtime/live/tick",
]) {
  assert(`${content.product}\n${content.workspace}\n${content.commandClient}`.includes(endpoint), `integrated product missing ${endpoint}`)
}

for (const operation of [
  "project.create",
  "ingress.register",
  "interpret.execute",
  "compile.execute",
  "emulator.create",
]) {
  assert(content.workspace.includes(operation), `integrated workspace missing ${operation}`)
  assert(content.programmer.includes(operation), `visual programming surface missing ${operation}`)
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

for (const token of ["lazyLoader", "resolveLazyComponent", "runtime_console", "calculator", "breadboard", "receipt_inspector", "replay_timeline"]) {
  assert(content.applicationRegistry.includes(token), `application registry missing ${token}`)
}

assert(content.windowManager.includes("export class RuntimeWindowManager"), "RuntimeWindowManager is not a constructible state class")
assert(content.runtimeOS.includes("new RuntimeWindowManager"), "legacy RuntimeOS state manager regression")
assert(!fs.existsSync(new URL("../runtime_os/core/RuntimeWindowManager.tsx", import.meta.url)), "same-stem RuntimeWindowManager.tsx would shadow the state manager constructor")
assert(content.vite.indexOf('".ts"') < content.vite.indexOf('".tsx"'), "Vite must resolve .ts state modules before .tsx view modules")
assert(content.vite.includes('"/ws"') && content.vite.includes("ws: true"), "Vite websocket proxy missing")
assert(!content.socket.includes("NODE_DEMO_STUB"), "socket manager contains Node demo authority")

for (const forbidden of ["ProductionApp", "runtime_application_missing", "detached deployment mode", "visual_shell_only: true"]) {
  const publicSources = `${content.canonicalIDE}\n${content.product}\n${content.programmer}\n${content.workspace}\n${content.assistant}`
  assert(!publicSources.includes(forbidden), `obsolete or shell-only public behavior leaked: ${forbidden}`)
}

console.log("live-gui-e2e-source-verify: PASS")
