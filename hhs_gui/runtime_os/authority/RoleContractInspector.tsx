import React from "react";

export type RoleContractInspectorProps = { data?: Record<string, unknown> };

export function RoleContractInspector({ data = {} }: RoleContractInspectorProps) {
  return (
    <section data-hhs-surface="PASS_054_RoleContractInspector">
      <h2>RoleContractInspector</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </section>
  );
}

export default RoleContractInspector;
