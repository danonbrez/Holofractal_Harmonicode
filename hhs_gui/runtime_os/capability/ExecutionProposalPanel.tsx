import React from "react"

export const ExecutionProposalPanel: React.FC = () => (
  <section data-testid="execution-proposal-panel" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-emerald-200">Execution Proposal</h3>
    <p className="text-[11px] text-neutral-300">Provider invocation begins as HHS_PROVIDER_EXECUTION_PROPOSAL_V1.</p>
    <p className="text-[11px] text-emerald-300">successful invocation ≠ admitted mutation</p>
  </section>
)
