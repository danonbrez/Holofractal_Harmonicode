import React, { FormEvent, useEffect, useState } from "react"

type JsonObject = Record<string, unknown>

type Surface = {
  id: string
  label: string
  url: string
}

const SURFACES: Surface[] = [
  { id: "observer", label: "Canonical observer", url: "/api/runtime/canonical-observer/status" },
  { id: "fabric", label: "Capability fabric", url: "/api/runtime/capability/status" },
  { id: "contracts", label: "Capability contracts", url: "/api/runtime/capability/contracts" },
  { id: "providers", label: "Provider registry", url: "/api/runtime/capability/providers" },
  { id: "documents", label: "Document perception", url: "/api/runtime/document/perception/status" },
  { id: "word2vec", label: "Word2Vec memory", url: "/v1/modalities/language/models/word2vec/status" },
]

async function fetchJson(url: string, init?: RequestInit): Promise<JsonObject> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 30000)
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
    const body = await response.json() as JsonObject
    if (!response.ok) throw new Error(JSON.stringify(body))
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

export const LiveBackendCapabilityPanel: React.FC = () => {
  const [selected, setSelected] = useState("fabric")
  const [result, setResult] = useState<JsonObject | null>(null)
  const [capabilityClass, setCapabilityClass] = useState("TEXT_GENERATION")
  const [busy, setBusy] = useState(false)

  async function load(surfaceId: string): Promise<void> {
    const surface = SURFACES.find((item) => item.id === surfaceId)
    if (!surface) return
    setSelected(surfaceId)
    setBusy(true)
    try {
      setResult(await fetchJson(surface.url))
    } catch (error: unknown) {
      setResult({ ok: false, error: error instanceof Error ? error.message : String(error), surface: surfaceId })
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => { void load("fabric") }, [])

  async function resolve(event: FormEvent): Promise<void> {
    event.preventDefault()
    setBusy(true)
    try {
      setResult(await fetchJson("/api/runtime/capability/resolve", {
        method: "POST",
        body: JSON.stringify({
          capability_class: capabilityClass,
          project_id: "project:visual-runtime-os",
          constraints: {},
        }),
      }))
      setSelected("resolve")
    } catch (error: unknown) {
      setResult({ ok: false, error: error instanceof Error ? error.message : String(error), capability_class: capabilityClass })
    } finally {
      setBusy(false)
    }
  }

  return (
    <section data-testid="live-backend-capability-panel" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 className="text-xs font-semibold text-emerald-200">Live Capability and Provider Fabric</h3>
          <p className="text-[10px] text-emerald-300">Every displayed result is fetched from the canonical backend.</p>
        </div>
        <span className="text-[10px] text-neutral-500">{busy ? "executing…" : selected}</span>
      </div>

      <div className="mt-2 flex flex-wrap gap-1">
        {SURFACES.map((surface) => (
          <button key={surface.id} className="runtime-button px-2 py-1 text-[10px]" type="button" onClick={() => void load(surface.id)} disabled={busy}>
            {surface.label}
          </button>
        ))}
      </div>

      <form className="mt-2 flex flex-wrap gap-1" onSubmit={resolve}>
        <input
          className="min-w-52 flex-1 rounded border border-neutral-700 bg-black px-2 py-1 text-[10px] text-white"
          value={capabilityClass}
          onChange={(event) => setCapabilityClass(event.target.value)}
          aria-label="Capability class"
        />
        <button className="runtime-button px-2 py-1 text-[10px]" type="submit" disabled={busy}>Resolve provider</button>
      </form>

      <pre className="mt-2 max-h-80 overflow-auto rounded-lg border border-neutral-800 bg-black/60 p-2 text-[9px] leading-relaxed text-neutral-300">
        {result ? JSON.stringify(result, null, 2) : "No backend result."}
      </pre>
    </section>
  )
}
