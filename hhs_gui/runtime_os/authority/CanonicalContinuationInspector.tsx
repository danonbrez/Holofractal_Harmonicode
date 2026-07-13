import React from "react";

export type CanonicalContinuationInspectorProps = { data?: Record<string, unknown> };

export function CanonicalContinuationInspector({ data = {} }: CanonicalContinuationInspectorProps) {
  return (
    <section data-hhs-surface="PASS_054_CanonicalContinuationInspector">
      <h2>CanonicalContinuationInspector</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </section>
  );
}

export default CanonicalContinuationInspector;
