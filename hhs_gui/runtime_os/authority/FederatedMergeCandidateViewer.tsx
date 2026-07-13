import React from "react";
export const FederatedMergeCandidateViewer: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="058" data-hhs-surface="FederatedMergeCandidateViewer">
    <h2>FederatedMergeCandidateViewer</h2><pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default FederatedMergeCandidateViewer;
