import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { PhaseLockView, PhaseWitnessView, RuntimeAnomalies, OperatorLoopView, ProjectionView } from '../runtimeData';

const RING = 72;
const MAJOR_SEGMENTS = 9;
const MINOR_SEGMENTS = 8;
const TORUS_R = 2.15;
const TORUS_r = 0.55;
const MAX_BRANCHES = 8;
const PRUNE_THRESHOLD = 18;

type Branch = {
  id: string;
  phases: number[];
  kind: 'drift' | 'correction';
  driftScore: number;
  degreesOfFreedomScore: number;
  emergenceScore: number;
};

type BranchMemory = Branch & {
  age: number;
  survivalScore: number;
  wins: number;
  pruned?: boolean;
};

function mod72(n: number): number { return ((Math.round(n) % RING) + RING) % RING; }
function circularDistance(a: number, b: number): number { const d = Math.abs(mod72(a) - mod72(b)); return Math.min(d, RING - d); }
function branchSignature(branch: Branch): string { return `${branch.kind}:${branch.phases.join('-')}`; }

function phaseToPoint(phaseIndex: number): [number, number, number] {
  const p = mod72(phaseIndex);
  const major = ((p % MAJOR_SEGMENTS) / MAJOR_SEGMENTS) * Math.PI * 2;
  const minor = (Math.floor(p / MAJOR_SEGMENTS) / MINOR_SEGMENTS) * Math.PI * 2;
  return [(TORUS_R + TORUS_r * Math.cos(minor)) * Math.cos(major), (TORUS_R + TORUS_r * Math.cos(minor)) * Math.sin(major), TORUS_r * Math.sin(minor)];
}

function PhaseLine({ phases, color, opacity = 1 }: { phases: number[]; color: string; opacity?: number }) {
  const geometry = useMemo(() => new THREE.BufferGeometry().setFromPoints(phases.map((p) => new THREE.Vector3(...phaseToPoint(p)))), [phases.join(',')]);
  if (phases.length < 2) return null;
  return <line geometry={geometry}><lineBasicMaterial color={color} transparent opacity={opacity} /></line>;
}

function TorusBody({ phaseIndex, anomalyStatus }: { phaseIndex: number; anomalyStatus?: string }) {
  const ref = useRef<any>();
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const p = mod72(phaseIndex);
    ref.current.rotation.y = ((p % MAJOR_SEGMENTS) / MAJOR_SEGMENTS) * Math.PI * 2;
    ref.current.rotation.x = (Math.floor(p / MAJOR_SEGMENTS) / MINOR_SEGMENTS) * Math.PI * 2 + Math.sin(clock.getElapsedTime() * 0.5) * 0.03;
  });
  const color = anomalyStatus === 'CRITICAL' ? '#ff0040' : anomalyStatus === 'WARN' ? '#ffaa00' : '#00f0ff';
  return <mesh ref={ref}><torusGeometry args={[TORUS_R, TORUS_r, 32, 144]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.25} wireframe /></mesh>;
}

function PhaseMarker({ index, color, scale = 1, pulse = false, onClick }: { index: number; color: string; scale?: number; pulse?: boolean; onClick?: () => void }) {
  const ref = useRef<any>();
  const pos = phaseToPoint(index);
  useFrame(({ clock }) => { if (!ref.current) return; const s = pulse ? scale * (1 + Math.sin(clock.getElapsedTime() * 7) * 0.35) : scale; ref.current.scale.set(s, s, s); });
  return <mesh ref={ref} position={pos} onClick={onClick}><sphereGeometry args={[0.075, 16, 16]} /><meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} /></mesh>;
}

function buildPredictionBranches(anchor: number, anomalies?: RuntimeAnomalies): Branch[] {
  const drift = anomalies?.drift_prediction;
  const risk = Number(drift?.risk ?? 0);
  if (risk < 20) return [];
  const maxDist = Math.max(1, Number(drift?.max_phase_distance ?? Math.ceil(risk / 25)));
  const affected = (drift?.affected_phase_indices ?? anomalies?.alerts?.flatMap((a: any) => a.affected_phase_indices ?? []) ?? []) as number[];
  const primaryDirection = affected.length ? (mod72(affected[0]) >= mod72(anchor) ? 1 : -1) : 1;
  const steps = risk >= 75 ? 8 : risk >= 45 ? 6 : 4;
  const candidates = [primaryDirection, -primaryDirection, primaryDirection * 2, -primaryDirection * 2, primaryDirection * 3, -primaryDirection * 3];
  return candidates.map((dir, i) => {
    const stride = Math.max(1, Math.min(9, maxDist + i));
    const phases = [anchor, ...new Array(steps).fill(0).map((_, k) => mod72(anchor + dir * stride * (k + 1)))];
    const endDist = circularDistance(anchor, phases[phases.length - 1]);
    const dof = new Set(phases.map((p) => `${p % 9}:${Math.floor(p / 9)}`)).size;
    const driftScore = Math.max(0, 100 - endDist * 10 - risk * 0.4);
    const degreesOfFreedomScore = Math.min(100, dof * 12);
    const emergenceScore = Math.round(driftScore * 0.45 + degreesOfFreedomScore * 0.55);
    return { id: `drift-${i}`, phases, kind: 'drift', driftScore, degreesOfFreedomScore, emergenceScore };
  });
}

