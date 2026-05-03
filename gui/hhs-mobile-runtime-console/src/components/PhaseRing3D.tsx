// TRAJECTORY SYSTEM EXTENSION
// motion memory + branch arcs + rejoin interpolation

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// 🔥 projection
function projectState(state: any): [number, number, number] {
  const v = Number(state?.state?.v ?? state?.v ?? 0);
  const s = Number(state?.state?.s ?? state?.s ?? 0);
  return [v, s, v - s];
}

// 🔥 TRAJECTORY LINE
function Trajectory({ history }: { history: any[] }) {
  const points = useMemo(() => {
    return history.map((s) => new THREE.Vector3(...projectState(s)));
  }, [history]);

  const geometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [points]);

  if (points.length < 2) return null;

  return (
    <line geometry={geometry}>
      <lineBasicMaterial color="#33f6ff" transparent opacity={0.8} />
    </line>
  );
}

// 🔥 BRANCH ARC (curved path)
function BranchArc({ from, to }: { from: any; to: any }) {
  const start = new THREE.Vector3(...projectState(from));
  const end = new THREE.Vector3(...projectState(to));

  const mid = start.clone().lerp(end, 0.5);
  mid.y += 0.5; // lift arc

  const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
  const points = curve.getPoints(20);

  const geometry = new THREE.BufferGeometry().setFromPoints(points);

  return (
    <line geometry={geometry}>
      <lineBasicMaterial color="#ff8844" transparent opacity={0.5} />
    </line>
  );
}

// 🔥 MOTION NODE
function MotionNode({ state, status }: any) {
  const ref = useRef<any>();
  const target = projectState(state);

  useFrame(() => {
    if (!ref.current) return;
    ref.current.position.lerp(new THREE.Vector3(...target), 0.1);
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

export default function PhaseRing3D({ projection, loop, phase }: any) {

  const [history, setHistory] = useState<any[]>([]);

  // 🔁 accumulate trajectory
  useEffect(() => {
    if (!projection) return;
    setHistory((prev) => [...prev.slice(-50), projection]);
  }, [projection]);

  return (
    <div style={{ height: '44vh' }}>
      <Canvas camera={{ position: [0, 0, 6] }}>

        <ambientLight intensity={0.5} />
        <pointLight position={[3, 3, 3]} />

        {/* CORE NODE */}
        <MotionNode state={projection} status={phase?.status} />

        {/* TRAJECTORY */}
        <Trajectory history={history} />

        {/* BRANCH ARCS */}
        {(loop?.proposals ?? []).map((p: any, i: number) => (
          <BranchArc
            key={i}
            from={projection}
            to={{ v: p.phase_distance_from_anchor, s: i }}
          />
        ))}

      </Canvas>
    </div>
  );
}
