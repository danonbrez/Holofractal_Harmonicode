import React from "react"
import { useFetchLatencyTelemetry, useFrameTelemetry } from "../telemetry/useFrontendTelemetry"

function metric(value: number, digits = 0): string {
  return value > 0 && Number.isFinite(value) ? value.toFixed(digits) : "—"
}

export const FrontendTelemetryBadge: React.FC = () => {
  const frame = useFrameTelemetry()
  const network = useFetchLatencyTelemetry()
  const slowest = network.endpoints[0]

  return (
    <div
      data-testid="hhs-frontend-telemetry"
      className="rounded-lg border border-neutral-800 bg-neutral-900 px-2 py-1 font-mono text-[9px] text-neutral-400"
      title="Frontend-only telemetry; does not alter runtime authority or Pass 217 state"
    >
      <span className="text-cyan-300">{metric(frame.effectiveFps)} FPS</span>
      <span className="px-1 text-neutral-700">·</span>
      <span>{metric(frame.estimatedRefreshHz)} Hz</span>
      <span className="px-1 text-neutral-700">·</span>
      <span>frame p95 {metric(frame.p95FrameMs, 1)} ms</span>
      <span className="px-1 text-neutral-700">·</span>
      <span>req {network.inFlight}</span>
      {slowest ? (
        <>
          <span className="px-1 text-neutral-700">·</span>
          <span>api p95 {metric(slowest.p95Ms)} ms</span>
        </>
      ) : null}
    </div>
  )
}
