import React from 'react';
import { OperatorLoopView } from '../runtimeData';

export default function OperatorPanel({ loop }: { loop: OperatorLoopView }) {
  return (
    <div style={{ padding: 10, fontSize: 12 }}>
      <div>Status: {loop.status}</div>
      <div>External Phase: {String(loop.external_phase_anchor_used)}</div>
      <div>Selected: {loop.selected_chain_hash72}</div>
      <div style={{ marginTop: 10 }}>
        {loop.proposals.map((p, i) => (
          <div key={i} style={{ borderBottom: '1px solid #333', padding: 5 }}>
            <div>{p.agent}</div>
            <div>phase_ok: {String(p.phase_ok)}</div>
            <div>distance: {p.phase_distance_from_anchor}</div>
            <div>score: {p.local_score}</div>
            <div>risk: {p.risk_score}</div>
          </div>
        ))}
      </div>
    </div>
  );
}