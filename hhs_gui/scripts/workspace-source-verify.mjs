import fs from "node:fs"

const read = (path) => fs.readFileSync(new URL(`../${path}`, import.meta.url), "utf8")
const readRepo = (path) => fs.readFileSync(new URL(`../../${path}`, import.meta.url), "utf8")
const assert = (condition, message) => { if (!condition) throw new Error(message) }

const content = {
  main: read("main.tsx"),
  canonicalIDE: read("runtime_os/core/CanonicalRuntimeIDE.tsx"),
  client: read("runtime_os/core/IntegratedRuntimeClient.ts"),
  product: read("runtime_os/workspace/HHSProductWorkspace.tsx"),
  mobileControl: read("runtime_os/workspace/ProductionMobileControlCenter.tsx"),
  mobileAssistant: read("runtime_os/workspace/ProductionAssistantChat.tsx"),
  acquisition: read("runtime_os/workspace/OpenSourceAcquisitionPanel.tsx"),
  programmer: read("runtime_os/workspace/RegistryVisualProgrammer.tsx"),
  shell: read("runtime_os/workspace/HHSWorkspaceShell.tsx"),
  assistant: read("runtime_os/assistant/RuntimeAssistantPanel.tsx"),
  projection: read("runtime_os/core/LiveRuntimeProjectionPanel.tsx"),
  commandClient: read("runtime_os/workspace/WorkspaceCommandClient.ts"),
  applicationRegistry: read("runtime_os/core/RuntimeApplicationRegistry.tsx"),
  productionServer: readRepo("hhs_backend/production_server.py"),
  postCompile: readRepo("bin/post_compile"),
}

const publicSource = `${content.main}\n${content.canonicalIDE}\n${content.product}\n${content.programmer}\n${content.shell}`
for (const token of [
  "hhs-canonical-runtime-ide",
  "hhs-product-workspace",
  "registry-visual-programmer",
  "hhs-visual-runtime-os-workspace",
  "CanonicalRuntimeIDE",
  "HHSProductWorkspace",
  "RegistryVisualProgrammer",
  "HHSWorkspaceShell",
  "IntegratedRuntimeClient",
]) {
  assert(publicSource.includes(token), `canonical workspace missing ${token}`)
}

assert(!content.main.includes('from "./runtime_os/core/RuntimeOS"'), "legacy desktop RuntimeOS remains in public entry")
assert(!content.client.includes("RuntimeWindowManager"), "integrated client imports desktop window manager")
assert(content.projection.includes("runtimeOS.initialize()"), "runtime transport is not activated by the selected Runtime surface")
assert(content.projection.includes("runtimeOS.shutdown()"), "runtime transport remains active after leaving the Runtime surface")
assert(content.projection.includes("/api/runtime/authority/status"), "runtime authority is inferred only from projection traffic")
assert(content.projection.includes("WebSockets are on-demand projection channels"), "projection channel role is not explicit")

for (const token of [
  'useState<ProductSurface>("control")',
  "Control",
  "Visual Program",
  "Workspace",
  "Authority",
  "RegistryVisualProgrammer",
  "HHSWorkspaceShell",
  "executeWorkspaceOperation",
  "/api/product/health",
  "runtimeOnline",
  "assistantOnline",
]) {
  assert(content.product.includes(token), `product composition missing ${token}`)
}

for (const token of [
  "ProductionAssistantChat",
  "/api/v1/pass174/sdlc/run",
  "/api/v1/pass174/hash216/query",
  "Hydrate vector store",
  "Files → multimodal ingress → vector store",
  "type=\"file\"",
  "multiple",
]) {
  assert(content.mobileControl.includes(token), `mobile control surface missing ${token}`)
}

for (const token of [
  "/api/assistant/health",
  "/api/assistant/chat",
  "New chat",
  "Message HHS",
  "How can I help?",
  "Enter sends",
  "uploaded payloads are not automatically attached to assistant prompts",
  "vector_payload_auto_attached_to_prompt: false",
  "Settings",
  "System instructions",
  "custom_system_instruction",
  "hhs.production.assistant.custom_system_instruction",
  "navigator.clipboard?.writeText",
  "navigator.clipboard?.readText",
  "Copy",
  "Paste",
  "Assistant mode",
  "GENERAL_CHAT",
  "AGENTIC_APPLICATION_DEVELOPMENT",
  "BOTH",
  "General chat",
  "Agentic application development",
  "hhs.production.assistant.mode",
  "assistant_mode: assistantMode",
]) {
  assert(content.mobileAssistant.includes(token), `mobile LLM assistant surface missing ${token}`)
}

