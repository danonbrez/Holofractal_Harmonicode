/* HHS Harmonicode Three/WebGL v1
 *
 * HHS-owned browser projection runtime for admitted immutable render state.
 * WebGL2 and JavaScript Number values are projection-only and have no VM81,
 * Hash72, Hash216, simulation, or canonical mutation authority.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined" && module.exports) module.exports=api;
  root.HHS3D=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";

  const AUTHORITY=Object.freeze({
    schema:"HHS_HARMONICODE_THREE_WEBGL_V1",
    canonicalMutationAuthority:false,
    vm81AdmissionAuthority:false,
    hash72CommitAuthority:false,
    hash216IdentityAuthority:false,
    gpuProjectionOnly:true,
    rendererWritebackForbidden:true,
    backend:"WEBGL2"
  });

  const AdditiveBlending=1;
  const NoBlending=0;
  const RGBAFormat=0x1908;
  const NearestFilter=0x2600;

  class HHS3DError extends Error {
    constructor(code,message){
      super(message);
      this.name="HHS3DError";
      this.code=code;
    }
  }

  class Vector2 {
    constructor(x=0,y=0){ this.x=x; this.y=y; }
    set(x,y){ this.x=x; this.y=y; return this; }
  }

  class Vector3 {
    constructor(x=0,y=0,z=0){ this.x=x; this.y=y; this.z=z; }
    set(x,y,z){ this.x=x; this.y=y; this.z=z; return this; }
  }

  class Object3D {
    constructor(){
      this.children=[];
      this.parent=null;
      this.position=new Vector3();
      this.visible=true;
      this.frustumCulled=true;
    }
    add(...nodes){
      for(const node of nodes){
        if(!node) continue;
        if(node.parent){
          const i=node.parent.children.indexOf(node);
          if(i>=0) node.parent.children.splice(i,1);
        }
        node.parent=this;
        this.children.push(node);
      }
      return this;
    }
  }

  class Scene extends Object3D {
    constructor(){ super(); this.background=null; this.isScene=true; }
  }

  function mat4Identity(){
    return new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);
  }

  function mat4Perspective(fovDeg,aspect,near,far){
    const f=1/Math.tan((fovDeg*Math.PI/180)/2);
    const nf=1/(near-far);
    return new Float32Array([
      f/aspect,0,0,0,
      0,f,0,0,
      0,0,(far+near)*nf,-1,
      0,0,(2*far*near)*nf,0
    ]);
  }

  function mat4Ortho(left,right,top,bottom,near,far){
    const lr=1/(left-right), bt=1/(bottom-top), nf=1/(near-far);
    return new Float32Array([
      -2*lr,0,0,0,
      0,-2*bt,0,0,
      0,0,2*nf,0,
      (left+right)*lr,(top+bottom)*bt,(far+near)*nf,1
    ]);
  }

  function normalize3(x,y,z){
    const n=Math.hypot(x,y,z)||1;
    return [x/n,y/n,z/n];
  }

  function cross3(ax,ay,az,bx,by,bz){
    return [ay*bz-az*by,az*bx-ax*bz,ax*by-ay*bx];
  }

  function mat4LookAt(eye,target,up){
    const z=normalize3(eye.x-target.x,eye.y-target.y,eye.z-target.z);
    let x=cross3(up.x,up.y,up.z,z[0],z[1],z[2]);
    x=normalize3(x[0],x[1],x[2]);
    const y=cross3(z[0],z[1],z[2],x[0],x[1],x[2]);
    return new Float32Array([
      x[0],y[0],z[0],0,
      x[1],y[1],z[1],0,
      x[2],y[2],z[2],0,
      -(x[0]*eye.x+x[1]*eye.y+x[2]*eye.z),
      -(y[0]*eye.x+y[1]*eye.y+y[2]*eye.z),
      -(z[0]*eye.x+z[1]*eye.y+z[2]*eye.z),
      1
    ]);
  }

  class Camera extends Object3D {
    constructor(){
      super();
      this.up=new Vector3(0,1,0);
      this._lookTarget=new Vector3(0,0,0);
      this.projectionMatrix=mat4Identity();
      this.isCamera=true;
    }
  }

  class PerspectiveCamera extends Camera {
    constructor(fov=50,aspect=1,near=0.1,far=2000){
      super();
      this.fov=fov; this.aspect=aspect; this.near=near; this.far=far;
      this.updateProjectionMatrix();
    }
    updateProjectionMatrix(){
      this.projectionMatrix=mat4Perspective(this.fov,this.aspect||1,this.near,this.far);
      return this;
    }
  }

  class OrthographicCamera extends Camera {
    constructor(left=-1,right=1,top=1,bottom=-1,near=0,far=1){
      super();
      this.left=left; this.right=right; this.top=top; this.bottom=bottom;
      this.near=near; this.far=far;
      this.updateProjectionMatrix();
    }
    updateProjectionMatrix(){
      this.projectionMatrix=mat4Ortho(this.left,this.right,this.top,this.bottom,this.near,this.far);
      return this;
    }
  }

  class BufferAttribute {
    constructor(array,itemSize){
      if(!ArrayBuffer.isView(array)) throw new HHS3DError("HHS3D_ATTRIBUTE_TYPE","BufferAttribute requires a typed array");
      if(!Number.isInteger(itemSize)||itemSize<1) throw new HHS3DError("HHS3D_ATTRIBUTE_SIZE","itemSize must be a positive integer");
      this.array=array;
      this.itemSize=itemSize;
      this.count=array.length/itemSize;
      if(!Number.isInteger(this.count)) throw new HHS3DError("HHS3D_ATTRIBUTE_ARITY","attribute length must be divisible by itemSize");
      this.normalized=false;
      this._buffers=new WeakMap();
    }
  }

  class BufferGeometry {
    constructor(){ this.attributes=Object.create(null); this.isBufferGeometry=true; }
    setAttribute(name,attribute){
      if(!(attribute instanceof BufferAttribute)) throw new HHS3DError("HHS3D_ATTRIBUTE_REQUIRED","setAttribute requires BufferAttribute");
      this.attributes[String(name)]=attribute;
      return this;
    }
    getAttribute(name){ return this.attributes[String(name)]; }
  }

  class PlaneGeometry extends BufferGeometry {
    constructor(width=1,height=1){
      super();
      const x=width/2,y=height/2;
      this.setAttribute("position",new BufferAttribute(new Float32Array([
        -x,-y,0,  x,-y,0,  x,y,0,
        -x,-y,0,  x,y,0, -x,y,0
      ]),3));
      this.setAttribute("uv",new BufferAttribute(new Float32Array([
        0,0, 1,0, 1,1,
        0,0, 1,1, 0,1
      ]),2));
    }
  }

  class ShaderMaterial {
    constructor(options={}){
      if(typeof options.vertexShader!=="string"||typeof options.fragmentShader!=="string"){
        throw new HHS3DError("HHS3D_SHADER_REQUIRED","ShaderMaterial requires vertexShader and fragmentShader");
      }
      this.vertexShader=options.vertexShader;
      this.fragmentShader=options.fragmentShader;
      this.uniforms=options.uniforms||{};
      this.transparent=Boolean(options.transparent);
      this.depthWrite=options.depthWrite!==false;
      this.depthTest=options.depthTest!==false;
      this.blending=options.blending===undefined?NoBlending:options.blending;
      this._programs=new WeakMap();
      this.isShaderMaterial=true;
    }
  }

  class Points extends Object3D {
    constructor(geometry,material){ super(); this.geometry=geometry; this.material=material; this.isPoints=true; }
  }

  class Mesh extends Object3D {
    constructor(geometry,material){ super(); this.geometry=geometry; this.material=material; this.isMesh=true; }
  }

  class WebGLRenderTarget {
    constructor(width,height,options={}){
      this.width=Math.max(1,width|0);
      this.height=Math.max(1,height|0);
      this.options=Object.assign({format:RGBAFormat,minFilter:NearestFilter,magFilter:NearestFilter,depthBuffer:true,stencilBuffer:false},options);
      this.texture={generateMipmaps:false,_target:this};
      this._version=1;
      this._resources=new WeakMap();
    }
    setSize(width,height){
      const w=Math.max(1,width|0), h=Math.max(1,height|0);
      if(w!==this.width||h!==this.height){
        this.width=w; this.height=h; this._version++;
      }
      return this;
    }
  }

  function hasDecl(src,kind,name){
    return new RegExp("\\b"+kind+"\\s+\\w+\\s+"+name+"\\b").test(src);
  }

  function vertex300(source){
    let src=String(source).replace(/^\s*#version[^\n]*\n?/,"");
    src=src.replace(/\battribute\b/g,"in").replace(/\bvarying\b/g,"out");
    const decl=[];
    if(/\bposition\b/.test(src) && !hasDecl(src,"in","position")) decl.push("in vec3 position;");
    if(/\buv\b/.test(src) && !hasDecl(src,"in","uv")) decl.push("in vec2 uv;");
    if(/\bmodelViewMatrix\b/.test(src) && !hasDecl(src,"uniform","modelViewMatrix")) decl.push("uniform mat4 modelViewMatrix;");
    if(/\bprojectionMatrix\b/.test(src) && !hasDecl(src,"uniform","projectionMatrix")) decl.push("uniform mat4 projectionMatrix;");
    return "#version 300 es\n"+decl.join("\n")+"\n"+src;
  }

  function fragment300(source){
    let src=String(source).replace(/^\s*#version[^\n]*\n?/,"");
    src=src.replace(/\bvarying\b/g,"in").replace(/\btexture2D\b/g,"texture");
    let outDecl="";
    if(/\bgl_FragColor\b/.test(src)){
      src=src.replace(/\bgl_FragColor\b/g,"hhs_FragColor");
      outDecl="out vec4 hhs_FragColor;\n";
    }
    return "#version 300 es\n"+outDecl+src;
  }

  function compileShader(gl,type,source){
    const shader=gl.createShader(type);
    gl.shaderSource(shader,source);
    gl.compileShader(shader);
    if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS)){
      const log=gl.getShaderInfoLog(shader)||"unknown shader error";
      gl.deleteShader(shader);
      throw new HHS3DError("HHS3D_SHADER_COMPILE",log);
    }
    return shader;
  }

  function linkProgram(gl,vertexSource,fragmentSource){
    const vs=compileShader(gl,gl.VERTEX_SHADER,vertex300(vertexSource));
    const fs=compileShader(gl,gl.FRAGMENT_SHADER,fragment300(fragmentSource));
    const program=gl.createProgram();
    gl.attachShader(program,vs);
    gl.attachShader(program,fs);
    gl.linkProgram(program);
    gl.deleteShader(vs);
    gl.deleteShader(fs);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS)){
      const log=gl.getProgramInfoLog(program)||"unknown link error";
      gl.deleteProgram(program);
      throw new HHS3DError("HHS3D_SHADER_LINK",log);
    }
    return program;
  }

  class WebGLRenderer {
    constructor(options={}){
      if(typeof document==="undefined") throw new HHS3DError("HHS3D_BROWSER_REQUIRED","WebGLRenderer requires a browser document");
      this.domElement=options.canvas||document.createElement("canvas");
      this._gl=this.domElement.getContext("webgl2",{
        alpha:options.alpha!==false,
        antialias:options.antialias!==false,
        premultipliedAlpha:options.premultipliedAlpha!==false,
        powerPreference:options.powerPreference||"default"
      });
      if(!this._gl) throw new HHS3DError("HHS3D_WEBGL2_REQUIRED","HHS Harmonicode renderer requires WebGL2");
      this._pixelRatio=1;
      this._target=null;
      this._clear=[0,0,0,0];
      this._gl.enable(this._gl.DEPTH_TEST);
      this._gl.depthFunc(this._gl.LEQUAL);
    }

    setPixelRatio(ratio){
      const n=Number(ratio);
      this._pixelRatio=Number.isFinite(n)&&n>0?n:1;
      return this;
    }

    setSize(width,height){
      const w=Math.max(1,Math.floor(Number(width)||1));
      const h=Math.max(1,Math.floor(Number(height)||1));
      this.domElement.style.width=w+"px";
      this.domElement.style.height=h+"px";
      this.domElement.width=Math.max(1,Math.floor(w*this._pixelRatio));
      this.domElement.height=Math.max(1,Math.floor(h*this._pixelRatio));
      if(!this._target) this._gl.viewport(0,0,this.domElement.width,this.domElement.height);
      return this;
    }

    getDrawingBufferSize(out){
      out.set(this._gl.drawingBufferWidth,this._gl.drawingBufferHeight);
      return out;
    }

    setClearColor(hex,alpha=1){
      const value=Number(hex)>>>0;
      this._clear=[((value>>16)&255)/255,((value>>8)&255)/255,(value&255)/255,Number(alpha)];
      this._gl.clearColor(this._clear[0],this._clear[1],this._clear[2],this._clear[3]);
      return this;
    }

    getContext(){ return this._gl; }

    _destroyTargetResource(target,resource){
      const gl=this._gl;
      if(resource.framebuffer) gl.deleteFramebuffer(resource.framebuffer);
      if(resource.texture) gl.deleteTexture(resource.texture);
      if(resource.depth) gl.deleteRenderbuffer(resource.depth);
      target._resources.delete(gl);
    }

    _ensureTarget(target){
      const gl=this._gl;
      let resource=target._resources.get(gl);
      if(resource && resource.version===target._version) return resource;
      if(resource) this._destroyTargetResource(target,resource);

      const framebuffer=gl.createFramebuffer();
      const texture=gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,target.options.minFilter===NearestFilter?gl.NEAREST:gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,target.options.magFilter===NearestFilter?gl.NEAREST:gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA8,target.width,target.height,0,gl.RGBA,gl.UNSIGNED_BYTE,null);

      gl.bindFramebuffer(gl.FRAMEBUFFER,framebuffer);
      gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,texture,0);

      let depth=null;
      if(target.options.depthBuffer!==false){
        depth=gl.createRenderbuffer();
        gl.bindRenderbuffer(gl.RENDERBUFFER,depth);
        gl.renderbufferStorage(gl.RENDERBUFFER,gl.DEPTH_COMPONENT16,target.width,target.height);
        gl.framebufferRenderbuffer(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.RENDERBUFFER,depth);
      }
      const status=gl.checkFramebufferStatus(gl.FRAMEBUFFER);
      if(status!==gl.FRAMEBUFFER_COMPLETE) throw new HHS3DError("HHS3D_FRAMEBUFFER","WebGL2 framebuffer is incomplete: "+status);

      resource={framebuffer,texture,depth,version:target._version};
      target._resources.set(gl,resource);
      gl.bindFramebuffer(gl.FRAMEBUFFER,null);
      return resource;
    }

    setRenderTarget(target){
      const gl=this._gl;
      this._target=target||null;
      if(target){
        const resource=this._ensureTarget(target);
        gl.bindFramebuffer(gl.FRAMEBUFFER,resource.framebuffer);
        gl.viewport(0,0,target.width,target.height);
      }else{
        gl.bindFramebuffer(gl.FRAMEBUFFER,null);
        gl.viewport(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight);
      }
      return this;
    }

    clear(color=true,depth=true,stencil=false){
      let bits=0;
      if(color) bits|=this._gl.COLOR_BUFFER_BIT;
      if(depth) bits|=this._gl.DEPTH_BUFFER_BIT;
      if(stencil) bits|=this._gl.STENCIL_BUFFER_BIT;
      this._gl.clear(bits);
      return this;
    }

    _program(material){
      const gl=this._gl;
      let record=material._programs.get(gl);
      if(record) return record;
      const program=linkProgram(gl,material.vertexShader,material.fragmentShader);
      const uniforms=Object.create(null);
      const count=gl.getProgramParameter(program,gl.ACTIVE_UNIFORMS);
      for(let i=0;i<count;i++){
        const info=gl.getActiveUniform(program,i);
        if(!info) continue;
        const name=info.name.replace(/\[0\]$/,"");
        uniforms[name]={location:gl.getUniformLocation(program,name),type:info.type};
      }
      record={program,uniforms};
      material._programs.set(gl,record);
      return record;
    }

    _bindAttribute(program,name,attribute){
      const gl=this._gl;
      const loc=gl.getAttribLocation(program,name);
      if(loc<0) return;
      let buffer=attribute._buffers.get(gl);
      if(!buffer){
        buffer=gl.createBuffer();
        attribute._buffers.set(gl,buffer);
        gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
        gl.bufferData(gl.ARRAY_BUFFER,attribute.array,gl.STATIC_DRAW);
      }else gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc,attribute.itemSize,gl.FLOAT,Boolean(attribute.normalized),0,0);
    }

    _uniform(record,name,value,textureUnit){
      const gl=this._gl;
      const slot=record.uniforms[name];
      if(!slot||slot.location===null) return textureUnit;
      if(typeof value==="number"){
        gl.uniform1f(slot.location,value);
      }else if(value instanceof Vector2){
        gl.uniform2f(slot.location,value.x,value.y);
      }else if(value instanceof Vector3){
        gl.uniform3f(slot.location,value.x,value.y,value.z);
      }else if(value && value._target instanceof WebGLRenderTarget){
        const resource=this._ensureTarget(value._target);
        gl.activeTexture(gl.TEXTURE0+textureUnit);
        gl.bindTexture(gl.TEXTURE_2D,resource.texture);
        gl.uniform1i(slot.location,textureUnit);
        return textureUnit+1;
      }else if(value instanceof Float32Array && value.length===16){
        gl.uniformMatrix4fv(slot.location,false,value);
      }
      return textureUnit;
    }

    _draw(object,camera){
      const gl=this._gl;
      if(!object.geometry||!object.material) return;
      const geometry=object.geometry, material=object.material;
      const record=this._program(material);
      gl.useProgram(record.program);

      for(const [name,attribute] of Object.entries(geometry.attributes)){
        this._bindAttribute(record.program,name,attribute);
      }

      if(material.depthTest) gl.enable(gl.DEPTH_TEST); else gl.disable(gl.DEPTH_TEST);
      gl.depthMask(Boolean(material.depthWrite));
      if(material.blending===AdditiveBlending){
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA,gl.ONE);
      }else{
        gl.disable(gl.BLEND);
      }

      const view=mat4LookAt(camera.position,camera._lookTarget||new Vector3(),camera.up||new Vector3(0,1,0));
      let unit=0;
      unit=this._uniform(record,"modelViewMatrix",view,unit);
      unit=this._uniform(record,"projectionMatrix",camera.projectionMatrix,unit);
      for(const [name,entry] of Object.entries(material.uniforms||{})){
        unit=this._uniform(record,name,entry?entry.value:undefined,unit);
      }

      const position=geometry.getAttribute("position");
      if(!position) throw new HHS3DError("HHS3D_POSITION_REQUIRED","renderable geometry requires position attribute");
      gl.drawArrays(object.isPoints?gl.POINTS:gl.TRIANGLES,0,position.count);
    }

    render(scene,camera){
      if(!(scene instanceof Scene)) throw new HHS3DError("HHS3D_SCENE_REQUIRED","render requires HHS3D.Scene");
      if(!(camera instanceof Camera)) throw new HHS3DError("HHS3D_CAMERA_REQUIRED","render requires HHS3D camera");
      const walk=(node)=>{
        if(!node||node.visible===false) return;
        if(node.isPoints||node.isMesh) this._draw(node,camera);
        for(const child of node.children||[]) walk(child);
      };
      walk(scene);
      return this;
    }
  }

  class OrbitControls {
    constructor(camera,domElement){
      this.camera=camera;
      this.domElement=domElement;
      this.enableDamping=false;
      this.enablePan=false;
      this.target=new Vector3();
      this.minDistance=0;
      this.maxDistance=Infinity;
      this._theta=0;
      this._phi=Math.PI/2;
      this._radius=Math.max(0.0001,Math.hypot(camera.position.x,camera.position.y,camera.position.z));
      this._drag=false;
      this._lastX=0;
      this._lastY=0;
      this._dTheta=0;
      this._dPhi=0;
      this._bind();
    }

    _bind(){
      const el=this.domElement;
      el.addEventListener("pointerdown",(e)=>{
        this._drag=true; this._lastX=e.clientX; this._lastY=e.clientY;
        if(el.setPointerCapture) el.setPointerCapture(e.pointerId);
      });
      el.addEventListener("pointermove",(e)=>{
        if(!this._drag) return;
        const dx=e.clientX-this._lastX, dy=e.clientY-this._lastY;
        this._lastX=e.clientX; this._lastY=e.clientY;
        this._dTheta-=dx*0.005;
        this._dPhi-=dy*0.005;
      });
      const stop=(e)=>{
        this._drag=false;
        if(el.releasePointerCapture && e && e.pointerId!==undefined){
          try{ el.releasePointerCapture(e.pointerId); }catch(_){}
        }
      };
      el.addEventListener("pointerup",stop);
      el.addEventListener("pointercancel",stop);
      el.addEventListener("wheel",(e)=>{
        e.preventDefault();
        const factor=Math.exp(e.deltaY*0.001);
        this._radius=Math.min(this.maxDistance,Math.max(this.minDistance,this._radius*factor));
      },{passive:false});
    }

    update(){
      const damping=this.enableDamping?0.18:1;
      this._theta+=this._dTheta*damping;
      this._phi+=this._dPhi*damping;
      if(this.enableDamping){
        this._dTheta*=0.82; this._dPhi*=0.82;
      }else{
        this._dTheta=0; this._dPhi=0;
      }
      const eps=1e-4;
      this._phi=Math.max(eps,Math.min(Math.PI-eps,this._phi));
      this._radius=Math.min(this.maxDistance,Math.max(this.minDistance,this._radius));
      const sinPhi=Math.sin(this._phi);
      this.camera.position.set(
        this.target.x+this._radius*sinPhi*Math.sin(this._theta),
        this.target.y+this._radius*Math.cos(this._phi),
        this.target.z+this._radius*sinPhi*Math.cos(this._theta)
      );
      this.camera._lookTarget.set(this.target.x,this.target.y,this.target.z);
      return true;
    }
  }

  return Object.freeze({
    AUTHORITY,
    HHS3DError,
    Vector2,Vector3,Object3D,Scene,Camera,PerspectiveCamera,OrthographicCamera,
    BufferAttribute,BufferGeometry,PlaneGeometry,ShaderMaterial,Points,Mesh,
    WebGLRenderTarget,WebGLRenderer,OrbitControls,
    AdditiveBlending,NoBlending,RGBAFormat,NearestFilter
  });
});
