import React from "react"
export const WorkspaceAuthorityStatus: React.FC<{ status: string; receiptHash72?: string | null }> = ({ status, receiptHash72 }) => (
  <div data-testid="workspace-authority-status" className="rounded-xl border border-cyan-900/60 bg-cyan-950/30 px-3 py-2">
    <div>{status}</div>
    <div className="max-w-[180px] truncate text-[10px] text-cyan-300">{receiptHash72 ?? "awaiting authority"}</div>
  </div>
)
