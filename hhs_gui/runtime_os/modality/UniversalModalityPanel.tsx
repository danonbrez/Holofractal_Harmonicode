import React from "react"

export const UniversalModalityPanel: React.FC = () => {
  const modalities = ["TEXT", "HARMONICODE_SOURCE", "CODE", "JSON", "YAML", "CSV", "PDF", "IMAGE", "AUDIO", "VIDEO", "BINARY", "DIRECTORY", "RUNTIME_RECEIPT", "LEDGER_FRAGMENT", "SEMANTIC_MEMORY_OBJECT", "GRAPH_OBJECT", "COMPILED_ARTIFACT", "EMULATOR_STATE"]
  return (
    <section data-testid="universal-modality-panel" className="rounded-xl border border-fuchsia-900/60 bg-neutral-950 p-2">
      <h3 className="text-xs font-semibold text-fuchsia-200">Universal Modality Adapter</h3>
      <p className="text-[11px] text-fuchsia-300">HHS_UNIVERSAL_MODALITY_ADAPTER_V1 prevents modality-specific private truth pipelines.</p>
      <p className="text-[11px] text-neutral-300">source ≠ projection ≠ artifact ≠ execution authority</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {modalities.map((modality) => <span key={modality} className="rounded border border-fuchsia-900/70 px-1 py-0.5 text-[10px]">{modality}</span>)}
      </div>
    </section>
  )
}
