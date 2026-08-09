import React, { useMemo, useState } from "react"
import { runtimeApplicationRegistry } from "../core/RuntimeApplicationRegistry"
import { useFetchLatencyTelemetry, useFrameTelemetry } from "../telemetry/useFrontendTelemetry"

type Json = Record<string, unknown>

interface RegistrySummary {
  total: number
  authoritative: number
  categories: Array<[string, number]>
  loadedAt: number
}

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback

function metric(value: number, digits = 0): string {
  return value > 0 && Number.isFinite(value) ? value.toFixed(digits) : "—"
}

function summarizeRegistry(body: Json): RegistrySummary {
  const services = Array.isArray(body.services) ? body.services : []
  const counts = new Map<string, number>()
  let authoritative = 0

  for (const raw of services) {
    const service = record(raw)
    const contract = record(service.runtime_contract)
    const category = text(service.service_type ?? contract.service_type, "runtime")
    counts.set(category, (counts.get(category) ?? 0) + 1)
    if (Boolean(service.requires_authority ?? contract.requires_authority ?? true)) authoritative += 1
  }

  return {
    total: services.length,
    authoritative,
    categories: [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])),
    loadedAt: Date.now(),
  }
}

export const RuntimeDiagnosticsDrawer: React.FC = () => {
  const frame = useFrameTelemetry()
  const network = useFetchLatencyTelemetry()
  const [open, setOpen] = useState(false)
  const [registry, setRegistry] = useState<RegistrySummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [applicationQuery, setApplicationQuery] = useState("")

  const runtimeEndpoints = useMemo(
    () => network.endpoints.filter((endpoint) => endpoint.url.includes("/api/")),
    [network.endpoints],
  )

  const applications = useMemo(
    () => runtimeApplicationRegistry.all().slice().sort((a, b) => a.title.localeCompare(b.title)),
    [],
  )

  const applicationAuthorityCounts = useMemo(() => {
    const counts = new Map<string, number>()
    for (const application of applications) {
      counts.set(application.authority, (counts.get(application.authority) ?? 0) + 1)
    }
    return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  }, [applications])

  const filteredApplications = useMemo(() => {
    const query = applicationQuery.trim().toLowerCase()
    if (!query) return applications
    return applications.filter((application) => [
      application.id,
      application.title,
      application.authority,
      application.description ?? "",
    ].join(" ").toLowerCase().includes(query))
  }, [applicationQuery, applications])

  const loadRegistry = async (): Promise<void> => {
    if (loading) return
    setLoading(true)
    setError(null)
    try {
      const response = await fetch("/api/runtime/services", { headers: { accept: "application/json" } })
      const body = record(await response.json())
      if (!response.ok) throw new Error(text(body.detail ?? body.error ?? body.status, response.statusText))
      setRegistry(summarizeRegistry(body))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setLoading(false)
    }
  }

  const toggle = (): void => {
    const next = !open
    setOpen(next)
    if (next && !registry && !loading) void loadRegistry()
  }

  const singletonCount = applications.filter((application) => application.singleton).length
  const mobileCount = applications.filter((application) => application.mobileSupported).length
  const experimentalCount = applications.filter((application) => application.experimental).length

  return (
    <aside data-testid="hhs-runtime-diagnostics" className="pointer-events-auto w-[min(440px,calc(100vw-1.5rem))] font-mono text-[10px]">
      <button
        type="button"
        onClick={toggle}
        className="ml-auto flex items-center gap-2 rounded-lg border border-neutral-800 bg-neutral-950/95 px-3 py-2 text-neutral-300 shadow-xl backdrop-blur"
        aria-expanded={open}
      >
        <span className="text-cyan-300">{metric(frame.effectiveFps)} FPS</span>
        <span>{metric(frame.estimatedRefreshHz)} Hz</span>
        <span>p95 {metric(frame.p95FrameMs, 1)} ms</span>
        <span>req {network.inFlight}</span>
        <span className="text-neutral-500">{open ? "close" : "diagnostics"}</span>
      </button>

      {open ? (
        <div className="mt-2 max-h-[70vh] overflow-auto rounded-xl border border-cyan-950 bg-neutral-950/98 p-3 text-neutral-300 shadow-2xl backdrop-blur-xl">
          <div className="flex items-center justify-between gap-3 border-b border-neutral-900 pb-2">
            <div>
              <div className="font-semibold text-cyan-200">Frontend + Registry diagnostics</div>
              <div className="mt-0.5 text-[9px] text-neutral-600">Read-only projection of existing runtime authority</div>
            </div>
            <button
              type="button"
              onClick={() => void loadRegistry()}
              disabled={loading}
              className="rounded-md border border-neutral-800 px-2 py-1 text-[9px] text-neutral-400 disabled:opacity-50"
            >
              {loading ? "refreshing" : "refresh registry"}
            </button>
          </div>

          <div className="grid grid-cols-3 gap-2 py-3">
            <div className="rounded-lg border border-neutral-900 bg-black/40 p-2">
              <div className="text-neutral-600">FPS / Hz</div>
              <div className="mt-1 text-cyan-300">{metric(frame.effectiveFps)} / {metric(frame.estimatedRefreshHz)}</div>
            </div>
            <div className="rounded-lg border border-neutral-900 bg-black/40 p-2">
              <div className="text-neutral-600">Frame p95/p99</div>
              <div className="mt-1">{metric(frame.p95FrameMs, 1)} / {metric(frame.p99FrameMs, 1)} ms</div>
            </div>
            <div className="rounded-lg border border-neutral-900 bg-black/40 p-2">
              <div className="text-neutral-600">Jank / drops</div>
              <div className="mt-1">{metric(frame.jankRate * 100, 1)}% / {frame.droppedFrames}</div>
            </div>
          </div>

          <section className="border-t border-neutral-900 pt-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-neutral-500">Service Registry</span>
              <span className="text-neutral-700">GET /api/runtime/services</span>
            </div>
            {error ? <div className="rounded-md border border-red-950 bg-red-950/20 p-2 text-red-300">{error}</div> : null}
            {registry ? (
              <>
                <div className="grid grid-cols-2 gap-2">
                  <div className="rounded-lg border border-neutral-900 p-2">services <span className="float-right text-cyan-300">{registry.total}</span></div>
                  <div className="rounded-lg border border-neutral-900 p-2">authority-gated <span className="float-right text-cyan-300">{registry.authoritative}</span></div>
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {registry.categories.map(([name, count]) => (
                    <span key={name} className="rounded border border-neutral-900 bg-black/30 px-1.5 py-1 text-neutral-500">{name} {count}</span>
                  ))}
                </div>
              </>
            ) : !loading && !error ? <div className="text-neutral-600">Registry inventory has not been loaded.</div> : null}
          </section>

          <section className="mt-3 border-t border-neutral-900 pt-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-neutral-500">Application Registry</span>
              <span className="text-neutral-700">frontend lazy modules</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5">
              <div className="rounded border border-neutral-900 p-2">apps <span className="float-right text-cyan-300">{applications.length}</span></div>
              <div className="rounded border border-neutral-900 p-2">mobile <span className="float-right">{mobileCount}</span></div>
              <div className="rounded border border-neutral-900 p-2">single <span className="float-right">{singletonCount}</span></div>
              <div className="rounded border border-neutral-900 p-2">exp <span className="float-right">{experimentalCount}</span></div>
            </div>
            <div className="mt-2 flex flex-wrap gap-1">
              {applicationAuthorityCounts.map(([authority, count]) => (
                <span key={authority} className="rounded border border-neutral-900 bg-black/30 px-1.5 py-1 text-neutral-500">{authority} {count}</span>
              ))}
            </div>
            <input
              value={applicationQuery}
              onChange={(event) => setApplicationQuery(event.target.value)}
              placeholder="filter applications"
              aria-label="Filter registered applications"
              className="mt-2 w-full rounded border border-neutral-900 bg-black/40 px-2 py-1.5 text-neutral-300 outline-none placeholder:text-neutral-700 focus:border-cyan-950"
            />
            <div className="mt-2 space-y-1">
              {filteredApplications.map((application) => (
                <div key={application.id} className="rounded border border-neutral-900 px-2 py-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-neutral-300">{application.title}</span>
                    <span className="text-neutral-600">{application.authority}</span>
                  </div>
                  <div className="mt-0.5 flex items-center gap-1.5 text-[9px] text-neutral-700">
                    <span className="truncate" title={application.id}>{application.id}</span>
                    {application.mobileSupported ? <span>mobile</span> : null}
                    {application.singleton ? <span>singleton</span> : null}
                    {application.experimental ? <span>experimental</span> : null}
                  </div>
                </div>
              ))}
              {filteredApplications.length === 0 ? <div className="text-neutral-700">No registered applications match the filter.</div> : null}
            </div>
          </section>

          <section className="mt-3 border-t border-neutral-900 pt-3">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-neutral-500">Observed API latency</span>
              <span className="text-neutral-700">{runtimeEndpoints.length} endpoints</span>
            </div>
            <div className="space-y-1">
              {runtimeEndpoints.slice(0, 8).map((endpoint) => (
                <div key={endpoint.url} className="grid grid-cols-[1fr_auto_auto] gap-2 rounded border border-neutral-900 px-2 py-1.5">
                  <span className="truncate text-neutral-500" title={endpoint.url}>{endpoint.url.replace(window.location.origin, "")}</span>
                  <span>p95 {metric(endpoint.p95Ms)} ms</span>
                  <span className={endpoint.lastStatus >= 500 || endpoint.lastStatus === 0 ? "text-red-300" : "text-neutral-600"}>{endpoint.lastStatus || "—"}</span>
                </div>
              ))}
              {runtimeEndpoints.length === 0 ? <div className="text-neutral-700">No API samples yet.</div> : null}
            </div>
          </section>
        </div>
      ) : null}
    </aside>
  )
}
