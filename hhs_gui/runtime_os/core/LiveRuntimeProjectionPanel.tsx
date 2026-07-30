import React, { useEffect, useState } from "react"
import type { RuntimeOS } from "./RuntimeOS"
import type { RuntimeChannelHealth, RuntimeSocketEvent } from "./RuntimeSocketManager"

export interface LiveRuntimeProjectionPanelProps {
  runtimeOS: RuntimeOS
}

type Json = Record<string, any>

const CHANNEL_LABELS: Record<string, string> = {
  runtime: "Runtime",
  replay: "Replay",
  graph: "Graph",
  transport: "Transport",
}

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
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

async function requestAuthorityStatus(): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 8000)
  try {
    const response = await fetch("/api/runtime/authority/status", {
      headers: { accept: "application/json" },
      signal: controller.signal,
    })
    const body = record(await response.json())
    if (!response.ok) throw new Error(String(body.error ?? body.status ?? response.statusText))
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

export const LiveRuntimeProjectionPanel: React.FC<LiveRuntimeProjectionPanelProps> = ({ runtimeOS }) => {
  const [channelHealth, setChannelHealth] = useState<RuntimeChannelHealth[]>(runtimeOS.socketManager.getChannelHealth())
  const [events, setEvents] = useState<Record<string, RuntimeSocketEvent | undefined>>(latestEvents(runtimeOS))
  const [authority, setAuthority] = useState<Json>({})
  const [connectionError, setConnectionError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    const refreshProjection = () => {
      if (!mounted) return
      setChannelHealth(runtimeOS.socketManager.getChannelHealth())
      setEvents(latestEvents(runtimeOS))
    }
    const refreshAuthority = async () => {
      try {
        const status = await requestAuthorityStatus()
        if (mounted) {
          setAuthority(status)
          setConnectionError(null)
        }
      } catch (error) {
        if (mounted) setConnectionError(error instanceof Error ? error.message : String(error))
      }
    }

    runtimeOS.initialize()
      .then(() => {
        refreshProjection()
        void refreshAuthority()
      })
      .catch((error: unknown) => {
        if (mounted) setConnectionError(error instanceof Error ? error.message : String(error))
      })

    const projectionInterval = window.setInterval(refreshProjection, 1500)
    const authorityInterval = window.setInterval(() => void refreshAuthority(), 5000)
    return () => {
      mounted = false
      window.clearInterval(projectionInterval)
      window.clearInterval(authorityInterval)
      runtimeOS.shutdown()
    }
  }, [runtimeOS])

  const workflow = record(authority.live_workflow)
  const runtime = record(authority.runtime)
  const authorityOnline = Boolean(authority.ok)

  return (
    <section data-testid="live-runtime-projection-panel" className="rounded-2xl border border-cyan-900/70 bg-black/80 p-3 font-mono shadow-2xl">
      <header className="mb-3 flex flex-wrap items-center justify-between gap-3 px-1">
        <div>
          <h2 className="text-sm font-semibold text-cyan-200">Live kernel authority and projection</h2>
          <p className="text-[9px] text-neutral-600">Backend authority is verified by HTTP; WebSockets are on-demand projection channels.</p>
        </div>
        <button type="button" onClick={() => void requestAuthorityStatus().then(setAuthority).catch((error) => setConnectionError(String(error)))} className={`rounded-full border px-3 py-1 text-[9px] ${authorityOnline ? "border-emerald-800 text-emerald-300" : "border-red-900 text-red-300"}`}>
          {authorityOnline ? "RUNTIME AUTHORITY ONLINE" : "RUNTIME AUTHORITY OFFLINE"}
        </button>
      </header>

      <div className="mb-3 grid gap-2 rounded-xl border border-neutral-800 bg-neutral-950/80 p-3 text-[10px] sm:grid-cols-4">
        <Field label="runtime step" value={String(runtime.step ?? "—")} />
        <Field label="workflow ticks" value={String(workflow.tick_count ?? "—")} />
        <Field label="background task" value={workflow.background_task_active ? "active" : "inactive"} />
        <Field label="state" value={shortHash(typeof runtime.state_hash72 === "string" ? runtime.state_hash72 : undefined)} />
      </div>

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
                {event ? Object.keys(event.payload ?? {}).join(", ") || "empty payload" : authorityOnline ? "authority online; projection packet pending" : "no live packet"}
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
