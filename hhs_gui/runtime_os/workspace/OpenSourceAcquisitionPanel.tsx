import React, { useEffect, useMemo, useState } from "react"

type Json = Record<string, any>
const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback
const short = (value: unknown): string => {
  const raw = text(value)
  return raw ? `${raw.slice(0, 10)}…${raw.slice(-6)}` : "—"
}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 90000): Promise<Json> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
      headers: { accept: "application/json", ...(init?.body ? { "content-type": "application/json" } : {}), ...(init?.headers ?? {}) },
    })
    const raw = await response.text()
    const body = raw ? record(JSON.parse(raw)) : {}
    if (!response.ok) {
      const detail = record(body.detail)
      throw new Error(text(detail.classification ?? body.detail ?? body.error, `${response.status} ${response.statusText}`))
    }
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

const emptyForm = {
  provider: "GITHUB",
  repoId: "huggingface/sentence-transformers",
  revision: "",
  licenseId: "apache-2.0",
  sourceUrl: "https://github.com/huggingface/sentence-transformers",
  artifactPath: "README.md",
  expectedSha256: "",
  expectedByteLength: "",
  mediaType: "TEXT",
  sourceLanguage: "en",
}

const sourcePayload = (form: typeof emptyForm): Json => ({
  repository: {
    provider: form.provider,
    repo_id: form.repoId,
    revision: form.revision.trim(),
    license_id: form.licenseId.trim(),
    repo_kind: "CODE",
    source_url: form.sourceUrl.trim(),
    modalities: [form.mediaType],
  },
  artifact_path: form.artifactPath.trim(),
  expected_sha256: form.expectedSha256.trim().toLowerCase(),
  expected_byte_length: Number(form.expectedByteLength),
  declared_media_type: form.mediaType,
  source_language: form.sourceLanguage.trim() || null,
})

