import React from "react";
export const PartitionAuthorityMatrix: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="PartitionAuthorityMatrix">
    <h2>PartitionAuthorityMatrix</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default PartitionAuthorityMatrix;
