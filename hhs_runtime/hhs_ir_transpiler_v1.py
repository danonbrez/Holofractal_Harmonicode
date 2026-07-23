"""
HHS IR Transpiler v1
====================

Neutral compiler artifact for translating HARMONICODE IR / branch-equation
manifests into backend source representations.

v1 target support
-----------------
- Python: concrete safe source-string generation for symbolic evaluation packets.
- C: complete C11 executable source generation.
- ASM: complete x86-64 System V GNU assembly source generation.

Source generation is deterministic. Explicit verification operations compile and execute generated artifacts through the host production toolchain and return observed Hash72 receipts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class TranspileTarget(str, Enum):
    PYTHON = "python"
    C = "c"
    ASM = "asm"


class TranspileStatus(str, Enum):
    GENERATED = "GENERATED"
    HELD = "HELD"
    INVALID = "INVALID"


@dataclass(frozen=True)
class TranspileArtifact:
    target: TranspileTarget
    source: str
    source_hash72: str
    status: TranspileStatus
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["target"] = self.target.value
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class TranspileReceipt:
    input_hash72: str
    artifacts: List[TranspileArtifact]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_hash72": self.input_hash72,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "receipt_hash72": self.receipt_hash72,
        }


def _extract_manifest_fields(manifest_or_ir: Dict[str, Any]) -> Dict[str, Any]:
    manifest = manifest_or_ir.get("manifest") if isinstance(manifest_or_ir.get("manifest"), dict) else manifest_or_ir
    packet = manifest.get("compiler_packet") if isinstance(manifest.get("compiler_packet"), dict) else {}
    equation_text = manifest.get("equation_text") or packet.get("equation_text") or packet.get("root_equation") or manifest.get("equation") or ""
    phases = manifest.get("phases") or packet.get("phases") or []
    equation_hash72 = manifest.get("equation_hash72") or packet.get("equation_hash72") or manifest.get("compression_hash72") or ""
    projection_hash72 = manifest.get("projection_receipt_hash72") or packet.get("projection_receipt_hash72") or ""
    manifest_hash72 = manifest.get("manifest_hash72") or manifest_or_ir.get("aggregate_hash72") or ""
    return {
        "equation_text": str(equation_text),
        "phases": [int(p) for p in phases if str(p).lstrip("-").isdigit()],
        "equation_hash72": str(equation_hash72),
        "projection_receipt_hash72": str(projection_hash72),
        "manifest_hash72": str(manifest_hash72),
        "raw": manifest_or_ir,
    }


def _python_string_literal(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _sanitize_symbolic_equation(equation: str) -> List[str]:
    lines = []
    for raw in equation.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = line.replace("≠", "!=").replace("²", "^2").replace("⁷²", "^72")
        lines.append(line)
    return lines


def transpile_to_python(manifest_or_ir: Dict[str, Any]) -> TranspileArtifact:
    fields = _extract_manifest_fields(manifest_or_ir)
    equation = fields["equation_text"]
    phases = fields["phases"]
    symbolic_lines = _sanitize_symbolic_equation(equation)
    source = f'''"""
Generated HHS Python symbolic packet.
This file is data-first and side-effect free.
It does not evaluate arbitrary code; it exposes the HHS equation as structured data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class HHSSymbolicPacket:
    equation_text: str
    symbolic_lines: List[str]
    phases: List[int]
    equation_hash72: str
    projection_receipt_hash72: str
    manifest_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {{
            "equation_text": self.equation_text,
            "symbolic_lines": self.symbolic_lines,
            "phases": self.phases,
            "equation_hash72": self.equation_hash72,
            "projection_receipt_hash72": self.projection_receipt_hash72,
            "manifest_hash72": self.manifest_hash72,
        }}


PACKET = HHSSymbolicPacket(
    equation_text={_python_string_literal(equation)},
    symbolic_lines={json.dumps(symbolic_lines, ensure_ascii=False)},
    phases={json.dumps(phases)},
    equation_hash72={_python_string_literal(fields["equation_hash72"])},
    projection_receipt_hash72={_python_string_literal(fields["projection_receipt_hash72"])},
    manifest_hash72={_python_string_literal(fields["manifest_hash72"])},
)


