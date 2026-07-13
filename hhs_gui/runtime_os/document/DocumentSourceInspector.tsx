import React from "react"

export const DocumentSourceInspector: React.FC = () => (
  <section data-testid="document-source-inspector" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Document Source Inspector</h3>
    <p className="text-[11px] text-amber-100/80">Source commitment remains canonical; projections never replace source identity.</p>
    <code className="text-[10px] text-amber-300">REJECT_OCR_TEXT_AS_DOCUMENT_SOURCE</code>
  </section>
)
