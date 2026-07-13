import React from "react";
export const StaleRemoteResultViewer: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="057" data-hhs-surface="StaleRemoteResultViewer">
    <h2>StaleRemoteResultViewer</h2>
    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default StaleRemoteResultViewer;
