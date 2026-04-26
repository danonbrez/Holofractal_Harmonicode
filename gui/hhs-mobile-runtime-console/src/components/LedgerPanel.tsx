import React from 'react';

export default function LedgerPanel() {
  const mock = new Array(6).fill(0).map((_, i) => ({
    index: i,
    hash: 'H72-RECEIPT-' + i,
    parent: i === 0 ? 'GENESIS' : 'H72-RECEIPT-' + (i - 1),
    valid: true
  }));

  return (
    <div style={{ padding: 10, fontSize: 11, borderTop: '1px solid #133' }}>
      <div style={{ marginBottom: 6 }}>Ledger Timeline</div>
      {mock.map(r => (
        <div key={r.hash} style={{ padding: 4, borderBottom: '1px solid #222' }}>
          <div>{r.index} · {r.valid ? 'valid' : 'invalid'}</div>
          <div style={{ opacity: 0.7 }}>{r.hash}</div>
        </div>
      ))}
    </div>
  );
}
