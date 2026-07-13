import React from "react"

export const CapabilityResolutionViewer: React.FC = () => (
  <section data-testid="capability-resolution-viewer" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-emerald-200">Capability Resolution</h3>
    <p className="text-[11px] text-neutral-300">workspace intent → capability requirement → deterministic provider resolution</p>
    <p className="text-[11px] text-emerald-300">capability selection does not grant execution authority.</p>
  </section>
)
