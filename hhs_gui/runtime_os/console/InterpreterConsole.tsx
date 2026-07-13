import React, { useState } from "react"
import type { WorkspaceCommandClient } from "../workspace/WorkspaceCommandClient"

export const InterpreterConsole: React.FC<{ commandClient: WorkspaceCommandClient; onAuthorityFeedback: (feedback: any) => void }> = ({ commandClient, onAuthorityFeedback }) => {
  const [expression, setExpression] = useState("1+2*3")
  const execute = async () => onAuthorityFeedback(await commandClient.submit("interpret.execute", { expression }))
  return (
    <section data-testid="interpreter-console" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
      <strong>Interpreter</strong>
      <input value={expression} onChange={(e) => setExpression(e.target.value)} className="mt-2 w-full rounded bg-neutral-950 p-2 font-mono" />
      <button onClick={execute} className="mt-2 rounded bg-cyan-800 px-2 py-1">authorized interpret</button>
      <p className="mt-1 text-[11px] text-neutral-400">No arbitrary host-language evaluation.</p>
    </section>
  )
}