def get_packet() -> Dict[str, Any]:
    return PACKET.to_dict()
'''.strip() + "\n"
    h = hash72_digest(("hhs_transpile_python_v1", fields, source), width=24)
    return TranspileArtifact(TranspileTarget.PYTHON, source, h, TranspileStatus.GENERATED, ["Generated side-effect-free Python symbolic packet."])


def _c_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def transpile_to_c(manifest_or_ir: Dict[str, Any]) -> TranspileArtifact:
    fields = _extract_manifest_fields(manifest_or_ir)
    phases = fields["phases"]
    phase_values = ", ".join(str(p) for p in phases) or "0"
    output_format = _c_string('{"target":"c","phase_count":%zu,"phase_sum":%ld,"equation_hash72":"%s","manifest_hash72":"%s"}\n')
    source = f'''/* Generated HHS C11 executable packet. */
#include <stdio.h>
#include <stddef.h>
static const int HHS_PHASES[] = {{{phase_values}}};
static const size_t HHS_PHASE_COUNT = {len(phases)}u;
static const char HHS_EQUATION_HASH72[] = {_c_string(fields['equation_hash72'])};
static const char HHS_MANIFEST_HASH72[] = {_c_string(fields['manifest_hash72'])};
long hhs_phase_sum(void) {{ long total=0; for(size_t i=0;i<HHS_PHASE_COUNT;++i) total+=HHS_PHASES[i]; return total; }}
int main(void) {{
  printf({output_format}, HHS_PHASE_COUNT, hhs_phase_sum(), HHS_EQUATION_HASH72, HHS_MANIFEST_HASH72);
  return 0;
}}
'''
    h = hash72_digest(("hhs_transpile_c11_v1", fields, source), width=24)
    return TranspileArtifact(TranspileTarget.C, source, h, TranspileStatus.GENERATED, ["Generated complete C11 executable packet."])


def _asm_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def transpile_to_asm(manifest_or_ir: Dict[str, Any]) -> TranspileArtifact:
    fields = _extract_manifest_fields(manifest_or_ir)
    phases = fields["phases"]
    phase_longs = ", ".join(str(p) for p in phases) or "0"
    source = f'''.text
.globl hhs_phase_sum
.type hhs_phase_sum, @function
hhs_phase_sum:
    xorq %rax, %rax
    xorq %rcx, %rcx
    leaq hhs_phases(%rip), %rdx
.Lhhs_sum_loop:
    cmpq ${len(phases)}, %rcx
    jae .Lhhs_sum_done
    addq (%rdx,%rcx,8), %rax
    incq %rcx
    jmp .Lhhs_sum_loop
.Lhhs_sum_done:
    ret
.size hhs_phase_sum, .-hhs_phase_sum
.globl hhs_phase_count
.type hhs_phase_count, @function
hhs_phase_count:
    movq ${len(phases)}, %rax
    ret
.size hhs_phase_count, .-hhs_phase_count
.section .rodata
.globl hhs_phases
.align 8
hhs_phases:
    .quad {phase_longs}
.globl hhs_equation_hash72
hhs_equation_hash72:
    .asciz {_asm_quote(fields['equation_hash72'])}
.globl hhs_manifest_hash72
hhs_manifest_hash72:
    .asciz {_asm_quote(fields['manifest_hash72'])}
