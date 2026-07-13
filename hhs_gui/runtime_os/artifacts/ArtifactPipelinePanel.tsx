import React from "react"

export const ArtifactPipelinePanel: React.FC = () => {
  return (
    <section data-testid="artifact-pipeline-panel" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
      <h3 className="text-xs font-semibold text-amber-200">Artifact Pipeline</h3>
      <p className="text-[11px] text-neutral-300">HHS_DERIVED_ARTIFACT_RECORD_V1 keeps artifact lineage separate from execution authority.</p>
      <p className="text-[11px] text-amber-300">valid artifact ≠ authorized execution</p>
    </section>
  )
}
