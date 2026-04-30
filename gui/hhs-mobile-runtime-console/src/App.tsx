import React, { useEffect, useMemo, useState } from 'react';
import PhaseRing3D from './components/PhaseRing3D';
import StatusHeader from './components/StatusHeader';
import AssistantWorkspace from './components/AssistantWorkspace';
import { loadRuntimeSnapshot, RuntimeSnapshot, connectRuntimeStream } from './runtimeData';

export type CalculatorPhaseToken = { id: string; text: string; kind: string; phaseIndex: number };

export default function App() {
  const [data, setData] = useState<RuntimeSnapshot | null>(null);
  const [activePhase, setActivePhase] = useState<number | null>(null);
  const [calculatorPhases, setCalculatorPhases] = useState<CalculatorPhaseToken[]>([]);

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
      proposals: data.operatorLoop.proposals?.length ?? 0
    };
  }, [data]);

  if (!data) {
    return <div className="hhs-loading">Loading HARMONICODE runtime…</div>;
  }

  return (
    <div className="hhs-shell">
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
