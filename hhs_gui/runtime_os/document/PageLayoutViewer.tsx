import React from "react"

export const PageLayoutViewer: React.FC = () => (
  <section data-testid="page-layout-viewer" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">Page Layout Projection</h3>
    <p className="text-[11px] text-amber-100/80">PAGE_LAYOUT_PROJECTION is geometry evidence, not document identity.</p>
    <code className="text-[10px] text-amber-300">REJECT_PDF_TEXT_AS_COMPLETE_DOCUMENT</code>
  </section>
)
