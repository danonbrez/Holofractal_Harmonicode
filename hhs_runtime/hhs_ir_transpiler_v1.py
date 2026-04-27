"""
HHS IR Transpiler v1
====================

Neutral compiler artifact for translating HARMONICODE IR / branch-equation
manifests into backend source representations.

v1 target support
-----------------
- Python: concrete safe source-string generation for symbolic evaluation packets.
- C: manifest/stub source generation preserving symbols and receipts.
- ASM: manifest/stub source generation preserving symbols and receipts.

This module is side-effect free. It does not execute generated code, write files,
call subprocesses, compile binaries, or perform external actions. It only returns
source strings and Hash72 receipts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List
import json
import re

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


def transpile_to_c_stub(manifest_or_ir: Dict[str, Any]) -> TranspileArtifact:
    fields = _extract_manifest_fields(manifest_or_ir)
    equation = fields["equation_text"].replace("*/", "* /")
    phases = ", ".join(str(p) for p in fields["phases"])
    source = f'''/*
Generated HHS C symbolic manifest stub.
This is a data artifact, not an evaluator.
*/

#ifndef HHS_SYMBOLIC_PACKET_V1_H
#define HHS_SYMBOLIC_PACKET_V1_H

static const char* HHS_EQUATION_TEXT = "{equation.replace('\\', '\\\\').replace('"', '\\"').replace(chr(10), '\\n')}";
static const int HHS_PHASES[] = {{{phases}}};
static const unsigned int HHS_PHASE_COUNT = {len(fields["phases"])};
static const char* HHS_EQUATION_HASH72 = "{fields['equation_hash72']}";
static const char* HHS_PROJECTION_RECEIPT_HASH72 = "{fields['projection_receipt_hash72']}";
static const char* HHS_MANIFEST_HASH72 = "{fields['manifest_hash72']}";

#endif
'''
    h = hash72_digest(("hhs_transpile_c_stub_v1", fields, source), width=24)
    return TranspileArtifact(TranspileTarget.C, source, h, TranspileStatus.HELD, ["Generated C manifest stub only; executable C backend is not implemented in v1."])


def transpile_to_asm_stub(manifest_or_ir: Dict[str, Any]) -> TranspileArtifact:
    fields = _extract_manifest_fields(manifest_or_ir)
    safe_equation = re.sub(r"[^A-Za-z0-9_:=+\-*/^() ,.;{}\[\]<>!ΩΨΔΘxyzu\n]", "?", fields["equation_text"])
    source = f'''; Generated HHS ASM symbolic manifest stub.
; This is a data artifact, not executable machine logic.

section .rodata
hhs_equation_text: db {json.dumps(safe_equation)}, 0
hhs_equation_hash72: db {json.dumps(fields["equation_hash72"])}, 0
hhs_projection_receipt_hash72: db {json.dumps(fields["projection_receipt_hash72"])}, 0
hhs_manifest_hash72: db {json.dumps(fields["manifest_hash72"])}, 0
'''
    h = hash72_digest(("hhs_transpile_asm_stub_v1", fields, source), width=24)
    return TranspileArtifact(TranspileTarget.ASM, source, h, TranspileStatus.HELD, ["Generated ASM manifest stub only; executable ASM backend is not implemented in v1."])


def transpile_manifest(manifest_or_ir: Dict[str, Any], targets: List[str] | None = None) -> TranspileReceipt:
    selected = [TranspileTarget(t) for t in (targets or ["python"])]
    input_hash = hash72_digest(("hhs_transpile_input_v1", manifest_or_ir, [t.value for t in selected]), width=24)
    artifacts: List[TranspileArtifact] = []
    for target in selected:
        if target == TranspileTarget.PYTHON:
            artifacts.append(transpile_to_python(manifest_or_ir))
        elif target == TranspileTarget.C:
            artifacts.append(transpile_to_c_stub(manifest_or_ir))
        elif target == TranspileTarget.ASM:
            artifacts.append(transpile_to_asm_stub(manifest_or_ir))
    receipt = hash72_digest(("hhs_transpile_receipt_v1", input_hash, [a.to_dict() for a in artifacts]), width=24)
    return TranspileReceipt(input_hash, artifacts, receipt)


def main() -> None:
    demo = {"manifest": {"status": "READY", "phases": [4, 12, 20, 36], "equation_text": "xy=-1/yx\nyx=-xy\nxy≠yx", "equation_hash72": "H72-DEMO"}}
    print(json.dumps(transpile_manifest(demo, ["python", "c", "asm"]).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