function buildCorrectionBranches(anchor: number, anomalies?: RuntimeAnomalies, corrections?: any): Branch[] {
  const affected = anomalies?.alerts?.flatMap((a: any) => a.affected_phase_indices ?? []) ?? [];
  const suggestions = corrections?.suggestions ?? [];
  if (!affected.length || !suggestions.length) return [];
  return suggestions.slice(0, 6).map((s: any, i: number) => {
    const start = mod72(Number(affected[i % affected.length]));
    const pivotA = mod72(Math.round((start * 2 + anchor) / 3) + i);
    const pivotB = mod72(Math.round((start + anchor * 2) / 3) - i);
    const phases = [start, pivotA, pivotB, anchor];
    const terminalDrift = circularDistance(anchor, phases[phases.length - 1]);
    const dof = new Set(phases.map((p) => `${p % 9}:${Math.floor(p / 9)}`)).size + (s.target_modalities?.length ?? 0);
    const priority = Number(s.priority ?? 0);
    const driftScore = Math.max(0, 100 - terminalDrift * 12 + priority * 0.2);
    const degreesOfFreedomScore = Math.min(100, dof * 14);
    const emergenceScore = Math.round(driftScore * 0.55 + degreesOfFreedomScore * 0.45);
    return { id: s.suggestion_hash72 ?? `correction-${i}`, phases, kind: 'correction', driftScore, degreesOfFreedomScore, emergenceScore };
  });
}

function competeAndPrune(prev: BranchMemory[], incoming: Branch[]): BranchMemory[] {
  const map = new Map<string, BranchMemory>();
  for (const old of prev) {
    const decayed = Math.max(0, old.survivalScore * 0.88 - old.age * 0.4);
    map.set(branchSignature(old), { ...old, age: old.age + 1, survivalScore: decayed });
  }
  for (const branch of incoming) {
    const sig = branchSignature(branch);
    const existing = map.get(sig);
    const novelty = new Set(branch.phases).size * 2;
    const correctionBonus = branch.kind === 'correction' ? 18 : 0;
    const survival = branch.emergenceScore + novelty + correctionBonus;
    if (existing) {
      map.set(sig, { ...branch, age: 0, wins: existing.wins + (survival > existing.survivalScore ? 1 : 0), survivalScore: Math.max(existing.survivalScore * 0.72 + survival * 0.45, survival) });
    } else {
      map.set(sig, { ...branch, age: 0, wins: 0, survivalScore: survival });
    }
  }
  return [...map.values()]
    .map((b) => ({ ...b, pruned: b.survivalScore < PRUNE_THRESHOLD }))
    .filter((b) => !b.pruned)
    .sort((a, b) => b.survivalScore - a.survivalScore)
    .slice(0, MAX_BRANCHES);
}

