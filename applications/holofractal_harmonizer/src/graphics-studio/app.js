(() => {
'use strict';
const API='/api/runtime/pass179-graphics';
const evidence=document.querySelector('#evidence');
const frame=document.querySelector('#frame');
const golden=document.querySelector('#golden');
let sceneId=null;
function show(v){evidence.textContent=typeof v==='string'?v:JSON.stringify(v,null,2)}
async function json(path,options){const r=await fetch(API+path,options);return r.json()}
async function status(){
  const s=await json('/status');
  show(s);
  const chips=document.querySelector('#chips');
  chips.innerHTML='';
  for(const [label,value] of [['VM81',s.vm81_authority_bound],['No GPU authority',!s.gpu_mutation_authority],['Terminal',s.terminal_pass179_completion]]){
    const span=document.createElement('span');span.className='chip';span.textContent=label+': '+String(value);chips.append(span);
  }
}
document.querySelector('#commit').onclick=async()=>{
  const name=golden.value;const r=await json('/golden/'+name+'/commit',{method:'POST'});
  show(r);if(r.ok){sceneId=r.scene_id;frame.src=API+'/scene/'+encodeURIComponent(sceneId)+'/png?ts='+Date.now()}
};
document.querySelector('#render').onclick=()=>{if(sceneId)frame.src=API+'/scene/'+encodeURIComponent(sceneId)+'/png?ts='+Date.now()};
for(const b of document.querySelectorAll('[data-shader]'))b.onclick=async()=>{
  let payload;try{payload=JSON.parse(document.querySelector('#shader').value)}catch(e){return show(e.message)}
  const r=await json('/shader/project/'+b.dataset.shader,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  show(r);
};
status();
})();
