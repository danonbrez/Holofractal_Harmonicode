import React from "react";
export const CommonAncestorViewer: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="058" data-hhs-surface="CommonAncestorViewer">
    <h2>CommonAncestorViewer</h2><pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default CommonAncestorViewer;