export const OpenSourceAcquisitionPanel: React.FC = () => {
  const [form, setForm] = useState(emptyForm)
  const [status, setStatus] = useState<Json>({})
  const [history, setHistory] = useState<Json[]>([])
  const [selected, setSelected] = useState<Json>({})
  const [projectorId, setProjectorId] = useState("SERVER_APPROVED_EXECUTION_V1")
  const [executionProfileId, setExecutionProfileId] = useState("MULTILINGUAL_MPNET_TEXT_V1")
  const [pivotText, setPivotText] = useState("Semantic similarity candidate")
  const [evidenceText, setEvidenceText] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const adapters = Array.isArray(status.projectors) ? status.projectors : []
  const executionProfiles = Array.isArray(status.execution_profiles) ? status.execution_profiles : []
  const serverExecution = record(status.server_execution)
  const completed = useMemo(() => history.filter((job) => text(job.status) === "COMPLETED").length, [history])

  const refresh = async (): Promise<void> => {
    const [service, jobs] = await Promise.all([
      requestJson("/api/v1/pass174/acquisition/status", undefined, 15000),
      requestJson("/api/v1/pass174/acquisition/jobs?limit=20", undefined, 15000),
    ])
    setStatus(service)
    setHistory(Array.isArray(jobs.jobs) ? jobs.jobs : [])
    setError(null)
  }

  useEffect(() => {
    void refresh().catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [])

  const setField = (key: keyof typeof emptyForm, value: string): void => setForm((current) => ({ ...current, [key]: value }))

  const parseProjectionEvidence = (): Json[] => {
    if (projectorId !== "EXTERNAL_EVIDENCE_V1") return []
    if (!evidenceText.trim()) throw new Error("EXTERNAL_EVIDENCE_V1 requires projector evidence JSON.")
    const parsed = JSON.parse(evidenceText)
    const rows = Array.isArray(parsed) ? parsed : [parsed]
    if (rows.length === 0 || rows.some((row) => !row || typeof row !== "object")) throw new Error("Projection evidence must be a JSON object or non-empty array of objects.")
    return rows.map((row) => record(row))
  }

  const submit = async (): Promise<void> => {
    setBusy(true)
    setError(null)
    try {
      const source = sourcePayload(form)
      const serverSide = projectorId === "SERVER_APPROVED_EXECUTION_V1"
      const result = serverSide
        ? await requestJson("/api/v1/pass174/acquisition/jobs/execute", {
            method: "POST",
            body: JSON.stringify({
              source,
              execution: {
                profile_id: executionProfileId,
                pivot_text: pivotText.trim(),
                pivot_language: "en",
                semantic_labels: [],
                translation_chain: [form.sourceLanguage.trim() || "unknown", "en"],
              },
            }),
          }, 600000)
        : await requestJson("/api/v1/pass174/acquisition/jobs", {
            method: "POST",
            body: JSON.stringify({
              projector_id: projectorId,
              source,
              projection_evidence: parseProjectionEvidence(),
            }),
          })
      setSelected(result)
      await refresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  const inspect = async (jobId: string): Promise<void> => {
    setBusy(true)
    try {
      setSelected(await requestJson(`/api/v1/pass174/acquisition/jobs/${jobId}`, undefined, 15000))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  const replay = async (jobId: string): Promise<void> => {
    setBusy(true)
    try {
      setSelected(await requestJson(`/api/v1/pass174/acquisition/jobs/${jobId}/replay`, { method: "POST" }, 90000))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  const selectedJob = record(selected.job ?? selected)
  const selectedResult = record(selectedJob.result)
  const selectedReport = record(selectedResult.report)
  const selectedIngress = record(selectedReport.ingress_record)
  const selectedReceipt = record(selectedResult.receipt)
  const selectedExecution = record(selected.execution)

  return (
    <section data-testid="open-source-acquisition-panel" className="rounded-3xl border border-indigo-950 bg-indigo-950/10 p-3 md:p-5">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-[10px] uppercase tracking-[0.22em] text-indigo-400">Pass 219 external ingress</div>
          <h2 className="mt-1 text-base font-semibold text-indigo-100">Open-source acquisition + replay jobs</h2>
          <p className="mt-1 max-w-3xl text-[11px] leading-5 text-neutral-500">Fetch immutable GitHub/Hugging Face revisions, verify exact bytes before inference, run approved models in an isolated subprocess, persist sealed evidence, and replay without network or model execution.</p>
        </div>
        <button type="button" onClick={() => void refresh()} className="runtime-button min-h-10 px-3 text-xs">Refresh jobs</button>
      </header>

      {error ? <div className="mt-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">{error}</div> : null}

      <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-6">
        <Mini label="Service" value={text(status.classification, "not loaded")} />
        <Mini label="Server projector" value={serverExecution.runtime_ready ? "ready" : "unavailable"} />
        <Mini label="Recent jobs" value={String(history.length)} />
        <Mini label="Completed" value={String(completed)} />
        <Mini label="Job adapters" value={String(adapters.length)} />
        <Mini label="Execution profiles" value={String(executionProfiles.length)} />
      </div>

      <details className="mt-3 rounded-2xl border border-neutral-800 bg-black/30 p-3" open>
        <summary className="cursor-pointer text-xs font-medium text-indigo-200">New verified source job</summary>
        <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          <Field label="Execution path"><select value={projectorId} onChange={(event) => setProjectorId(event.target.value)} className="runtime-input w-full"><option value="SERVER_APPROVED_EXECUTION_V1">Approved server projector</option><option value="SOURCE_ONLY_V1">Verify source only</option><option value="EXTERNAL_EVIDENCE_V1">Manual sealed evidence</option></select></Field>
          <Field label="Provider"><select value={form.provider} onChange={(event) => setField("provider", event.target.value)} className="runtime-input w-full"><option>GITHUB</option><option>HUGGING_FACE</option></select></Field>
          <Field label="Repository"><input value={form.repoId} onChange={(event) => setField("repoId", event.target.value)} className="runtime-input w-full" /></Field>
          <Field label="Immutable 40-hex revision"><input value={form.revision} onChange={(event) => setField("revision", event.target.value)} placeholder="commit/model revision" className="runtime-input w-full font-mono" /></Field>
          <Field label="Artifact path"><input value={form.artifactPath} onChange={(event) => setField("artifactPath", event.target.value)} className="runtime-input w-full" /></Field>
          <Field label="Expected SHA-256"><input value={form.expectedSha256} onChange={(event) => setField("expectedSha256", event.target.value)} className="runtime-input w-full font-mono" /></Field>
          <Field label="Exact bytes"><input inputMode="numeric" value={form.expectedByteLength} onChange={(event) => setField("expectedByteLength", event.target.value)} className="runtime-input w-full" /></Field>
          <Field label="License"><input value={form.licenseId} onChange={(event) => setField("licenseId", event.target.value)} className="runtime-input w-full" /></Field>
          <Field label="Media type"><select value={form.mediaType} onChange={(event) => setField("mediaType", event.target.value)} className="runtime-input w-full"><option>TEXT</option><option>MARKDOWN</option><option>JSON</option><option>CSV</option><option>IMAGE</option><option>AUDIO</option><option>VIDEO</option><option>BINARY_OBJECT</option></select></Field>
          <Field label="Source URL"><input value={form.sourceUrl} onChange={(event) => setField("sourceUrl", event.target.value)} className="runtime-input w-full" /></Field>
          <Field label="Language"><input value={form.sourceLanguage} onChange={(event) => setField("sourceLanguage", event.target.value)} className="runtime-input w-full" /></Field>
          {projectorId === "SERVER_APPROVED_EXECUTION_V1" ? <Field label="Approved profile"><select value={executionProfileId} onChange={(event) => setExecutionProfileId(event.target.value)} className="runtime-input w-full">{executionProfiles.filter((profile: Json) => profile.production_approved).map((profile: Json) => <option key={text(profile.profile_id)} value={text(profile.profile_id)}>{text(profile.profile_id)}</option>)}</select></Field> : null}
        </div>
        {projectorId === "SERVER_APPROVED_EXECUTION_V1" ? (
          <Field label="Semantic pivot text"><textarea value={pivotText} onChange={(event) => setPivotText(event.target.value)} rows={3} className="runtime-input w-full" /></Field>
        ) : null}
        {projectorId === "EXTERNAL_EVIDENCE_V1" ? (
          <label className="mt-3 block text-[10px] text-neutral-500">
            <span className="mb-1 block">Approved projector evidence JSON</span>
            <textarea value={evidenceText} onChange={(event) => setEvidenceText(event.target.value)} rows={8} placeholder="Paste the object emitted by hhs_pass219_approved_projector_execution_v1" className="runtime-input w-full font-mono text-[10px]" />
          </label>
        ) : null}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <button type="button" disabled={busy} onClick={() => void submit()} className="runtime-button min-h-10 px-4 text-xs">{busy ? "Working…" : projectorId === "SERVER_APPROVED_EXECUTION_V1" ? "Acquire + run approved model" : projectorId === "EXTERNAL_EVIDENCE_V1" ? "Acquire + sealed projection" : "Acquire + verify"}</button>
          <span className="text-[10px] text-neutral-600">Approved inference runs in an isolated ML subprocess outside canonical VM81 authority. Source bytes are verified first; persistence reuses the same captured bytes and offline replay never reruns the model.</span>
        </div>
      </details>

      <section className="mt-3 rounded-2xl border border-neutral-800 bg-black/20 p-3">
        <div className="text-xs font-medium text-neutral-300">Approved execution profiles</div>
        <div className="mt-2 grid gap-2 sm:grid-cols-2">
          {executionProfiles.map((profile: Json) => <div key={text(profile.profile_id)} className="rounded-xl border border-neutral-800 bg-neutral-950/50 p-2"><div className="text-[10px] font-medium text-indigo-200">{text(profile.profile_id)}</div><div className={`mt-1 text-[9px] ${profile.production_approved ? "text-emerald-400" : "text-amber-400"}`}>{profile.production_approved ? "production approved" : "blocked / calibration only"}</div>{profile.blocked_reason ? <div className="mt-1 text-[9px] leading-4 text-neutral-600">{text(profile.blocked_reason)}</div> : null}</div>)}
          {executionProfiles.length === 0 ? <div className="text-xs text-neutral-600">Execution profiles have not loaded.</div> : null}
        </div>
      </section>

      <div className="mt-3 grid gap-3 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="rounded-2xl border border-neutral-800 bg-black/30 p-3">
          <div className="text-xs font-medium text-neutral-300">Job history</div>
          <div className="mt-2 max-h-80 space-y-2 overflow-auto">
            {history.map((job) => (
              <div key={text(job.job_id)} className="rounded-xl border border-neutral-800 bg-neutral-950/60 p-2">
                <div className="flex items-center justify-between gap-2"><span className="font-mono text-[10px] text-neutral-300">{short(job.job_id)}</span><span className={`text-[10px] ${text(job.status) === "COMPLETED" ? "text-emerald-400" : text(job.status) === "FAILED" ? "text-red-400" : "text-amber-400"}`}>{text(job.status)}</span></div>
                <div className="mt-1 text-[9px] text-neutral-600">{text(job.projector_id)} · receipt {short(job.receipt_hash72)}</div>
                <div className="mt-2 flex gap-2"><button type="button" onClick={() => void inspect(text(job.job_id))} className="runtime-button min-h-8 px-2 text-[10px]">Inspect</button>{text(job.status) === "COMPLETED" ? <button type="button" onClick={() => void replay(text(job.job_id))} className="runtime-button min-h-8 px-2 text-[10px]">Replay offline</button> : null}</div>
              </div>
            ))}
            {history.length === 0 ? <div className="py-6 text-center text-xs text-neutral-600">No acquisition jobs yet.</div> : null}
          </div>
        </section>
        <section className="rounded-2xl border border-neutral-800 bg-black/30 p-3">
          <div className="text-xs font-medium text-neutral-300">Selected job / replay receipt</div>
          {Object.keys(selected).length ? (
            <div className="mt-2 space-y-2">
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                <Mini label="Status" value={text(selected.status ?? selectedJob.status, "result")} />
                <Mini label="Job" value={short(selectedJob.job_id)} />
                <Mini label="Classification" value={text(selectedIngress.classification ?? record(selected.replay).ingress_record?.classification, "—")} />
                <Mini label="Receipt" value={short(selectedReceipt.job_receipt_hash72 ?? selectedJob.receipt_hash72)} />
                <Mini label="Profile" value={text(selectedExecution.profile_id, "—")} />
                <Mini label="Replay closure" value={short(selectedReport.replay_closure_hash72 ?? record(selected.replay).replay_closure_hash72)} />
              </div>
              <details className="rounded-xl border border-neutral-800 bg-neutral-950/50 p-2">
                <summary className="cursor-pointer text-[10px] text-neutral-400">Exact receipt / diagnostic JSON</summary>
                <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap break-all text-[10px] leading-4 text-neutral-600">{JSON.stringify(selected, null, 2)}</pre>
              </details>
            </div>
          ) : <div className="mt-3 text-xs text-neutral-600">Select a job to inspect provenance, receipt identity, candidate classification, or replay closure.</div>}
        </section>
      </div>
    </section>
  )
}

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => <label className="mt-3 block text-[10px] text-neutral-500"><span className="mb-1 block">{label}</span>{children}</label>
const Mini: React.FC<{ label: string; value: string }> = ({ label, value }) => <div className="rounded-xl border border-neutral-800 bg-black/30 p-2"><div className="text-[9px] text-neutral-600">{label}</div><div className="mt-1 truncate text-[10px] text-neutral-300" title={value}>{value}</div></div>

export default OpenSourceAcquisitionPanel