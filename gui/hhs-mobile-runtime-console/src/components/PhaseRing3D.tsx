import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { PhaseLockView, PhaseWitnessView, RuntimeAnomalies, OperatorLoopView, ProjectionView } from '../runtimeData';

const RING = 72;
const MAJOR_SEGMENTS = 9;
const MINOR_SEGMENTS = 8;
const TORUS_R = 2.15;
const TORUS_r = 0.55;

function phaseToPoint(phaseIndex: number): [number, number, number] {
  const p = ((Math.round(phaseIndex) % RING) + RING) % RING;
  const major = ((p % MAJOR_SEGMENTS) / MAJOR_SEGMENTS) * Math.PI * 2;
  const minor = (Math.floor(p / MAJOR_SEGMENTS) / MINOR_SEGMENTS) * Math.PI * 2;
  const x = (TORUS_R + TORUS_r * Math.cos(minor)) * Math.cos(major);
  const y = (TORUS_R + TORUS_r * Math.cos(minor)) * Math.sin(major);
  const z = TORUS_r * Math.sin(minor);
  return [x, y, z];
}

function PhaseLine({ phases, color, opacity = 1 }: { phases: number[]; color: string; opacity?: number }) {
  const geometry = useMemo(() => {
    const points = phases.map((p) => new THREE.Vector3(...phaseToPoint(p)));
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [phases.join(',')]);
  if (phases.length < 2) return null;
  return (
    <line geometry={geometry}>
      <lineBasicMaterial color={color} transparent opacity={opacity} />
    </line>
  );
}

function TorusBody({ phaseIndex, anomalyStatus }: { phaseIndex: number; anomalyStatus?: string }) {
  const ref = useRef<any>();
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const p = ((phaseIndex % RING) + RING) % RING;
    const major = ((p % MAJOR_SEGMENTS) / MAJOR_SEGMENTS) * Math.PI * 2;
    const minor = (Math.floor(p / MAJOR_SEGMENTS) / MINOR_SEGMENTS) * Math.PI * 2;
    const t = clock.getElapsedTime();
    ref.current.rotation.y = major;
    ref.current.rotation.x = minor + Math.sin(t * 0.5) * 0.03;
  });
  const color = anomalyStatus === 'CRITICAL' ? '#ff0040' : anomalyStatus === 'WARN' ? '#ffaa00' : '#00f0ff';
  return (
    <mesh ref={ref}>
      <torusGeometry args={[TORUS_R, TORUS_r, 32, 144]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.25} wireframe />
    </mesh>
  );
}

function PhaseMarker({ index, color, scale = 1, pulse = false, onClick }: { index: number; color: string; scale?: number; pulse?: boolean; onClick?: () => void }) {
  const ref = useRef<any>();
  const pos = phaseToPoint(index);
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const s = pulse ? scale * (1 + Math.sin(clock.getElapsedTime() * 7) * 0.35) : scale;
    ref.current.scale.set(s, s, s);
  });
  return (
    <mesh ref={ref} position={pos} onClick={onClick}>
      <sphereGeometry args={[0.075, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.9} />
    </mesh>
  );
}

function predictedTrajectory(anchor: number, anomalies?: RuntimeAnomalies): number[] {
  const drift = anomalies?.drift_prediction;
  const risk = Number(drift?.risk ?? 0);
  const maxDist = Number(drift?.max_phase_distance ?? 0);
  const direction = (drift?.affected_phase_indices?.[0] ?? anchor) >= anchor ? 1 : -1;
  const steps = risk >= 75 ? 8 : risk >= 45 ? 6 : risk >= 20 ? 4 : 0;
  const stride = Math.max(1, maxDist || Math.ceil(risk / 25));
  return new Array(steps).fill(0).map((_, i) => (anchor + direction * stride * (i + 1) + RING) % RING);
}

