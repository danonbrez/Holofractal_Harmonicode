/* Phase-coupled particle membranes — render-only overlay.
 * Bond topology is read from the existing simulation. No physics/receipt writes.
 * Two vertices: narrow quad ribbon. Three or more: a triangular fan at each
 * coupled junction, bounded for predictable projection memory.
 */
(function(){
"use strict";
const GROUPS=32, MAX_TRIANGLES=1600;
const settings=Array.from({length:GROUPS},(_,i)=>({shift:0,saturation:1,opacity:0.43,visible:true}));
let enabled=true, theme="native";
const themes={native:0,aurora:0.12,ember:-0.11,ultraviolet:0.32,monochrome:0};
let meshes=[], initialized=false;
const tmp=new THREE.Color(), color=new THREE.Color();
function groupId(p){
  const u=p.userData||{};
  return (u.layer2?16:0)+(u.recip?8:0)+((u.spiral||0)&7);
}
function mixColor(ids,g){
  let r=0,gr=0,b=0;
  for(let k=0;k<ids.length;k++){
    const p=particles[ids[k]];
    if(!p)continue;
    const c=p.material.color;r+=c.r;gr+=c.g;b+=c.b;
  }
  // RGB vector sum carries all constituent vertex colors; normalize only
  // for display gamut, then derive hue from that summed vector.
  const peak=Math.max(r,gr,b,1e-9);
  tmp.setRGB(r/peak,gr/peak,b/peak);
  const hsl=tmp.getHSL({h:0,s:0,l:0});
  const opts=settings[g];
  color.setHSL(((hsl.h+opts.shift+themes[theme])%1+1)%1,
    theme==="monochrome"?0:Math.min(1,hsl.s*opts.saturation),
    Math.max(0.12,Math.min(0.74,hsl.l)));
  return color;
}
function makeMesh(g){
  const positions=new Float32Array(MAX_TRIANGLES*9);
  const colors=new Float32Array(MAX_TRIANGLES*9);
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute("position",new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
  geometry.setAttribute("color",new THREE.BufferAttribute(colors,3).setUsage(THREE.DynamicDrawUsage));
  geometry.setDrawRange(0,0);
  const material=new THREE.MeshBasicMaterial({
    vertexColors:true,side:THREE.DoubleSide,transparent:true,
    opacity:settings[g].opacity,depthWrite:false,depthTest:true,
    blending:THREE.NormalBlending
  });
  const mesh=new THREE.Mesh(geometry,material);
  mesh.frustumCulled=false;mesh.renderOrder=1;
  scene.add(mesh);
  return {mesh,positions,colors,n:0};
}
function init(){
  if(initialized||!scene)return;
  meshes=Array.from({length:GROUPS},(_,g)=>makeMesh(g));
  initialized=true;
}
function push(g,a,b,c,ids){
  const entry=meshes[g];
  if(entry.n>=MAX_TRIANGLES)return;
  const offset=entry.n++*9;
  const verts=[a,b,c],cc=mixColor(ids,g);
  for(let k=0;k<3;k++){
    const v=verts[k],j=offset+k*3;
    entry.positions[j]=v.x;entry.positions[j+1]=v.y;entry.positions[j+2]=v.z;
    entry.colors[j]=cc.r;entry.colors[j+1]=cc.g;entry.colors[j+2]=cc.b;
  }
}
const world=[new THREE.Vector3(),new THREE.Vector3(),new THREE.Vector3()];
const up=new THREE.Vector3(0,1,0), edge=new THREE.Vector3(),side=new THREE.Vector3();
function projectedPosition(id,target){
  const p=particles[id];
  return p.getWorldPosition(target);
}
function ribbon(g,i,j){
  const a=projectedPosition(i,world[0]),b=projectedPosition(j,world[1]);
  edge.subVectors(b,a);
  if(edge.lengthSq()<1e-12)return;
  side.crossVectors(edge,up);
  if(side.lengthSq()<1e-12)side.set(1,0,0);
  side.normalize().multiplyScalar(0.12);
  const aa=a.clone().add(side),ab=a.clone().sub(side);
  const ba=b.clone().add(side),bb=b.clone().sub(side);
  push(g,aa,ab,ba,[i,j]);push(g,ab,bb,ba,[i,j]);
}
function sync(){
  init();
  if(!initialized)return;
  for(let g=0;g<GROUPS;g++){
    const e=meshes[g];e.n=0;
    e.mesh.visible=enabled&&settings[g].visible;
    e.mesh.material.opacity=settings[g].opacity;
  }
  if(!enabled)return;
  if(typeof bondN!=="number"||!particles.length)return;
  const adjacency=new Map();
  for(let k=0;k<bondN;k++){
    const i=bondI[k],j=bondJ[k];
    if(i<0||j<0||i>=particles.length||j>=particles.length)continue;
    const g=groupId(particles[i]);
    if(settings[g].visible)ribbon(g,i,j);
    if(!adjacency.has(i))adjacency.set(i,[]);
    if(!adjacency.has(j))adjacency.set(j,[]);
    adjacency.get(i).push(j);adjacency.get(j).push(i);
  }
  // Joined coupling groups of >=3 particles yield actual 2D triangle
  // patches; each patch uses three existing graph-connected vertices.
  for(const [center,neighbors] of adjacency){
    if(neighbors.length<2)continue;
    const g=groupId(particles[center]);
    if(!settings[g].visible)continue;
    const origin=projectedPosition(center,world[0]).clone();
    for(let n=1;n<neighbors.length;n++){
      if(meshes[g].n>=MAX_TRIANGLES)break;
      const a=projectedPosition(neighbors[n-1],world[1]).clone();
      const b=projectedPosition(neighbors[n],world[2]).clone();
      if(new THREE.Vector3().subVectors(a,origin).cross(new THREE.Vector3().subVectors(b,origin)).lengthSq()<1e-12)continue;
      push(g,origin,a,b,[center,neighbors[n-1],neighbors[n]]);
    }
  }
  for(let g=0;g<GROUPS;g++){
    const e=meshes[g],geo=e.mesh.geometry;
    geo.setDrawRange(0,e.n*3);
    geo.attributes.position.needsUpdate=true;
    geo.attributes.color.needsUpdate=true;
  }
}
function controls(){
  const parent=document.getElementById("osShell");
  if(!parent)return;
  const field=document.createElement("fieldset");
  field.id="phaseMembranePanel";
  field.innerHTML='<legend>Phase-coupled membranes (view only)</legend>'+
    '<label><input id="membraneEnabled" type="checkbox" checked> Show membrane surfaces</label>'+
    '<label>Theme <select id="membraneTheme"><option value="native">Native</option><option value="aurora">Aurora</option><option value="ember">Ember</option><option value="ultraviolet">Ultraviolet</option><option value="monochrome">Monochrome</option></select></label>'+
    '<label>Group <select id="membraneGroup"></select></label>'+
    '<label>Group hue shift <input type="range" id="membraneHue" min="-180" max="180" value="0"> <output id="membraneHueValue">0°</output></label>'+
    '<label>Group opacity <input type="range" id="membraneOpacity" min="0" max="0.7" step="0.01" value="0.43"> <output id="membraneOpacityValue">0.43</output></label>'+
    '<label>Group saturation <input type="range" id="membraneSat" min="0" max="2" step="0.05" value="1"></label>'+
    '<label><input id="membraneGroupVisible" type="checkbox" checked> Selected group visible</label>';
  field.style.cssText="border:1px solid #3a5377;border-radius:5px;margin:8px 0;padding:6px";
  for(const label of field.querySelectorAll("label"))label.style.cssText="display:block;margin:6px 0";
  field.style.cssText+=";position:fixed;right:10px;bottom:70px;width:245px;max-height:45vh;overflow:auto;background:rgba(5,12,30,.88);color:#def;z-index:125;box-shadow:0 0 16px rgba(75,180,240,.35)";
  document.body.appendChild(field);
  const get=id=>document.getElementById(id);
  const sel=get("membraneGroup");
  for(let g=0;g<GROUPS;g++){
    const op=document.createElement("option");
    op.value=g;op.textContent="Layer "+(g>=16?2:1)+" · "+(g%16>=8?"exchange":"spiral")+" "+(g%8+1);
    sel.appendChild(op);
  }
  function refresh(){
    const s=settings[+sel.value];
    get("membraneHue").value=String(Math.round(s.shift*360));
    get("membraneOpacity").value=String(s.opacity);
    get("membraneSat").value=String(s.saturation);
    get("membraneGroupVisible").checked=s.visible;
    get("membraneHueValue").textContent=Math.round(s.shift*360)+"°";
    get("membraneOpacityValue").textContent=s.opacity.toFixed(2);
  }
  get("membraneEnabled").addEventListener("change",e=>enabled=e.target.checked);
  get("membraneTheme").addEventListener("change",e=>theme=e.target.value);
  sel.addEventListener("change",refresh);
  get("membraneHue").addEventListener("input",e=>{settings[+sel.value].shift=+e.target.value/360;refresh()});
  get("membraneOpacity").addEventListener("input",e=>{settings[+sel.value].opacity=+e.target.value;refresh()});
  get("membraneSat").addEventListener("input",e=>{settings[+sel.value].saturation=+e.target.value;refresh()});
  get("membraneGroupVisible").addEventListener("change",e=>settings[+sel.value].visible=e.target.checked);
  refresh();
}
controls();
window.HHSPhaseMembranes=Object.freeze({
  sync,settings,
  get enabled(){return enabled;},
  get theme(){return theme;},
  get diagnostics(){return {triangles:meshes.reduce((n,e)=>n+e.n,0),groups:GROUPS,renderOnly:true};}
});
})();