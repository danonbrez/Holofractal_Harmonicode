import React, { useEffect, useMemo, useState } from "react"

type Json = Record<string, any>

const STATUS_PATH = "/api/runtime/pass218/authority/status"
const ALERTS_PATH = "/api/runtime/pass218/authority/alerts"
const PREPARE_PATH = "/api/runtime/pass218/authority/actions/prepare"

const ACTIONS = [
  ["PROBE_CLUSTER", "Prepare cluster probe"],
  ["PREPARE_CREDENTIAL_ROTATION", "Prepare credential rotation"],
  ["PREPARE_MEMBER_REPLACEMENT", "Prepare member replacement"],
  ["REQUEST_SNAPSHOT_REHEARSAL", "Prepare snapshot rehearsal"],
  ["EXPORT_EVIDENCE", "Prepare evidence export"],
] as const

const record = (value: unknown): Json => value && typeof value === "object" ? value as Json : {}
const text = (value: unknown, fallback = ""): string => typeof value === "string" ? value : fallback

async function requestJson(url: string, init?: RequestInit): Promise<Json> {
  const response = await fetch(url, {
    ...init,
    headers: {
      accept: "application/json",
      ...(init?.body ? { "content-type": "application/json" } : {}),
      ...(init?.headers ?? {}),
    },
  })
  const body = record(await response.json())
  if (!response.ok) {
    throw new Error(text(body.detail ?? body.error ?? body.status, response.statusText))
  }
  return body
}

function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-black/30 p-2">
      <div className="text-[9px] uppercase tracking-wide text-neutral-500">{label}</div>
      <div className="mt-1 break-all font-mono text-[11px] text-neutral-200">{value}</div>
    </div>
  )
}

export const AuthorityOperationsPanel: React.FC = () => {
  const [status, setStatus] = useState<Json>({})
  const [alerts, setAlerts] = useState<Json>({})
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState<string | null>(null)
  const [preparedAction, setPreparedAction] = useState<Json | null>(null)
  const [operatorId, setOperatorId] = useState("runtime-operator")

  const refresh = async (): Promise<void> => {
    try {
      const [nextStatus, nextAlerts] = await Promise.all([
        requestJson(STATUS_PATH),
        requestJson(ALERTS_PATH),
      ])
      setStatus(nextStatus)
      setAlerts(nextAlerts)
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

  const health = text(status.health, "UNKNOWN")
  const alertList = Array.isArray(alerts.alerts) ? alerts.alerts.map(record) : []
  const healthClass = health === "READY"
    ? "border-emerald-800 bg-emerald-950/30 text-emerald-200"
    : health === "BLOCKED"
      ? "border-red-800 bg-red-950/30 text-red-200"
      : "border-amber-800 bg-amber-950/30 text-amber-200"

  const authoritySummary = useMemo(() => {
    const held = Boolean(status.distributed_authority_held)
    const fence = status.distributed_fence_epoch
    return held ? `held · fence ${fence ?? "unknown"}` : "not held"
  }, [status])

  const prepare = async (action: string): Promise<void> => {
    setBusy(action)
    try {
      const result = await requestJson(PREPARE_PATH, {
        method: "POST",
        body: JSON.stringify({
          operator_id: operatorId.trim(),
          action,
        }),
      })
      setPreparedAction(result)
      setError(null)
      await refresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(null)
    }
  }

  return (
    <section data-testid="pass218-authority-operations" className="mx-auto max-w-[1800px] p-3">
      <div className={`mb-3 rounded-xl border p-3 ${healthClass}`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="text-xs font-semibold">Pass 218 authority observability</div>
            <div className="mt-1 text-[10px] opacity-80">
              I9 local fence + I10 distributed fence + I11 quorum + I12 maintenance constraints. I13 controls prepare operator work only; they cannot mint canonical authority.
            </div>
          </div>
          <button type="button" onClick={() => void refresh()} className="rounded-lg border border-current px-3 py-1 text-[10px]">
            Refresh evidence
          </button>
        </div>
      </div>

      {error ? (
        <div className="mb-3 rounded-xl border border-red-900 bg-red-950/30 p-3 text-xs text-red-200">
          Authority control plane request failed: {error}
        </div>
      ) : null}

      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Health" value={health} />
        <Metric label="Canonical writer" value={authoritySummary} />
        <Metric label="Cluster quorum" value={`${status.cluster_reachable_member_count ?? 0}/${status.cluster_expected_member_count ?? 0} · quorum ${status.cluster_quorum_size ?? "?"}`} />
        <Metric label="Ingress" value={status.ingestion_enabled ? "OPEN" : "CLOSED"} />
        <Metric label="Certificate seconds" value={status.certificate_seconds_remaining ?? "unknown"} />
        <Metric label="Snapshot age seconds" value={status.snapshot_age_seconds ?? "unknown"} />
        <Metric label="Rehearsal age seconds" value={status.rehearsal_age_seconds ?? "unknown"} />
        <Metric label="Pending operator intents" value={status.pending_operator_actions ?? 0} />
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-[1fr_1.2fr]">
        <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 p-3">
          <div className="mb-2 text-xs font-semibold text-cyan-200">Operational alerts</div>
          {alertList.length === 0 ? (
            <div className="rounded-lg border border-emerald-900 bg-emerald-950/20 p-2 text-[10px] text-emerald-200">No active I13 alerts.</div>
          ) : (
            <div className="space-y-2">
              {alertList.map((alert, index) => (
                <div key={`${text(alert.code)}-${index}`} className="rounded-lg border border-neutral-800 bg-black/30 p-2">
                  <div className="flex items-center justify-between gap-2">
                    <code className="text-[9px] text-cyan-300">{text(alert.code, "UNKNOWN")}</code>
                    <span className="text-[9px] font-semibold text-neutral-300">{text(alert.severity, "INFO")}</span>
                  </div>
                  <div className="mt-1 text-[10px] text-neutral-400">{text(alert.detail)}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-xl border border-neutral-800 bg-neutral-900/60 p-3">
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <div>
              <div className="text-xs font-semibold text-cyan-200">Bounded operator orchestration</div>
              <div className="text-[9px] text-neutral-500">Preparation receipts only. External maintenance execution remains separate and fenced.</div>
            </div>
            <input
              aria-label="Operator identity"
              value={operatorId}
              onChange={(event) => setOperatorId(event.target.value)}
              className="min-w-48 rounded-lg border border-neutral-700 bg-black px-2 py-1 text-[10px] text-neutral-200"
            />
          </div>

          <div className="grid gap-2 sm:grid-cols-2">
            {ACTIONS.map(([action, label]) => (
              <button
                key={action}
                type="button"
                disabled={busy !== null || !operatorId.trim()}
                onClick={() => void prepare(action)}
                className="min-h-10 rounded-lg border border-cyan-900 bg-cyan-950/30 px-3 text-left text-[10px] text-cyan-100 disabled:opacity-40"
              >
                {busy === action ? "Preparing…" : label}
              </button>
            ))}
          </div>

          <div className="mt-3 rounded-lg border border-neutral-800 bg-black/40 p-2">
            <div className="mb-1 text-[9px] uppercase tracking-wide text-neutral-500">Latest prepared receipt</div>
            {preparedAction ? (
              <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-all text-[9px] text-neutral-300">{JSON.stringify(preparedAction, null, 2)}</pre>
            ) : (
              <div className="text-[10px] text-neutral-500">No operator action prepared in this browser session.</div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default AuthorityOperationsPanel
