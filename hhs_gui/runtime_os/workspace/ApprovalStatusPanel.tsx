import React, { useEffect, useState } from "react"

type Json = Record<string, any>

const STATUS_PATH = "/api/runtime/pass218/authority/approval/status"
const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}

async function requestStatus(): Promise<Json> {
  const response = await fetch(STATUS_PATH, { headers: { accept: "application/json" } })
  const body = record(await response.json())
  if (!response.ok) throw new Error(String(body.detail ?? response.statusText))
  return body
}

function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-black/30 p-2">
      <div className="text-[9px] uppercase tracking-wide text-neutral-500">{label}</div>
      <div className="mt-1 font-mono text-[11px] text-neutral-200">{value}</div>
    </div>
  )
}

export const ApprovalStatusPanel: React.FC = () => {
  const [status, setStatus] = useState<Json>({})
  const [error, setError] = useState<string | null>(null)

  const refresh = async (): Promise<void> => {
    try {
      setStatus(await requestStatus())
      setError(null)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    }
  }

  useEffect(() => {
    void refresh()
    const interval = window.setInterval(() => void refresh(), 15000)
    return () => window.clearInterval(interval)
  }, [])

  const roles = record(status.role_counts)
  return (
    <section data-testid="pass218-i14-approval-status" className="mx-auto mt-3 max-w-[1800px] rounded-xl border border-violet-900 bg-violet-950/20 p-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-xs font-semibold text-violet-200">Pass 218 I14 multi-party approval</div>
          <div className="mt-1 text-[10px] text-neutral-400">Read-only projection of the configured approval policy and operator-role coverage. An empty registry remains fail-closed.</div>
        </div>
        <button type="button" onClick={() => void refresh()} className="rounded-lg border border-violet-800 px-3 py-1 text-[10px] text-violet-200">Refresh</button>
      </div>
      {error ? <div className="mt-2 rounded-lg border border-red-900 bg-red-950/30 p-2 text-[10px] text-red-200">{error}</div> : null}
      <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
        <Metric label="Registered" value={status.configured_operator_count ?? 0} />
        <Metric label="Threshold" value={status.approval_threshold ?? 2} />
        <Metric label="Preparers" value={roles.PREPARER ?? 0} />
        <Metric label="Approvers" value={roles.APPROVER ?? 0} />
        <Metric label="Executors" value={roles.EXECUTOR ?? 0} />
      </div>
      <div className={`mt-2 rounded-lg border p-2 text-[10px] ${status.release_possible_from_registry ? "border-emerald-900 text-emerald-300" : "border-amber-900 text-amber-300"}`}>
        {status.release_possible_from_registry ? "Configured role coverage satisfies the I14 registry minimum." : "I14 remains fail-closed until configured role coverage satisfies the policy."}
      </div>
    </section>
  )
}

export default ApprovalStatusPanel
