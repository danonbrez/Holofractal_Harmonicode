import React from "react";
export const RevocationEpochInspector: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="RevocationEpochInspector">
    <h2>RevocationEpochInspector</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default RevocationEpochInspector;
