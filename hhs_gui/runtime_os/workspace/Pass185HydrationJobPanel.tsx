import React, { useRef, useState } from "react"

type Json = Record<string, any>
type Busy = "CREATING" | "PREPARING_RUN" | "RUNNING" | "CANCELLING" | "RECOVERING" | null

const record = (value: unknown): Json =>
  value && typeof value === "object" ? value as Json : {}

async function requestJson(url: string, init?: RequestInit, timeoutMs = 120000): Promise<Json> {
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
    const body = record(await response.json())
    if (!response.ok) throw new Error(String(body.detail ?? body.status ?? response.statusText))
    return body
  } finally {
    window.clearTimeout(timeout)
  }
}

async function authorityTick(): Promise<Json> {
  const response = await requestJson("/api/runtime/authority/tick", { method: "POST" })
  const execution = record(response.authority_execution)
  if (!record(execution.runtime).state_hash72) throw new Error("AUTHORITY_RUNTIME_STATE_MISSING")
  if (!record(execution.receipt).receipt_hash72) throw new Error("AUTHORITY_RECEIPT_MISSING")
  if (record(execution.authority_audit).ok !== true) throw new Error("AUTHORITY_AUDIT_REJECTED")
  return execution
}

export const Pass185HydrationJobPanel: React.FC = () => {
  const [job, setJob] = useState<Json | null>(null)
  const [busy, setBusy] = useState<Busy>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastAction, setLastAction] = useState("NONE")
  const preparedCancelAuthority = useRef<Json | null>(null)
  const runGeneration = useRef(0)

  const jobId = typeof job?.job_id === "string" ? job.job_id : ""
  const stage = typeof job?.stage === "string" ? job.stage : "NONE"
  const terminal = ["COMPLETED", "FAILED", "CANCELLED", "BLOCKED"].includes(stage)

  const createJob = async (mode: "CREATING" | "RECOVERING" = "CREATING"): Promise<void> => {
    if (busy) return
    setBusy(mode)
    setError(null)
    try {
      const execution = await authorityTick()
      const created = await requestJson("/v1/hydration/jobs", {
        method: "POST",
        body: JSON.stringify({
          commit: "HEAD",
          authority_execution: execution,
        }),
      })
      preparedCancelAuthority.current = null
      setJob(created)
      setLastAction(mode === "RECOVERING" ? "RECOVERY_JOB_QUEUED" : "JOB_QUEUED")
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(null)
    }
  }

  const runJob = async (): Promise<void> => {
    if (busy || !jobId || terminal) return
    setBusy("PREPARING_RUN")
    setError(null)
    const generation = ++runGeneration.current
    try {
      const runAuthority = await authorityTick()
      preparedCancelAuthority.current = await authorityTick()
      if (generation !== runGeneration.current) return
      setBusy("RUNNING")
      setLastAction("RUN_REQUEST_IN_FLIGHT")
      void requestJson(`/v1/hydration/jobs/${encodeURIComponent(jobId)}/resume`, {
        method: "POST",
        body: JSON.stringify({ authority_execution: runAuthority }),
      }).then((result) => {
        if (generation === runGeneration.current) {
          setJob(result)
          setLastAction(result.stage === "CANCELLED" ? "RUN_CANCELLED" : "RUN_FINISHED")
        }
      }).catch((reason) => {
        if (generation === runGeneration.current) {
          setError(reason instanceof Error ? reason.message : String(reason))
          setLastAction("RUN_FAILED")
        }
      }).finally(() => {
        if (generation === runGeneration.current) setBusy(null)
      })
    } catch (reason) {
      setBusy(null)
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  const cancelJob = async (): Promise<void> => {
    if (!jobId || terminal) return
    setBusy("CANCELLING")
    setError(null)
    try {
      const execution = preparedCancelAuthority.current ?? await authorityTick()
      preparedCancelAuthority.current = null
      const cancelled = await requestJson(
        `/v1/hydration/jobs/${encodeURIComponent(jobId)}/cancel`,
        {
          method: "POST",
          body: JSON.stringify({ authority_execution: execution }),
        },
      )
      runGeneration.current += 1
      setJob(cancelled)
      setLastAction("JOB_CANCELLED")
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(null)
    }
  }

  const refresh = async (): Promise<void> => {
    if (!jobId || busy) return
    setError(null)
    try {
      const current = await requestJson(`/v1/hydration/jobs/${encodeURIComponent(jobId)}`)
      setJob(current)
      setLastAction("JOB_REFRESHED")
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  return (
    <section data-testid="pass185-hydration-job-panel" className="rounded-2xl border border-neutral-800 bg-neutral-900/50 p-4">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-cyan-200">Governed lifecycle job</h2>
          <p className="mt-1 text-[10px] leading-5 text-neutral-500">
            Pass 191 durable job lifecycle using explicit singleton VM81 authority receipts.
          </p>
        </div>
        <span data-testid="pass185-hydration-job-stage" className="rounded-full border border-neutral-700 bg-black px-3 py-1 font-mono text-[10px] text-cyan-300">
          {busy ?? stage}
        </span>
      </header>

      {error ? (
        <div data-testid="pass185-hydration-job-error" className="mt-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">
          {error}
        </div>
      ) : null}

      <div className="mt-4 grid gap-2 sm:grid-cols-5">
        <button data-testid="pass185-hydration-create" type="button" className="runtime-button min-h-10 text-xs" disabled={Boolean(busy)} onClick={() => void createJob()}>
          Create job
        </button>
        <button data-testid="pass185-hydration-run" type="button" className="runtime-button min-h-10 text-xs" disabled={Boolean(busy) || !jobId || terminal} onClick={() => void runJob()}>
          Run / resume
        </button>
        <button data-testid="pass185-hydration-cancel" type="button" className="runtime-button min-h-10 text-xs" disabled={!jobId || terminal || (Boolean(busy) && busy !== "RUNNING")} onClick={() => void cancelJob()}>
          Cancel
        </button>
        <button data-testid="pass185-hydration-refresh" type="button" className="runtime-button min-h-10 text-xs" disabled={Boolean(busy) || !jobId} onClick={() => void refresh()}>
          Refresh
        </button>
        <button data-testid="pass185-hydration-recover" type="button" className="runtime-button min-h-10 text-xs" disabled={Boolean(busy) || !terminal} onClick={() => void createJob("RECOVERING")}>
          Recover / new job
        </button>
      </div>

      <div className="mt-4 grid gap-2 text-[10px] sm:grid-cols-2">
        <div className="rounded-xl border border-neutral-800 bg-black/50 p-3">
          <div className="text-neutral-600">job</div>
          <div data-testid="pass185-hydration-job-id" className="mt-1 break-all font-mono text-neutral-300">{jobId || "none"}</div>
        </div>
        <div className="rounded-xl border border-neutral-800 bg-black/50 p-3">
          <div className="text-neutral-600">last action</div>
          <div data-testid="pass185-hydration-last-action" className="mt-1 font-mono text-neutral-300">{lastAction}</div>
        </div>
      </div>

      <details className="mt-3 rounded-xl border border-neutral-800 bg-black/40 p-3">
        <summary className="cursor-pointer text-[10px] text-neutral-500">Lifecycle evidence</summary>
        <pre data-testid="pass185-hydration-job-json" className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap break-all font-mono text-[10px] text-neutral-400">
          {job ? JSON.stringify(job, null, 2) : "No durable job created."}
        </pre>
      </details>

      <footer className="mt-3 text-[10px] text-neutral-600">
        frontend_job_authority=false · authority_source=/api/runtime/authority/tick · cancellation=PASS191_DURABLE
      </footer>
    </section>
  )
}

export default Pass185HydrationJobPanel