assert(content.mobileAssistant.includes("min-h-[42vh]"), "mobile assistant chat does not reserve a usable touch viewport")
assert(content.mobileAssistant.includes("bg-neutral-900/70"), "mobile assistant dark-theme surface missing")
assert(content.mobileControl.includes("ProductionAssistantChat"), "production mobile control does not mount the LLM assistant")
assert(content.mobileControl.includes("Inspect technical JSON"), "vector technical JSON does not require explicit inspection")
assert(content.mobileControl.indexOf("Inspect technical JSON") < content.mobileControl.indexOf("JSON.stringify(vectorQuery"), "vector JSON appears before its inspect control")
assert(content.acquisition.includes("Inspect technical JSON"), "acquisition technical JSON does not require explicit inspection")
assert(content.acquisition.indexOf("Inspect technical JSON") < content.acquisition.indexOf("JSON.stringify(selected"), "acquisition JSON appears before its inspect control")
for (const token of [
  "/api/runtime/services",
  "/api/runtime/services/dispatch",
  "runtimeApplicationRegistry.all()",
  "resolveLazyComponent",
  "topologicalOrder",
  "executeNode",
  "runGraph",
  "sourcePath",
  "targetPath",
  "schemaDefaults",
  "setPath",
  "getPath",
  "HHS_REGISTRY_VISUAL_PROGRAM_V1",
  "JSON_EXECUTION_GRAPH",
  "Witness graph",
  "Run graph",
  "Schema inputs",
  "Raw payload",
  "Data edges",
  "Suspense",
  "ApplicationBoundary",
]) {
  assert(content.programmer.includes(token), `registry visual programmer missing ${token}`)
}

assert(content.programmer.includes("visibleDefinitions.map"), "registry palette does not expose every matching definition")
assert(content.programmer.includes('definition.kind === "service"'), "backend services are not executable nodes")
assert(content.programmer.includes('definition.kind === "workspace"'), "workspace operations are not executable nodes")
assert(content.programmer.includes("setActiveApplicationId"), "application registry modules are inactive catalog entries")
assert(content.programmer.includes("resultMap"), "graph execution does not propagate actual prior-node results")
assert(content.programmer.includes('throw new Error("Visual program contains a cycle'), "graph cycle rejection is missing")
assert(!content.programmer.includes("disabled registry item"), "registry contains intentionally inactive buttons")

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
  assert(content.programmer.includes(operation), `visual programming registry missing workspace operation ${operation}`)
  assert(content.shell.includes(operation), `integrated workflow missing ${operation}`)
}

for (const token of [
  "lazyLoader",
  "resolveLazyComponent",
  "runtime_console",
  "calculator",
  "graph_projection",
  "breadboard",
  "receipt_inspector",
  "replay_timeline",
]) {
  assert(content.applicationRegistry.includes(token), `runtime application registry missing ${token}`)
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
  "/api/runtime/authority/status",
  "/api/product/health",
  "_runtime_authority_status",
  "_assistant_health",
  "self_tests_executed",
  "_workspace_session_snapshot",
  'os.environ.setdefault("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC", "0")',
]) {
  assert(content.productionServer.includes(token), `production authority composition missing ${token}`)
}
assert(content.postCompile.includes("--require-assistant"), "deployment can publish without an executable assistant provider")
assert(content.postCompile.includes("HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC"), "hosted native assistant mode is not explicit")

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
assert(content.shell.includes("Project objects"), "workspace does not expose real project objects")

for (const forbidden of [
  "ProductionApp",
  "runtime_application_missing",
  "visual_shell_only: true",
]) {
  assert(!publicSource.includes(forbidden), `obsolete public fallback leaked: ${forbidden}`)
}

console.log("workspace-source-verify: PASS")
