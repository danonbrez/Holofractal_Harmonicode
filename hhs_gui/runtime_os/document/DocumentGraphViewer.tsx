import React from "react"

export const DocumentGraphViewer: React.FC = () => (
  <section data-testid="document-graph-viewer" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Document Graph Projection</h3>
    <p className="text-[11px] text-amber-100/80">DOCUMENT_GRAPH_PROJECTION preserves lineage; document graph ≠ document identity.</p>
    <code className="text-[10px] text-amber-300">DOCUMENT_GRAPH_PROJECTION</code>
  </section>
)
