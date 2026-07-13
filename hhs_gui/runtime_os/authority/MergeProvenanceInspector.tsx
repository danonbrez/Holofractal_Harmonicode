import React from "react";
export const MergeProvenanceInspector: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="058" data-hhs-surface="MergeProvenanceInspector">
    <h2>MergeProvenanceInspector</h2><pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default MergeProvenanceInspector;
