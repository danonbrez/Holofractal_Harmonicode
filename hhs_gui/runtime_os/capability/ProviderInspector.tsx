import React from "react"

export const ProviderInspector: React.FC = () => (
  <section data-testid="provider-inspector" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-emerald-200">Provider Inspector</h3>
    <p className="text-[11px] text-neutral-300">Providers are peripherals from the Runtime perspective.</p>
    <p className="text-[11px] text-emerald-300">provider output ≠ canonical truth</p>
    <p className="text-[10px] text-neutral-400">Raw provider results must re-enter Runtime ingress and the universal modality pipeline.</p>
  </section>
)
