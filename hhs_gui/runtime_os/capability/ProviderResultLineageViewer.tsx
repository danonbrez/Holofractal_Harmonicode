import React from "react"

export const ProviderResultLineageViewer: React.FC = () => (
  <section data-testid="provider-result-lineage-viewer" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-emerald-200">Provider Result Lineage</h3>
    <p className="text-[11px] text-neutral-300">raw provider result → Runtime ingress → typed projection → artifact lineage → reconstruction recipe</p>
    <p className="text-[11px] text-emerald-300">REJECT_RAW_PROVIDER_OUTPUT_AS_CANONICAL_SOURCE</p>
  </section>
)
