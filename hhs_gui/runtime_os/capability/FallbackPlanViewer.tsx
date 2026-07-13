import React from "react"

export const FallbackPlanViewer: React.FC = () => (
  <section data-testid="fallback-plan-viewer" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-emerald-200">Fallback Plan</h3>
    <p className="text-[11px] text-neutral-300">Fallback preserves failed attempt history and artifact lineage.</p>
    <p className="text-[11px] text-emerald-300">REJECT_FALLBACK_HISTORY_ERASURE</p>
  </section>
)
