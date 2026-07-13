import React from "react";
export const StaleLeaseQuarantineInspector: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="StaleLeaseQuarantineInspector">
    <h2>StaleLeaseQuarantineInspector</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default StaleLeaseQuarantineInspector;