function correctionSimulationPath(anchor: number, anomalies?: RuntimeAnomalies, corrections?: any): number[] {
  const affected = anomalies?.alerts?.flatMap((a: any) => a.affected_phase_indices ?? []) ?? [];
  const suggestions = corrections?.suggestions ?? [];
  if (!affected.length || !suggestions.length) return [];
  const start = Number(affected[0]);
  const mid = Math.round((start + anchor) / 2) % RING;
  return [start, mid, anchor];
}

export default function PhaseRing3D({ phase, anomalies, projection, loop, corrections }: { phase: PhaseLockView; anomalies?: RuntimeAnomalies; projection?: ProjectionView; loop?: OperatorLoopView; corrections?: any }) {
  const [selected, setSelected] = useState<{ index: number; witnesses: PhaseWitnessView[] } | null>(null);
  const phaseIndex = projection?.phase_index ?? phase.anchor_phase_index ?? 0;
  const [history, setHistory] = useState<number[]>([phaseIndex]);

  useEffect(() => {
    setHistory((prev) => {
      const next = prev[prev.length - 1] === phaseIndex ? prev : [...prev, phaseIndex];
      return next.slice(-64);
    });
  }, [phaseIndex]);

  const affected = new Set((anomalies?.alerts ?? []).flatMap((a: any) => a.affected_phase_indices ?? []));
  const forecast = predictedTrajectory(phaseIndex, anomalies);
  const correctionPath = correctionSimulationPath(phaseIndex, anomalies, corrections);

  return (
    <div style={{ height: '44vh', position: 'relative' }}>
      <Canvas camera={{ position: [0, -0.2, 5.4] }}>
        <ambientLight intensity={0.8} />
        <pointLight position={[3, 3, 4]} intensity={1.2} />
        <TorusBody phaseIndex={phaseIndex} anomalyStatus={anomalies?.status} />
        <PhaseLine phases={history} color="#00ffff" opacity={0.9} />
        <PhaseLine phases={[phaseIndex, ...forecast]} color="#ffaa00" opacity={0.65} />
        <PhaseLine phases={correctionPath} color="#00ff88" opacity={0.8} />
        <PhaseMarker index={phaseIndex} color="#00ff88" scale={1.4} pulse />
        {phase.witnesses.map((w) => (
          <PhaseMarker key={w.witness_hash72} index={w.phase_index} color={affected.has(w.phase_index) ? '#ff0040' : '#ffff00'} scale={0.85} pulse={affected.has(w.phase_index)} onClick={() => setSelected({ index: w.phase_index, witnesses: phase.witnesses.filter((x) => x.phase_index === w.phase_index) })} />
        ))}
        {(loop?.proposals ?? []).map((p, i) => {
          const agentPhase = (phaseIndex + Number(p.phase_distance_from_anchor ?? 0) + RING) % RING;
          return <PhaseMarker key={`${p.proposal_hash72}-${i}`} index={agentPhase} color={p.phase_ok ? '#55aaff' : '#ff0040'} scale={0.65} pulse={!p.phase_ok} />;
        })}
        {forecast.map((p, i) => <PhaseMarker key={`forecast-${i}`} index={p} color="#ffaa00" scale={0.45} pulse={i === forecast.length - 1} />)}
        {correctionPath.map((p, i) => <PhaseMarker key={`correction-${i}`} index={p} color="#00ff88" scale={0.5} pulse={i === correctionPath.length - 1} />)}
      </Canvas>
      <div style={{ position: 'absolute', top: 8, left: 10, right: 10, display: 'flex', justifyContent: 'space-between', fontSize: 11, pointerEvents: 'none' }}>
        <span>phase {phaseIndex}/72 · {projection?.target_layer ?? 'runtime'}</span>
        <span>trail {history.length} · forecast {forecast.length} · correction {correctionPath.length}</span>
      </div>
      {selected && (
        <div style={{ position: 'absolute', bottom: 10, left: 10, right: 10, background: '#111', padding: 10, fontSize: 12 }}>
          <div>Phase: {selected.index}</div>
          {selected.witnesses.map((w) => <div key={w.witness_hash72}>{w.modality} · {w.temporal_status}</div>)}
        </div>
      )}
    </div>
  );
}
