import React, { useEffect, useState } from "react"
import type { RuntimeOS } from "./RuntimeOS"
import type { RuntimeChannelHealth, RuntimeSocketEvent } from "./RuntimeSocketManager"

export interface LiveRuntimeProjectionPanelProps {
  runtimeOS: RuntimeOS
}

const CHANNEL_LABELS: Record<string, string> = {
  runtime: "Runtime",
  replay: "Replay",
  graph: "Graph",
  transport: "Transport",
}

const shortHash = (value?: string): string => value ? `${value.slice(0, 10)}…${value.slice(-6)}` : "—"

const statusClass = (status: RuntimeChannelHealth["status"]): string => {
  if (status === "LIVE_KERNEL_CONNECTED") return "text-emerald-300"
  if (status === "STALE_LIVE_KERNEL_STATE") return "text-amber-300"
  return "text-red-300"
}

const latestEvents = (runtimeOS: RuntimeOS): Record<string, RuntimeSocketEvent | undefined> => ({
  runtime: runtimeOS.socketManager.state.lastRuntimeEvent,
  replay: runtimeOS.socketManager.state.lastReplayEvent,
  graph: runtimeOS.socketManager.state.lastGraphEvent,
  transport: runtimeOS.socketManager.state.lastTransportEvent,
})

export const LiveRuntimeProjectionPanel: React.FC<LiveRuntimeProjectionPanelProps> = ({ runtimeOS }) => {
  const [channelHealth, setChannelHealth] = useState<RuntimeChannelHealth[]>(runtimeOS.socketManager.getChannelHealth())
  const [events, setEvents] = useState<Record<string, RuntimeSocketEvent | undefined>>(latestEvents(runtimeOS))
  const [connectionError, setConnectionError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const refresh = () => {
      if (!mounted) return
      setChannelHealth(runtimeOS.socketManager.getChannelHealth())
      setEvents(latestEvents(runtimeOS))
    }

    runtimeOS.initialize()
      .then(refresh)
      .catch((error: unknown) => {
        if (mounted) setConnectionError(error instanceof Error ? error.message : String(error))
      })

    const interval = window.setInterval(refresh, 1500)
    return () => {
      mounted = false
      window.clearInterval(interval)
      runtimeOS.shutdown()
    }
  }, [runtimeOS])

  return (
    <section data-testid="live-runtime-projection-panel" className="rounded-2xl border border-cyan-900/70 bg-black/80 p-3 font-mono shadow-2xl">
      <header className="mb-3 flex items-center justify-between gap-3 px-1">
        <div>
          <h2 className="text-sm font-semibold text-cyan-200">Live kernel projection</h2>
          <p className="text-[9px] text-neutral-600">Connected only while this tab is active · refresh 1500 ms</p>
        </div>
        <span className="text-[9px] uppercase tracking-widest text-neutral-600">projection only</span>
      </header>

      {connectionError ? <p className="mb-3 rounded-lg border border-red-900 bg-red-950/30 p-2 text-[10px] text-red-300">{connectionError}</p> : null}

      <div className="grid gap-2 md:grid-cols-2">
        {channelHealth.map((health) => {
          const event = events[health.channel]
          return (
            <article key={health.channel} data-testid={`live-channel-${health.channel}`} className="rounded-xl border border-neutral-800 bg-neutral-950/80 p-3">
              <div className="flex items-center justify-between gap-2">
                <strong className="text-xs text-white">{CHANNEL_LABELS[health.channel] ?? health.channel}</strong>
                <span className={`text-[9px] ${statusClass(health.status)}`}>{health.status}</span>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-[10px]">
                <Field label="events" value={String(health.totalEvents)} />
                <Field label="sequence" value={String(health.lastSequenceId ?? "—")} />
                <Field label="tick" value={String(health.lastKernelTick ?? "—")} />
                <Field label="age" value={`${String(health.lastPacketAgeMs ?? "—")} ms`} />
                <Field label="receipt" value={shortHash(health.lastReceiptHash72)} />
                <Field label="state" value={shortHash(health.lastRuntimeStateHash72)} />
              </div>
              <div className="mt-3 truncate text-[9px] text-neutral-600" title={event ? Object.keys(event.payload ?? {}).join(", ") : "no packet"}>
                {event ? Object.keys(event.payload ?? {}).join(", ") || "empty payload" : "no live packet"}
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}

const Field: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="min-w-0 rounded-lg bg-black/40 p-2">
    <div className="text-neutral-600">{label}</div>
    <div className="mt-1 truncate text-neutral-300" title={value}>{value}</div>
  </div>
)

export default LiveRuntimeProjectionPanel
