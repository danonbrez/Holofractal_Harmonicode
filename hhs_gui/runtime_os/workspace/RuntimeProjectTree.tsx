import React from "react"
import type { WorkspaceCommandClient } from "./WorkspaceCommandClient"
import type { WorkspaceProjectionState } from "./WorkspaceProjectionStore"

export const RuntimeProjectTree: React.FC<{ projection: WorkspaceProjectionState; commandClient: WorkspaceCommandClient; onAuthorityFeedback: (feedback: any) => void }> = ({ projection, commandClient, onAuthorityFeedback }) => {
  const createProject = async () => onAuthorityFeedback(await commandClient.submit("project.create", { name: "HHS Workspace" }))
  return (
    <nav data-testid="runtime-project-tree" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
      <div className="mb-2 flex items-center justify-between"><strong>Project Tree</strong><button onClick={createProject} className="rounded bg-cyan-800 px-2 py-1">create</button></div>
      <p className="text-[11px] text-neutral-400">No direct filesystem mutation from browser.</p>
      <ul className="mt-2 space-y-1">
        <li>PROJECT · {projection.projectId ?? "unopened"}</li>
        <li>SOURCE_DOCUMENT</li>
        <li>MULTIMODAL_OBJECT</li>
        <li>COMPILED_ARTIFACT</li>
        <li>EMULATOR_SESSION</li>
        <li>RECEIPT_CHAIN</li>
      </ul>
    </nav>
  )
}
