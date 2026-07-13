import React, { useState } from "react"
import type { WorkspaceCommandClient } from "./WorkspaceCommandClient"

export const MultimodalIngressPanel: React.FC<{ commandClient: WorkspaceCommandClient; onAuthorityFeedback: (feedback: any) => void; projectId: string }> = ({ commandClient, onAuthorityFeedback, projectId }) => {
  const [sourcePayload, setSourcePayload] = useState("a²+b²=c²")
  const ingest = async () => onAuthorityFeedback(await commandClient.submit("ingress.register", { project_id: projectId, source_name: "main.hhs", source_payload: sourcePayload, declared_modality: "HARMONICODE_SOURCE" }))
  return (
    <section data-testid="multimodal-ingress-panel" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
      <strong>Multimodal Ingress</strong>
      <p className="text-[11px] text-neutral-400">Original source is preserved; projections never replace source.</p>
      <textarea value={sourcePayload} onChange={(e) => setSourcePayload(e.target.value)} className="mt-2 h-16 w-full rounded bg-neutral-950 p-2" />
      <button onClick={ingest} className="mt-2 rounded bg-cyan-800 px-2 py-1">witness ingress</button>
    </section>
  )
}
