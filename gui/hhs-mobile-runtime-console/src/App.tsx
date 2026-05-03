import React, { useEffect, useMemo, useState } from 'react';
import PhaseRing3D from './components/PhaseRing3D';
import StatusHeader from './components/StatusHeader';
import AssistantWorkspace from './components/AssistantWorkspace';
import { loadRuntimeSnapshot, RuntimeSnapshot } from './runtimeData';
import { hhsApi } from './api/hhsApi';
import { useHHSStream } from './hooks/useHHSStream';

export type CalculatorPhaseToken = { id: string; text: string; kind: string; phaseIndex: number };

function isRuntimeSnapshot(value: any): value is RuntimeSnapshot {
  return Boolean(value?.phase && value?.operatorLoop);
}

export default function App() {
  const [snapshot, setSnapshot] = useState<RuntimeSnapshot | null>(null);
  const [activePhase, setActivePhase] = useState<number | null>(null);
  const [calculatorPhases, setCalculatorPhases] = useState<CalculatorPhaseToken[]>([]);
  const [input, setInput] = useState('');

  const stream = useHHSStream();
  const activeState = stream ?? snapshot;
  const data = isRuntimeSnapshot(activeState) ? activeState : snapshot;

  useEffect(() => {
    let mounted = true;
    loadRuntimeSnapshot().then(runtimeSnapshot => { if (mounted) setSnapshot(runtimeSnapshot); });
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (!activeState) return;

    if ((window as any).updateScene) {
      (window as any).updateScene(activeState);
    }
  }, [activeState]);

  const run = (cmd: string) => {
    switch (cmd) {
      case 'solve': return hhsApi.solve({ expression: input });
      case 'branch': return hhsApi.branch();
      case 'rejoin': return hhsApi.rejoin();
      case 'trace': return hhsApi.trace();
      case 'invariant': return hhsApi.invariants();
      case 'receipt': return hhsApi.receipt();
      case 'tensor': return hhsApi.tensor();
      case 'adaptive': return hhsApi.adaptive();
      case 'reset': return hhsApi.reset();
      default: return;
    }
  };

  const metrics = useMemo(() => {
    if (!data) return null;
    return {
      phase: data.projection?.phase_index ?? data.phase.anchor_phase_index,
      status: data.phase.status,
      proposals: data.operatorLoop.proposals?.length ?? 0
    };
  }, [data]);

  if (!data) {
    return <div className="hhs-loading">Loading HARMONICODE runtime…</div>;
  }

  return (
    <div className="hhs-shell">

      {/* CONTROL MATRIX */}
      <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 10, display: 'grid', gridTemplateColumns: 'repeat(3, auto)', gap: 6 }}>
        {[
          'solve','branch','rejoin',
          'trace','invariant','receipt',
          'tensor','adaptive','reset'
        ].map(cmd => (
          <button key={cmd} onClick={() => run(cmd)}>{cmd}</button>
        ))}
      </div>

      {/* INPUT */}
      <div style={{ position: 'absolute', bottom: 10, left: 10, zIndex: 10 }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Enter expression" />
        <button onClick={() => run('solve')}>run</button>
      </div>

      {/* LIVE PANEL */}
      <div style={{ position: 'absolute', top: 10, right: 10, width: 260, height: '40%', overflow: 'auto', border: '1px solid #00ffcc', padding: 6, zIndex: 10 }}>
        {activeState && <pre>{JSON.stringify(activeState, null, 2)}</pre>}
      </div>

      <div className="hhs-topbar">
        <StatusHeader data={data} />
      </div>

      <div className="hhs-main">
        <section className="hhs-card hhs-left-card">
          <div className="hhs-card-head">
            <div>
              <div className="hhs-eyebrow">Runtime Field</div>
              <div className="hhs-title">Live Phase Space</div>
            </div>
            <div className="hhs-metric-grid">
              <div className="hhs-metric"><div className="hhs-metric-label">Phase</div><div className="hhs-metric-value">{metrics?.phase}</div></div>
              <div className="hhs-metric"><div className="hhs-metric-label">State</div><div className="hhs-metric-value">{metrics?.status}</div></div>
              <div className="hhs-metric"><div className="hhs-metric-label">Operators</div><div className="hhs-metric-value">{metrics?.proposals}</div></div>
            </div>
          </div>

          <div className="hhs-viewport">
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
        </section>

        <section className="hhs-card hhs-right-card">
          <AssistantWorkspace
            data={data}
            activePhase={activePhase}
            onActivePhase={setActivePhase}
            onPhaseMapChange={setCalculatorPhases}
          />
        </section>
      </div>
    </div>
  );
}
