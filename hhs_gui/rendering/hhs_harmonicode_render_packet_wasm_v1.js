/* Generated bridge for native Pass 179 C11 packet builder.
 * Source: native_projects/hhs_pass220_gfx1_native_render_commands/
 * Embedded WASM SHA-256: 31c34c0d79a5532a340bca5b46347154c6098f9787f2f5f9a147f91b018015af
 */
(function(root,factory){
  "use strict";
  const api=factory();
  if(typeof module!=="undefined" && module.exports) module.exports=api;
  root.HHSRenderPacketWasm=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";

  const EMBEDDED_WASM_SHA256="31c34c0d79a5532a340bca5b46347154c6098f9787f2f5f9a147f91b018015af";
  const WASM_BASE64="AGFzbQEAAAABNQhgAX8Bf2AEf39/fwF/YAJ/fgBgAn9/AX9gA39/fwF/YAF/AX5gAAF/YAh/f39/f35+fgF/AxMSAAECAQMEBQMGBwAAAAYGBgYABQQBAQICBggBfwFBkLkECweVAgsGbWVtb3J5AgAXaGhzMTc5X3dhc21fYWJpX3ZlcnNpb24ACBFoaHMxNzlfd2FzbV9yZXNldAAJGGhoczE3OV93YXNtX2lkZW50aXR5X3B0cgAKGmhoczE3OV93YXNtX2lkZW50aXR5X2J5dGVzAAsXaGhzMTc5X3dhc21fY29tbWFuZF9wdHIADBxoaHMxNzlfd2FzbV9jb21tYW5kX2NhcGFjaXR5AA0WaGhzMTc5X3dhc21fcGFja2V0X3B0cgAOG2hoczE3OV93YXNtX3BhY2tldF9jYXBhY2l0eQAPF2hoczE3OV93YXNtX3BhY2tldF9zaXplABAYaGhzMTc5X3dhc21fYnVpbGRfcGFja2V0ABEKxRsSGgBBACAAQQV0QcAIaiAAQYCAfGpBgYB8SRsLoAgBAn9BASEEAkAgAEUNACACRQ0AIAIoAgBBmAhHDQBBAiEEIANBgIB8aiIFQYGAfEkNAEEAIANBBXRBwAhqIAVBgYB8SRsiBSABSw0AQQUhBCACKAIMRQ0AIAIoAhBFDQAgAikDKFANACACKAIEIQRBACEBA0AgACABakIANwAAIAUgAUEIaiIBRw0ACyAAQQE6AB8gAEGAiIwQNgAbIAAgBToAGCAAQQA7ABYgACADOgAUIABBIDYAECAAQoGAgICAiAE3AAggAELIkM2K86bOoTE3AAAgACAEQRh2OgAjIAAgBEEQdjoAIiAAIARBCHY6ACEgACAFQRB2OgAaIAAgBUEIdjoAGSAAIANBCHY6ABUgACAEQfwBcUECcjoAICAAIAIoAgg2ACQgACACKAIMNgAoIAAgAigCEDYALCAAIAIoAhQ2ADAgACACKQMYNwA4IAAgAikDIDcAQCAAIAIpAyg3AEhBqH4hAQNAIAAgAWoiBEGoAmogAiABaiIDQYgCai0AADoAACAEQakCaiADQYkCai0AADoAACAEQaoCaiADQYoCai0AADoAACAEQasCaiADQYsCai0AADoAACABQQRqIgENAAtBqH4hAQNAIAAgAWoiBEGABGogAiABaiIDQeADai0AADoAACAEQYEEaiADQeEDai0AADoAACAEQYIEaiADQeIDai0AADoAACAEQYMEaiADQeMDai0AADoAACABQQRqIgENAAtBqH4hAQNAIAAgAWoiBEHYBWogAiABaiIDQbgFai0AADoAACAEQdkFaiADQbkFai0AADoAACAEQdoFaiADQboFai0AADoAACAEQdsFaiADQbsFai0AADoAACABQQRqIgENAAtBqH4hAQNAIAAgAWoiBEGwB2ogAiABaiIDQZAHai0AADoAACAEQbEHaiADQZEHai0AADoAACAEQbIHaiADQZIHai0AADoAACAEQbMHaiADQZMHai0AADoAACABQQRqIgENAAtBuH8hAQNAIAAgAWoiBEH4B2ogAiABaiIDQdgHai0AADoAACAEQfkHaiADQdkHai0AADoAACAEQfoHaiADQdoHai0AADoAACAEQfsHaiADQdsHai0AADoAACABQQRqIgENAAtBYCEBA0AgACABaiIEQZgIaiACIAFqIgNB+AdqLQAAOgAAIARBmQhqIANB+QdqLQAAOgAAIARBmghqIANB+gdqLQAAOgAAIARBmwhqIANB+wdqLQAAOgAAIAFBBGoiAQ0AC0FgIQEDQCAAIAFqIgRBuAhqIAIgAWoiA0GYCGotAAA6AAAgBEG5CGogA0GZCGotAAA6AAAgBEG6CGogA0GaCGotAAA6AAAgBEG7CGogA0GbCGotAAA6AABBACEEIAFBBGoiAQ0ACwsgBAsJACAAIAE3AAAL9wEBAn9BASEEAkAgAEUNACADRQ0AAkAgAUHACE8NAEECDwsCQCAALQAgQQFxRQ0AQQkPC0EFIQQgACgAFCIFIAJNDQAgBUF/akH+/wNLDQAgBUEFdEHACGogAUsNAAJAIAMvAQAiAUFnakH//wNxQej/A08NAEEHDwsgAygCBEEgRw0AQQAhBCAAIAJBBXRqIgBBwQhqQQA6AAAgAEHACGogAToAACAAQcIIaiADLwECOwAAIABBxAhqIAMoAgQ2AAAgAEHICGogAykDCBCCgICAACAAQdAIaiADKQMQEIKAgIAAIABB2AhqIAMpAxgQgoCAgAALIAQLmwICA38BfgJAIAANAEEBDwsCQCABQcAITw0AQQUPCwJAIAAoACAiAkEBcUUNAEEJDwtBACEDAkAgACABQQAQhYCAgAAiBA0A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DwtBmJCAgAAPC0EAIQELIAELKgEBf0EAIQECQCAAQX9qIgBBBksNACAAQQJ0QYCIgIAAaigCACEBCyABCxYAQQAgAEEFdEHAkICAAGogAEE/SxsLBQBBwAALCABBwKCAgAALBQBBwBgLCwBBACgCgLmAgAALvQEBBH8gABCAgICAACEBQQBBADYCgLmAgABBAiECAkAgAUG/Z2pBwGdJDQBBwKCAgABBwBhBoIiAgAAgABCBgICAACICDQACQCAARQ0AQQAhA0HAkICAACEEA0BBwKCAgABBwBggAyAEEIOAgIAAIgINAiAEQSBqIQQgACADQQFqIgNHDQALC0HAoICAACABEISAgIAAIgINAEHAoICAACABEIeAgIAAIgINAEEAIQJBACABNgKAuYCAAAsgAgsLIwEAQYAICxzYAAAA2AAAANgAAADYAAAASAAAACAAAAAgAAAAAJcEBG5hbWUAIyJoaHNfcGFzczE3OV9yZW5kZXJfY29tbWFuZF92MS53YXNtAcoDEgAjaGhzMTc5X3JlbmRlcl9wYWNrZXRfcmVxdWlyZWRfYnl0ZXMBGWhoczE3OV9yZW5kZXJfcGFja2V0X2luaXQCCXB1dF91NjRsZQMiaGhzMTc5X3JlbmRlcl9wYWNrZXRfd3JpdGVfY29tbWFuZAQZaGhzMTc5X3JlbmRlcl9wYWNrZXRfc2VhbAUSdmFsaWRhdGVfc3RydWN0dXJlBglnZXRfdTY0bGUHHWhoczE3OV9yZW5kZXJfcGFja2V0X3ZhbGlkYXRlCBdoaHMxNzlfd2FzbV9hYmlfdmVyc2lvbgkRaGhzMTc5X3dhc21fcmVzZXQKGGhoczE3OV93YXNtX2lkZW50aXR5X3B0cgsaaGhzMTc5X3dhc21faWRlbnRpdHlfYnl0ZXMMF2hoczE3OV93YXNtX2NvbW1hbmRfcHRyDRxoaHMxNzlfd2FzbV9jb21tYW5kX2NhcGFjaXR5DhZoaHMxNzlfd2FzbV9wYWNrZXRfcHRyDxtoaHMxNzlfd2FzbV9wYWNrZXRfY2FwYWNpdHkQF2hoczE3OV93YXNtX3BhY2tldF9zaXplERhoaHMxNzlfd2FzbV9idWlsZF9wYWNrZXQHEgEAD19fc3RhY2tfcG9pbnRlcgkKAQAHLnJvZGF0YQB/CXByb2R1Y2VycwEMcHJvY2Vzc2VkLWJ5AQVjbGFuZ18xNy4wLjAgKGh0dHBzOi8vZ2l0aHViLmNvbS9zd2lmdGxhbmcvbGx2bS1wcm9qZWN0LmdpdCAxMDk5OWI2ZDAzNGZlMzE4ZjNkNTZjODNiZGRiNjU3MjU5M2E4YmIwKQBJD3RhcmdldF9mZWF0dXJlcwQrCm11bHRpdmFsdWUrD211dGFibGUtZ2xvYmFscysPcmVmZXJlbmNlLXR5cGVzKwhzaWduLWV4dA==";
  const IDENTITY_KIND=Object.freeze({
    SCENE:1,FRAME:2,PRIOR:3,RESOURCES:4,CAMERA:5,SOFTWARE_DIGEST:6,BACKEND_EVIDENCE:7
  });

  class NativePacketWasmError extends Error{
    constructor(code,message){ super(message); this.name="NativePacketWasmError"; this.code=code; }
  }

  function decodeBase64(){
    if(typeof atob==="function"){
      const raw=atob(WASM_BASE64), out=new Uint8Array(raw.length);
      for(let i=0;i<raw.length;i++) out[i]=raw.charCodeAt(i);
      return out;
    }
    if(typeof Buffer!=="undefined") return new Uint8Array(Buffer.from(WASM_BASE64,"base64"));
    throw new NativePacketWasmError("HHS179_WASM_BASE64","no base64 decoder available");
  }

  async function sha256Hex(bytes){
    if(typeof crypto!=="undefined" && crypto.subtle){
      const digest=await crypto.subtle.digest("SHA-256",bytes);
      return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,"0")).join("");
    }
    if(typeof require==="function"){
      const c=require("crypto");
      return c.createHash("sha256").update(Buffer.from(bytes)).digest("hex");
    }
    return null;
  }

  function putCommand(view,ptr,command){
    const C=(typeof HHSRenderPacket!=="undefined" && HHSRenderPacket.COMMAND_BYTES)||32;
    view.setUint16(ptr,Number(command.opcode),true);
    view.setUint16(ptr+2,Number(command.flags||0),true);
    view.setUint32(ptr+4,C,true);
    view.setBigUint64(ptr+8,BigInt(command.resourceId||0),true);
    view.setBigUint64(ptr+16,BigInt(command.arg0||0),true);
    view.setBigUint64(ptr+24,BigInt(command.arg1||0),true);
  }

  class NativePacketBuilder{
    constructor(instance,wasmSha256){
      this.instance=instance;
      this.exports=instance.exports;
      this.memory=instance.exports.memory;
      this.wasmSha256=wasmSha256;
      if(this.exports.hhs179_wasm_abi_version()!==1){
        throw new NativePacketWasmError("HHS179_WASM_VERSION","native WASM ABI version mismatch");
      }
    }

    _view(){ return new DataView(this.memory.buffer); }
    _bytes(){ return new Uint8Array(this.memory.buffer); }

    setIdentity(kind,value){
      const id=Number(kind), ptr=this.exports.hhs179_wasm_identity_ptr(id);
      const expected=this.exports.hhs179_wasm_identity_bytes(id);
      if(!ptr||!expected) throw new NativePacketWasmError("HHS179_WASM_IDENTITY_KIND","invalid identity kind");
      const bytes=value instanceof Uint8Array?value:new Uint8Array(value);
      if(bytes.byteLength!==expected) throw new NativePacketWasmError("HHS179_WASM_IDENTITY_SIZE","identity byte length mismatch");
      this._bytes().set(bytes,ptr);
      return this;
    }

    build(options={}){
      const commands=Array.isArray(options.commands)?options.commands:[];
      if(commands.length<1 || commands.length>this.exports.hhs179_wasm_command_capacity()){
        throw new NativePacketWasmError("HHS179_WASM_COMMAND_COUNT","command count outside native capacity");
      }
      const compatibilityUnadmitted=options.compatibilityUnadmitted===true;
      const flags=compatibilityUnadmitted?4:0;
      const status=this.exports.hhs179_wasm_reset(
        flags,
        Number(options.projectionProfile||1),
        Math.max(1,Number(options.targetWidth)||1),
        Math.max(1,Number(options.targetHeight)||1),
        Number(options.targetFormat||1),
        BigInt(options.frameIndex||0),
        BigInt(options.exactTimeNum||0),
        BigInt(options.exactTimeDen||1)
      );
      if(status!==0) throw new NativePacketWasmError("HHS179_WASM_RESET","native reset rejected packet metadata: "+status);

      const identities=options.identities||{};
      for(const [name,kind] of Object.entries(IDENTITY_KIND)){
        const key=name.toLowerCase();
        if(identities[key]!==undefined) this.setIdentity(kind,identities[key]);
      }

      const view=this._view();
      commands.forEach((command,index)=>{
        const ptr=this.exports.hhs179_wasm_command_ptr(index);
        if(!ptr) throw new NativePacketWasmError("HHS179_WASM_COMMAND_PTR","native command staging pointer unavailable");
        putCommand(view,ptr,command);
      });

      const buildStatus=this.exports.hhs179_wasm_build_packet(commands.length);
      if(buildStatus!==0) throw new NativePacketWasmError("HHS179_WASM_BUILD","native packet build rejected: "+buildStatus);
      const ptr=this.exports.hhs179_wasm_packet_ptr();
      const size=this.exports.hhs179_wasm_packet_size();
      if(!ptr||!size) throw new NativePacketWasmError("HHS179_WASM_PACKET","native packet export is empty");
      const copy=this._bytes().slice(ptr,ptr+size);
      const buffer=copy.buffer.slice(copy.byteOffset,copy.byteOffset+copy.byteLength);
      if(typeof HHSRenderPacket!=="undefined") HHSRenderPacket.validate(buffer);
      return buffer;
    }
  }

  async function create(){
    const bytes=decodeBase64();
    const sha=await sha256Hex(bytes);
    if(sha!==null && sha!==EMBEDDED_WASM_SHA256){
      throw new NativePacketWasmError("HHS179_WASM_SHA256","embedded native WASM identity mismatch");
    }
    const instantiated=await WebAssembly.instantiate(bytes,{});
    const instance=instantiated.instance||instantiated;
    return new NativePacketBuilder(instance,sha||EMBEDDED_WASM_SHA256);
  }

  return Object.freeze({
    AUTHORITY:Object.freeze({
      schema:"HHS_PASS_179_NATIVE_WASM_RENDER_PACKET_BRIDGE_V1",
      c11BinaryAuthority:true,
      packetSerializationInJavaScript:false,
      canonicalMutationAuthority:false,
      compatibilityAdmissionMustRemainExplicit:true
    }),
    EMBEDDED_WASM_SHA256,
    IDENTITY_KIND,
    NativePacketWasmError,
    NativePacketBuilder,
    create
  });
});
