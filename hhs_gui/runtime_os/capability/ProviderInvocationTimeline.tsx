import React from "react"

export const ProviderInvocationTimeline: React.FC = () => (
  <section data-testid="provider-invocation-timeline" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-emerald-200">Provider Invocation Timeline</h3>
    <ol className="list-decimal pl-4 text-[10px] text-neutral-300">
      <li>capability resolution</li>
      <li>execution proposal</li>
      <li>policy gate</li>
      <li>provider invocation receipt</li>
      <li>provider result ingress</li>
    </ol>
  </section>
)
