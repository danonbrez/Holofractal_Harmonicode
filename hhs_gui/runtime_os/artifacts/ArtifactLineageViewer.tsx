import React from "react"

export const ArtifactLineageViewer: React.FC<{ lineage?: any }> = ({ lineage }) => {
  return (
    <section data-testid="artifact-lineage-viewer" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
      <h3 className="text-xs font-semibold text-amber-200">Artifact Lineage</h3>
      <p className="text-[11px] text-neutral-300">HHS_ARTIFACT_LINEAGE_RECORD_V1: source → projection → transformation plan → derived artifact → reconstruction recipe.</p>
      <pre className="max-h-24 overflow-auto text-[10px]">{JSON.stringify(lineage ?? { artifact_execution_authority_inferred: false }, null, 2)}</pre>
    </section>
  )
}
