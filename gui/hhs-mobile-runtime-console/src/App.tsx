import React, { useEffect, useState } from 'react';
import PhaseRing3D from './components/PhaseRing3D';
import OperatorPanel from './components/OperatorPanel';
import StatusHeader from './components/StatusHeader';
import LedgerPanel from './components/LedgerPanel';
import ExecutionPanel from './components/ExecutionPanel';
import CertificationPanel from './components/CertificationPanel';
import { loadRuntimeSnapshot, RuntimeSnapshot } from './runtimeData';

export default function App() {
  const [data, setData] = useState<RuntimeSnapshot | null>(null);

  useEffect(() => {
    loadRuntimeSnapshot().then(setData);
  }, []);

  if (!data) return <div style={{ color: '#0f0', padding: 20 }}>Loading...</div>;

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#000', color: '#0f0', display: 'flex', flexDirection: 'column' }}>
      <StatusHeader data={data} />
      <PhaseRing3D phase={data.phase} />
      <OperatorPanel loop={data.operatorLoop} />
      <ExecutionPanel />
      <LedgerPanel />
      <CertificationPanel />
    </div>
  );
}