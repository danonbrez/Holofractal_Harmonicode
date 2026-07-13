import React from "react"

export const DocumentReconstructionViewer: React.FC = () => (
  <section data-testid="document-reconstruction-viewer" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Document Reconstruction</h3>
    <p className="text-[11px] text-amber-100/80">Reconstruction uses source commitment, observation roots, fusion, bundle, and perception receipt.</p>
    <code className="text-[10px] text-amber-300">REJECT_DOCUMENT_PROJECTION_WITHOUT_RECONSTRUCTION</code>
  </section>
)
