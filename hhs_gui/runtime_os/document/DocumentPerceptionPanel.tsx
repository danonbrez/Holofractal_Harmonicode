import React from "react"

export const DocumentPerceptionPanel: React.FC = () => (
  <section data-testid="document-perception-panel" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Deep Document Perception</h3>
    <p className="text-[11px] text-amber-100/80">PDF parser output ≠ PDF; OCR text ≠ document source; provider agreement ≠ automatic truth.</p>
    <code className="text-[10px] text-amber-300">HHS_DEEP_DOCUMENT_PERCEPTION_PIPELINE_RUN_V1</code>
  </section>
)
