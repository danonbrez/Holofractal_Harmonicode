import React from "react"

export const OCRProjectionViewer: React.FC = () => (
  <section data-testid="ocr-projection-viewer" className="rounded-xl border border-amber-900/60 bg-neutral-950 p-2">
    <h3 className="text-xs font-semibold text-amber-200">OCR Projection Viewer</h3>
    <p className="text-[11px] text-amber-100/80">OCR_TEXT_PROJECTION is a lossy text proposal from an image region.</p>
    <code className="text-[10px] text-amber-300">OCR text ≠ page image</code>
  </section>
)
