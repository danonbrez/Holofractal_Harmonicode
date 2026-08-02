import React, { useEffect, useMemo, useRef, useState } from "react"

type Operation = {
  operation_id: string
  canonical_name: string
  capability_scope: string
}

type RuntimeEvent = {
  sequence?: number
  event_type: string
  operation_id?: string
  hash72?: string
  fencing_token?: number
  kernel_authority_hash72?: string
}

type ArbitrationStatus = {
  active?: boolean
  lease_state?: string
  holder_id?: string | null
  fencing_token?: number
  fence_count?: number
  highest_committed_fence?: number
  lease_expires_ns?: number
  lease_transition_count?: number
  last_transition?: string | null
  last_transition_hash72?: string | null
  lease_receipt_chain_verified?: boolean
}

type ResourceRegistryStatus = {
  counts?: Record<string, number>
  active_job_count?: number
  governed_operation_count?: number
  native_operation_count?: number
  compiler_fallback_operation_count?: number
  resource_registry_hash72?: string
  state_root?: string
}

const field: React.CSSProperties = {
  width: "100%",
  borderRadius: 8,
  border: "1px solid #315064",
  background: "#07131c",
  color: "#e8f7ff",
  padding: 9,
  boxSizing: "border-box",
}

const serviceBase = String(import.meta.env.VITE_PASS190_BASE_URL || "").replace(/\/$/, "")
const apiUrl = (path: string) => serviceBase ? `${serviceBase}${path}` : path
const wsUrl = (after: number) => {
  if (serviceBase) return `${serviceBase.replace(/^http:/, "ws:").replace(/^https:/, "wss:")}/api/pass190/ws?after=${after}`
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
  return `${protocol}//${window.location.host}/api/pass190/ws?after=${after}`
}

async function checkedJson(response: Response) {
  const payload = await response.json()
  if (!response.ok) throw new Error(payload.message || payload.error || `HTTP ${response.status}`)
  return payload
}

