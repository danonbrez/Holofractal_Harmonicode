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

type Iteration2Status = {
  classification: string
  events: number
  profiles: number
  validated_profiles: number
  samples: number
  checkpoints: number
  root_hash72: string
}

const field: React.CSSProperties = { width: "100%", borderRadius: 8, border: "1px solid #315064", background: "#07131c", color: "#e8f7ff", padding: 9 }
const card: React.CSSProperties = { border: "1px solid #294556", borderRadius: 12, padding: 14, background: "#091720" }

export default function Pass189HQLHSurface() {
  const [projected, setProjected] = useState(0)
  const [path, setPath] = useState("8,-8,0")
  const [source, setSource] = useState("List(01,xy)==(yx=01)+(zw*wz)")
  const [health, setHealth] = useState("CONNECTING")
  const [node, setNode] = useState<HydrationNode | null>(null)
  const [iteration2, setIteration2] = useState<Iteration2Status | null>(null)
  const [profileId, setProfileId] = useState("")
  const [iteration2Result, setIteration2Result] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState("")
  const parsedPath = useMemo(() => path.trim() ? path.split(",").map(value => Number(value.trim())) : [], [path])

  async function refreshIteration2() {
    const response = await fetch("/api/pass189/i2/status")
    const payload = await response.json()
    if (!response.ok) throw new Error(payload.error || "Pass 189 Iteration 2 unavailable")
    setIteration2(payload)
  }

  useEffect(() => {
    Promise.all([
      fetch("/api/pass189/health").then(response => response.json()),
      refreshIteration2(),
    ]).then(([payload]) => setHealth(payload.status === "ok" ? "DIGITALOCEAN READY" : "DEGRADED")).catch(() => setHealth("DEGRADED"))
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

  async function iteration2Request(pathname: string, body: Record<string, unknown>) {
    setError("")
    try {
      const response = await fetch(pathname, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error || "Iteration 2 request failed")
      setIteration2Result(payload)
      await refreshIteration2()
      return payload
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
      return null
    }
  }

  async function registerSyntheticProfile() {
    const payload = await iteration2Request("/api/pass189/i2/calibration/profile", {
      device_id: "adc-visual", variable: "V", unit: "volt", dimension: "electric_potential",
      scale: { numerator: 1, denominator: 1000 }, offset: 0, raw_min: 0, raw_max: 5000,
      canonical_min: 0, canonical_max: 5, resolution: { numerator: 1, denominator: 1000 },
      tolerance: { numerator: 1, denominator: 100 }, required_samples: 3, evidence_class: "SYNTHETIC",
      calibration_source: "visual-fixture", device_attested: false, operator_arm_hash72: "0".repeat(72), created_ns: 1,
    })
    if (payload?.profile_id) setProfileId(String(payload.profile_id))
  }

  async function resolveWorldlines() {
    const inputReceipt = iteration2?.events ?? 0
    await iteration2Request("/api/pass189/i2/worldline/resolve", {
      causal_rate: 1,
      collision_policy: "REJECT",
      candidates: [
        { object_id: "alpha", input_receipt_index: inputReceipt, position4: [0, 0, 0, 0], delta4: [2, 1, 0, 0] },
        { object_id: "beta", input_receipt_index: inputReceipt, position4: [0, 4, 0, 0], delta4: [2, -1, 0, 0] },
      ],
    })
  }

  return <div style={{ minHeight: "100%", padding: 16, background: "#071017", color: "#e8f7ff", fontFamily: "system-ui" }}>
    <header style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
      <div><h2 style={{ margin: 0 }}>Pass 189 HQLH Runtime</h2><small style={{ color: "#9fb5c3" }}>Lo Shu 41 · P+1 · XNOR · V72 · persistent calibration · atomic causal batches</small></div>
      <b style={{ color: health.includes("READY") ? "#72e7ff" : "#ffbf69" }}>{health}</b>
    </header>
    <div style={{ display: "grid", gridTemplateColumns: "minmax(260px, 360px) 1fr", gap: 14, marginTop: 14 }}>
      <section style={{ display: "grid", gap: 10, alignContent: "start" }}>
        <label>Projected address<input style={field} type="number" min={0} max={1259711} value={projected} onChange={event => setProjected(Number(event.target.value))} /></label>
        <label>Base-41 path<input style={field} value={path} onChange={event => setPath(event.target.value)} /></label>
        <label>Exact source<textarea style={{ ...field, minHeight: 100 }} value={source} onChange={event => setSource(event.target.value)} /></label>
        <button style={{ ...field, cursor: "pointer", fontWeight: 700 }} onClick={hydrate}>Hydrate and admit</button>
        {error && <div style={{ color: "#ff8d8d" }}>{error}</div>}
        <small style={{ color: "#9fb5c3" }}>Physical dispatch requires validated measured evidence, device attestation, and operator arming.</small>
      </section>
      <section style={{ display: "grid", gap: 14, overflow: "auto" }}>
        <div style={card}>
          {!node ? <p>Submit a state to inspect the shared hydration authority.</p> : <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,minmax(90px,1fr))", gap: 8 }}>
              {[["Cell", node.resolved_cell81], ["Phase", node.phase72], ["Ternary", node.ternary], ["Receipt", node.transition_receipt.receipt_index]].map(([label, value]) => <div key={String(label)} style={{ background: "#0d1b25", borderRadius: 8, padding: 9 }}><small>{label}</small><strong style={{ display: "block", color: "#ffd675" }}>{value}</strong></div>)}
            </div>
            <h3>Membranes</h3>{node.membranes.map((membrane, index) => <div key={index} style={{ borderLeft: "3px solid #ffd675", padding: 8, marginBottom: 7, background: "#0b1821" }}><b>{membrane.kind}</b> <code>{membrane.operator}</code><br /><small>P={membrane.interior_states}, P+1={membrane.outer_boundary}</small><br />{membrane.exact_source}</div>)}
            <h3>Receipt</h3><pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all" }}>{JSON.stringify({ hash72: node.hash72, hash216: node.hash216, physicalOutput: node.transition_receipt.physical_output_reason }, null, 2)}</pre>
          </>}
        </div>
        <div style={card}>
          <h3 style={{ marginTop: 0 }}>Iteration 2 · Persistent authority</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,minmax(80px,1fr))", gap: 8 }}>
            {[["Events", iteration2?.events ?? 0], ["Profiles", iteration2?.profiles ?? 0], ["Validated", iteration2?.validated_profiles ?? 0], ["Checkpoints", iteration2?.checkpoints ?? 0]].map(([label, value]) => <div key={String(label)} style={{ background: "#0d1b25", borderRadius: 8, padding: 9 }}><small>{label}</small><strong style={{ display: "block", color: "#72e7ff" }}>{value}</strong></div>)}
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 8, marginTop: 10 }}>
            <button style={field} onClick={registerSyntheticProfile}>Register synthetic profile</button>
            <button style={field} disabled={!profileId} onClick={() => iteration2Request("/api/pass189/i2/calibration/admit", { profile_id: profileId, requested: 1, mode: "SIMULATION" })}>Admit simulation candidate</button>
            <button style={field} onClick={resolveWorldlines}>Resolve joint worldlines</button>
            <button style={field} onClick={() => iteration2Request("/api/pass189/i2/checkpoint", { label: "visual-checkpoint" })}>Create checkpoint</button>
          </div>
          {profileId && <p><small>Active profile</small><br /><code style={{ wordBreak: "break-all" }}>{profileId}</code></p>}
          <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word", maxHeight: 300, overflow: "auto" }}>{JSON.stringify(iteration2Result ?? { classification: iteration2?.classification, root_hash72: iteration2?.root_hash72 }, null, 2)}</pre>
        </div>
      </section>
    </div>
  </div>
}