export default function PhaseRing3D({ phase, anomalies, projection, loop, corrections }: { phase: PhaseLockView; anomalies?: RuntimeAnomalies; projection?: ProjectionView; loop?: OperatorLoopView; corrections?: any }) {
  const [selected, setSelected] = useState<{ index: number; witnesses: PhaseWitnessView[] } | null>(null);
  const phaseIndex = projection?.phase_index ?? phase.anchor_phase_index ?? 0;
  const [history, setHistory] = useState<number[]>([phaseIndex]);
  const [branchFrontier, setBranchFrontier] = useState<BranchMemory[]>([]);

  const affected = new Set((anomalies?.alerts ?? []).flatMap((a: any) => a.affected_phase_indices ?? []));
  const incomingBranches = useMemo(() => [...buildPredictionBranches(phaseIndex, anomalies), ...buildCorrectionBranches(phaseIndex, anomalies, corrections)], [phaseIndex, anomalies?.summary_hash72, corrections?.summary_hash72]);

  useEffect(() => {
    setHistory((prev) => {
      const next = prev[prev.length - 1] === phaseIndex ? prev : [...prev, phaseIndex];
      return next.slice(-64);
    });
  }, [phaseIndex]);

  useEffect(() => {
    setBranchFrontier((prev) => competeAndPrune(prev, incomingBranches));
  }, [incomingBranches.map((b) => b.id + b.emergenceScore).join('|')]);

  const bestBranch = branchFrontier[0];
  const bestCorrection = branchFrontier.find((b) => b.kind === 'correction');

  return (
    <div style={{ height: '44vh', position: 'relative' }}>
      <Canvas camera={{ position: [0, -0.2, 5.4] }}>
        <ambientLight intensity={0.8} />
        <pointLight position={[3, 3, 4]} intensity={1.2} />
        <TorusBody phaseIndex={phaseIndex} anomalyStatus={anomalies?.status} />
        <PhaseLine phases={history} color="#00ffff" opacity={0.9} />
        {branchFrontier.map((b, i) => {
          const isBest = b.id === bestBranch?.id;
          const color = b.kind === 'correction' ? '#00ff88' : '#ffaa00';
          const opacity = isBest ? 0.95 : Math.max(0.15, Math.min(0.62, b.survivalScore / 160));
          return <PhaseLine key={b.id} phases={b.phases} color={color} opacity={opacity} />;
        })}
        <PhaseMarker index={phaseIndex} color="#00ff88" scale={1.4} pulse />
        {phase.witnesses.map((w) => <PhaseMarker key={w.witness_hash72} index={w.phase_index} color={affected.has(w.phase_index) ? '#ff0040' : '#ffff00'} scale={0.85} pulse={affected.has(w.phase_index)} onClick={() => setSelected({ index: w.phase_index, witnesses: phase.witnesses.filter((x) => x.phase_index === w.phase_index) })} />)}
        {(loop?.proposals ?? []).map((p, i) => <PhaseMarker key={`${p.proposal_hash72}-${i}`} index={mod72(phaseIndex + Number(p.phase_distance_from_anchor ?? 0))} color={p.phase_ok ? '#55aaff' : '#ff0040'} scale={0.65} pulse={!p.phase_ok} />)}
        {branchFrontier.flatMap((b) => b.phases.slice(1).map((p, i) => <PhaseMarker key={`${b.id}-${i}`} index={p} color={b.kind === 'correction' ? '#00ff88' : '#ffaa00'} scale={b.id === bestBranch?.id ? 0.46 : 0.28} pulse={b.id === bestBranch?.id && i === b.phases.length - 2} />))}
      </Canvas>
      <div style={{ position: 'absolute', top: 8, left: 10, right: 10, display: 'flex', justifyContent: 'space-between', fontSize: 11, pointerEvents: 'none' }}>
        <span>phase {phaseIndex}/72 · {projection?.target_layer ?? 'runtime'}</span>
        <span>frontier {branchFrontier.length}/{MAX_BRANCHES} · winner {bestBranch?.survivalScore.toFixed(1) ?? 0}</span>
      </div>
      {bestBranch && (
        <div style={{ position: 'absolute', bottom: selected ? 86 : 10, left: 10, right: 10, background: bestBranch.kind === 'correction' ? '#06120b' : '#201400', color: bestBranch.kind === 'correction' ? '#8cffb0' : '#ffd27a', padding: 8, fontSize: 11, border: `1px solid ${bestBranch.kind === 'correction' ? '#0f6' : '#fa0'}` }}>
          DOMINANT BRANCH · {bestBranch.kind.toUpperCase()} · survival={bestBranch.survivalScore.toFixed(1)} · emergence={bestBranch.emergenceScore} · drift={Math.round(bestBranch.driftScore)} · dof={Math.round(bestBranch.degreesOfFreedomScore)} · wins={bestBranch.wins}
          {bestCorrection && bestCorrection.id !== bestBranch.id ? <div>BEST CORRECTION · survival={bestCorrection.survivalScore.toFixed(1)} · emergence={bestCorrection.emergenceScore}</div> : null}
        </div>
      )}
      {selected && (
        <div style={{ position: 'absolute', bottom: 10, left: 10, right: 10, background: '#111', padding: 10, fontSize: 12 }}>
          <div>Phase: {selected.index}</div>
          {selected.witnesses.map((w) => <div key={w.witness_hash72}>{w.modality} · {w.temporal_status}</div>)}
        </div>
      )}
    </div>
  );
}
