/* Pass 220: 17-state Fourier phase basis for reciprocal particle-group properties.
   A read-only relationship transform. Not a force solver, particle allocator,
   or replacement for ordered native HNAN/VM81 tensors. */
(function(root) {
"use strict";
const N=17, TWOPI=2*Math.PI, INV_SQRT=1/Math.sqrt(N);
const basis=Object.freeze(Array.from({length:N},(_,j)=>
  Object.freeze(Array.from({length:N},(_,k)=>{
    const angle=TWOPI*((j*k)%N)/N;
    return Object.freeze([INV_SQRT*Math.cos(angle),INV_SQRT*Math.sin(angle)]);
  }))
));
function valid(a){return Array.isArray(a)&&a.length===N&&a.every(x=>Array.isArray(x)&&x.length===2&&x.every(Number.isFinite));}
function transform(amplitudes,inverse=false){
  if(!valid(amplitudes))throw new TypeError("Expected 17 complex amplitude pairs");
  return Array.from({length:N},(_,j)=>{
    let re=0,im=0;
    for(let k=0;k<N;k++){
      const [ur,ui]=inverse?basis[k][j]:basis[j][k];
      const vi=inverse?-ui:ui,[ar,ai]=amplitudes[k];
      re+=ur*ar-vi*ai;im+=ur*ai+vi*ar;
    }
    return [re,im];
  });
}
function quarterTurn(amplitudes){
  if(!valid(amplitudes))throw new TypeError("Expected 17 complex amplitude pairs");
  return amplitudes.map(([re,im])=>[-im,re]);
}
function rotateParticleBasis(amplitudes,step){
  if(!Number.isInteger(step))throw new TypeError("Integer phase step required");
  /* R(theta)=U D(theta) U†, theta = 2π step /17. */
  const spectral=transform(amplitudes,true);
  for(let k=0;k<N;k++){
    const [re,im]=spectral[k],angle=TWOPI*(((step%N+N)%N)*k%N)/N;
    const c=Math.cos(angle),s=Math.sin(angle);
    spectral[k]=[re*c-im*s,re*s+im*c];
  }
  return transform(spectral);
}
function reciprocalSlot(row,column,view=0){
  if(!Number.isInteger(row)||row<0||row>=N||
     !Number.isInteger(column)||column<0||column>=N||
     (view!==0&&view!==1))return null;
  return Object.freeze({row:view?column:row,column:view?row:column,
    slot:(view?column:row)*N+(view?row:column),
    quarterTurn:view===1,physicalParticle:false});
}
root.HHSFourier17=Object.freeze({
  schema:"HHS_PASS220_FOURIER17_QUADRATURE_V1",size:N,relationshipSlots:N*N,
  basis,transform,quarterTurn,rotateParticleBasis,reciprocalSlot,
  physicsMutation:false
});
})(typeof window!=="undefined"?window:globalThis);
