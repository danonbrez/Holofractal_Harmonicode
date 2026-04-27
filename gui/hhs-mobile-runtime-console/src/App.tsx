import React, { useEffect, useState } from 'react';
import PhaseRing3D from './components/PhaseRing3D';
import OperatorPanel from './components/OperatorPanel';
import StatusHeader from './components/StatusHeader';
import LedgerPanel from './components/LedgerPanel';
import ExecutionPanel from './components/ExecutionPanel';
import CertificationPanel from './components/CertificationPanel';
import AlertPanel, { AlertBanner } from './components/AlertPanel';
import CalculatorPanel from './components/CalculatorPanel';
import { loadRuntimeSnapshot, RuntimeSnapshot, connectRuntimeStream } from './runtimeData';

export default function App() {
  const [data, setData] = useState<RuntimeSnapshot | null>(null);

  useEffect(() => {
    let mounted = true;

    loadRuntimeSnapshot().then(snapshot => {
      if (mounted) setData(snapshot);
    });

    const disconnect = connectRuntimeStream((snapshot) => {
      setData(snapshot);
    });

    return () => {
      mounted = false;
      disconnect();
    };
  }, []);

  if (!data) return <div style={{ color: '#0f0', padding: 20 }}>Loading...</div>;

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#000', color: '#0f0', display: 'flex', flexDirection: 'column' }}>
      <StatusHeader data={data} />
      <AlertBanner anomalies={data.anomalies} />
      <PhaseRing3D phase={data.phase} anomalies={data.anomalies} />
      <OperatorPanel loop={data.operatorLoop} />
      <AlertPanel anomalies={data.anomalies} />
      <CalculatorPanel equationManifest={(data as any).equationManifest} />
      <ExecutionPanel />
      <LedgerPanel />
      <CertificationPanel />
    </div>
  );
}
