"use strict";
/* Execute the real derived inline scripts with deterministic browser/Three
   doubles. CI smoke is not equivalent to hardware WebGL screenshot testing. */
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const html=fs.readFileSync(path.resolve(__dirname,"../../examples/ParticleSimulationAtomicNeural.html"),"utf8");
const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)]
  .map(match=>match[1]).filter(s=>s.trim());
assert.equal(scripts.length,3);
scripts.forEach((source,index)=>new vm.Script(source,{filename:"inline-"+index+".js"}));

function harness(controlsAvailable=true, neuralAvailable=true) {
  let renders=0, scheduled=[], now=1000;
  class Vector {
    constructor(x=0,y=0,z=0){this.set(x,y,z)}
    set(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;return this}
    copy(o){return this.set(o.x,o.y,o.z)}
    add(o){this.x+=o.x;this.y+=o.y;this.z+=o.z;return this}
    sub(o){this.x-=o.x;this.y-=o.y;this.z-=o.z;return this}
    multiplyScalar(n){this.x*=n;this.y*=n;this.z*=n;return this}
    length(){return Math.hypot(this.x,this.y,this.z)}
    normalize(){return this.multiplyScalar(1/(this.length()||1))}
    lerp(o,t){this.x+=(o.x-this.x)*t;this.y+=(o.y-this.y)*t;this.z+=(o.z-this.z)*t;return this}
    unproject(){return this}
  }
  class Object3D {
    constructor(geometry,material){
      this.position=new Vector;this.rotation=new Vector;this.children=[];
      this.userData={};this.visible=true;this.geometry=geometry;this.material=material;
    }
    add(item){this.children.push(item);return this}
    getWorldPosition(out){return out.copy(this.position)}
  }
  class Geometry {
    constructor(){this.attributes={}}
    setAttribute(key,val){this.attributes[key]=val;return this}
    setFromPoints(){return this}
  }
  class Attribute {
    constructor(array,itemSize){this.array=array;this.itemSize=itemSize;this.needsUpdate=false}
    setUsage(){return this}
  }
  class Color {
    constructor(){this.r=0.5;this.g=0.5;this.b=0.5}
    setHSL(h,s,l){this.r=h;this.g=s;this.b=l;return this}
  }
  class Material {constructor(){this.color=new Color}}
  class Instance extends Object3D {
    constructor(geometry,material,count){super(geometry,material);this.count=count;
      this.instanceMatrix=new Attribute;this.instanceColor=new Attribute}
    setMatrixAt(){}setColorAt(){}
  }
  class Renderer {constructor(){this.domElement={}}setSize(){}render(){renders++}}
  class Camera extends Object3D {constructor(){super();this.aspect=1}updateProjectionMatrix(){}lookAt(){}}
  class Matrix {makeTranslation(){return this}}
  class OrbitControls {constructor(){this.enabled=true}update(){}}
  const THREE={Scene:Object3D,PerspectiveCamera:Camera,WebGLRenderer:Renderer,
    PointLight:Object3D,AmbientLight:Object3D,SphereGeometry:Geometry,
    BufferGeometry:Geometry,BufferAttribute:Attribute,MeshBasicMaterial:Material,
    LineBasicMaterial:Material,PointsMaterial:Material,Mesh:Object3D,Group:Object3D,
    Line:Object3D,LineLoop:Object3D,LineSegments:Object3D,Points:Object3D,
    Vector2:Vector,Vector3:Vector,Color,InstancedMesh:Instance,Matrix4:Matrix,
    DynamicDrawUsage:1,AdditiveBlending:1};
  if(controlsAvailable) THREE.OrbitControls=OrbitControls;
  const elements=new Map;
  const domElement=()=>({style:{},value:"1",textContent:"",innerText:"",disabled:false,
    addEventListener(name,callback){this["on"+name]=callback}});
  const document={
    body:{appendChild(){}},
    getElementById(id){if(!elements.has(id)) elements.set(id,domElement());
      return elements.get(id)}
  };
  const window={addEventListener(){},innerWidth:1024,innerHeight:768,updateFunctions:[]};
  const ctx={window,document,Float32Array,Float64Array,Uint8Array,Int32Array,
    Math,Number,Object,Array,Map,Set,BigInt,JSON,performance:{now:()=>now},
    THREE,innerWidth:1024,innerHeight:768,
    requestAnimationFrame:cb=>scheduled.push(cb),
    setTimeout(){},console:{log(){}}};
  vm.runInNewContext(scripts[0],ctx,{filename:"diagnostics.js"});
  if(neuralAvailable)vm.runInNewContext(scripts[1],ctx,{filename:"recurrent_neural.js"});
  vm.runInNewContext(scripts[2],ctx,{filename:"physical_scene.js"});
  return {
    window,document,get renders(){return renders},get queued(){return scheduled.length},
    el:id=>document.getElementById(id),
    frames(n){for(let i=0;i<n;i++){const callback=scheduled.shift();assert(callback);
      now+=16.667;callback();}},
  };
}
const normal=harness(true,true);
assert.equal(normal.window.HHS.boot.boot_halt,false);
assert.equal(normal.renders,1,"The first physics tick must create the first image");
assert(normal.queued>0,"requestAnimationFrame should have another frame scheduled");
normal.frames(8);
assert.equal(normal.renders,3,"First render + every fourth callback must be visible");
normal.el("runCalibration").onclick();
const calibration=JSON.parse(normal.el("output").textContent);
assert.equal(calibration.status,"success");
assert(calibration.observed_render_fps>0);
normal.el("agentInspectIndex").value="5184";
normal.el("inspectAgent").onclick();
assert.match(normal.el("agentDetail").textContent,/Agent 5184 \/ layer 1 \/ local 0/);
assert.match(normal.el("agentDetail").textContent,/Applied to physics: NO/);
assert.equal(normal.el("freqSlider").disabled,true);
assert.equal(normal.el("massSlider").disabled,true);
normal.el("commandInput").value='{"command":"run_module","module":"AgenticElectronSpriteStatus","parameters":{"agent_index":5184}}';
normal.el("runCommand").onclick();
assert.match(normal.el("output").innerText,/AgenticElectronSpriteStatus/);
normal.el("commandInput").value='{bad json';
normal.el("runCommand").onclick();
assert.match(normal.el("output").innerText,/Invalid JSON:/);
normal.el("jsonCommandInput").value='{"command":"init_system","config":{"HHS_System":{"global_parameters":{"mu":2}}}}';
assert.equal(typeof normal.window.HHS.boot.boot_halt,"boolean");

assert.equal(normal.el("topoBtn").disabled,true);

const noOrbit=harness(false,true);
assert.equal(noOrbit.renders,1,"Missing camera controls cannot suppress field rendering");
assert.match(noOrbit.el("runtimeDiagnostics").textContent,/static camera fallback/);
noOrbit.frames(4);
assert.equal(noOrbit.renders,2);

const noNeural=harness(true,false);
assert.equal(noNeural.renders,1,"Missing optional neural controller cannot halt I057");
assert.match(noNeural.el("agentStatus").textContent,/Neural preview disabled/);
noNeural.frames(4);
assert.equal(noNeural.renders,2);

console.log("PASS: startup rendered first frame; 8-frame continuation; measured FPS; inspection; frozen controls; OrbitControls and neural fallbacks.");
