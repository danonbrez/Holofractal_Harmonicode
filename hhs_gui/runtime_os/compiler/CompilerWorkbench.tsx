import React from "react"
import type { WorkspaceCommandClient } from "../workspace/WorkspaceCommandClient"

export const CompilerWorkbench: React.FC<{ commandClient: WorkspaceCommandClient; onAuthorityFeedback: (feedback: any) => void }> = ({ commandClient, onAuthorityFeedback }) => {
  const compile = async () => onAuthorityFeedback(await commandClient.submit("compile.execute", { source_text: "a²=1 b²=2", target: "HHS_IR" }))
  return (
    <section data-testid="compiler-workbench" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
      <strong>Compiler</strong>
      <button onClick={compile} className="mt-2 rounded bg-cyan-800 px-2 py-1">emit witnessed HHS IR</button>
      <p className="mt-1 text-[11px] text-neutral-400">Compilation does not imply execution authorization.</p>
    </section>
  )
}
