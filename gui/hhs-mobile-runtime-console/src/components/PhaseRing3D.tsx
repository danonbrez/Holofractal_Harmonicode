// AGENT INTERACTION PHYSICS EXTENSION (incremental, no bypass)

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

function projectState(state: any): [number, number, number] {
  const v = Number(state?.state?.v ?? state?.v ?? state?.phase_index ?? state?.phase_distance_from_anchor ?? 0);
  const s = Number(state?.state?.s ?? state?.s ?? state?.local_score ?? state?.risk_score ?? 0) / 20;
  return [v / 12, s, (v / 12) - s];
}

function MotionNode({ state, status, attractors, agents }: any) {
  const ref = useRef<any>();
  const velocity = useRef(new THREE.Vector3());

  useFrame(() => {
    if (!ref.current) return;

    const current = ref.current.position;
    const target = new THREE.Vector3(...projectState(state));

    const baseForce = target.clone().sub(current).multiplyScalar(0.08);

    const attractorForce = attractors.reduce((acc: any, a: any) => {
      const aPos = new THREE.Vector3(...projectState(a));
      const dir = aPos.clone().sub(current);
      const dist = dir.length() + 0.001;
      const strength = 1 / (dist * dist);
      return acc.add(dir.normalize().multiplyScalar(strength * 0.03));
    }, new THREE.Vector3());

    const agentForce = (agents ?? []).reduce((acc: any, other: any) => {
      if (other === state) return acc;
      const otherPos = new THREE.Vector3(...projectState(other));
      const dir = otherPos.clone().sub(current);
      const dist = dir.length() + 0.001;

      const aligned = (state.phase_ok === other.phase_ok);
      const sign = aligned ? 1 : -1;

      return acc.add(dir.normalize().multiplyScalar(sign * 0.015 / dist));
    }, new THREE.Vector3());

    velocity.current.multiplyScalar(0.86);
    velocity.current.add(baseForce).add(attractorForce).add(agentForce);
    current.add(velocity.current);
  });

  const color = state.phase_ok === false ? '#ff6644' : '#55ffaa';

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.12, 20, 20]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.4} />
    </mesh>
  );
}

export default function PhaseRing3D({ projection, loop, phase }: any) {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (!projection) return;
    setHistory((prev) => [...prev.slice(-30), projection]);
  }, [projection]);

  const attractors = useMemo(() => history.slice(-6), [history]);
  const agents = useMemo(() => (loop?.proposals ?? []), [loop]);

  return (
    <div style={{ height: '44vh' }}>
      <Canvas camera={{ position: [0, 0, 6], fov: 60 }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[3, 3, 4]} intensity={1.8} />

        <MotionNode state={projection} status={phase?.status} attractors={attractors} agents={agents} />

        {agents.map((a: any, i: number) => (
          <MotionNode key={i} state={a} attractors={attractors} agents={agents} />
        ))}

        <OrbitControls enableZoom enableRotate enableDamping dampingFactor={0.05} />
      </Canvas>
    </div>
  );
}
