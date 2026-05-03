// PHASE MAPPING EXTENSION
// motion = computation layer

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { PhaseLockView, PhaseWitnessView, RuntimeAnomalies, OperatorLoopView, ProjectionView } from '../runtimeData';
import { topDisplayInfluences } from '../displayPhaseAnalysis';

const RING = 72;

function mod72(n: number): number { return ((Math.round(n) % RING) + RING) % RING; }

// 🔥 NEW: STATE → SPATIAL PROJECTION
function projectState(state: any): [number, number, number] {
  const v = Number(state?.state?.v ?? state?.v ?? 0);
  const s = Number(state?.state?.s ?? state?.s ?? 0);

  return [
    v,
    s,
    v - s
  ];
}

// 🔥 NEW: SMOOTH MOTION NODE
function MotionNode({ state, status }: { state: any; status?: string }) {
  const ref = useRef<any>();
  const target = projectState(state);

  useFrame(() => {
    if (!ref.current) return;

    ref.current.position.lerp(
      new THREE.Vector3(...target),
      0.1
    );
  });

  const color =
    status === 'closed' ? '#00ff88' :
    status === 'branched' ? '#ff4444' :
    status === 'rejoining' ? '#4488ff' :
    '#ffffff';

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.12, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.2} />
    </mesh>
  );
}

export default function PhaseRing3D({ phase, anomalies, projection, loop, corrections, activePhase, onPhaseSelect, calculatorPhases = [] }: any) {

  const phaseIndex = activePhase ?? projection?.phase_index ?? phase.anchor_phase_index ?? 0;

  return (
    <div style={{ height: '44vh', position: 'relative' }}>
      <Canvas camera={{ position: [0, 0, 6] }}>

        <ambientLight intensity={0.5} />
        <pointLight position={[3, 3, 3]} />

        {/* 🔥 CORE NODE (live state) */}
        <MotionNode
          state={projection}
          status={phase?.status}
        />

        {/* 🔥 BRANCH VISUALIZATION */}
        {(loop?.proposals ?? []).map((p: any, i: number) => (
          <MotionNode
            key={i}
            state={{ v: p.phase_distance_from_anchor, s: i }}
            status={p.phase_ok ? 'rejoining' : 'branched'}
          />
        ))}

      </Canvas>
    </div>
  );
}
