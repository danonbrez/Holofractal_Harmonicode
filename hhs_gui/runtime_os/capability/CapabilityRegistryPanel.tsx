import React from "react"

export const CapabilityRegistryPanel: React.FC = () => {
  const capabilities = ["TEXT_GENERATION", "TEXT_EMBEDDING", "OCR", "IMAGE_ANALYSIS", "IMAGE_GENERATION", "SPEECH_TO_TEXT", "TEXT_TO_SPEECH", "AUDIO_ANALYSIS", "VIDEO_DECODING", "CODE_ANALYSIS", "CODE_EXECUTION", "DOCUMENT_EXTRACTION", "GRAPH_ANALYSIS", "SEARCH", "MEMORY_RETRIEVAL", "COMPILATION", "EMULATION"]
  return (
    <section data-testid="capability-registry-panel" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
      <h3 className="text-xs font-semibold text-emerald-200">Capability Registry</h3>
      <p className="text-[11px] text-emerald-300">provider ≠ capability; capability ≠ authority</p>
      <div className="mt-2 flex flex-wrap gap-1">
        {capabilities.map((cap) => <span key={cap} className="rounded border border-emerald-900/70 px-1 py-0.5 text-[10px]">{cap}</span>)}
      </div>
    </section>
  )
}
