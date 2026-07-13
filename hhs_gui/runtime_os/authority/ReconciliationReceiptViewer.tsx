import React from "react";
export const ReconciliationReceiptViewer: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="ReconciliationReceiptViewer">
    <h2>ReconciliationReceiptViewer</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default ReconciliationReceiptViewer;
