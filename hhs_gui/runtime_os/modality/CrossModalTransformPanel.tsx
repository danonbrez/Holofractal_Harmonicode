import React from "react"

export const CrossModalTransformPanel: React.FC = () => {
  return (
    <section data-testid="cross-modal-transform-panel" className="rounded-xl border border-fuchsia-900/60 bg-neutral-950 p-2">
      <h3 className="text-xs font-semibold text-fuchsia-200">Cross-Modal Transform Plan</h3>
      <p className="text-[11px] text-neutral-300">Cross-modal requests create HHS_CROSS_MODAL_TRANSFORMATION_PLAN_V1 before any artifact.</p>
      <p className="text-[11px] text-fuchsia-300">Every plan requires source commitment, typed projection roots, witness, and reconstruction recipe.</p>
    </section>
  )
}
