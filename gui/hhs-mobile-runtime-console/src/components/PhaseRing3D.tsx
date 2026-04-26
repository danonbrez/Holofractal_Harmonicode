import React, { useMemo, useState, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { PhaseLockView, PhaseWitnessView, RuntimeAnomalies } from '../runtimeData';

function Node({ index, anchor, witnesses, anomalies, onSelect }: any) {
  const meshRef = useRef<any>();
  const angle = (index / 72) * Math.PI * 2;
  const x = Math.cos(angle) * 2;
  const y = Math.sin(angle) * 2;
  const isAnchor = index === anchor;
  const matching = witnesses.filter((w: PhaseWitnessView) => w.phase_index === index);

  const hasCritical = anomalies?.alerts?.some((a: any) => a.severity === 'CRITICAL');

  const color = hasCritical ? 'red' : isAnchor ? 'green' : matching.length ? 'yellow' : 'gray';

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();
    const pulse = hasCritical ? 1 + Math.sin(t * 8) * 0.5 : isAnchor ? 1 + Math.sin(t * 4) * 0.3 : 1;
    meshRef.current.scale.set(pulse, pulse, pulse);
  });

  return (
    <mesh ref={meshRef} position={[x, y, 0]} onClick={() => onSelect(index, matching)}>
      <sphereGeometry args={[0.06, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={hasCritical ? 1.2 : isAnchor ? 0.8 : 0.2} />
    </mesh>
  );
}

function RotatingGroup({ children }: any) {
  const ref = useRef<any>();
  useFrame(({ clock }) => {
    if (ref.current) ref.current.rotation.z = clock.getElapsedTime() * 0.2;
  });
  return <group ref={ref}>{children}</group>;
}

export default function PhaseRing3D({ phase, anomalies }: { phase: PhaseLockView, anomalies?: RuntimeAnomalies }) {
  const [selected, setSelected] = useState<{ index: number; witnesses: PhaseWitnessView[] } | null>(null);
  const nodes = useMemo(() => new Array(72).fill(0), []);

  return (
    <div style={{ height: '40vh' }}>
      <Canvas camera={{ position: [0, 0, 5] }}>
        <ambientLight />
        <RotatingGroup>
          {nodes.map((_, i) => (
            <Node key={i} index={i} anchor={phase.anchor_phase_index} witnesses={phase.witnesses} anomalies={anomalies} onSelect={(idx: number, w: PhaseWitnessView[]) => setSelected({ index: idx, witnesses: w })} />
          ))}
        </RotatingGroup>
      </Canvas>
      {selected && (
        <div style={{ position: 'absolute', bottom: 10, left: 10, right: 10, background: '#111', padding: 10 }}>
          <div>Phase: {selected.index}</div>
          {selected.witnesses.map((w) => (
            <div key={w.witness_hash72}>{w.modality} · {w.temporal_status}</div>
          ))}
        </div>
      )}
    </div>
  );
}
