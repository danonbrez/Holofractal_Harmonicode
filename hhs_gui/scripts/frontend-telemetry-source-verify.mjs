import fs from "node:fs"
import path from "node:path"
import process from "node:process"

const root = process.cwd()
const required = {
  "runtime_os/telemetry/FrameTelemetry.ts": [
    "FRAME_PUBLISH_INTERVAL_MS = 500",
    "document.visibilityState !== \"hidden\"",
    "estimatedRefreshHz",
    "droppedFrames",
  ],
  "runtime_os/telemetry/FetchLatencyTelemetry.ts": [
    "__hhsFrontendFetchLatencyState_v1__",
    "input instanceof Request",
    "authorization",
    "response.clone()",
    "getSnapshot",
  ],
  "runtime_os/telemetry/useFrontendTelemetry.ts": [
    "useSyncExternalStore",
    "frameTelemetryMonitor.acquire()",
    "fetchLatencyTelemetry.getSnapshot",
  ],
  "runtime_os/workspace/RuntimeDiagnosticsDrawer.tsx": [
    "GET /api/runtime/services",
    "requires_authority",
    "Observed API latency",
    "Read-only projection of existing runtime authority",
    "runtimeApplicationRegistry.all()",
    "Application Registry",
    "frontend lazy modules",
  ],
  "runtime_os/core/CanonicalRuntimeIDE.tsx": [
    "RuntimeDiagnosticsDrawer",
    "transportState=\"ON_DEMAND\"",
  ],
}

for (const [relativePath, needles] of Object.entries(required)) {
  const source = fs.readFileSync(path.join(root, relativePath), "utf8")
  for (const needle of needles) {
    if (!source.includes(needle)) throw new Error(`${relativePath} missing required source marker: ${needle}`)
  }
}

for (const relativePath of Object.keys(required)) {
  const source = fs.readFileSync(path.join(root, relativePath), "utf8")
  if (source.includes("pass217_genesis") || source.includes("/api/runtime/services/dispatch")) {
    throw new Error(`${relativePath} crosses the Iteration 4 read-only authority boundary`)
  }
}

console.log("frontend telemetry + service/application registry diagnostics source verification: PASS")
