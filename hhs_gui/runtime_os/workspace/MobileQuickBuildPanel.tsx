import React, { useMemo, useRef, useState } from "react"

type Json = Record<string, any>

type BuildStage = {
  stage?: string
  status?: string
  [key: string]: unknown
}

const MAX_SOURCE_BYTES = 4 * 1024 * 1024
const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const short = (value: unknown): string => {
  const raw = text(value)
  return raw ? `${raw.slice(0, 10)}…${raw.slice(-6)}` : "—"
}

function sourceModality(sourceName: string): string {
  const name = sourceName.toLowerCase()
  if (name.endsWith(".hhs") || name.endsWith(".harmonicode")) return "HARMONICODE_SOURCE"
  if (name.endsWith(".json")) return "JSON"
  if (name.endsWith(".csv")) return "CSV"
  if (name.endsWith(".html") || name.endsWith(".htm")) return "TEXT"
  if (/\.(py|c|cc|cpp|h|hpp|js|mjs|ts|tsx|jsx|rs|go|java|sh|sql)$/i.test(name)) return "CODE"
  return "TEXT"
}

function mediaType(sourceName: string): string {
  const name = sourceName.toLowerCase()
  if (name.endsWith(".html") || name.endsWith(".htm")) return "text/html"
  if (name.endsWith(".css")) return "text/css"
  if (name.endsWith(".json")) return "application/json"
  if (name.endsWith(".js") || name.endsWith(".mjs")) return "text/javascript"
  if (name.endsWith(".ts") || name.endsWith(".tsx")) return "text/typescript"
  if (name.endsWith(".py")) return "text/x-python"
  return "text/plain"
}

function bytesToBase64(bytes: Uint8Array): string {
  const chunk = 0x8000
  let binary = ""
  for (let offset = 0; offset < bytes.length; offset += chunk) {
    binary += String.fromCharCode(...bytes.subarray(offset, Math.min(offset + chunk, bytes.length)))
  }
  return btoa(binary)
}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 90000): Promise<Json> {
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
  } catch (reason) {
    if (reason instanceof DOMException && reason.name === "AbortError") {
      throw new Error(`${url} timed out after ${Math.round(timeoutMs / 1000)} seconds`)
    }
    throw reason
  } finally {
    window.clearTimeout(timeout)
  }
}

export interface MobileQuickBuildPanelProps {
  projectId: string | null
  defaultProjectName: string
  onOpenWorkspace: () => void
}

