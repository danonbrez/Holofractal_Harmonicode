import fs from "node:fs"

const read = (path) => fs.readFileSync(new URL(`../${path}`, import.meta.url), "utf8")
const assert = (condition, message) => { if (!condition) throw new Error(message) }

const files = {
  main: "main.tsx",
  canonicalIDE: "runtime_os/core/CanonicalRuntimeIDE.tsx",
  shell: "runtime_os/workspace/HHSWorkspaceShell.tsx",
  projectTree: "runtime_os/workspace/RuntimeProjectTree.tsx",
  ingress: "runtime_os/workspace/MultimodalIngressPanel.tsx",
  assistant: "runtime_os/assistant/RuntimeAssistantPanel.tsx",
  capability: "runtime_os/capability/LiveBackendCapabilityPanel.tsx",
  editor: "runtime_os/editor/HHSSymbolicEditor.tsx",
  interpreter: "runtime_os/console/InterpreterConsole.tsx",
  compiler: "runtime_os/compiler/CompilerWorkbench.tsx",
  emulator: "runtime_os/emulator/EmulatorControlPanel.tsx",
  graph: "runtime_os/graph/RuntimeGraphCanvas.tsx",
  memory: "runtime_os/memory/SemanticMemoryPanel.tsx",
  ledger: "runtime_os/ledger/ReceiptLedgerInspector.tsx",
  history: "runtime_os/history/MutationHistoryPanel.tsx",
  store: "runtime_os/workspace/WorkspaceProjectionStore.ts",
  commandClient: "runtime_os/workspace/WorkspaceCommandClient.ts",
}

const content = Object.fromEntries(Object.entries(files).map(([key, value]) => [key, read(value)]))

for (const token of [
  "hhs-canonical-runtime-ide",
  "hhs-visual-runtime-os-workspace",
  "CanonicalRuntimeIDE",
  "HHSWorkspaceShell",
]) {
  const combined = `${content.main}\n${content.canonicalIDE}\n${content.shell}`
  assert(combined.includes(token), `canonical workspace missing ${token}`)
}

for (const token of [
  "HHS_WORKSPACE_COMMAND_ENVELOPE_V1",
  "frontend_may_commit_runtime_truth: false",
  "/api/runtime/workspace/command",
  "PRESENTATION_ONLY",
]) {
  assert(content.commandClient.includes(token), `workspace command client missing ${token}`)
}

for (const [name, token] of Object.entries({
  projectTree: "runtime-project-tree",
  ingress: "multimodal-ingress-panel",
  assistant: "runtime-assistant-panel",
  capability: "live-backend-capability-panel",
  editor: "hhs-symbolic-editor",
  interpreter: "interpreter-console",
  compiler: "compiler-workbench",
  emulator: "emulator-control-panel",
  graph: "runtime-graph-canvas",
  memory: "semantic-memory-panel",
  ledger: "receipt-ledger-inspector",
  history: "mutation-history-panel",
})) {
  assert(content[name].includes(token), `${name} missing ${token}`)
}

assert(content.ingress.includes("Original source is preserved"), "ingress panel must preserve original source")
assert(content.editor.includes("local buffer non-authoritative"), "editor buffer must be non-authoritative")
assert(content.interpreter.includes("No arbitrary host-language evaluation"), "interpreter host eval boundary missing")
assert(content.compiler.includes("Compilation does not imply execution authorization"), "compiler authorization boundary missing")
assert(content.emulator.includes("rewind never erases history"), "emulator history boundary missing")
assert(content.graph.includes("Canvas layout is presentation state"), "graph presentation/truth boundary missing")
assert(content.memory.includes("ranking are projections"), "semantic memory projection boundary missing")
assert(content.store.includes("frontendCacheIsAuthority: false"), "projection store must reject frontend cache authority")

for (const endpoint of [
  "/api/assistant/health",
  "/api/assistant/chat",
  "/api/runtime/capability/status",
  "/api/runtime/capability/resolve",
  "/api/runtime/document/perception/status",
  "/v1/modalities/language/models/word2vec/status",
]) {
  const combined = `${content.assistant}\n${content.capability}`
  assert(combined.includes(endpoint), `live workspace missing backend endpoint ${endpoint}`)
}

for (const forbidden of [
  "ProductionApp",
  "CapabilityRegistryPanel",
  "DocumentPerceptionPanel",
  "runtime_application_missing",
]) {
  assert(!content.main.includes(forbidden) && !content.shell.includes(forbidden), `obsolete public surface leaked: ${forbidden}`)
}

console.log("workspace-source-verify: PASS")
