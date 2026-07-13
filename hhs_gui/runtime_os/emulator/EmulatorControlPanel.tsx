import React, { useState } from "react"
import type { WorkspaceCommandClient } from "../workspace/WorkspaceCommandClient"

export const EmulatorControlPanel: React.FC<{ commandClient: WorkspaceCommandClient; onAuthorityFeedback: (feedback: any) => void }> = ({ commandClient, onAuthorityFeedback }) => {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const create = async () => {
    const feedback = await commandClient.submit("emulator.create", { program_artifact_id: "artifact:hhs-ir" })
    setSessionId(feedback?.result?.session?.session_id ?? null)
    onAuthorityFeedback(feedback)
  }
  const step = async () => onAuthorityFeedback(await commandClient.submit("emulator.step", { session_id: sessionId }))
  return (
    <section data-testid="emulator-control-panel" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
      <strong>Emulator</strong>
      <div className="mt-2 flex gap-2"><button onClick={create} className="rounded bg-cyan-800 px-2 py-1">create</button><button onClick={step} className="rounded bg-cyan-800 px-2 py-1">step</button></div>
      <p className="mt-1 text-[11px] text-neutral-400">Step/run/pause/replay use the same authority path; rewind never erases history.</p>
    </section>
  )
}
