import React from 'react';
import { Canvas } from '@react-three/fiber';
import * as THREE from 'three';

const mockPhase = {
  anchor: 36,
  witnesses: [36,36,36,36]
};

function PhaseRing() {
  const points = new Array(72).fill(0);
  return (
    <>
      {points.map((_,i)=>{
        const angle = (i/72)*Math.PI*2;
        const x = Math.cos(angle)*2;
        const y = Math.sin(angle)*2;
        const isAnchor = i===mockPhase.anchor;
        return (
          <mesh key={i} position={[x,y,0]}>
            <sphereGeometry args={[0.05,16,16]} />
            <meshStandardMaterial color={isAnchor?'green':'gray'} />
          </mesh>
        );
      })}
    </>
  );
}

export default function App(){
  return (
    <div style={{width:'100vw',height:'100vh',background:'#000',color:'#0f0'}}>
      <div style={{padding:10}}>HHS Runtime Console</div>
      <Canvas camera={{position:[0,0,5]}}>
        <ambientLight />
        <PhaseRing />
      </Canvas>
    </div>
  );
}