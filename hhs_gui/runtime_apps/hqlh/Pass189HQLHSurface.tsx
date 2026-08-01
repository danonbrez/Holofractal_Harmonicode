import React, { useEffect, useMemo, useState } from "react"

type HydrationNode = {
  resolved_cell81: number
  phase72: number
  ternary: number
  hash72: string
  hash216: string
  membranes: Array<{ kind: string; operator: string; interior_states: number; outer_boundary: number; exact_source: string }>
  transition_receipt: { receipt_index: number; physical_output_authorized: boolean; physical_output_reason: string }
}

const field: React.CSSProperties = { width: "100%", borderRadius: 8, border: "1px solid #315064", background: "#07131c", color: "#e8f7ff", padding: 9 }

export default function Pass189HQLHSurface() {
  const [projected, setProjected] = useState(0)
  const [path, setPath] = useState("8,-8,0")
  const [source, setSource] = useState("List(01,xy)==(yx=01)+(zw*wz)")
  const [health, setHealth] = useState("CONNECTING")
  const [node, setNode] = useState<HydrationNode | null>(null)
  const [error, setError] = useState("")
  const parsedPath = useMemo(() => path.trim() ? path.split(",").map(value => Number(value.trim())) : [], [path])

  useEffect(() => {
    fetch("/api/pass189/health").then(response => response.json()).then(payload => setHealth(payload.status === "ok" ? "DIGITALOCEAN READY" : "DEGRADED")).catch(() => setHealth("DEGRADED"))
  }, [])

  async function hydrate() {
    setError("")
    try {
      const response = await fetch("/api/pass189/hydrate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ projected, path: parsedPath, source, xnor_a: 1, xnor_b: 1, admit: true }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error || "Pass 189 hydration failed")
      setNode(payload)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    }
  }

  return <div style={{ minHeight: "100%", padding: 16, background: "#071017", color: "#e8f7ff", fontFamily: "system-ui" }}>
    <header style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
      <div><h2 style={{ margin: 0 }}>Pass 189 HQLH Runtime</h2><small style={{ color: "#9fb5c3" }}>Lo Shu 41 · P+1 membranes · XNOR ternary · V72 · Hash216</small></div>
      <b style={{ color: health.includes("READY") ? "#72e7ff" : "#ffbf69" }}>{health}</b>
    </header>
    <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 360px) 1fr", gap: 14, marginTop: 14 }}>
      <section style={{ display: "grid", gap: 10, alignContent: "start" }}>
        <label>Projected address<input style={field} type="number" min={0} max={1259711} value={projected} onChange={event => setProjected(Number(event.target.value))} /></label>
        <label>Base-41 path<input style={field} value={path} onChange={event => setPath(event.target.value)} /></label>
        <label>Exact source<textarea style={{ ...field, minHeight: 100 }} value={source} onChange={event => setSource(event.target.value)} /></label>
        <button style={{ ...field, cursor: "pointer", fontWeight: 700 }} onClick={hydrate}>Hydrate and admit</button>
        {error && <div style={{ color: "#ff8d8d" }}>{error}</div>}
        <small style={{ color: "#9fb5c3" }}>Physical output remains blocked until real calibration evidence is admitted.</small>
      </section>
      <section style={{ border: "1px solid #294556", borderRadius: 12, padding: 14, overflow: "auto" }}>
        {!node ? <p>Submit a state to inspect the shared equation authority.</p> : <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,minmax(90px,1fr))", gap: 8 }}>
            {[["Cell", node.resolved_cell81], ["Phase", node.phase72], ["Ternary", node.ternary], ["Receipt", node.transition_receipt.receipt_index]].map(([label, value]) => <div key={String(label)} style={{ background: "#0d1b25", borderRadius: 8, padding: 9 }}><small>{label}</small><strong style={{ display: "block", color: "#ffd675" }}>{value}</strong></div>)}
          </div>
          <h3>Membranes</h3>{node.membranes.map((membrane, index) => <div key={index} style={{ borderLeft: "3px solid #ffd675", padding: 8, marginBottom: 7, background: "#0b1821" }}><b>{membrane.kind}</b> <code>{membrane.operator}</code><br /><small>P={membrane.interior_states}, P+1={membrane.outer_boundary}</small><br />{membrane.exact_source}</div>)}
          <h3>Receipt</h3><pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}>{JSON.stringify({ hash72: node.hash72, hash216: node.hash216, physicalOutput: node.transition_receipt.physical_output_reason }, null, 2)}</pre>
        </>}
      </section>
    </div>
  </div>
}
