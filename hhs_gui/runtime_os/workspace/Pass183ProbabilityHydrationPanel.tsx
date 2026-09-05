import React, { useEffect, useMemo, useState } from "react"

type Json = Record<string, any>
const rec = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const txt = (value: unknown, fallback = "—"): string => typeof value === "string" && value ? value : fallback

async function requestJson(path: string, init?: RequestInit): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 30000)
  try {
    const response = await fetch(path, {
      ...init,
      signal: controller.signal,
      headers: { accept: "application/json", ...(init?.body ? { "content-type": "application/json" } : {}), ...(init?.headers ?? {}) },
    })
    const body = rec(await response.json())
    if (!response.ok) {
      const detail = rec(body.detail)
      throw new Error(txt(detail.detail ?? detail.classification ?? body.status, response.statusText))
    }
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

const defaults: Record<string, Json> = {
  bayes: { p_a: "1/4", p_b: "1/2", p_b_given_a: "4/5", p_a_given_b: "2/5" },
  conditional_probability: { p_a_and_b: "1/4", p_b: "1/2", p_a_given_b: "1/2" },
  independent_intersection: { p_a: "1/2", p_b: "1/3", p_a_and_b: "1/6" },
  total_probability: { p_h: "1/4", p_e_given_h: "3/4", p_e_given_not_h: "1/4", p_e: "3/8" },
  expectation: { outcomes: [0, 2], probabilities: ["1/4", "3/4"], expected: "3/2" },
  markov_chain: { matrix: [["1/2", "1/2"], ["1/4", "3/4"]] },
  binomial: { n: 8, p: "1/3" },
  weighted_choice: { weights: ["1/4", "1/4", "1/2"] },
}

export const Pass183ProbabilityHydrationPanel: React.FC = () => {
  const [status, setStatus] = useState<Json | null>(null)
  const [adapters, setAdapters] = useState<Json[]>([])
  const [adapter, setAdapter] = useState("bayes")
  const [equation, setEquation] = useState("")
  const [manifest, setManifest] = useState("{}")
  const [seedClass, setSeedClass] = useState("DETERMINISTIC_ENUMERATION")
  const [seed, setSeed] = useState("")
  const [result, setResult] = useState<Json | null>(null)
  const [busy, setBusy] = useState<string | null>("boot")
  const [error, setError] = useState<string | null>(null)

  const equations = useMemo(() => Object.fromEntries(adapters.map(item => [String(item.adapter), String(item.canonical_equation)])), [adapters])

  const loadAdapter = (name: string): void => {
    setAdapter(name)
    setEquation(equations[name] ?? "")
    setManifest(JSON.stringify(defaults[name] ?? {}, null, 2))
    setSeedClass(["weighted_choice", "monte_carlo_control"].includes(name) ? "CONTENT_ADDRESSED_SEED" : "DETERMINISTIC_ENUMERATION")
  }

  useEffect(() => {
    let active = true
    Promise.all([
      requestJson("/api/v1/probability/status"),
      requestJson("/api/v1/probability/adapters"),
    ]).then(([nextStatus, nextAdapters]) => {
      if (!active) return
      const items = Array.isArray(nextAdapters.adapters) ? nextAdapters.adapters.map(rec) : []
      setStatus(nextStatus)
      setAdapters(items)
      const bayes = items.find(item => item.adapter === "bayes")
      setEquation(txt(bayes?.canonical_equation))
      setManifest(JSON.stringify(defaults.bayes, null, 2))
    }).catch(reason => {
      if (active) setError(reason instanceof Error ? reason.message : String(reason))
    }).finally(() => {
      if (active) setBusy(null)
    })
    return () => { active = false }
  }, [])

  const body = (): Json => {
    let parsed: Json
    try { parsed = JSON.parse(manifest) as Json }
    catch { throw new Error("Manifest must be valid JSON using exact integer or rational strings.") }
    return { adapter, equation, manifest: parsed, seed_class: seedClass, seed: seed || null, modulus: 1259713, timeout_ms: 30000 }
  }

  const run = async (name: string, endpoint: string): Promise<void> => {
    if (busy) return
    setBusy(name)
    setError(null)
    try {
      setResult(await requestJson(endpoint, { method: "POST", body: JSON.stringify(body()) }))
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(null)
    }
  }

  const evaluation = rec(rec(result?.result).evaluation ?? result?.evaluation)
  const receipt = rec(rec(result?.result).receipt ?? result?.receipt)
  const archive = rec(receipt.hash216_archive ?? result?.hash216_archive)
  const membranes = Array.isArray(evaluation.membranes) ? evaluation.membranes.map(rec) : []

  return <section data-testid="pass183-probability-hydration-panel" className="grid gap-3 xl:grid-cols-[430px_minmax(0,1fr)]">
    <aside className="rounded-2xl border border-neutral-800 bg-neutral-900/60 p-4">
      <h2 className="text-sm font-semibold text-cyan-200">Exact Probability Hydration</h2>
      <p className="mt-1 text-[10px] leading-4 text-neutral-500">Exact rational equation validation, membrane witnesses, Factorial-72 lanes, typed zero bypass, singleton VM81 admission, canonical Hash72 receipt, then archival Hash216.</p>
      <div className="mt-4 space-y-3">
        <label className="block text-[10px] text-neutral-500">Adapter<select data-testid="pass183-adapter" value={adapter} onChange={event => loadAdapter(event.target.value)} className="mt-1 min-h-10 w-full rounded-lg border border-neutral-700 bg-black px-3 text-sm">{adapters.map(item => <option key={txt(item.adapter)} value={txt(item.adapter)}>{txt(item.adapter).replaceAll("_", " ")}</option>)}</select></label>
        <label className="block text-[10px] text-neutral-500">Exact equation<textarea data-testid="pass183-equation" value={equation} onChange={event => setEquation(event.target.value)} rows={4} className="mt-1 w-full rounded-lg border border-neutral-700 bg-black p-3 font-mono text-xs"/></label>
        <label className="block text-[10px] text-neutral-500">Exact manifest<textarea data-testid="pass183-manifest" value={manifest} onChange={event => setManifest(event.target.value)} rows={10} className="mt-1 w-full rounded-lg border border-neutral-700 bg-black p-3 font-mono text-xs"/></label>
        <label className="block text-[10px] text-neutral-500">Seed class<select value={seedClass} onChange={event => setSeedClass(event.target.value)} className="mt-1 min-h-10 w-full rounded-lg border border-neutral-700 bg-black px-3 text-sm">{["DETERMINISTIC_ENUMERATION","CONTENT_ADDRESSED_SEED","EXPLICIT_USER_SEED","HASH72_CLOCK_SEED","EXTERNAL_ENTROPY_EVIDENCE"].map(item => <option key={item}>{item}</option>)}</select></label>
        <input value={seed} onChange={event => setSeed(event.target.value)} placeholder="Optional exact seed evidence" className="min-h-10 w-full rounded-lg border border-neutral-700 bg-black px-3 text-xs"/>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <button data-testid="pass183-parse" disabled={Boolean(busy)} onClick={() => void run("parse","/api/v1/probability/parse")} className="runtime-button min-h-10 text-xs">Inspect membranes</button>
        <button data-testid="pass183-validate" disabled={Boolean(busy)} onClick={() => void run("validate","/api/v1/probability/validate")} className="runtime-button min-h-10 text-xs">Validate</button>
        <button data-testid="pass183-hydrate" disabled={Boolean(busy)} onClick={() => void run("hydrate","/api/v1/probability/hydrate")} className="runtime-button min-h-10 text-xs">Preview hydration</button>
        <button data-testid="pass183-execute" disabled={Boolean(busy)} onClick={() => void run("execute","/api/v1/probability/execute")} className="runtime-button min-h-10 text-xs">Execute through VM81</button>
        <button data-testid="pass183-replay" disabled={Boolean(busy)} onClick={() => void run("replay","/api/v1/probability/replay")} className="runtime-button col-span-2 min-h-10 text-xs">Replay receipts</button>
      </div>
      {error ? <p className="mt-3 rounded-lg border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">{error}</p> : null}
      {busy ? <p className="mt-3 text-[10px] text-cyan-300">{busy}…</p> : null}
    </aside>
    <div className="space-y-3">
      <section className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4">
        <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
          <Metric label="runtime" value={txt(status?.classification)} />
          <Metric label="domain" value={String(evaluation.probability_domain_valid ?? "—")} />
          <Metric label="equation truth" value={String(evaluation.source_equation_true ?? "—")} />
          <Metric label="closure" value={txt(evaluation.closure_exact)} />
          <Metric label="outer residue" value={String(rec(evaluation.outer_modulus).residue ?? "—")} />
          <Metric label="Hash72 receipt" value={txt(receipt.receipt_hash72)} />
          <Metric label="Hash216 archive" value={txt(archive.archive_root_sha256)} />
          <Metric label="archive authority" value={String(archive.mutation_authority ?? false)} />
        </div>
      </section>
      <section className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4">
        <h3 className="text-xs font-semibold text-cyan-200">Nested membrane witnesses</h3>
        <div className="mt-3 space-y-2">
          {membranes.length ? membranes.map((item, index) => <div key={txt(item.membrane_id,String(index))} className="rounded-lg border border-neutral-800 bg-black/50 p-3 text-[10px]"><div className="text-cyan-300">depth {String(item.depth_n)} · {String(item.boundary_residue_n)} MOD {String(item.boundary_modulus_n_plus_1)}</div><div className="mt-1 break-all font-mono text-neutral-500">{txt(item.content_hash)}</div></div>) : <p className="text-xs text-neutral-500">Run a preview or execution to inspect membranes.</p>}
        </div>
      </section>
      <section className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4 text-[10px] text-neutral-400">
        <div>Legacy precommit “Hash216” fields remain compatibility witnesses only and are prohibited from mutation authority.</div>
        <div className="mt-2">Canonical order: exact evaluation → inherited VM81 commit → Hash72 receipt → Hash216 archive.</div>
      </section>
    </div>
  </section>
}

const Metric: React.FC<{label:string;value:string}> = ({label,value}) => <div className="min-w-0 rounded-xl border border-neutral-800 bg-black/50 p-3"><div className="text-[9px] uppercase tracking-wide text-neutral-600">{label}</div><div className="mt-1 break-all font-mono text-[10px] text-neutral-200">{value}</div></div>
