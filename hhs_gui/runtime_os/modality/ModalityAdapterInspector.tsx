import React from "react"

export const ModalityAdapterInspector: React.FC<{ adapter?: any }> = ({ adapter }) => {
  const record = adapter ?? { schema: "HHS_UNIVERSAL_MODALITY_ADAPTER_V1", private_truth_pipeline_allowed: false, projection_replaces_source: false }
  return (
    <section data-testid="modality-adapter-inspector" className="rounded-xl border border-fuchsia-900/60 bg-neutral-950 p-2">
      <h3 className="text-xs font-semibold text-fuchsia-200">Adapter Inspector</h3>
      <dl className="grid grid-cols-2 gap-1 text-[11px]">
        <dt>schema</dt><dd>{record.schema}</dd>
        <dt>private truth pipeline</dt><dd>{String(record.private_truth_pipeline_allowed)}</dd>
        <dt>projection replaces source</dt><dd>{String(record.projection_replaces_source)}</dd>
      </dl>
    </section>
  )
}