export default function Pass190OperationFabricSurface() {
  const [operations, setOperations] = useState<Operation[]>([])
  const [selected, setSelected] = useState("system.status")
  const [argumentsText, setArgumentsText] = useState("{}")
  const [capabilityToken, setCapabilityToken] = useState("")
  const [status, setStatus] = useState("CONNECTING")
  const [integrity, setIntegrity] = useState<Record<string, unknown> | null>(null)
  const [arbitration, setArbitration] = useState<ArbitrationStatus | null>(null)
  const [resources, setResources] = useState<ResourceRegistryStatus | null>(null)
  const [result, setResult] = useState<Record<string, any> | null>(null)
  const [events, setEvents] = useState<RuntimeEvent[]>([])
  const [error, setError] = useState("")
  const socketRef = useRef<WebSocket | null>(null)
  const stoppedRef = useRef(false)
  const lastSequenceRef = useRef(0)
  const reconnectAttemptRef = useRef(0)
  const reconnectTimerRef = useRef<number | null>(null)
  const authorityTimerRef = useRef<number | null>(null)

  const current = useMemo(
    () => operations.find((operation) => operation.operation_id === selected),
    [operations, selected],
  )

  async function refreshAuthority() {
    const [integrityPayload, arbitrationPayload, resourcePayload] = await Promise.all([
      fetch(apiUrl("/api/pass190/integrity")).then(checkedJson),
      fetch(apiUrl("/api/pass190/arbitration")).then(checkedJson),
      fetch(apiUrl("/api/pass190/resource-registry")).then(checkedJson),
    ])
    if (stoppedRef.current) return
    setIntegrity(integrityPayload)
    setArbitration(arbitrationPayload)
    setResources(resourcePayload)
    setStatus(integrityPayload.status === "ok" ? "UNIFIED AUTHORITY READY" : "DEGRADED")
  }

  useEffect(() => {
    stoppedRef.current = false
    Promise.all([
      fetch(apiUrl("/api/pass190/operations")).then(checkedJson),
      fetch(apiUrl("/api/pass190/integrity")).then(checkedJson),
      fetch(apiUrl("/api/pass190/arbitration")).then(checkedJson),
      fetch(apiUrl("/api/pass190/resource-registry")).then(checkedJson),
    ]).then(([registry, integrityPayload, arbitrationPayload, resourcePayload]) => {
      if (stoppedRef.current) return
      setOperations(registry.operations || [])
      setIntegrity(integrityPayload)
      setArbitration(arbitrationPayload)
      setResources(resourcePayload)
      setStatus(integrityPayload.status === "ok" ? "UNIFIED AUTHORITY READY" : "DEGRADED")
    }).catch((caught) => {
      if (!stoppedRef.current) {
        setStatus("DEGRADED")
        setError(caught instanceof Error ? caught.message : String(caught))
      }
    })

    authorityTimerRef.current = window.setInterval(() => {
      void refreshAuthority().catch((caught) => {
        if (!stoppedRef.current) {
          setStatus("AUTHORITY REFRESH DEGRADED")
          setError(caught instanceof Error ? caught.message : String(caught))
        }
      })
    }, 2000)

    const connect = () => {
      if (stoppedRef.current) return
      const socket = new WebSocket(wsUrl(lastSequenceRef.current))
      socketRef.current = socket
      setStatus(reconnectAttemptRef.current ? "EVENT CHANNEL RECOVERING" : "EVENT CHANNEL CONNECTING")
      socket.onopen = () => {
        reconnectAttemptRef.current = 0
        setStatus("UNIFIED AUTHORITY READY")
      }
      socket.onmessage = (message) => {
        try {
          const event = JSON.parse(String(message.data)) as RuntimeEvent
          if (typeof event.sequence === "number") {
            if (event.sequence <= lastSequenceRef.current) return
            lastSequenceRef.current = event.sequence
          }
          setEvents((previous) => [...previous.slice(-49), event])
          void refreshAuthority().catch(() => undefined)
        } catch (caught) {
          setStatus("EVENT PAYLOAD REJECTED")
          setError(caught instanceof Error ? caught.message : String(caught))
        }
      }
      socket.onerror = () => socket.close()
      socket.onclose = () => {
        if (stoppedRef.current || socketRef.current !== socket) return
        socketRef.current = null
        const delay = Math.min(1000 * (2 ** reconnectAttemptRef.current++), 15_000)
        setStatus("EVENT CHANNEL RECOVERING")
        reconnectTimerRef.current = window.setTimeout(connect, delay)
      }
    }
    connect()
    return () => {
      stoppedRef.current = true
      if (reconnectTimerRef.current !== null) window.clearTimeout(reconnectTimerRef.current)
      if (authorityTimerRef.current !== null) window.clearInterval(authorityTimerRef.current)
      socketRef.current?.close()
      socketRef.current = null
    }
  }, [])

  async function invoke() {
    setError("")
    try {
      const parsed = JSON.parse(argumentsText)
      if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") throw new Error("Arguments must be a JSON object")
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (capabilityToken.trim()) headers.Authorization = `HHS-Capability ${capabilityToken.trim()}`
      const payload = await fetch(apiUrl("/api/pass190/invoke"), {
        method: "POST",
        headers,
        body: JSON.stringify({ operation_id: selected, arguments: parsed }),
      }).then(checkedJson)
      setResult(payload)
      await refreshAuthority()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    }
  }

  const counts = resources?.counts || {}

  return <div style={{ minHeight: "100%", padding: 16, background: "#071017", color: "#e8f7ff", fontFamily: "system-ui" }}>
    <header style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
      <div>
        <h2 style={{ margin: 0 }}>Pass 190 Operation Fabric</h2>
        <p style={{ margin: "4px 0 0", color: "#9ab9c9" }}>Unified workspace, artifact, provider, capability, and job registries under atomic VM81 admission, Hash72 lineage, native ABI, and exact compiler fallback.</p>
      </div>
      <strong>{status}</strong>
    </header>
    <main style={{ display: "grid", gridTemplateColumns: "minmax(280px, 1fr) minmax(320px, 1.4fr)", gap: 14, marginTop: 16 }}>
      <section style={{ border: "1px solid #284552", borderRadius: 10, padding: 14 }}>
        <label>Registered operation<select value={selected} onChange={(event) => setSelected(event.target.value)} style={{ ...field, marginTop: 6 }}>
          {operations.map((operation) => <option key={operation.operation_id}>{operation.operation_id}</option>)}
        </select></label>
        <p style={{ color: "#9ab9c9" }}>{current?.canonical_name || "Loading registry"}</p>
        <label>Arguments<textarea value={argumentsText} onChange={(event) => setArgumentsText(event.target.value)} rows={8} style={{ ...field, marginTop: 6, fontFamily: "monospace" }} /></label>
        <label style={{ display: "block", marginTop: 10 }}>Signed capability token<input type="password" autoComplete="off" value={capabilityToken} onChange={(event) => setCapabilityToken(event.target.value)} placeholder={current?.capability_scope === "public" ? "Not required" : current?.capability_scope || "Protected operation"} style={{ ...field, marginTop: 6 }} /></label>
        <button onClick={invoke} style={{ marginTop: 12, borderRadius: 8, padding: "10px 16px", cursor: "pointer" }}>Invoke through unified VM81 authority</button>
        {error && <p role="alert" style={{ color: "#ffb2a6" }}>{error}</p>}
      </section>
      <section style={{ display: "grid", gap: 14 }}>
        <article style={{ border: "1px solid #284552", borderRadius: 10, padding: 14 }}>
          <h3 style={{ marginTop: 0 }}>Unified resource registry</h3>
          <dl style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "6px 12px" }}>
            <dt>Governed operations</dt><dd>{String(resources?.governed_operation_count ?? operations.length)}</dd>
            <dt>Native ABI operations</dt><dd>{String(resources?.native_operation_count ?? 0)}</dd>
            <dt>Exact fallback operations</dt><dd>{String(resources?.compiler_fallback_operation_count ?? 0)}</dd>
            <dt>Workspaces</dt><dd>{String(counts.workspaces ?? 0)}</dd>
            <dt>Artifacts</dt><dd>{String(counts.artifacts ?? 0)}</dd>
            <dt>Providers</dt><dd>{String(counts.providers ?? 0)}</dd>
            <dt>Capabilities</dt><dd>{String(counts.capabilities ?? 0)}</dd>
            <dt>Jobs</dt><dd>{String(counts.jobs ?? 0)}</dd>
            <dt>Active jobs</dt><dd>{String(resources?.active_job_count ?? 0)}</dd>
            <dt>Registry Hash72</dt><dd style={{ overflowWrap: "anywhere" }}>{resources?.resource_registry_hash72 || "—"}</dd>
          </dl>
        </article>
        <article style={{ border: "1px solid #284552", borderRadius: 10, padding: 14 }}>
          <h3 style={{ marginTop: 0 }}>Authority integrity</h3>
          <dl style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "6px 12px" }}>
            <dt>Receipts</dt><dd>{String(integrity?.receipt_count ?? 0)}</dd>
            <dt>Events</dt><dd>{String(integrity?.event_count ?? 0)}</dd>
            <dt>Fence witnesses</dt><dd>{String(arbitration?.fence_count ?? 0)}</dd>
            <dt>Highest fence</dt><dd>{String(arbitration?.highest_committed_fence ?? 0)}</dd>
            <dt>Lease transitions</dt><dd>{String(arbitration?.lease_transition_count ?? 0)}</dd>
            <dt>Last transition</dt><dd>{arbitration?.last_transition || "—"}</dd>
            <dt>Admission lease</dt><dd>{String(arbitration?.lease_state || "absent").toUpperCase()}</dd>
            <dt>Lease holder</dt><dd style={{ overflowWrap: "anywhere" }}>{arbitration?.holder_id || "—"}</dd>
            <dt>Resource registry</dt><dd>{integrity?.resource_registry_verified ? "VERIFIED" : "UNVERIFIED"}</dd>
            <dt>Atomic snapshot</dt><dd>{integrity?.atomic_snapshot_verified ? "VERIFIED" : "UNVERIFIED"}</dd>
            <dt>Kernel authority</dt><dd>{integrity?.kernel_authority_verified ? "VERIFIED" : "UNVERIFIED"}</dd>
            <dt>Chain head</dt><dd style={{ overflowWrap: "anywhere" }}>{String(integrity?.chain_head ?? "—")}</dd>
            <dt>State root</dt><dd style={{ overflowWrap: "anywhere" }}>{String(integrity?.state_root ?? "—")}</dd>
          </dl>
        </article>
        <article style={{ border: "1px solid #284552", borderRadius: 10, padding: 14 }}>
          <h3 style={{ marginTop: 0 }}>Latest admitted result</h3>
          {result ? <pre style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{JSON.stringify(result, null, 2)}</pre> : <p style={{ color: "#9ab9c9" }}>No operation admitted in this window.</p>}
        </article>
        <article style={{ border: "1px solid #284552", borderRadius: 10, padding: 14, maxHeight: 260, overflow: "auto" }}>
          <h3 style={{ marginTop: 0 }}>Verified kernel-authority event channel</h3>
          {events.slice().reverse().map((event, index) => <div key={`${event.sequence ?? event.event_type}-${index}`} style={{ borderTop: "1px solid #203845", padding: "8px 0" }}>
            <strong>{event.event_type}</strong>{event.operation_id && <span> · {event.operation_id}</span>}{typeof event.sequence === "number" && <span> · sequence {event.sequence}</span>}{typeof event.fencing_token === "number" && <span> · fence {event.fencing_token}</span>}
            {event.hash72 && <div style={{ color: "#9ab9c9", overflowWrap: "anywhere" }}>{event.hash72}</div>}
            {event.kernel_authority_hash72 && <div style={{ color: "#7898aa", overflowWrap: "anywhere" }}>kernel {event.kernel_authority_hash72}</div>}
          </div>)}
        </article>
      </section>
    </main>
  </div>
}
