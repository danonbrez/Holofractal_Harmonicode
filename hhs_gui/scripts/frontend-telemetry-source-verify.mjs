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
    "inflight",
  ],
  "runtime_os/telemetry/useFrontendTelemetry.ts": [
    "useSyncExternalStore",
    "frameTelemetryMonitor.acquire()",
    "fetchLatencyTelemetry.instrument()",
  ],
  "runtime_os/workspace/FrontendTelemetryBadge.tsx": [
    "hhs-frontend-telemetry",
    "Frontend-only telemetry",
  ],
  "runtime_os/core/CanonicalRuntimeIDE.tsx": [
    "FrontendTelemetryBadge",
    "pointer-events-none",
  ],
}

for (const [relativePath, needles] of Object.entries(required)) {
  const absolutePath = path.join(root, relativePath)
  const source = fs.readFileSync(absolutePath, "utf8")
  for (const needle of needles) {
    if (!source.includes(needle)) throw new Error(`${relativePath} missing required source marker: ${needle}`)
  }
}

for (const relativePath of Object.keys(required)) {
  if (relativePath.includes("telemetry") || relativePath.includes("FrontendTelemetryBadge")) {
    const source = fs.readFileSync(path.join(root, relativePath), "utf8")
    if (source.includes("hhs_backend") || source.includes("pass217_genesis")) {
      throw new Error(`${relativePath} crosses the frontend/backend authority boundary`)
    }
  }
}

console.log("frontend telemetry source verification: PASS")