export const MobileQuickBuildPanel: React.FC<MobileQuickBuildPanelProps> = ({
  projectId,
  defaultProjectName,
  onOpenWorkspace,
}) => {
  const fileInput = useRef<HTMLInputElement | null>(null)
  const [projectName, setProjectName] = useState(defaultProjectName || "HHS Mobile App")
  const [sourceName, setSourceName] = useState("index.html")
  const [sourceText, setSourceText] = useState("")
  const [target, setTarget] = useState("HHS_IR")
  const [steps, setSteps] = useState(8)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<Json>({})
  const [error, setError] = useState<string | null>(null)
  const [previewOpen, setPreviewOpen] = useState(false)

  const encoded = useMemo(() => new TextEncoder().encode(sourceText), [sourceText])
  const stages = Array.isArray(result.stages) ? result.stages.map((item: unknown) => record(item) as BuildStage) : []
  const canPreview = /\.html?$/i.test(sourceName) && Boolean(sourceText.trim())
  const lifecycleHash216 = result.lifecycle_hash216 ?? record(result.pass174_continuation).lifecycle_hash216
  const receiptHash72 = result.lifecycle_receipt_hash72
    ?? record(result.pass174_continuation).receipt_hash72
    ?? record(record(result.pass174_continuation).receipt).receipt_hash72

  const loadFile = async (file: File): Promise<void> => {
    if (file.size > MAX_SOURCE_BYTES) throw new Error("Quick Build accepts source files up to 4 MB. Use the multimodal ingress surface for larger files.")
    setSourceName(file.name || "main.hhs")
    setSourceText(await file.text())
    setResult({})
    setPreviewOpen(false)
    setError(null)
  }

  const buildAndRun = async (): Promise<void> => {
    if (!sourceText.trim()) {
      setError("Paste source code or load a source file first.")
      return
    }
    if (encoded.byteLength > MAX_SOURCE_BYTES) {
      setError("Quick Build source is larger than 4 MB. Use the multimodal ingress surface for larger inputs.")
      return
    }

    setBusy(true)
    setError(null)
    setResult({})
    setPreviewOpen(false)
    try {
      const response = await requestJson("/api/v1/pass174/sdlc/run", {
        method: "POST",
        body: JSON.stringify({
          project_id: projectId || null,
          project_name: projectName.trim() || "HHS Mobile App",
          source_name: sourceName.trim() || "main.hhs",
          source_modality: sourceModality(sourceName),
          source_payload: {
            source_b64: bytesToBase64(encoded),
            mime_type: mediaType(sourceName),
            source_size_bytes: encoded.byteLength,
          },
          requested_output: "VALIDATED_ARTIFACT",
          expression: null,
          target,
          steps,
          provenance: "RUNTIME_OS_MOBILE_QUICK_BUILD",
          authorization_scope: "P174_MOBILE_APPLICATION_DEVELOPMENT_PIPELINE",
          thread: 0,
        }),
      }, 120000)
      setResult(response)
      if (canPreview) setPreviewOpen(true)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section data-testid="mobile-quick-build-panel" className="mx-auto max-w-6xl px-3 pt-3 md:px-5 md:pt-5">
      <div className="rounded-3xl border border-cyan-800/60 bg-gradient-to-b from-cyan-950/50 to-neutral-950 p-4 shadow-2xl md:p-6">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-[10px] uppercase tracking-[0.24em] text-cyan-400">Quick Build</div>
            <h1 className="mt-1 text-xl font-semibold text-white md:text-2xl">Paste → build → run</h1>
            <p className="mt-2 max-w-3xl text-xs leading-5 text-neutral-400">The short path for this self-hosted VM. Paste an app or source file and run the governed Pass 174 pipeline without navigating internal pass controls. The backend remains the execution authority.</p>
          </div>
          <button type="button" onClick={onOpenWorkspace} className="runtime-button min-h-11 shrink-0 px-4 text-sm">Full workspace</button>
        </header>

        {error ? <div className="mt-4 rounded-xl border border-red-900 bg-red-950/30 p-3 text-sm text-red-200">{error}</div> : null}

        <div className="mt-4 grid gap-2 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_160px_96px]">
          <label className="text-[10px] text-neutral-500">
            <span className="mb-1 block">Project</span>
            <input value={projectName} onChange={(event) => setProjectName(event.target.value)} className="runtime-input min-h-11 w-full text-sm" />
          </label>
          <label className="text-[10px] text-neutral-500">
            <span className="mb-1 block">Source file</span>
            <input value={sourceName} onChange={(event) => setSourceName(event.target.value)} className="runtime-input min-h-11 w-full font-mono text-sm" />
          </label>
          <label className="text-[10px] text-neutral-500">
            <span className="mb-1 block">Target</span>
            <select value={target} onChange={(event) => setTarget(event.target.value)} className="runtime-input min-h-11 w-full text-sm">
              <option>HHS_IR</option>
              <option>C_KERNEL_PLAN</option>
              <option>C_SOURCE</option>
              <option>PYTHON_ADAPTER</option>
              <option>JSON_EXECUTION_GRAPH</option>
              <option>BYTECODE_OR_VM_PLAN</option>
            </select>
          </label>
          <label className="text-[10px] text-neutral-500">
            <span className="mb-1 block">Run steps</span>
            <select value={steps} onChange={(event) => setSteps(Number(event.target.value))} className="runtime-input min-h-11 w-full text-sm">
              {[1, 2, 4, 8, 16, 32].map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
          </label>
        </div>

        <div className="mt-3 rounded-2xl border border-neutral-800 bg-black/50 p-2">
          <textarea
            data-testid="mobile-quick-build-source"
            value={sourceText}
            onChange={(event) => { setSourceText(event.target.value); setResult({}); setPreviewOpen(false) }}
            placeholder="Paste HTML, HARMONICODE, JavaScript, Python, C/C++, JSON, or other source here…"
            spellCheck={false}
            className="min-h-[32vh] w-full resize-y rounded-xl border border-neutral-800 bg-neutral-950 p-3 font-mono text-sm leading-6 text-cyan-50 outline-none focus:border-cyan-600 md:min-h-[260px]"
          />
          <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap gap-2">
              <button type="button" onClick={() => fileInput.current?.click()} className="runtime-button min-h-11 px-4 text-sm">Load source file</button>
              <input
                ref={fileInput}
                type="file"
                className="hidden"
                onChange={(event) => {
                  const file = event.currentTarget.files?.[0]
                  event.currentTarget.value = ""
                  if (file) void loadFile(file).catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
                }}
              />
              {canPreview ? <button type="button" onClick={() => setPreviewOpen((value) => !value)} className="runtime-button min-h-11 px-4 text-sm">{previewOpen ? "Hide preview" : "Preview HTML"}</button> : null}
            </div>
            <div className="text-[10px] text-neutral-600">{encoded.byteLength.toLocaleString()} bytes · {projectId ? `workspace ${short(projectId)}` : "project auto-created"}</div>
          </div>
        </div>

        <button
          data-testid="mobile-quick-build-run"
          type="button"
          disabled={busy || !sourceText.trim()}
          onClick={() => void buildAndRun()}
          className="mt-3 min-h-14 w-full rounded-2xl border border-cyan-700 bg-cyan-900/70 px-5 text-base font-semibold text-white shadow-lg transition hover:bg-cyan-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? "Building and running on HHS…" : "Build & Run"}
        </button>

        {stages.length > 0 ? (
          <section className="mt-4 rounded-2xl border border-neutral-800 bg-black/40 p-3">
            <div className="text-xs font-semibold text-cyan-200">Pipeline</div>
            <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-7">
              {stages.map((stage, index) => (
                <div key={`${text(stage.stage)}:${index}`} className="rounded-xl border border-neutral-800 bg-neutral-950 p-2">
                  <div className="truncate text-[9px] text-neutral-500">{text(stage.stage, `stage ${index + 1}`)}</div>
                  <div className={`mt-1 truncate text-[10px] ${text(stage.status).toLowerCase().includes("fail") || text(stage.status).toLowerCase().includes("reject") ? "text-red-300" : "text-emerald-300"}`}>{text(stage.status, "complete")}</div>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {Object.keys(result).length > 0 ? (
          <section className="mt-4 rounded-2xl border border-emerald-900/60 bg-emerald-950/10 p-3">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="text-sm font-semibold text-emerald-300">{text(result.classification ?? result.status, "Build pipeline completed")}</div>
                <div className="mt-1 font-mono text-[9px] text-neutral-500">receipt {short(receiptHash72)} · Hash216 {short(lifecycleHash216)}</div>
              </div>
              <button type="button" onClick={onOpenWorkspace} className="runtime-button min-h-10 px-4 text-sm">Continue in workspace</button>
            </div>
            <details className="mt-3 rounded-xl border border-neutral-800 bg-black/40 p-2">
              <summary className="cursor-pointer text-[10px] text-neutral-500">Build evidence</summary>
              <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap break-all text-[9px] text-neutral-400">{JSON.stringify(result, null, 2)}</pre>
            </details>
          </section>
        ) : null}

        {previewOpen && canPreview ? (
          <section className="mt-4 overflow-hidden rounded-2xl border border-neutral-700 bg-white">
            <div className="flex items-center justify-between bg-neutral-900 px-3 py-2 text-[10px] text-neutral-400"><span>Sandboxed browser preview</span><span>local projection · no runtime authority</span></div>
            <iframe title="Quick Build HTML preview" sandbox="allow-scripts" srcDoc={sourceText} className="h-[62vh] min-h-[360px] w-full border-0 bg-white" />
          </section>
        ) : null}
      </div>
    </section>
  )
}

export default MobileQuickBuildPanel
