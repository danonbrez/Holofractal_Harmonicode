// MULTI-AGENT MANIFOLD EXTENSION
// render-only projection of existing runtime proposals/witnesses
// no kernel bypass, no local solve path, no redundant execution logic

import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

function projectState(state: any): [number, number, number] {
  const v = Number(state?.state?.v ?? state?.v ?? state?.phase_index ?? state?.phase_distance_from_anchor ?? 0);
  const s = Number(state?.state?.s ?? state?.s ?? state?.local_score ?? state?.risk_score ?? 0) / 20;
  return [v / 12, s, (v / 12) - s];
}

function statusColor(status?: string): string {
  return status === 'closed' || status === 'LOCKED' || status === 'PROJECTED' ? '#00ff88' :
    status === 'branched' || status === 'QUARANTINED' || status === 'CRITICAL' ? '#ff4444' :
    status === 'rejoining' || status === 'PHASE_STALLED' || status === 'WARN' ? '#4488ff' :
    '#ffffff';
}

function proposalState(proposal: any, index: number) {
  return {
    phase_distance_from_anchor: proposal?.phase_distance_from_anchor ?? index,
    local_score: proposal?.local_score ?? 0,
    risk_score: proposal?.risk_score ?? 0,
    agent: proposal?.agent ?? `AGENT_${index}`,
    phase_ok: Boolean(proposal?.phase_ok),
  };
}

function Trail({ history }: any) {
  const points = useMemo(() => history.map((s: any) => new THREE.Vector3(...projectState(s))), [history]);

  return (
    <group>
      {points.map((p: any, i: number) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshStandardMaterial
            color="#33f6ff"
            transparent
            opacity={Math.max(0.06, i / Math.max(1, points.length))}
            emissive="#33f6ff"
            emissiveIntensity={0.45}
          />
        </mesh>
      ))}
    </group>
  );
}

function Connection({ from, to, color = '#77ffee', opacity = 0.34 }: any) {
  const geometry = useMemo(() => {
    const start = new THREE.Vector3(...projectState(from));
    const end = new THREE.Vector3(...projectState(to));
    const mid = start.clone().lerp(end, 0.5);
    mid.z += 0.35;
    const curve = new THREE.QuadraticBezierCurve3(start, mid, end);
    return new THREE.BufferGeometry().setFromPoints(curve.getPoints(24));
  }, [from, to]);

  return (
    <line geometry={geometry}>
      <lineBasicMaterial color={color} transparent opacity={opacity} />
    </line>
  );
}

function MotionNode({ state, status, attractors, radius = 0.14, color }: any) {
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

    velocity.current.multiplyScalar(0.86);
    velocity.current.add(baseForce).add(attractorForce);
    current.add(velocity.current);
    ref.current.rotation.y += 0.018;
  });

  const nodeColor = color ?? statusColor(status);

  return (
    <mesh ref={ref}>
      <sphereGeometry args={[radius, 20, 20]} />
      <meshStandardMaterial
        color={nodeColor}
        emissive={nodeColor}
        emissiveIntensity={1.4}
        roughness={0.2}
        metalness={0.55}
      />
    </mesh>
  );
}

function AttractorField({ attractors }: any) {
  return (
    <group>
      {attractors.map((a: any, i: number) => (
        <mesh key={i} position={projectState(a)}>
          <sphereGeometry args={[0.3 + i * 0.025, 16, 16]} />
          <meshStandardMaterial
            color="#00ffaa"
            transparent
            opacity={0.08}
            emissive="#00ffaa"
            emissiveIntensity={0.7}
          />
        </mesh>
      ))}
    </group>
  );
}

function MultiAgentManifold({ projection, loop, phase }: any) {
  const proposals = loop?.proposals ?? [];
  const witnesses = phase?.witnesses ?? [];

  const agents = useMemo(() => proposals.map((p: any, i: number) => proposalState(p, i)), [proposals]);
  const witnessesAsNodes = useMemo(() => witnesses.map((w: any) => ({ ...w, phase_distance_from_anchor: w.phase_index, local_score: 10, phase_ok: w.temporal_status === 'ADMISSIBLE' })), [witnesses]);

  return (
    <group>
      {agents.map((agent: any, i: number) => (
        <group key={`agent-${agent.agent}-${i}`}>
          <Connection
            from={projection}
            to={agent}
            color={agent.phase_ok ? '#55ffaa' : '#ff6644'}
            opacity={agent.phase_ok ? 0.42 : 0.58}
          />
          <MotionNode
            state={agent}
            status={agent.phase_ok ? 'closed' : 'branched'}
            attractors={[projection]}
            radius={0.09 + Math.min(0.07, Math.max(0, Number(agent.local_score ?? 0)) / 700)}
            color={agent.phase_ok ? '#55ffaa' : '#ff6644'}
          />
        </group>
      ))}

      {witnessesAsNodes.map((w: any, i: number) => (
        <group key={`witness-${w.witness_hash72 ?? i}`}>
          <Connection from={projection} to={w} color="#aa88ff" opacity={0.18} />
          <MotionNode
            state={w}
            status={w.phase_ok ? 'closed' : 'branched'}
            attractors={[projection]}
            radius={0.055}
            color={w.phase_ok ? '#aa88ff' : '#ff4477'}
          />
        </group>
      ))}
    </group>
  );
}

export default function PhaseRing3D({ projection, loop, phase }: any) {
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    if (!projection) return;
    setHistory((prev) => [...prev.slice(-30), projection]);
  }, [projection]);

  const attractors = useMemo(() => history.slice(-6), [history]);

  return (
    <div style={{ height: '44vh' }}>
      <Canvas camera={{ position: [0, 0, 6], fov: 60 }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[3, 3, 4]} intensity={1.8} />

        <AttractorField attractors={attractors} />
        <Trail history={history} />

        <MotionNode
          state={projection}
          status={phase?.status ?? projection?.status}
          attractors={attractors}
        />

        <MultiAgentManifold projection={projection} loop={loop} phase={phase} />

        <OrbitControls enableZoom enableRotate enableDamping dampingFactor={0.05} />
      </Canvas>
    </div>
  );
}
