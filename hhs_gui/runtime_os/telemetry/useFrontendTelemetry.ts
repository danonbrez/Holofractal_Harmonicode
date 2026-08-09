import { useEffect, useSyncExternalStore } from "react"
import { fetchLatencyTelemetry } from "./FetchLatencyTelemetry"
import { frameTelemetryMonitor } from "./FrameTelemetry"

export function useFrameTelemetry() {
  useEffect(() => frameTelemetryMonitor.acquire(), [])
  return useSyncExternalStore(
    frameTelemetryMonitor.subscribe,
    frameTelemetryMonitor.getSnapshot,
    frameTelemetryMonitor.getServerSnapshot,
  )
}

export function useFetchLatencyTelemetry() {
  useEffect(() => {
    fetchLatencyTelemetry.instrument()
  }, [])

  return useSyncExternalStore(
    fetchLatencyTelemetry.subscribe,
    fetchLatencyTelemetry.getSnapshot,
    fetchLatencyTelemetry.getServerSnapshot,
  )
}
