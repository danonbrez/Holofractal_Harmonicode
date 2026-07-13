import React from "react"

export const RuntimeCanonicalObserverPanel: React.FC = () => (
  <section data-testid="runtime-canonical-observer-panel" className="rounded-xl border border-emerald-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-emerald-200">Runtime Canonical Observer</h3>
    <p className="text-[11px] text-emerald-300">HHS_RUNTIME_CANONICAL_OBSERVER_INVARIANT_V1</p>
    <ul className="mt-1 list-disc pl-4 text-[10px] text-neutral-300">
      <li>NO_INTERFACE_IS_CANONICAL</li>
      <li>NO_PROVIDER_IS_CANONICAL</li>
      <li>NO_PROJECTION_IS_CANONICAL</li>
      <li>NO_TRANSLATION_SELF_AUTHORIZES</li>
      <li>ONLY_RUNTIME_ADMITTED_IDENTITY_MAY_ENTER_CANONICAL_RUNTIME_STATE</li>
    </ul>
  </section>
)