.section .note.GNU-stack,"",@progbits
'''
    h = hash72_digest(("hhs_transpile_asm_x86_64_v1", fields, source), width=24)
    return TranspileArtifact(TranspileTarget.ASM, source, h, TranspileStatus.GENERATED, ["Generated complete x86-64 System V GNU assembly module."])


def compile_and_execute_artifact(artifact: TranspileArtifact, *, timeout_seconds: int = 20) -> Dict[str, Any]:
    if artifact.status != TranspileStatus.GENERATED:
        raise RuntimeError("artifact is not executable")
    gcc = shutil.which("gcc") or shutil.which("clang")
    if not gcc:
        raise RuntimeError("no C compiler available")
    with tempfile.TemporaryDirectory(prefix="hhs_transpile_") as td:
        work = Path(td); exe = work / "packet"
        if artifact.target == TranspileTarget.C:
            src = work / "packet.c"; src.write_text(artifact.source, encoding="utf-8")
            command = [gcc, "-std=c11", "-Wall", "-Wextra", "-Werror", str(src), "-o", str(exe)]
        elif artifact.target == TranspileTarget.ASM:
            asm = work / "packet.S"; asm.write_text(artifact.source, encoding="utf-8")
            harness = work / "harness.c"
            harness.write_text('#include <stdio.h>\nextern long hhs_phase_sum(void);\nextern long hhs_phase_count(void);\nextern const char hhs_equation_hash72[];\nextern const char hhs_manifest_hash72[];\nint main(void){printf("{\\"target\\":\\"asm\\",\\"phase_count\\":%ld,\\"phase_sum\\":%ld,\\"equation_hash72\\":\\"%s\\",\\"manifest_hash72\\":\\"%s\\"}\\n",hhs_phase_count(),hhs_phase_sum(),hhs_equation_hash72,hhs_manifest_hash72);return 0;}\n', encoding="utf-8")
            command = [gcc, "-std=c11", "-Wall", "-Wextra", "-Werror", str(harness), str(asm), "-o", str(exe)]
        else:
            raise ValueError("compile verification supports only C and ASM")
        compiled = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, check=False)
        if compiled.returncode != 0:
            raise RuntimeError(f"compiler failed: {compiled.stderr.strip()}")
        executed = subprocess.run([str(exe)], capture_output=True, text=True, timeout=timeout_seconds, check=False)
        if executed.returncode != 0:
            raise RuntimeError(f"generated executable failed: {executed.stderr.strip()}")
        observed = json.loads(executed.stdout.strip())
        receipt = {"schema":"HHS_REAL_TRANSPILER_EXECUTION_RECEIPT_V1","target":artifact.target.value,"source_hash72":artifact.source_hash72,"compiler":os.path.realpath(gcc),"compile_command":command,"compiler_returncode":compiled.returncode,"execution_returncode":executed.returncode,"observed":observed,"compiled_and_executed":True}
        receipt["execution_receipt_hash72"] = hash72_digest(("hhs_real_transpiler_execution_v1", receipt), width=24)
        return receipt


def transpile_to_c_stub(manifest_or_ir: Dict[str, Any]) -> TranspileArtifact:
    return transpile_to_c(manifest_or_ir)


def transpile_to_asm_stub(manifest_or_ir: Dict[str, Any]) -> TranspileArtifact:
    return transpile_to_asm(manifest_or_ir)

def transpile_manifest(manifest_or_ir: Dict[str, Any], targets: List[str] | None = None) -> TranspileReceipt:
    selected = [TranspileTarget(t) for t in (targets or ["python"])]
    input_hash = hash72_digest(("hhs_transpile_input_v1", manifest_or_ir, [t.value for t in selected]), width=24)
    artifacts: List[TranspileArtifact] = []
    for target in selected:
        if target == TranspileTarget.PYTHON:
            artifacts.append(transpile_to_python(manifest_or_ir))
        elif target == TranspileTarget.C:
            artifacts.append(transpile_to_c(manifest_or_ir))
        elif target == TranspileTarget.ASM:
            artifacts.append(transpile_to_asm(manifest_or_ir))
    receipt = hash72_digest(("hhs_transpile_receipt_v1", input_hash, [a.to_dict() for a in artifacts]), width=24)
    return TranspileReceipt(input_hash, artifacts, receipt)


def main() -> None:
    demo = {"manifest": {"status": "READY", "phases": [4, 12, 20, 36], "equation_text": "xy=-1/yx\nyx=-xy\nxy≠yx", "equation_hash72": "H72-DEMO"}}
    print(json.dumps(transpile_manifest(demo, ["python", "c", "asm"]).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
