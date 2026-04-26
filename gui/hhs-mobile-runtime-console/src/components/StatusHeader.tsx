import React from 'react';
import { RuntimeSnapshot } from '../runtimeData';

function Flag({ label, ok }: { label: string; ok: boolean }) {
  return (
    <span style={{ padding: '4px 8px', borderRadius: 999, background: ok ? '#073' : '#520', color: ok ? '#9f9' : '#f99', fontSize: 11 }}>
      {label}
    </span>
  );
}

function StreamIndicator({ data }: { data: RuntimeSnapshot }) {
  const source = data.stream?.source ?? 'mock';
  const connected = Boolean(data.stream?.connected);
  const color = connected ? '#4f4' : source === 'rest' ? '#ff4' : '#f66';
  const label = connected ? 'LIVE' : source.toUpperCase();
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color }}>
      <span style={{ width: 9, height: 9, borderRadius: 99, background: color, boxShadow: `0 0 10px ${color}` }} />
      {label}
    </div>
  );
}

export default function StatusHeader({ data }: { data: RuntimeSnapshot }) {
  const locked = data.phase.status === 'LOCKED';
  const loopOk = data.operatorLoop.status === 'EXECUTED';
  return (
    <div style={{ padding: 10, borderBottom: '1px solid #143', background: '#020802' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'center' }}>
        <div>
          <div style={{ fontWeight: 700 }}>HHS Runtime Console</div>
          <div style={{ fontSize: 11, opacity: 0.8 }}>receipt: {data.phase.receipt_hash72 || 'pending'}</div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
          <div style={{ fontSize: 12, color: locked && loopOk ? '#9f9' : '#ff9' }}>{locked && loopOk ? 'LOCKED' : data.phase.status}</div>
          <StreamIndicator data={data} />
        </div>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
        <Flag label="Δe=0" ok={locked} />
        <Flag label="Ψ=0" ok={locked && loopOk} />
        <Flag label="Θ15" ok={true} />
        <Flag label="Ω" ok={data.phase.phase_locked && data.phase.temporal_ok} />
        <Flag label="Replay" ok={true} />
        <Flag label="External Phase" ok={data.operatorLoop.external_phase_anchor_used} />
      </div>
    </div>
  );
}
