from pathlib import Path
import json
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "native_projects" / "hhs_pass220_gfx1_native_render_commands"
HEADER = NATIVE / "include" / "hhs_pass179_render_command_v1.h"
SOURCE = NATIVE / "src" / "hhs_pass179_render_command_v1.c"
C_TEST = NATIVE / "tests" / "hhs_pass179_render_command_v1_test.c"
JS_PACKET = ROOT / "hhs_gui" / "rendering" / "hhs_harmonicode_render_packet_v1.js"
JS_WASM = ROOT / "hhs_gui" / "rendering" / "hhs_harmonicode_render_packet_wasm_v1.js"
WASM_BUILD = NATIVE / "tools" / "build_wasm.sh"
JS_RENDERER = ROOT / "hhs_gui" / "rendering" / "hhs_harmonicode_three_webgl_v1.js"
LANE5 = ROOT / "applications" / "holofractal_harmonizer" / "lane5_holographic_sprite_5184.html"


def test_native_c11_render_packet_abi_compiles_and_runs(tmp_path: Path) -> None:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    exe = tmp_path / "hhs179_render_packet_test"
    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            f"-I{NATIVE / 'include'}",
            str(SOURCE),
            str(C_TEST),
            "-o",
            str(exe),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    result = subprocess.run(
        [str(exe)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "PASS hhs_pass179_render_command_v1" in result.stdout


def test_native_and_browser_packet_schema_constants_remain_locked() -> None:
    header = HEADER.read_text(encoding="utf-8")
    js = JS_PACKET.read_text(encoding="utf-8")
    locks = {
        "HHS179_RENDER_PACKET_HEADER_BYTES 1088U": "const HEADER_BYTES=1088;",
        "HHS179_RENDER_COMMAND_BYTES 32U": "const COMMAND_BYTES=32;",
        "HHS179_RENDER_ENDIAN_MARKER 0x01020304U": "const ENDIAN_MARKER=0x01020304;",
        "HHS179_RENDER_PACKET_FLAG_SEALED 0x00000001U": "const FLAG_SEALED=0x1;",
        "HHS179_RENDER_PACKET_FLAG_PROJECTION_ONLY 0x00000002U": "const FLAG_PROJECTION_ONLY=0x2;",
        "HHS179_RENDER_PACKET_FLAG_COMPATIBILITY_UNADMITTED 0x00000004U": "const FLAG_COMPATIBILITY_UNADMITTED=0x4;",
    }
    for c_token, js_token in locks.items():
        assert c_token in header
        assert js_token in js

    for opcode, value in (
        ("BEGIN_FRAME", 1),
        ("SET_VIEWPORT", 2),
        ("SET_CAMERA", 3),
        ("SET_TARGET", 4),
        ("CLEAR", 5),
        ("DRAW_POINTS", 14),
        ("DRAW_MESHES", 16),
        ("BEGIN_COMPOSITE_PASS", 19),
        ("END_COMPOSITE_PASS", 21),
        ("END_FRAME", 24),
    ):
        assert f"HHS179_CMD_{opcode} = {value}" in header
        assert f"{opcode}:{value}" in js


def test_browser_packet_builder_validator_rejects_post_seal_mutation() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js unavailable")
    script = r"""
const fs=require("fs");
const vm=require("vm");
vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"),{filename:process.argv[1]});
const p=global.HHSRenderPacket;
const O=p.OPCODE;
const packet=p.buildCompatibilityPacket({
  targetWidth:1920,
  targetHeight:1080,
  frameIndex:7n,
  exactTimeNum:7n,
  exactTimeDen:60n,
  commands:[
    {opcode:O.BEGIN_FRAME},
    {opcode:O.SET_CAMERA,resourceId:1n},
    {opcode:O.DRAW_POINTS,resourceId:2n},
    {opcode:O.END_FRAME}
  ]
});
const before=p.validate(packet);
if(before.commands.length!==4 || !before.compatibilityUnadmitted) process.exit(2);
new Uint8Array(packet)[p.HEADER_BYTES+2*p.COMMAND_BYTES+16]^=1;
try{
  p.validate(packet);
  process.exit(3);
}catch(error){
  if(error.code!=="HHS179_PACKET_FINGERPRINT") throw error;
}
process.stdout.write(JSON.stringify({status:"PASS",commands:before.commands.length}));
"""
    result = subprocess.run(
        [node, "-e", script, str(JS_PACKET)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(result.stdout)
    assert data == {"status": "PASS", "commands": 4}


def test_lane5_frame_submission_uses_immutable_packet_executor() -> None:
    html = LANE5.read_text(encoding="utf-8")
    renderer = JS_RENDERER.read_text(encoding="utf-8")
    packet = JS_PACKET.read_text(encoding="utf-8")

    assert "../../hhs_gui/rendering/hhs_harmonicode_render_packet_v1.js" in html
    assert "new HHSRenderPacket.ResourceRegistry()" in html
    assert "../../hhs_gui/rendering/hhs_harmonicode_render_packet_wasm_v1.js" in html
    assert "nativePacketBuilder=await HHSRenderPacketWasm.create()" in html
    assert "nativePacketBuilder.build({" in html
    assert "HHSRenderPacket.buildCompatibilityPacket({" not in html
    assert "HHSRenderPacket.execute(renderer,packet,renderResources)" in html
    assert "immutableRenderCommandStream:true" in html
    assert 'renderPacketBinaryAuthority:"C11"' in html
    assert "renderPacketProducedByNativeWasm:true" in html
    assert "renderPacketJavaScriptSerialization:false" in html
    assert "renderPacketCompatibilityUnadmitted:true" in html
    assert "renderPacketCanonicalIdentity:false" in html
    assert "renderer.render(scene,camera)" not in html
    assert "renderer.render(postScene,postCamera)" not in html

    for token in (
        "O.SET_TARGET",
        "O.SET_VIEWPORT",
        "O.SET_CAMERA",
        "O.CLEAR",
        "O.DRAW_POINTS",
        "O.BEGIN_COMPOSITE_PASS",
        "O.DRAW_MESHES",
        "O.END_COMPOSITE_PASS",
    ):
        assert token in html

    assert "renderObject(object,camera)" in renderer
    assert 'binaryAuthority:"C11"' in packet
    assert "canonicalMutationAuthority:false" in packet
    assert "hash72CommitAuthority:false" in packet
    assert "hash216IdentityAuthority:false" in packet


def test_freestanding_wasm_bridge_rebuilds_and_instantiates(tmp_path: Path) -> None:
    clang = shutil.which("clang")
    node = shutil.which("node")
    if not clang or not node:
        pytest.skip("clang or Node.js unavailable")
    subprocess.run(
        ["sh", str(WASM_BUILD)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
        env={**__import__("os").environ, "WASM_CC": clang},
    )
    wasm = NATIVE / "build" / "hhs_pass179_render_command_v1.wasm"
    assert wasm.is_file()
    script = r"""
const fs=require("fs");
const bytes=fs.readFileSync(process.argv[1]);
WebAssembly.instantiate(bytes,{}).then(({instance})=>{
  const e=instance.exports;
  if(e.hhs179_wasm_abi_version()!==1) process.exit(2);
  if(e.hhs179_wasm_command_capacity()!==64) process.exit(3);
  if(!e.memory || e.memory.buffer.byteLength<131072) process.exit(4);
  process.stdout.write("PASS");
}).catch(error=>{ console.error(error); process.exit(5); });
"""
    result = subprocess.run(
        [node, "-e", script, str(wasm)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert result.stdout == "PASS"


def test_embedded_native_wasm_builder_enforces_identity_boundary() -> None:
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js unavailable")
    script = r"""
const fs=require("fs");
const vm=require("vm");
vm.runInThisContext(fs.readFileSync(process.argv[1],"utf8"),{filename:process.argv[1]});
vm.runInThisContext(fs.readFileSync(process.argv[2],"utf8"),{filename:process.argv[2]});
const packet=global.HHSRenderPacket;
const wasm=global.HHSRenderPacketWasm;
(async()=>{
  const builder=await wasm.create();
  const O=packet.OPCODE;
  const commands=[
    {opcode:O.BEGIN_FRAME},
    {opcode:O.SET_CAMERA,resourceId:1n},
    {opcode:O.DRAW_POINTS,resourceId:2n},
    {opcode:O.END_FRAME}
  ];
  let missingIdentityRejected=false;
  try{
    builder.build({
      compatibilityUnadmitted:false,
      targetWidth:640,targetHeight:480,
      frameIndex:1n,exactTimeNum:1n,exactTimeDen:60n,
      commands
    });
  }catch(error){
    missingIdentityRejected=
      error.code==="HHS179_WASM_BUILD" &&
      /: 6$/.test(error.message);
  }
  if(!missingIdentityRejected) process.exit(2);

  const identities={
    scene:new Uint8Array(216).fill(1),
    frame:new Uint8Array(216).fill(2),
    resources:new Uint8Array(216).fill(3),
    camera:new Uint8Array(72).fill(4)
  };
  const nativePacket=builder.build({
    compatibilityUnadmitted:false,
    targetWidth:640,targetHeight:480,
    frameIndex:2n,exactTimeNum:2n,exactTimeDen:60n,
    identities,commands
  });
  const decoded=packet.validate(nativePacket);
  if(decoded.compatibilityUnadmitted) process.exit(3);
  if(decoded.commands.length!==4) process.exit(4);

  const compatPacket=builder.build({
    compatibilityUnadmitted:true,
    targetWidth:640,targetHeight:480,
    frameIndex:3n,exactTimeNum:3n,exactTimeDen:60n,
    commands
  });
  if(!packet.validate(compatPacket).compatibilityUnadmitted) process.exit(5);
  process.stdout.write(JSON.stringify({
    status:"PASS",
    wasmSha256:builder.wasmSha256,
    admittedCommands:decoded.commands.length
  }));
})().catch(error=>{ console.error(error); process.exit(6); });
"""
    result = subprocess.run(
        [node, "-e", script, str(JS_PACKET), str(JS_WASM)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(result.stdout)
    assert data["status"] == "PASS"
    assert data["admittedCommands"] == 4
    assert data["wasmSha256"] == (
        "31c34c0d79a5532a340bca5b46347154c6098f9787f2f5f9a147f91b018015af"
    )
