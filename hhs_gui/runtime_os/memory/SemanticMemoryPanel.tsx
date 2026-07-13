import React from "react"
import type { WorkspaceCommandClient } from "../workspace/WorkspaceCommandClient"
export const SemanticMemoryPanel: React.FC<{ commandClient: WorkspaceCommandClient; onAuthorityFeedback: (feedback: any) => void }> = ({ commandClient, onAuthorityFeedback }) => {
  const search = async () => onAuthorityFeedback(await commandClient.submit("memory.search", { query_text: "source", objects: [] }))
  return <section data-testid="semantic-memory-panel" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3"><strong>Semantic Memory</strong><button onClick={search} className="ml-2 rounded bg-cyan-800 px-2 py-1">search</button><p className="text-[11px] text-neutral-400">Embeddings and ranking are projections, not identity authority.</p></section>
}
