import React from "react"
export const ReceiptLedgerInspector: React.FC<{ projection: any }> = ({ projection }) => (
  <section data-testid="receipt-ledger-inspector" className="rounded-xl border border-neutral-800 bg-neutral-900/80 p-3">
    <strong>Receipt / Ledger</strong>
    <p className="break-all text-[11px] text-neutral-400">tip: {projection.lastReceiptHash72 ?? "no receipt yet"}</p>
  </section>
)
