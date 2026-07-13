import React from "react"
export const WorkspaceObjectInspector: React.FC<{ projection: any }> = ({ projection }) => (
  <section data-testid="workspace-object-inspector" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
    <strong>Object Inspector</strong>
    <p className="text-[11px] text-neutral-400">canonical identity · schema · witnesses · receipts · reconstruction path</p>
    <div>selected: {projection.selectedObjectId ?? "none"}</div>
  </section>
)
