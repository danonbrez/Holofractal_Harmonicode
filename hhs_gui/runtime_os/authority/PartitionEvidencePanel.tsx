import React from "react";
export const PartitionEvidencePanel: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="PartitionEvidencePanel">
    <h2>PartitionEvidencePanel</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default PartitionEvidencePanel;
