import fs from "node:fs"

const read = (path) => fs.readFileSync(new URL(`../${path}`, import.meta.url), "utf8")
const readRepo = (path) => fs.readFileSync(new URL(`../../${path}`, import.meta.url), "utf8")
const assert = (condition, message) => { if (!condition) throw new Error(message) }

const content = {
  main: read("main.tsx"),
  canonicalIDE: read("runtime_os/core/CanonicalRuntimeIDE.tsx"),
  shell: read("runtime_os/workspace/HHSWorkspaceShell.tsx"),
  assistant: read("runtime_os/assistant/RuntimeAssistantPanel.tsx"),
  projection: read("runtime_os/core/LiveRuntimeProjectionPanel.tsx"),
  commandClient: read("runtime_os/workspace/WorkspaceCommandClient.ts"),
  productionServer: readRepo("hhs_backend/production_server.py"),
}

const publicSource = `${content.main}\n${content.canonicalIDE}\n${content.shell}`
for (const token of [
  "hhs-canonical-runtime-ide",
  "hhs-visual-runtime-os-workspace",
  "CanonicalRuntimeIDE",
  "HHSWorkspaceShell",
]) {
  assert(publicSource.includes(token), `canonical workspace missing ${token}`)
}

for (const token of [
  "projectId",
  "selectedObjectId",
  "artifactId",
  "sessionId",
  "ensureProject",
  "ensureSource",
  "applyFeedback",
]) {
  assert(content.shell.includes(token), `integrated workspace missing shared state ${token}`)
}

for (const operation of [
  "project.create",
  "ingress.register",
  "interpret.execute",
  "compile.execute",
  "emulator.create",
  "emulator.step",
  "emulator.run",
  "emulator.snapshot",
]) {
  assert(content.shell.includes(operation), `integrated workflow missing ${operation}`)
}

for (const tab of ["workbench", "assistant", "runtime", "receipts"]) {
  assert(content.shell.includes(`tab === \"${tab}\"`), `responsive workspace missing active surface ${tab}`)
}

for (const token of [
  "HHS_WORKSPACE_COMMAND_ENVELOPE_V1",
  "frontend_may_commit_runtime_truth: false",
  "/api/runtime/workspace/command",
  "AUTHORIZED_NONMUTATING",
  "AbortController",
]) {
  assert(content.commandClient.includes(token), `workspace command client missing ${token}`)
}

for (const token of [
  "/api/runtime/workspace/session",
  "self_tests_executed",
  "_workspace_session_snapshot",
]) {
  assert(content.productionServer.includes(token), `lightweight workspace session missing ${token}`)
}

for (const token of [
  "projectId",
  "sourceObjectId",
  "artifactId",
  "workspace_surface",
  "/api/assistant/health",
  "/api/assistant/chat",
]) {
  assert(content.assistant.includes(token), `assistant workspace binding missing ${token}`)
}

assert(content.projection.includes("1500"), "runtime projection refresh is not bounded")
assert(content.shell.includes("Only operations that actually returned from the backend appear here"), "receipt surface may display fabricated activity")
assert(content.shell.includes("project objects".replace("p", "P")), "workspace does not expose real project objects")

for (const forbidden of [
  "RuntimeProjectTree",
  "MultimodalIngressPanel",
  "LiveBackendCapabilityPanel",
  "HHSSymbolicEditor",
  "InterpreterConsole",
  "CompilerWorkbench",
  "EmulatorControlPanel",
  "RuntimeGraphCanvas",
  "SemanticMemoryPanel",
  "ReceiptLedgerInspector",
  "MutationHistoryPanel",
  "RuntimeCommandPanel",
  "RuntimeMutationPanel",
  "ProductionApp",
  "runtime_application_missing",
]) {
  assert(!publicSource.includes(forbidden), `isolated or obsolete public panel leaked: ${forbidden}`)
}

console.log("workspace-source-verify: PASS")
