import fs from "node:fs"

const files = {
  socket: "runtime_os/core/RuntimeSocketManager.ts",
  projectionPanel: "runtime_os/core/LiveRuntimeProjectionPanel.tsx",
  commandClient: "runtime_os/core/RuntimeCommandClient.ts",
  commandPanel: "runtime_os/core/RuntimeCommandPanel.tsx",
  mutationClient: "runtime_os/core/RuntimeMutationClient.ts",
  mutationPanel: "runtime_os/core/RuntimeMutationPanel.tsx",
  shell: "runtime_os/core/RuntimeShell.tsx",
  vite: "vite.config.ts",
}

const read = (path) => fs.readFileSync(new URL(`../${path}`, import.meta.url), "utf8")
const assert = (condition, message) => {
  if (!condition) {
    throw new Error(message)
  }
}

const socket = read(files.socket)
const projectionPanel = read(files.projectionPanel)
const commandClient = read(files.commandClient)
const commandPanel = read(files.commandPanel)
const mutationClient = read(files.mutationClient)
const mutationPanel = read(files.mutationPanel)
const shell = read(files.shell)
const vite = read(files.vite)

for (const token of ["runtime_state_hash72", "kernel_tick", "receipt_hash72", "getChannelHealth", "LIVE_KERNEL_CONNECTED"]) {
  assert(socket.includes(token), `RuntimeSocketManager missing ${token}`)
}

const channelTestIds = ["live-channel-runtime", "live-channel-replay", "live-channel-graph", "live-channel-transport"]
for (const channel of ["runtime", "replay", "graph", "transport"]) {
  assert(projectionPanel.includes(channel), `LiveRuntimeProjectionPanel missing ${channel}`)
}
for (const testId of channelTestIds) {
  const channel = testId.replace("live-channel-", "")
  assert(projectionPanel.includes("live-channel-${health.channel}") || projectionPanel.includes(testId), `LiveRuntimeProjectionPanel missing ${testId}`)
  assert(projectionPanel.includes(channel), `LiveRuntimeProjectionPanel missing ${channel}`)
}

for (const token of ["HHS_LIVE_GUI_COMMAND_ENVELOPE_V1", "/api/runtime/gui/command", "requires_admissibility", "REQUEST_ONLY_NO_DIRECT_MUTATION"]) {
  assert(commandClient.includes(token) || commandPanel.includes(token), `GUI command path missing ${token}`)
}

for (const token of ["AUTHORIZED_MUTATION", "runtime-mutation-panel", "pre_state_hash72", "transformation_hash72", "post_state_hash72", "NO_UI_EVENT_AS_TRUTH"]) {
  assert(mutationClient.includes(token) || mutationPanel.includes(token), `GUI mutation path missing ${token}`)
}

assert(projectionPanel.includes("GUI projection only"), "projection panel does not declare projection-only role")
assert(commandPanel.includes("GUI may request; kernel decides"), "command panel does not declare request-only command doctrine")
assert(commandPanel.includes("runtime-command-panel"), "command panel test id missing")
assert(shell.includes("LiveRuntimeProjectionPanel"), "RuntimeShell does not mount LiveRuntimeProjectionPanel")
assert(shell.includes("RuntimeCommandPanel"), "RuntimeShell does not mount RuntimeCommandPanel")
assert(shell.includes("RuntimeMutationPanel"), "RuntimeShell does not mount RuntimeMutationPanel")
assert(vite.includes('"/ws"') && vite.includes("ws: true"), "Vite websocket proxy missing")
assert(!socket.includes("NODE_DEMO_STUB"), "socket manager contains Node demo authority")
console.log("live-gui-e2e-source-verify: PASS")

const workspaceShell = read("runtime_os/workspace/HHSWorkspaceShell.tsx")
const capabilityFiles = [
  "runtime_os/capability/RuntimeCanonicalObserverPanel.tsx",
  "runtime_os/capability/CapabilityRegistryPanel.tsx",
  "runtime_os/capability/ProviderInspector.tsx",
  "runtime_os/capability/CapabilityResolutionViewer.tsx",
  "runtime_os/capability/ExecutionProposalPanel.tsx",
  "runtime_os/capability/ProviderInvocationTimeline.tsx",
  "runtime_os/capability/FallbackPlanViewer.tsx",
  "runtime_os/capability/ProviderResultLineageViewer.tsx",
  "runtime_os/capability/CapabilityAuthorityStatus.tsx",
]
for (const file of capabilityFiles) {
  const source = read(file)
  assert(source.includes("data-testid"), `${file} missing source-verifiable test id`)
}
for (const token of ["RuntimeCanonicalObserverPanel", "CapabilityRegistryPanel", "ProviderInspector", "CapabilityResolutionViewer", "ExecutionProposalPanel", "ProviderInvocationTimeline", "FallbackPlanViewer", "ProviderResultLineageViewer", "CapabilityAuthorityStatus"]) {
  assert(workspaceShell.includes(token), `HHSWorkspaceShell missing ${token}`)
}
for (const token of ["NO_INTERFACE_IS_CANONICAL", "NO_PROVIDER_IS_CANONICAL", "provider ≠ capability", "provider output ≠ canonical truth", "successful invocation ≠ admitted mutation", "REJECT_RAW_PROVIDER_OUTPUT_AS_CANONICAL_SOURCE"]) {
  const haystack = capabilityFiles.map((file) => read(file)).join("\n")
  assert(haystack.includes(token), `capability GUI surfaces missing ${token}`)
}
console.log("capability-provider-fabric-source-verify: PASS")


const documentFiles = [
  "runtime_os/document/DocumentPerceptionPanel.tsx",
  "runtime_os/document/DocumentSourceInspector.tsx",
  "runtime_os/document/PageLayoutViewer.tsx",
  "runtime_os/document/OCRProjectionViewer.tsx",
  "runtime_os/document/DocumentFusionViewer.tsx",
  "runtime_os/document/TableProjectionViewer.tsx",
  "runtime_os/document/DocumentGraphViewer.tsx",
  "runtime_os/document/DocumentAmbiguityInspector.tsx",
  "runtime_os/document/DocumentReconstructionViewer.tsx",
]
for (const file of documentFiles) {
  const source = read(file)
  assert(source.includes("data-testid"), `${file} missing source-verifiable test id`)
}
for (const token of ["DocumentPerceptionPanel", "DocumentSourceInspector", "PageLayoutViewer", "OCRProjectionViewer", "DocumentFusionViewer", "TableProjectionViewer", "DocumentGraphViewer", "DocumentAmbiguityInspector", "DocumentReconstructionViewer"]) {
  assert(workspaceShell.includes(token), `HHSWorkspaceShell missing ${token}`)
}
const documentHaystack = documentFiles.map((file) => read(file)).join("\n")
for (const token of ["OCR text ≠ page image", "provider disagreement", "REJECT_PROVIDER_DISAGREEMENT_COLLAPSED_SILENTLY", "REJECT_OCR_TEXT_AS_DOCUMENT_SOURCE", "DOCUMENT_GRAPH_PROJECTION", "REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION"]) {
  assert(documentHaystack.includes(token), `document perception GUI surfaces missing ${token}`)
}
console.log("deep-document-perception-source-verify: PASS")
