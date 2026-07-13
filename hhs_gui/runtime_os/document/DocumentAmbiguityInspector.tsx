import React from "react"

export const DocumentAmbiguityInspector: React.FC = () => (
  <section data-testid="document-ambiguity-inspector" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Document Ambiguity Inspector</h3>
    <p className="text-[11px] text-amber-100/80">provider disagreement ≠ failure; ambiguity is represented instead of erased.</p>
    <code className="text-[10px] text-amber-300">UNRESOLVED_AMBIGUITY</code>
  </section>
)
