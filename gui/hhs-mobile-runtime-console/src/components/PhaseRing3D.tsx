// ATTRACTOR DYNAMICS EXTENSION

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

function projectState(state: any): [number, number, number] {
  const v = Number(state?.state?.v ?? state?.v ?? 0);
  const s = Number(state?.state?.s ?? state?.s ?? 0);
  return [v, s, v - s];
}

function MotionNode({ state, status, attractors }: any) {
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
      return acc.add(dir.normalize().multiplyScalar(strength * 0.05));
    }, new THREE.Vector3());

    velocity.current.multiplyScalar(0.85);
    velocity.current.add(baseForce).add(attractorForce);
    current.add(velocity.current);
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

function AttractorField({ attractors }: any) {
  return (
    <group>
      {attractors.map((a: any, i: number) => (
        <mesh key={i} position={projectState(a)}>
          <sphereGeometry args={[0.25, 16, 16]} />
          <meshStandardMaterial color="#00ffaa" transparent opacity={0.15} emissive="#00ffaa" />
        </mesh>
      ))}
    </group>
  );
}

export default function PhaseRing3D({ projection, loop, phase }: any) {

  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (!projection) return;
    setHistory((prev) => [...prev.slice(-20), projection]);
  }, [projection]);

  const attractors = useMemo(() => history.slice(-5), [history]);

  return (
    <div style={{ height: '44vh' }}>
      <Canvas camera={{ position: [0, 0, 6] }}>

        <ambientLight intensity={0.5} />
        <pointLight position={[3, 3, 3]} />

        <AttractorField attractors={attractors} />

        <MotionNode
          state={projection}
          status={phase?.status}
          attractors={attractors}
        />

      </Canvas>
    </div>
  );
}
