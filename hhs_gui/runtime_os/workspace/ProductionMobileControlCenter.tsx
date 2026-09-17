import React, { useEffect, useMemo, useRef, useState } from "react"
import OpenSourceAcquisitionPanel from "./OpenSourceAcquisitionPanel"

type Json = Record<string, any>
type Surface = "program" | "workspace" | "authority"

const MAX_INGRESS_BYTES = 24 * 1024 * 1024
const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const short = (value: unknown): string => {
  const raw = text(value)
  return raw ? `${raw.slice(0, 10)}…${raw.slice(-6)}` : "—"
}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 30000): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: {
        accept: "application/json",
        ...(init?.body ? { "content-type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    })
    const raw = await response.text()
    let body: Json = {}
    try {
      body = raw ? record(JSON.parse(raw)) : {}
    } catch {
      body = { detail: raw || response.statusText }
    }
    if (!response.ok) {
      const detail = record(body.detail)
      throw new Error(text(detail.classification ?? detail.detail ?? body.detail ?? body.error ?? body.status, `${response.status} ${response.statusText}`))
    }
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

function modalityFor(file: File): string {
  const name = file.name.toLowerCase()
  const mime = file.type.toLowerCase()
  if (name.endsWith(".hhs") || name.endsWith(".harmonicode")) return "HARMONICODE_SOURCE"
  if (name.endsWith(".json")) return "JSON"
  if (name.endsWith(".yaml") || name.endsWith(".yml")) return "YAML"
  if (name.endsWith(".csv")) return "CSV"
  if (name.endsWith(".pdf") || mime === "application/pdf") return "PDF"
  if (mime.startsWith("image/")) return "IMAGE"
  if (mime.startsWith("audio/")) return "AUDIO"
  if (mime.startsWith("video/")) return "VIDEO"
  if (/\.(py|c|cc|cpp|h|hpp|js|mjs|ts|tsx|jsx|rs|go|java|sh|sql)$/i.test(name)) return "CODE"
  if (mime.startsWith("text/") || /\.(txt|md|html|xml|css)$/i.test(name)) return "TEXT"
  return "BINARY"
}

function isTextReadable(file: File): boolean {
  return ["TEXT", "HARMONICODE_SOURCE", "CODE", "JSON", "YAML", "CSV"].includes(modalityFor(file))
}

function bytesToBase64(bytes: Uint8Array): string {
  const chunk = 0x8000
  let binary = ""
  for (let offset = 0; offset < bytes.length; offset += chunk) {
    binary += String.fromCharCode(...bytes.subarray(offset, Math.min(offset + chunk, bytes.length)))
  }
  return btoa(binary)
}

function findOperationKey(result: Json): string | null {
  const continuation = record(result.pass174_continuation)
  const receipt = record(continuation.receipt)
  const vector = record(continuation.vector)
  for (const candidate of [continuation.operation_key, receipt.operation_key, vector.operation_key]) {
    if (typeof candidate === "string" && /^[0-9a-f]{64}$/i.test(candidate)) return candidate
  }
  return null
}

export interface ProductionMobileControlCenterProps {
  projectId: string | null
  projectName: string
  onNavigate: (surface: Surface) => void
}

export const ProductionMobileControlCenter: React.FC<ProductionMobileControlCenterProps> = ({
  projectId,
  projectName,
  onNavigate,
}) => {
  const fileInput = useRef<HTMLInputElement | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [previewText, setPreviewText] = useState("")
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [health, setHealth] = useState<Json>({})
  const [vectorStatus, setVectorStatus] = useState<Json>({})
  const [lastIngress, setLastIngress] = useState<Json>({})
  const [vectorQuery, setVectorQuery] = useState<Json>({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selected = files[selectedIndex] ?? null
  const modality = selected ? modalityFor(selected) : "—"
  const persistentStore = record(vectorStatus.persistent_vector_store)
  const runtimeReady = text(health.status).toLowerCase() === "healthy"
  const vectorReady = Boolean(vectorStatus.classification) && Boolean(vectorStatus.persistent_vector_store)
  const operationKey = useMemo(() => findOperationKey(lastIngress), [lastIngress])

  const refresh = async (): Promise<void> => {
    const [healthResult, vectorResult] = await Promise.all([
      requestJson("/health", undefined, 8000),
      requestJson("/api/v1/pass174/status", undefined, 12000),
    ])
    setHealth(healthResult)
    setVectorStatus(vectorResult)
    setError(null)
  }

  useEffect(() => {
    void refresh().catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
    const interval = window.setInterval(() => void refresh().catch(() => undefined), 15000)
    return () => window.clearInterval(interval)
  }, [])

  useEffect(() => {
    let active = true
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setPreviewText("")
    if (!selected) return () => { active = false }

    if (isTextReadable(selected)) {
      selected.text()
        .then((value) => { if (active) setPreviewText(value.slice(0, 250000)) })
        .catch((reason) => { if (active) setError(String(reason)) })
    } else if (selected.type.startsWith("image/") || selected.type.startsWith("audio/") || selected.type.startsWith("video/") || selected.type === "application/pdf") {
      setPreviewUrl(URL.createObjectURL(selected))
    }
    return () => { active = false }
  }, [selected])

  useEffect(() => () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl)
  }, [previewUrl])

  const chooseFiles = (incoming: FileList | null): void => {
    const next = incoming ? Array.from(incoming) : []
    setFiles(next)
    setSelectedIndex(0)
    setLastIngress({})
    setVectorQuery({})
    setError(null)
  }

  const ingest = async (): Promise<void> => {
    if (!selected) return
    if (selected.size > MAX_INGRESS_BYTES) {
      setError(`File is ${(selected.size / 1024 / 1024).toFixed(1)} MB; this mobile ingress surface is bounded to 24 MB per file.`)
      return
    }
    setBusy(true)
    setError(null)
    try {
      const bytes = new Uint8Array(await selected.arrayBuffer())
      const result = await requestJson("/api/v1/pass174/sdlc/run", {
        method: "POST",
        body: JSON.stringify({
          project_id: projectId || null,
          project_name: projectName || "HHS Mobile Ingress",
          source_name: selected.name,
          source_modality: modality,
          source_payload: {
            source_b64: bytesToBase64(bytes),
            mime_type: selected.type || "application/octet-stream",
            source_size_bytes: selected.size,
          },
          requested_output: "VALIDATED_ARTIFACT",
          expression: null,
          target: "HHS_IR",
          steps: 8,
          provenance: "RUNTIME_OS_MOBILE_MULTIMODAL_INGRESS",
          authorization_scope: "P174_MULTIMODAL_SDLC_PIPELINE",
          thread: 0,
        }),
      }, 90000)
      setLastIngress(result)
      setVectorQuery({})
      await refresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  const queryPersistedVector = async (): Promise<void> => {
    if (!operationKey) return
    setBusy(true)
    setError(null)
    try {
      setVectorQuery(await requestJson("/api/v1/pass174/hash216/query", {
        method: "POST",
        body: JSON.stringify({ operation_key: operationKey }),
      }, 30000))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  return (
    <main data-testid="production-mobile-control-center" className="mx-auto max-w-6xl space-y-3 p-3 pb-24 md:p-5">
      <section className="rounded-3xl border border-cyan-950 bg-gradient-to-b from-cyan-950/30 to-neutral-950 p-4 shadow-2xl md:p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="text-[10px] uppercase tracking-[0.24em] text-cyan-500">Production control</div>
            <h1 className="mt-1 text-xl font-semibold text-white md:text-2xl">HHS application server</h1>
            <p className="mt-2 max-w-2xl text-xs leading-5 text-neutral-400">One mobile surface for runtime health, real file reading, governed multimodal ingress, persistent Hash216 vector hydration, open-source acquisition/replay jobs, and click-through application control.</p>
          </div>
          <button type="button" onClick={() => void refresh().catch((reason) => setError(String(reason)))} className="runtime-button min-h-11 px-4 text-sm">Refresh server</button>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-4">
          <StatusCard label="Runtime" value={runtimeReady ? "online" : "check"} ready={runtimeReady} />
          <StatusCard label="Vector store" value={vectorReady ? "persistent" : "check"} ready={vectorReady} />
          <StatusCard label="Project" value={projectId ? short(projectId) : "auto-create"} ready={Boolean(projectId)} />
          <StatusCard label="Ingress" value={lastIngress.classification ? "hydrated" : "ready"} ready={Boolean(lastIngress.classification)} />
        </div>
      </section>

      {error ? <section className="rounded-2xl border border-red-900 bg-red-950/30 p-3 text-sm text-red-200">{error}</section> : null}

      <section className="grid gap-2 sm:grid-cols-3">
        <LaunchCard title="Visual Program" detail="Registry canvas and executable application objects" onClick={() => onNavigate("program")} />
        <LaunchCard title="Workspace" detail="Source, compiler, emulator, assistant, jobs and receipts" onClick={() => onNavigate("workspace")} />
        <LaunchCard title="Authority" detail="Approvals and governed production operations" onClick={() => onNavigate("authority")} />
      </section>

      <OpenSourceAcquisitionPanel />

      <section className="rounded-3xl border border-neutral-800 bg-neutral-900/60 p-3 md:p-5">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-cyan-200">Files → multimodal ingress → vector store</h2>
            <p className="mt-1 text-[11px] leading-5 text-neutral-500">Files are read locally for preview, then transmitted as exact base64 source bytes through the Pass 174 SDLC route into the persistent encrypted Hash216 vector-store continuation.</p>
          </div>
          <button type="button" onClick={() => fileInput.current?.click()} className="runtime-button min-h-11 px-4 text-sm">Choose files</button>
          <input ref={fileInput} type="file" multiple className="hidden" onChange={(event) => { chooseFiles(event.currentTarget.files); event.currentTarget.value = "" }} />
        </header>

        {files.length === 0 ? (
          <button type="button" onClick={() => fileInput.current?.click()} className="mt-4 min-h-40 w-full rounded-2xl border border-dashed border-neutral-700 bg-black/30 p-6 text-center text-sm text-neutral-400">
            Tap to select text, source, JSON, CSV, PDF, image, audio, video, or binary files
          </button>
        ) : (
          <div className="mt-4 grid gap-3 lg:grid-cols-[260px_minmax(0,1fr)]">
            <aside className="space-y-2">
              {files.map((file, index) => (
                <button key={`${file.name}:${file.size}:${index}`} type="button" onClick={() => setSelectedIndex(index)} className={`w-full rounded-xl border p-3 text-left ${index === selectedIndex ? "border-cyan-700 bg-cyan-950/30" : "border-neutral-800 bg-black/30"}`}>
                  <div className="truncate text-xs font-medium text-white">{file.name}</div>
                  <div className="mt-1 text-[10px] text-neutral-500">{modalityFor(file)} · {(file.size / 1024).toFixed(1)} KB</div>
                </button>
              ))}
            </aside>

            <div className="min-w-0 space-y-3">
              <div className="rounded-2xl border border-neutral-800 bg-black/40 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-white">{selected?.name}</div>
                    <div className="mt-1 text-[10px] text-neutral-500">{modality} · {selected?.type || "application/octet-stream"} · {selected ? `${selected.size} bytes` : ""}</div>
                  </div>
                  <button type="button" disabled={busy || !selected} onClick={() => void ingest()} className="runtime-button min-h-10 px-4 text-sm">{busy ? "Working…" : "Hydrate vector store"}</button>
                </div>

                <div className="mt-3 min-h-48 overflow-hidden rounded-xl border border-neutral-800 bg-neutral-950">
                  {previewText ? <pre className="max-h-[52vh] overflow-auto whitespace-pre-wrap break-words p-3 text-xs leading-5 text-neutral-300">{previewText}</pre> : null}
                  {previewUrl && selected?.type.startsWith("image/") ? <img src={previewUrl} alt={selected.name} className="max-h-[52vh] w-full object-contain" /> : null}
                  {previewUrl && selected?.type.startsWith("audio/") ? <div className="grid min-h-48 place-items-center p-4"><audio src={previewUrl} controls className="w-full" /></div> : null}
                  {previewUrl && selected?.type.startsWith("video/") ? <video src={previewUrl} controls className="max-h-[52vh] w-full bg-black" /> : null}
                  {previewUrl && selected?.type === "application/pdf" ? <iframe src={previewUrl} title={selected.name} className="h-[52vh] w-full border-0" /> : null}
                  {!previewText && !previewUrl ? <div className="grid min-h-48 place-items-center p-4 text-xs text-neutral-600">Binary preview is intentionally withheld; exact bytes can still be ingressed.</div> : null}
                </div>
              </div>

              {lastIngress.classification ? (
                <section className="rounded-2xl border border-emerald-900/60 bg-emerald-950/10 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <div className="text-xs font-semibold text-emerald-300">{text(lastIngress.classification)}</div>
                      <div className="mt-1 font-mono text-[9px] text-neutral-500">source {short(lastIngress.source_identity_sha256)} · Hash216 {short(lastIngress.lifecycle_hash216)}</div>
                    </div>
                    {operationKey ? <button type="button" onClick={() => void queryPersistedVector()} disabled={busy} className="runtime-button min-h-9 px-3 text-xs">Read persisted vector</button> : null}
                  </div>
                  {Array.isArray(lastIngress.stages) ? (
                    <div className="mt-3 grid grid-cols-2 gap-1 sm:grid-cols-4 lg:grid-cols-7">
                      {lastIngress.stages.map((stage: Json, index: number) => <div key={`${text(stage.stage)}:${index}`} className="rounded-lg bg-black/30 p-2"><div className="text-[9px] text-neutral-500">{text(stage.stage)}</div><div className="mt-1 text-[9px] text-emerald-300">{text(stage.status)}</div></div>)}
                    </div>
                  ) : null}
                </section>
              ) : null}

              {Object.keys(vectorQuery).length > 0 ? (
                <details open className="rounded-2xl border border-cyan-950 bg-black/40 p-3">
                  <summary className="cursor-pointer text-xs font-medium text-cyan-300">Persisted vector readback</summary>
                  <pre className="mt-3 max-h-72 overflow-auto whitespace-pre-wrap break-all text-[10px] text-neutral-400">{JSON.stringify(vectorQuery, null, 2)}</pre>
                </details>
              ) : null}
            </div>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-neutral-800 bg-neutral-900/40 p-3">
        <div className="flex items-center justify-between gap-3"><h2 className="text-xs font-semibold text-cyan-200">Persistent vector-store status</h2><span className="text-[9px] text-neutral-500">Pass 174</span></div>
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {Object.entries(persistentStore).slice(0, 8).map(([key, value]) => <div key={key} className="rounded-lg bg-black/40 p-2"><div className="truncate text-[9px] text-neutral-600">{key}</div><div className="mt-1 truncate font-mono text-[10px] text-neutral-300" title={String(value)}>{String(value)}</div></div>)}
          {Object.keys(persistentStore).length === 0 ? <div className="col-span-2 text-xs text-neutral-600">Vector-store status has not loaded.</div> : null}
        </div>
      </section>
    </main>
  )
}

const StatusCard: React.FC<{ label: string; value: string; ready: boolean }> = ({ label, value, ready }) => (
  <div className="rounded-2xl border border-neutral-800 bg-black/40 p-3">
    <div className="flex items-center gap-2 text-[10px] text-neutral-500"><span className={`h-2 w-2 rounded-full ${ready ? "bg-emerald-400" : "bg-amber-400"}`} />{label}</div>
    <div className="mt-2 truncate text-sm font-medium text-white">{value}</div>
  </div>
)

const LaunchCard: React.FC<{ title: string; detail: string; onClick: () => void }> = ({ title, detail, onClick }) => (
  <button type="button" onClick={onClick} className="min-h-24 rounded-2xl border border-neutral-800 bg-neutral-900/60 p-4 text-left transition hover:border-cyan-800 hover:bg-cyan-950/20">
    <div className="text-sm font-semibold text-white">{title}</div>
    <div className="mt-2 text-[11px] leading-4 text-neutral-500">{detail}</div>
  </button>
)

export default ProductionMobileControlCenter
