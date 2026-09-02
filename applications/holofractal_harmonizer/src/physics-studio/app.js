(()=>{'use strict';
const API='/api/runtime/pass178-physics';const ev=document.querySelector('#evidence'),ta=document.querySelector('#model'),sel=document.querySelector('#template');
let active=null;
const show=v=>ev.textContent=typeof v==='string'?v:JSON.stringify(v,null,2);
async function j(path,opt){const r=await fetch(API+path,opt);return r.json()}
async function load(){const t=await j('/templates');ta.value=JSON.stringify(t[sel.value],null,2);show(t[sel.value])}
document.querySelector('#load').onclick=load;
document.querySelector('#create').onclick=async()=>{const t=JSON.parse(ta.value),id='studio:'+sel.value,sourceId=id+':source';
await j('/source/'+encodeURIComponent(sourceId),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source:t.source})});
let params=t.parameters||{};if(params.matrix_dimension){const d=params.matrix_dimension,flat=params.hamiltonian,rows=[];for(let i=0;i<d;i++)rows.push(flat.slice(i*d,(i+1)*d));params={...params,hamiltonian:rows}}
const reg=await j('/model/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({model_id:id,model_kind:t.model_kind,source_id:sourceId,parameters:params})});
if(!reg.ok)return show(reg);const init=await j('/model/'+encodeURIComponent(id)+'/initial',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(t.initial_state)});active=id;show(init);draw(await j('/model/'+encodeURIComponent(id)+'/render-packet'))};
document.querySelector('#step').onclick=async()=>{if(!active)return;const r=await j('/model/'+encodeURIComponent(active)+'/step',{method:'POST'});show(r);draw(await j('/model/'+encodeURIComponent(active)+'/render-packet'))};
document.querySelector('#replay').onclick=async()=>{if(active)show(await j('/model/'+encodeURIComponent(active)+'/replay'))};
function draw(p){const c=document.querySelector('#view'),x=c.getContext('2d');x.clearRect(0,0,c.width,c.height);x.fillStyle='#07121d';x.fillRect(0,0,c.width,c.height);x.strokeStyle='#2f7898';for(let i=0;i<18;i++){x.beginPath();x.moveTo(0,i*24);x.lineTo(c.width,i*24);x.stroke()}x.fillStyle='#68e3ce';const q=p.position_q32_32||[0,0,0],px=c.width/2+q[0]/4294967296*60,py=c.height/2-q[1]/4294967296*60;x.beginPath();x.arc(px,py,8,0,Math.PI*2);x.fill();x.fillStyle='#dcecff';x.fillText('projection-only step '+String(p.step_index||0),16,24)}
j('/status').then(s=>{show(s);const chips=document.querySelector('#chips');[['VM81',s.vm81_authority_bound],['No float authority',!s.floating_point_canonical_authority],['Terminal',s.terminal_pass178_completion]].forEach(([a,b])=>{const e=document.createElement('span');e.className='chip';e.textContent=a+': '+b;chips.append(e)})});load();
})();