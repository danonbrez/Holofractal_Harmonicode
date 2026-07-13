import React from "react";
export const ConflictPreservingMergePanel: React.FC<{ data?: unknown }> = ({ data }) => (
  <section data-hhs-pass="058" data-hhs-surface="ConflictPreservingMergePanel">
    <h2>ConflictPreservingMergePanel</h2><pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
  </section>
);
export default ConflictPreservingMergePanel;
