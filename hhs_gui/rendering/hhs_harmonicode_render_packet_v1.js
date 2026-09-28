/* HHS Pass 179 render-command packet bridge v1.
 * Binary schema authority is defined by the C11 ABI in
 * native_projects/hhs_pass220_gfx1_native_render_commands/.
 * JavaScript is a projection-only decoder/executor and migration adapter.
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined" && module.exports) module.exports=api;
  root.HHSRenderPacket=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";

  const SCHEMA_VERSION=1;
  const HEADER_BYTES=1088;
  const COMMAND_BYTES=32;
  const ENDIAN_MARKER=0x01020304;
  const FLAG_SEALED=0x1;
  const FLAG_PROJECTION_ONLY=0x2;
  const FLAG_COMPATIBILITY_UNADMITTED=0x4;
  const FINGERPRINT_OFFSET=1080;
  const MAGIC="HHS179C1";

  const OPCODE=Object.freeze({
    BEGIN_FRAME:1, SET_VIEWPORT:2, SET_CAMERA:3, SET_TARGET:4, CLEAR:5,
    BIND_PIPELINE:6, BIND_MATERIAL:7, BIND_TEXTURES:8, SET_SCISSOR:9,
    SET_CLIP:10, DRAW_SPRITES:11, DRAW_PATHS:12, DRAW_TEXT:13,
    DRAW_POINTS:14, DRAW_LINES:15, DRAW_MESHES:16, DRAW_INSTANCES:17,
    DISPATCH_PARTICLE_UPDATE_PROJECTION:18, BEGIN_COMPOSITE_PASS:19,
    APPLY_EFFECT:20, END_COMPOSITE_PASS:21, COPY_OR_RESOLVE:22,
    READBACK_CAPTURE:23, END_FRAME:24
  });

  class RenderPacketError extends Error{
    constructor(code,message){ super(message); this.name="RenderPacketError"; this.code=code; }
  }

  function asBuffer(input){
    if(input instanceof ArrayBuffer) return input;
    if(ArrayBuffer.isView(input)) return input.buffer.slice(input.byteOffset,input.byteOffset+input.byteLength);
    throw new RenderPacketError("HHS179_PACKET_TYPE","render packet must be ArrayBuffer or typed array");
  }

  function readMagic(bytes){
    let out="";
    for(let i=0;i<8;i++) out+=String.fromCharCode(bytes[i]);
    return out;
  }

  function fnv1a64(bytes){
    let h=14695981039346656037n;
    for(let i=0;i<bytes.length;i++){
      if(i>=FINGERPRINT_OFFSET && i<FINGERPRINT_OFFSET+8) continue;
      h^=BigInt(bytes[i]);
      h=BigInt.asUintN(64,h*1099511628211n);
    }
    return h;
  }

  function drawOpcode(op){ return op>=OPCODE.DRAW_SPRITES && op<=OPCODE.DRAW_INSTANCES; }

  function validate(input){
    const buffer=asBuffer(input);
    const bytes=new Uint8Array(buffer);
    const view=new DataView(buffer);
    if(buffer.byteLength<HEADER_BYTES) throw new RenderPacketError("HHS179_PACKET_BOUNDS","packet shorter than header");
    if(readMagic(bytes)!==MAGIC) throw new RenderPacketError("HHS179_PACKET_MAGIC","invalid packet magic");
    if(view.getUint32(8,true)!==SCHEMA_VERSION) throw new RenderPacketError("HHS179_PACKET_VERSION","unsupported schema version");
    if(view.getUint32(12,true)!==HEADER_BYTES || view.getUint32(16,true)!==COMMAND_BYTES) throw new RenderPacketError("HHS179_PACKET_LAYOUT","header or command width drift");
    if(view.getUint32(28,true)!==ENDIAN_MARKER) throw new RenderPacketError("HHS179_PACKET_ENDIAN","little-endian marker mismatch");
    const commandCount=view.getUint32(20,true);
    const expected=HEADER_BYTES+commandCount*COMMAND_BYTES;
    if(commandCount<1 || expected!==buffer.byteLength || view.getUint32(24,true)!==expected) throw new RenderPacketError("HHS179_PACKET_BOUNDS","command count/byte length mismatch");
    if(view.getUint32(40,true)===0 || view.getUint32(44,true)===0) throw new RenderPacketError("HHS179_PACKET_TARGET","target dimensions must be nonzero");
    if(view.getBigUint64(72,true)===0n) throw new RenderPacketError("HHS179_PACKET_TIME","exact time denominator must be nonzero");
    if(view.getUint32(52,true)!==0) throw new RenderPacketError("HHS179_PACKET_LAYOUT","reserved header field must remain zero");
    const flags=view.getUint32(32,true);
    if((flags&FLAG_SEALED)===0) throw new RenderPacketError("HHS179_PACKET_UNSEALED","packet must be sealed");
    if((flags&FLAG_PROJECTION_ONLY)===0) throw new RenderPacketError("HHS179_PACKET_AUTHORITY","packet must remain projection-only");
    if((flags&FLAG_COMPATIBILITY_UNADMITTED)===0){
      const nonzero=(start,n)=>{ for(let i=start;i<start+n;i++) if(bytes[i]!==0) return true; return false; };
      if(!nonzero(80,216)||!nonzero(296,216)||!nonzero(728,216)||!nonzero(944,72)) throw new RenderPacketError("HHS179_PACKET_IDENTITY","admitted packet identities are required");
    }
    let compositeDepth=0;
    const commands=[];
    for(let i=0;i<commandCount;i++){
      const o=HEADER_BYTES+i*COMMAND_BYTES;
      const opcode=view.getUint16(o,true);
      const commandBytes=view.getUint32(o+4,true);
      const resourceId=view.getBigUint64(o+8,true);
      const arg0=view.getBigUint64(o+16,true);
      const arg1=view.getBigUint64(o+24,true);
      if(opcode<OPCODE.BEGIN_FRAME || opcode>OPCODE.END_FRAME) throw new RenderPacketError("HHS179_PACKET_OPCODE","unknown opcode "+opcode);
      if(commandBytes!==COMMAND_BYTES) throw new RenderPacketError("HHS179_PACKET_COMMAND_BYTES","command width drift");
      if(i===0 && opcode!==OPCODE.BEGIN_FRAME) throw new RenderPacketError("HHS179_PACKET_SEQUENCE","first command must BEGIN_FRAME");
      if(i===commandCount-1 && opcode!==OPCODE.END_FRAME) throw new RenderPacketError("HHS179_PACKET_SEQUENCE","last command must END_FRAME");
      if(i!==0 && opcode===OPCODE.BEGIN_FRAME) throw new RenderPacketError("HHS179_PACKET_SEQUENCE","nested BEGIN_FRAME");
      if(i!==commandCount-1 && opcode===OPCODE.END_FRAME) throw new RenderPacketError("HHS179_PACKET_SEQUENCE","early END_FRAME");
      if(opcode===OPCODE.BEGIN_COMPOSITE_PASS){ if(compositeDepth) throw new RenderPacketError("HHS179_PACKET_SEQUENCE","nested composite pass"); compositeDepth=1; }
      if(opcode===OPCODE.END_COMPOSITE_PASS){ if(!compositeDepth) throw new RenderPacketError("HHS179_PACKET_SEQUENCE","orphan composite end"); compositeDepth=0; }
      if((drawOpcode(opcode)||opcode===OPCODE.SET_CAMERA||opcode===OPCODE.BIND_PIPELINE||opcode===OPCODE.BIND_MATERIAL||opcode===OPCODE.BIND_TEXTURES||opcode===OPCODE.APPLY_EFFECT) && resourceId===0n){
        throw new RenderPacketError("HHS179_PACKET_RESOURCE","opcode requires nonzero resource identity");
      }
      commands.push(Object.freeze({opcode,flags:view.getUint16(o+2,true),resourceId,arg0,arg1}));
    }
    if(compositeDepth) throw new RenderPacketError("HHS179_PACKET_SEQUENCE","unterminated composite pass");
    const stored=view.getBigUint64(FINGERPRINT_OFFSET,true);
    const actual=fnv1a64(bytes);
    if(stored===0n || stored!==actual) throw new RenderPacketError("HHS179_PACKET_FINGERPRINT","projection fingerprint mismatch");
    return Object.freeze({
      schema:"HHS_PASS_179_RENDER_COMMAND_PACKET_V1",
      canonicalMutationAuthority:false,
      vm81AdmissionAuthority:false,
      hash72CommitAuthority:false,
      hash216IdentityAuthority:false,
      compatibilityUnadmitted:Boolean(flags&FLAG_COMPATIBILITY_UNADMITTED),
      frameIndex:view.getBigUint64(56,true),
      exactTimeNum:view.getBigInt64(64,true),
      exactTimeDen:view.getBigUint64(72,true),
      targetWidth:view.getUint32(40,true),
      targetHeight:view.getUint32(44,true),
      projectionProfile:view.getUint32(36,true),
      fingerprint:stored,
      commands:Object.freeze(commands)
    });
  }

  class ResourceRegistry{
    constructor(){ this._resources=new Map(); }
    register(id,value){
      const key=BigInt(id);
      if(key===0n) throw new RenderPacketError("HHS179_RESOURCE_ZERO","resource id zero is reserved for default/null");
      if(value===undefined||value===null) throw new RenderPacketError("HHS179_RESOURCE_VALUE","resource value required");
      this._resources.set(key,value);
      return this;
    }
    require(id){
      const key=BigInt(id);
      if(!this._resources.has(key)) throw new RenderPacketError("HHS179_RESOURCE_MISSING","missing projection resource "+key.toString());
      return this._resources.get(key);
    }
  }

  function execute(renderer,input,registry){
    if(!renderer || typeof renderer.renderObject!=="function") throw new RenderPacketError("HHS179_RENDERER_API","renderer must expose renderObject");
    if(!(registry instanceof ResourceRegistry)) throw new RenderPacketError("HHS179_RESOURCE_REGISTRY","ResourceRegistry required");
    const packet=validate(input);
    let camera=null;
    for(const command of packet.commands){
      const op=command.opcode;
      if(op===OPCODE.BEGIN_FRAME || op===OPCODE.END_FRAME || op===OPCODE.BEGIN_COMPOSITE_PASS || op===OPCODE.END_COMPOSITE_PASS) continue;
      if(op===OPCODE.SET_CAMERA){ camera=registry.require(command.resourceId); continue; }
      if(op===OPCODE.SET_TARGET){ renderer.setRenderTarget(command.resourceId===0n?null:registry.require(command.resourceId)); continue; }
      if(op===OPCODE.SET_VIEWPORT){ renderer.getContext().viewport(0,0,Number(command.arg0),Number(command.arg1)); continue; }
      if(op===OPCODE.CLEAR){ const bits=Number(command.arg0); renderer.clear(Boolean(bits&1),Boolean(bits&2),Boolean(bits&4)); continue; }
      if(op===OPCODE.DRAW_POINTS || op===OPCODE.DRAW_MESHES){
        if(!camera) throw new RenderPacketError("HHS179_CAMERA_REQUIRED","draw command has no active camera");
        renderer.renderObject(registry.require(command.resourceId),camera);
        continue;
      }
      if(op===OPCODE.BIND_PIPELINE || op===OPCODE.BIND_MATERIAL || op===OPCODE.BIND_TEXTURES){ registry.require(command.resourceId); continue; }
      throw new RenderPacketError("HHS179_EXEC_UNSUPPORTED","opcode not implemented by WebGL2 GFX1 executor: "+op);
    }
    return packet;
  }

  function putAscii(bytes,offset,text){ for(let i=0;i<text.length;i++) bytes[offset+i]=text.charCodeAt(i)&0xff; }

  function buildCompatibilityPacket(options={}){
    const commands=Array.isArray(options.commands)?options.commands:[];
    if(commands.length<1) throw new RenderPacketError("HHS179_COMPAT_COMMANDS","commands required");
    const buffer=new ArrayBuffer(HEADER_BYTES+commands.length*COMMAND_BYTES);
    const bytes=new Uint8Array(buffer);
    const view=new DataView(buffer);
    putAscii(bytes,0,MAGIC);
    view.setUint32(8,SCHEMA_VERSION,true);
    view.setUint32(12,HEADER_BYTES,true);
    view.setUint32(16,COMMAND_BYTES,true);
    view.setUint32(20,commands.length,true);
    view.setUint32(24,buffer.byteLength,true);
    view.setUint32(28,ENDIAN_MARKER,true);
    view.setUint32(32,FLAG_SEALED|FLAG_PROJECTION_ONLY|FLAG_COMPATIBILITY_UNADMITTED,true);
    view.setUint32(36,Number(options.projectionProfile||1),true);
    view.setUint32(40,Math.max(1,Number(options.targetWidth)||1),true);
    view.setUint32(44,Math.max(1,Number(options.targetHeight)||1),true);
    view.setUint32(48,Number(options.targetFormat||1),true);
    view.setBigUint64(56,BigInt(options.frameIndex||0),true);
    view.setBigInt64(64,BigInt(options.exactTimeNum||0),true);
    view.setBigUint64(72,BigInt(options.exactTimeDen||1),true);
    commands.forEach((c,i)=>{
      const o=HEADER_BYTES+i*COMMAND_BYTES;
      view.setUint16(o,Number(c.opcode),true);
      view.setUint16(o+2,Number(c.flags||0),true);
      view.setUint32(o+4,COMMAND_BYTES,true);
      view.setBigUint64(o+8,BigInt(c.resourceId||0),true);
      view.setBigUint64(o+16,BigInt(c.arg0||0),true);
      view.setBigUint64(o+24,BigInt(c.arg1||0),true);
    });
    view.setBigUint64(FINGERPRINT_OFFSET,fnv1a64(bytes),true);
    validate(buffer);
    return buffer;
  }

  return Object.freeze({
    AUTHORITY:Object.freeze({schema:"HHS_PASS_179_RENDER_COMMAND_PACKET_V1",binaryAuthority:"C11",projectionOnly:true,canonicalMutationAuthority:false}),
    OPCODE, HEADER_BYTES, COMMAND_BYTES, ENDIAN_MARKER,
    FLAG_SEALED, FLAG_PROJECTION_ONLY, FLAG_COMPATIBILITY_UNADMITTED,
    RenderPacketError, ResourceRegistry, validate, execute, buildCompatibilityPacket, projectionFingerprint:fnv1a64
  });
});
