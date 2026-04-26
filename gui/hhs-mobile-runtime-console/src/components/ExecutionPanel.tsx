import React from 'react';

export default function ExecutionPanel() {
  return (
    <div style={{ padding: 10, fontSize: 11, borderTop: '1px solid #133' }}>
      <div>Execution Trace</div>
      <div style={{ marginTop: 6 }}>
        <div>input → operator chain → output</div>
        <div style={{ opacity: 0.7 }}>HHS alignment axiom → style → process</div>
      </div>
    </div>
  );
}
