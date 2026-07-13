import React from "react";
export const FederatedRecoveryPanel: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="FederatedRecoveryPanel">
    <h2>FederatedRecoveryPanel</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default FederatedRecoveryPanel;
