import React, { useEffect, useMemo, useState } from 'react';
import PhaseRing3D from './components/PhaseRing3D';
import OperatorPanel from './components/OperatorPanel';
import StatusHeader from './components/StatusHeader';
import LedgerPanel from './components/LedgerPanel';
import ExecutionPanel from './components/ExecutionPanel';
import CertificationPanel from './components/CertificationPanel';
import AlertPanel, { AlertBanner } from './components/AlertPanel';
import CalculatorPanelV2 from './components/CalculatorPanelV2';
import { loadRuntimeSnapshot, RuntimeSnapshot, connectRuntimeStream } from './runtimeData';

export type CalculatorPhaseToken = { id: string; text: string; kind: string; phaseIndex: number };

type TabKey = 'operator' | 'calculator' | 'execution' | 'ledger' | 'certification' | 'diagnostics';

const shell: React.CSSProperties = {
  width: '100vw',
  height: '100vh',
  background: 'radial-gradient(circle at 20% 0%, #102334 0%, #061018 32%, #020406 100%)',
  color: '#d9fbff',
  display: 'grid',
  gridTemplateRows: 'auto 1fr',
  overflow: 'hidden',
  fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
};

const mainGrid: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'minmax(440px, 1.1fr) minmax(460px, 0.9fr)',
  gap: 14,
  padding: 14,
  minHeight: 0
};

const glass: React.CSSProperties = {
  background: 'linear-gradient(180deg, rgba(14,28,39,.92), rgba(4,9,14,.96))',
  border: '1px solid rgba(111,235,255,.22)',
  boxShadow: '0 18px 50px rgba(0,0,0,.45), inset 0 0 30px rgba(0,255,255,.03)',
  borderRadius: 18,
  overflow: 'hidden'
};

const tabStyle = (active: boolean): React.CSSProperties => ({
  border: active ? '1px solid rgba(122,255,229,.8)' : '1px solid rgba(122,255,229,.16)',
  color: active ? '#081014' : '#b9f8ff',
  background: active ? 'linear-gradient(90deg,#7affd8,#8fd7ff)' : 'rgba(255,255,255,.045)',
  borderRadius: 999,
  padding: '8px 12px',
  fontSize: 12,
  fontWeight: 700,
  letterSpacing: '.04em',
  cursor: 'pointer'
});

function Metric({ label, value }: { label: string; value: React.ReactNode }) {
  return <div style={{ ...glass, padding: '10px 12px', borderRadius: 14 }}><div style={{ fontSize: 10, opacity: .58, textTransform: 'uppercase', letterSpacing: '.12em' }}>{label}</div><div style={{ fontSize: 17, fontWeight: 800 }}>{value}</div></div>;
}

export default function App() {
  const [data, setData] = useState<RuntimeSnapshot | null>(null);
  const [activePhase, setActivePhase] = useState<number | null>(null);
  const [calculatorPhases, setCalculatorPhases] = useState<CalculatorPhaseToken[]>([]);
  const [activeTab, setActiveTab] = useState<TabKey>('operator');

  useEffect(() => {
    let mounted = true;
    loadRuntimeSnapshot().then(snapshot => { if (mounted) setData(snapshot); });
    const disconnect = connectRuntimeStream((snapshot) => setData(snapshot));
    return () => { mounted = false; disconnect(); };
  }, []);

  const metrics = useMemo(() => {
    if (!data) return null;
    return {
      phase: data.projection?.phase_index ?? data.phase.anchor_phase_index,
      status: data.phase.status,
      proposals: data.operatorLoop.proposals?.length ?? 0,
      shells: data.temporalShells?.total_steps ?? 0,
      artifacts: data.transpileReceipt?.artifacts?.length ?? 0,
      stream: data.stream?.connected ? 'LIVE' : (data.stream?.source ?? 'REST').toUpperCase()
    };
  }, [data]);

  if (!data) {
    return <div style={{ ...shell, display: 'grid', placeItems: 'center', color: '#7affd8' }}><div>Loading HARMONICODE runtime…</div></div>;
  }

  const tabs: [TabKey, string][] = [
    ['operator', 'Operators'],
    ['calculator', 'Compiler / Calculator'],
    ['execution', 'Execution'],
    ['ledger', 'Ledger'],
    ['certification', 'Certification'],
    ['diagnostics', 'Diagnostics']
  ];

  return (
    <div style={shell}>
      <div style={{ borderBottom: '1px solid rgba(122,255,229,.15)', background: 'rgba(0,0,0,.35)' }}>
        <StatusHeader data={data} />
        <AlertBanner anomalies={data.anomalies} />
      </div>

      <div style={mainGrid}>
        <section style={{ ...glass, display: 'grid', gridTemplateRows: 'auto 1fr auto', minHeight: 0 }}>
          <div style={{ padding: '14px 16px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
            <div>
              <div style={{ fontSize: 11, color: '#7affd8', letterSpacing: '.18em', textTransform: 'uppercase' }}>Holofractal Runtime Manifold</div>
              <div style={{ fontSize: 26, fontWeight: 900 }}>Phase / Torus / Branch Console</div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(70px, 1fr))', gap: 8 }}>
              <Metric label="Phase" value={metrics?.phase} />
              <Metric label="Stream" value={metrics?.stream} />
              <Metric label="State" value={metrics?.status} />
            </div>
          </div>

          <div style={{ minHeight: 0, padding: 10 }}>
            <PhaseRing3D
              phase={data.phase}
              anomalies={data.anomalies}
              projection={data.projection}
              loop={data.operatorLoop}
              corrections={data.corrections}
              activePhase={activePhase}
              onPhaseSelect={setActivePhase}
              calculatorPhases={calculatorPhases}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, padding: '0 14px 14px' }}>
            <Metric label="Operators" value={metrics?.proposals} />
            <Metric label="Shell Steps" value={metrics?.shells} />
            <Metric label="Artifacts" value={metrics?.artifacts} />
            <Metric label="Manifest" value={data.equationManifest?.status ?? 'NONE'} />
          </div>
        </section>

        <section style={{ ...glass, display: 'grid', gridTemplateRows: 'auto 1fr', minHeight: 0 }}>
          <div style={{ padding: 14, display: 'flex', flexWrap: 'wrap', gap: 8, borderBottom: '1px solid rgba(122,255,229,.12)' }}>
            {tabs.map(([key, label]) => <button key={key} style={tabStyle(activeTab === key)} onClick={() => setActiveTab(key)}>{label}</button>)}
          </div>
          <div style={{ overflow: 'auto', padding: 14, minHeight: 0 }}>
            {activeTab === 'operator' && <OperatorPanel loop={data.operatorLoop} />}
            {activeTab === 'calculator' && <CalculatorPanelV2 equationManifest={data.equationManifest} transpileReceipt={data.transpileReceipt} activePhase={activePhase} onActivePhase={setActivePhase} onPhaseMapChange={setCalculatorPhases} />}
            {activeTab === 'execution' && <ExecutionPanel />}
            {activeTab === 'ledger' && <LedgerPanel />}
            {activeTab === 'certification' && <CertificationPanel />}
            {activeTab === 'diagnostics' && <AlertPanel anomalies={data.anomalies} />}
          </div>
        </section>
      </div>
    </div>
  );
}
