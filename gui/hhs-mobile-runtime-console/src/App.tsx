import React, { useEffect, useState } from 'react';
import PhaseRing3D from './components/PhaseRing3D';
import OperatorPanel from './components/OperatorPanel';
import { loadRuntimeSnapshot, RuntimeSnapshot } from './runtimeData';

export default function App() {
  const [data, setData] = useState<RuntimeSnapshot | null>(null);

  useEffect(() => {
    loadRuntimeSnapshot().then(setData);
  }, []);

  if (!data) return <div style={{ color: '#0f0', padding: 20 }}>Loading...</div>;

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#000', color: '#0f0', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: 10 }}>
        HHS Runtime Console · {data.phase.status}
      </div>
      <PhaseRing3D phase={data.phase} />
      <OperatorPanel loop={data.operatorLoop} />
    </div>
  );
}