import React, { useState } from "react"
import type { WorkspaceCommandClient } from "../workspace/WorkspaceCommandClient"

export const HHSSymbolicEditor: React.FC<{ commandClient: WorkspaceCommandClient; onAuthorityFeedback: (feedback: any) => void; projectId: string }> = ({ commandClient, onAuthorityFeedback, projectId }) => {
  const [buffer, setBuffer] = useState("a²=1\nb²=2\nc²=3")
  const submitPatch = async () => onAuthorityFeedback(await commandClient.submit("source.patch", { project_id: projectId, replacement_text: buffer }))
  return (
    <section data-testid="hhs-symbolic-editor" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
      <div className="flex items-center justify-between"><strong>HHS Symbolic Editor</strong><span className="text-[10px] text-yellow-300">local buffer non-authoritative</span></div>
      <textarea value={buffer} onChange={(e) => setBuffer(e.target.value)} className="mt-2 h-24 w-full rounded bg-neutral-950 p-2 font-mono" />
      <button onClick={submitPatch} className="mt-2 rounded bg-cyan-800 px-2 py-1">submit witnessed source.patch</button>
      <p className="mt-1 text-[11px] text-neutral-400">No silent auto-correction; exact symbolic values are never replaced by display floats.</p>
    </section>
  )
}
