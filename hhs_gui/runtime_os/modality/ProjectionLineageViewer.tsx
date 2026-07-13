import React from "react"

export const ProjectionLineageViewer: React.FC<{ lineage?: any }> = ({ lineage }) => {
  return (
    <section data-testid="projection-lineage-viewer" className="rounded-xl border border-fuchsia-900/60 bg-neutral-950 p-2">
      <h3 className="text-xs font-semibold text-fuchsia-200">Projection Lineage</h3>
      <p className="text-[11px] text-neutral-300">Displays HHS_MODALITY_PROJECTION_RECORD_V1 without allowing projections to replace sources.</p>
      <pre className="max-h-24 overflow-auto text-[10px]">{JSON.stringify(lineage ?? { source_not_replaced_by_projection: true }, null, 2)}</pre>
    </section>
  )
}
