import React from "react";
export const RevocationConsensusViewer: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="RevocationConsensusViewer">
    <h2>RevocationConsensusViewer</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default RevocationConsensusViewer;
