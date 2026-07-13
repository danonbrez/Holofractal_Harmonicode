import React from "react"
export const MutationHistoryPanel: React.FC<{ history: unknown[] }> = ({ history }) => (
  <section data-testid="mutation-history-panel" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
    <strong>Mutation / Command History</strong>
    <p className="text-[11px] text-neutral-400">bounded UI history · canonical chain resolves by receipts</p>
    <div>{history.length} records</div>
  </section>
)
