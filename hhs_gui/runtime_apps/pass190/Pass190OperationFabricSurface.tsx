import React, { useEffect, useMemo, useRef, useState } from "react"

type Operation = {
  operation_id: string
  canonical_name: string
  effect_class: string
  capability_scope: string
  argument_schema: { properties?: Record<string, unknown>; required?: string[] }
}

type RuntimeEvent = {
  sequence?: number
  event_type: string
  operation_id?: string
  receipt_index?: number
  hash72?: string
  state_after?: string
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

export default function Pass190OperationFabricSurface() {
  const [operations, setOperations] = useState<Operation[]>([])
  const [selected, setSelected] = useState("system.status")
  const [argumentsText, setArgumentsText] = useState("{}")
  const [capability, setCapability] = useState("")
  const [status, setStatus] = useState("CONNECTING")
  const [integrity, setIntegrity] = useState<Record<string, unknown> | null>(null)
  const [result, setResult] = useState<Record<string, any> | null>(null)
  const [events, setEvents] = useState<RuntimeEvent[]>([])
  const [error, setError] = useState("")
  const socketRef = useRef<WebSocket | null>(null)

  const current = useMemo(() => operations.find((operation) => operation.operation_id === selected), [operations, selected])

  useEffect(() => {
    let cancelled = false
    Promise.all([
      fetch("/api/pass190/operations").then((response) => response.json()),
      fetch("/api/pass190/integrity").then((response) => response.json()),
    ]).then(([registry, integrityPayload]) => {
      if (cancelled) return
      setOperations(registry.operations || [])
      setIntegrity(integrityPayload)
      setStatus(integrityPayload.status === "ok" ? "AUTHORITY READY" : "DEGRADED")
    }).catch((caught) => {
      if (!cancelled) {
        setStatus("DEGRADED")
        setError(caught instanceof Error ? caught.message : String(caught))
      }
    })

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
    const socket = new WebSocket(`${protocol}//${window.location.host}/api/pass190/ws?after=0`)
    socketRef.current = socket
    socket.onmessage = (message) => {
      const event = JSON.parse(String(message.data)) as RuntimeEvent
      setEvents((previous) => [...previous.slice(-49), event])
    }
    socket.onerror = () => setStatus("EVENT CHANNEL DEGRADED")
    return () => {
      cancelled = true
      socket.close()
      socketRef.current = null
    }
  }, [])

  async function invoke() {
    setError("")
    try {
      const parsed = JSON.parse(argumentsText)
      if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") throw new Error("Arguments must be a JSON object")
      const headers: Record<string, string> = { "Content-Type": "application/json" }
      if (capability.trim()) headers["X-HHS-Capability"] = capability.trim()
      const response = await fetch("/api/pass190/invoke", {
        method: "POST",
        headers,
        body: JSON.stringify({ operation_id: selected, arguments: parsed }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.message || payload.error || "Operation failed")
      setResult(payload)
      const integrityResponse = await fetch("/api/pass190/integrity")
      setIntegrity(await integrityResponse.json())
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    }
  }

  return <div style={{ minHeight: "100%", padding: 16, background: "#071017", color: "#e8f7ff", fontFamily: "system-ui" }}>
    <header style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
      <div>
        <h2 style={{ margin: 0 }}>Pass 190 Operation Fabric</h2>
        <p style={{ margin: "4px 0 0", color: "#9ab9c9" }}>One registry, one persistent receipt chain, generated SDKs, and resumable events.</p>
      </div>
      <strong>{status}</strong>
    </header>

    <main style={{ display: "grid", gridTemplateColumns: "minmax(280px, 1fr) minmax(320px, 1.4fr)", gap: 14, marginTop: 16 }}>
      <section style={{ border: "1px solid #284552", borderRadius: 10, padding: 14 }}>
        <label>Registered operation<select value={selected} onChange={(event) => setSelected(event.target.value)} style={{ ...field, marginTop: 6 }}>
          {operations.map((operation) => <option key={operation.operation_id} value={operation.operation_id}>{operation.operation_id}</option>)}
        </select></label>
        <p style={{ color: "#9ab9c9" }}>{current?.canonical_name || "Loading registry"}</p>
        <label>Arguments<textarea value={argumentsText} onChange={(event) => setArgumentsText(event.target.value)} rows={8} style={{ ...field, marginTop: 6, fontFamily: "monospace" }} /></label>
        <label style={{ display: "block", marginTop: 10 }}>Capability<input value={capability} onChange={(event) => setCapability(event.target.value)} placeholder={current?.capability_scope || "public"} style={{ ...field, marginTop: 6 }} /></label>
        <button onClick={invoke} style={{ marginTop: 12, borderRadius: 8, padding: "10px 16px", cursor: "pointer" }}>Invoke through VM81 authority</button>
        {error && <p role="alert" style={{ color: "#ffb2a6" }}>{error}</p>}
      </section>

      <section style={{ display: "grid", gap: 14 }}>
        <article style={{ border: "1px solid #284552", borderRadius: 10, padding: 14 }}>
          <h3 style={{ marginTop: 0 }}>Authority integrity</h3>
          <dl style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "6px 12px" }}>
            <dt>Receipts</dt><dd>{String(integrity?.receipt_count ?? 0)}</dd>
            <dt>Events</dt><dd>{String(integrity?.event_count ?? 0)}</dd>
            <dt>Chain head</dt><dd style={{ overflowWrap: "anywhere" }}>{String(integrity?.chain_head ?? "—")}</dd>
            <dt>State root</dt><dd style={{ overflowWrap: "anywhere" }}>{String(integrity?.state_root ?? "—")}</dd>
          </dl>
        </article>
        <article style={{ border: "1px solid #284552", borderRadius: 10, padding: 14 }}>
          <h3 style={{ marginTop: 0 }}>Latest admitted result</h3>
          {result ? <dl style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "6px 12px" }}>
            <dt>Operation</dt><dd>{result.operation_id}</dd>
            <dt>Receipt</dt><dd>{result.receipt?.receipt_index}</dd>
            <dt>Hash72</dt><dd style={{ overflowWrap: "anywhere" }}>{result.receipt?.hash72}</dd>
            <dt>Result</dt><dd><pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{JSON.stringify(result.result, null, 2)}</pre></dd>
          </dl> : <p style={{ color: "#9ab9c9" }}>No operation admitted in this window.</p>}
        </article>
        <article style={{ border: "1px solid #284552", borderRadius: 10, padding: 14, maxHeight: 260, overflow: "auto" }}>
          <h3 style={{ marginTop: 0 }}>Receipt event channel</h3>
          {events.slice().reverse().map((event, index) => <div key={`${event.sequence ?? "channel"}-${index}`} style={{ borderTop: "1px solid #203845", padding: "8px 0" }}>
            <strong>{event.event_type}</strong> {event.operation_id && <span>· {event.operation_id}</span>}
            {event.hash72 && <div style={{ color: "#9ab9c9", overflowWrap: "anywhere" }}>{event.hash72}</div>}
          </div>)}
        </article>
      </section>
    </main>
  </div>
}
