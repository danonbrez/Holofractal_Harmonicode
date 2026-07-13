import React from "react"

export const DocumentFusionViewer: React.FC = () => (
  <section data-testid="document-fusion-viewer" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Document Fusion Viewer</h3>
    <p className="text-[11px] text-amber-100/80">OBSERVATION_AGREEMENT, OBSERVATION_DISAGREEMENT, and UNRESOLVED_AMBIGUITY remain visible.</p>
    <code className="text-[10px] text-amber-300">REJECT_PROVIDER_DISAGREEMENT_COLLAPSED_SILENTLY</code>
  </section>
)
