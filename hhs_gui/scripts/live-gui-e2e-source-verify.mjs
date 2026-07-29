import fs from "node:fs"

const files = {
  socket: "runtime_os/core/RuntimeSocketManager.ts",
  runtimeOS: "runtime_os/core/RuntimeOS.ts",
  windowManager: "runtime_os/core/RuntimeWindowManager.ts",
  projectionPanel: "runtime_os/core/LiveRuntimeProjectionPanel.tsx",
  commandClient: "runtime_os/core/RuntimeCommandClient.ts",
  commandPanel: "runtime_os/core/RuntimeCommandPanel.tsx",
  mutationClient: "runtime_os/core/RuntimeMutationClient.ts",
  mutationPanel: "runtime_os/core/RuntimeMutationPanel.tsx",
  canonicalIDE: "runtime_os/core/CanonicalRuntimeIDE.tsx",
  workspace: "runtime_os/workspace/HHSWorkspaceShell.tsx",
  assistant: "runtime_os/assistant/RuntimeAssistantPanel.tsx",
  capability: "runtime_os/capability/LiveBackendCapabilityPanel.tsx",
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

for (const token of ["HHS_LIVE_GUI_COMMAND_ENVELOPE_V1", "/api/runtime/gui/command", "requires_admissibility", "REQUEST_ONLY_NO_DIRECT_MUTATION"]) {
  assert(content.commandClient.includes(token) || content.commandPanel.includes(token), `GUI command path missing ${token}`)
}

for (const token of ["AUTHORIZED_MUTATION", "runtime-mutation-panel", "pre_state_hash72", "transformation_hash72", "post_state_hash72", "NO_UI_EVENT_AS_TRUTH"]) {
  assert(content.mutationClient.includes(token) || content.mutationPanel.includes(token), `GUI mutation path missing ${token}`)
}

assert(content.projectionPanel.includes("GUI projection only"), "projection panel does not declare projection-only role")
assert(content.commandPanel.includes("GUI may request; kernel decides"), "command panel does not declare request-only command doctrine")
assert(content.canonicalIDE.includes("LiveRuntimeProjectionPanel"), "CanonicalRuntimeIDE does not mount LiveRuntimeProjectionPanel")
assert(content.canonicalIDE.includes("RuntimeCommandPanel"), "CanonicalRuntimeIDE does not mount RuntimeCommandPanel")
assert(content.canonicalIDE.includes("RuntimeMutationPanel"), "CanonicalRuntimeIDE does not mount RuntimeMutationPanel")
assert(content.canonicalIDE.includes("HHSWorkspaceShell"), "CanonicalRuntimeIDE does not mount HHSWorkspaceShell")
assert(content.vite.includes('"/ws"') && content.vite.includes("ws: true"), "Vite websocket proxy missing")
assert(!content.socket.includes("NODE_DEMO_STUB"), "socket manager contains Node demo authority")

assert(content.windowManager.includes("export class RuntimeWindowManager"), "RuntimeWindowManager is not a constructible state class")
assert(content.runtimeOS.includes("new RuntimeWindowManager"), "RuntimeOS does not instantiate the state manager")
assert(
  !fs.existsSync(new URL("../runtime_os/core/RuntimeWindowManager.tsx", import.meta.url)),
  "same-stem RuntimeWindowManager.tsx would shadow the state manager constructor",
)
assert(
  content.vite.indexOf('".ts"') < content.vite.indexOf('".tsx"'),
  "Vite must resolve .ts state modules before .tsx view modules",
)

for (const endpoint of [
  "/api/assistant/health",
  "/api/assistant/chat",
  "/api/runtime/canonical-observer/status",
  "/api/runtime/capability/status",
  "/api/runtime/capability/contracts",
  "/api/runtime/capability/providers",
  "/api/runtime/capability/resolve",
  "/api/runtime/document/perception/status",
  "/v1/modalities/language/models/word2vec/status",
]) {
  const livePanels = `${content.assistant}\n${content.capability}`
  assert(livePanels.includes(endpoint), `canonical IDE missing live endpoint ${endpoint}`)
}

for (const token of ["RuntimeAssistantPanel", "LiveBackendCapabilityPanel", "HHSSymbolicEditor", "CompilerWorkbench", "EmulatorControlPanel", "ReceiptLedgerInspector"]) {
  assert(content.workspace.includes(token), `HHSWorkspaceShell missing integrated surface ${token}`)
}

for (const forbidden of ["ProductionApp", "runtime_application_missing", "detached deployment mode"]) {
  const publicSources = `${content.canonicalIDE}\n${content.workspace}\n${content.assistant}\n${content.capability}`
  assert(!publicSources.includes(forbidden), `obsolete public behavior leaked: ${forbidden}`)
}

console.log("live-gui-e2e-source-verify: PASS")
