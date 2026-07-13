import fs from "node:fs"

const read = (path) => fs.readFileSync(new URL(`../${path}`, import.meta.url), "utf8")
const assert = (condition, message) => { if (!condition) throw new Error(message) }

const files = {
  shell: "runtime_os/workspace/HHSWorkspaceShell.tsx",
  projectTree: "runtime_os/workspace/RuntimeProjectTree.tsx",
  ingress: "runtime_os/workspace/MultimodalIngressPanel.tsx",
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
  runtimeShell: "runtime_os/core/RuntimeShell.tsx",
  universalModality: "runtime_os/modality/UniversalModalityPanel.tsx",
  adapterInspector: "runtime_os/modality/ModalityAdapterInspector.tsx",
  projectionLineage: "runtime_os/modality/ProjectionLineageViewer.tsx",
  crossModal: "runtime_os/modality/CrossModalTransformPanel.tsx",
  artifactPipeline: "runtime_os/artifacts/ArtifactPipelinePanel.tsx",
  artifactLineage: "runtime_os/artifacts/ArtifactLineageViewer.tsx",
}

const content = Object.fromEntries(Object.entries(files).map(([key, value]) => [key, read(value)]))

for (const token of [
  "HHS_VISUAL_RUNTIME_OS_WORKSPACE_V1",
  "hhs-visual-runtime-os-workspace",
  "request/projection only",
  "HHSWorkspaceShell",
]) {
  assert(content.shell.includes(token) || content.runtimeShell.includes(token) || content.store.includes(token), `workspace shell missing ${token}`)
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
assert(content.runtimeShell.includes("HHSWorkspaceShell"), "RuntimeShell does not mount workspace shell")


for (const token of [
  "HHS_UNIVERSAL_MODALITY_ADAPTER_V1",
  "private truth pipelines",
  "source ≠ projection ≠ artifact ≠ execution authority",
]) {
  assert(content.universalModality.includes(token), `universal modality panel missing ${token}`)
}
assert(content.adapterInspector.includes("projection_replaces_source"), "adapter inspector must expose projection/source separation")
assert(content.projectionLineage.includes("HHS_MODALITY_PROJECTION_RECORD_V1"), "projection lineage viewer missing projection schema")
assert(content.crossModal.includes("HHS_CROSS_MODAL_TRANSFORMATION_PLAN_V1"), "cross-modal panel missing transformation plan schema")
assert(content.artifactPipeline.includes("valid artifact ≠ authorized execution"), "artifact pipeline must preserve execution boundary")
assert(content.artifactLineage.includes("HHS_ARTIFACT_LINEAGE_RECORD_V1"), "artifact lineage viewer missing lineage schema")

console.log("workspace-source-verify: PASS")
