import React from "react"

export const TableProjectionViewer: React.FC = () => (
  <section data-testid="table-projection-viewer" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Table Projection Viewer</h3>
    <p className="text-[11px] text-amber-100/80">Table extraction requires a region/source witness and cannot become table source.</p>
    <code className="text-[10px] text-amber-300">REJECT_TABLE_EXTRACTION_WITHOUT_REGION_SOURCE</code>
  </section>
)
