from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .core import ExactRational, canonical_bytes, digest256, write_json


def _header_guard(name: str) -> str:
    return name.upper().replace(".", "_").replace("/", "_").replace("-", "_")


def _write(path: Path, content: str) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = content.replace("\r\n", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return {"path": path.as_posix(), "size": path.stat().st_size, "sha256": digest256({"bytes_hex": path.read_bytes().hex()})}


def generate_parameters(workload: Mapping[str, Any], out_dir: Path) -> list[dict[str, Any]]:
    ratio = workload["stage_ratio"]
    values = workload["shell"]["values"]
    header = """#ifndef HHS_GFCC_GENERATED_PARAMETERS_H
#define HHS_GFCC_GENERATED_PARAMETERS_H
#include <stdint.h>
#define HHS_GFCC_GENERATED_SCHEMA_VERSION 1u
#define HHS_GFCC_GENERATED_INTERPRETATION_VERSION 1u
typedef struct hhs_gfcc_generated_ratio { int64_t numerator; int64_t denominator; } hhs_gfcc_generated_ratio;
extern const int64_t HHS_GFCC_A2;
extern const int64_t HHS_GFCC_B2;
extern const int64_t HHS_GFCC_C2;
extern const int64_t HHS_GFCC_D2;
extern const int64_t HHS_GFCC_E2;
extern const int64_t HHS_GFCC_NUMERATOR_SHELL;
extern const int64_t HHS_GFCC_DENOMINATOR_SHELL;
extern const int64_t HHS_GFCC_TERMINAL_RESIDUAL;
extern const hhs_gfcc_generated_ratio HHS_GFCC_STAGE_RATIO;
#endif
"""
    source = f"""#include \"hhs_gfcc_parameters.h\"
const int64_t HHS_GFCC_A2 = {values['a2']['numerator']};
const int64_t HHS_GFCC_B2 = {values['b2']['numerator']};
const int64_t HHS_GFCC_C2 = {values['c2']['numerator']};
const int64_t HHS_GFCC_D2 = {values['d2']['numerator']};
const int64_t HHS_GFCC_E2 = {values['e2']['numerator']};
const int64_t HHS_GFCC_NUMERATOR_SHELL = {values['e2']['numerator']};
const int64_t HHS_GFCC_DENOMINATOR_SHELL = {values['b4']['numerator']};
const int64_t HHS_GFCC_TERMINAL_RESIDUAL = {values['terminal_residual']['numerator']};
const hhs_gfcc_generated_ratio HHS_GFCC_STAGE_RATIO = {{ {ratio['numerator']}, {ratio['denominator']} }};
"""
    records = [
        _write(out_dir / "hhs_gfcc_parameters.h", header),
        _write(out_dir / "hhs_gfcc_parameters.c", source),
    ]
    return records


def generate_tables(workload: Mapping[str, Any], out_dir: Path) -> list[dict[str, Any]]:
    vm_cells = workload["vm81"]["cells"]
    residues = ",".join(str(cell["nonary_residue"]) for cell in vm_cells)
    phases = ",".join(str(cell["phase_lane"]) for cell in vm_cells)
    rows = ",".join(str(cell["row"]) for cell in vm_cells)
    columns = ",".join(str(cell["column"]) for cell in vm_cells)
    header = """#ifndef HHS_GFCC_GENERATED_TABLES_H
#define HHS_GFCC_GENERATED_TABLES_H
#include <stdint.h>
extern const uint8_t HHS_GFCC_VM81_ROWS[81];
extern const uint8_t HHS_GFCC_VM81_COLUMNS[81];
extern const uint8_t HHS_GFCC_VM81_RESIDUES[81];
extern const uint8_t HHS_GFCC_VM81_PHASE_LANES[81];
extern const uint8_t HHS_GFCC_DELTA369_ZERO_INDEXED[9];
#endif
"""
    source = f"""#include \"hhs_gfcc_tables.h\"
const uint8_t HHS_GFCC_VM81_ROWS[81] = {{{rows}}};
const uint8_t HHS_GFCC_VM81_COLUMNS[81] = {{{columns}}};
const uint8_t HHS_GFCC_VM81_RESIDUES[81] = {{{residues}}};
const uint8_t HHS_GFCC_VM81_PHASE_LANES[81] = {{{phases}}};
const uint8_t HHS_GFCC_DELTA369_ZERO_INDEXED[9] = {{0,3,6,1,4,7,2,5,8}};
"""
    return [
        _write(out_dir / "hhs_gfcc_tables.h", header),
        _write(out_dir / "hhs_gfcc_tables.c", source),
    ]


def generate_vm81_map(workload: Mapping[str, Any], out_dir: Path) -> list[dict[str, Any]]:
    header = """#ifndef HHS_GFCC_GENERATED_VM81_MAP_H
#define HHS_GFCC_GENERATED_VM81_MAP_H
#include <stdint.h>
uint32_t hhs_gfcc_generated_vm81_index(uint32_t row, uint32_t column);
int hhs_gfcc_generated_vm81_inverse(uint32_t index, uint32_t *row, uint32_t *column);
#endif
"""
    source = """#include \"hhs_gfcc_vm81_map.h\"
uint32_t hhs_gfcc_generated_vm81_index(uint32_t row, uint32_t column) {
    return (row < 9u && column < 9u) ? (9u * row + column) : 81u;
}
int hhs_gfcc_generated_vm81_inverse(uint32_t index, uint32_t *row, uint32_t *column) {
    if (!row || !column || index >= 81u) return 0;
    *row = index / 9u; *column = index % 9u; return 1;
}
"""
    return [
        _write(out_dir / "hhs_gfcc_vm81_map.h", header),
        _write(out_dir / "hhs_gfcc_vm81_map.c", source),
    ]


def generate_hash_maps(workload: Mapping[str, Any], out_dir: Path) -> list[dict[str, Any]]:
    hash72 = workload["hash72"]["value"]
    hash216 = workload["hash216"]["value"]
    records: list[dict[str, Any]] = []
    for name, length, value in (("hash72", 72, hash72), ("hash216", 216, hash216)):
        upper = name.upper()
        header = f"""#ifndef HHS_GFCC_GENERATED_{upper}_MAP_H
#define HHS_GFCC_GENERATED_{upper}_MAP_H
#define HHS_GFCC_GENERATED_{upper}_POSITIONS {length}u
extern const char HHS_GFCC_GENERATED_{upper}[{length + 1}];
#endif
"""
        source = f"#include \"hhs_gfcc_{name}_map.h\"\nconst char HHS_GFCC_GENERATED_{upper}[{length + 1}] = \"{value}\";\n"
        records.extend([
            _write(out_dir / f"hhs_gfcc_{name}_map.h", header),
            _write(out_dir / f"hhs_gfcc_{name}_map.c", source),
        ])
    return records


def generate_collision_table(workload: Mapping[str, Any], out_dir: Path) -> list[dict[str, Any]]:
    correction = workload["collision"]["correction"]
    header = """#ifndef HHS_GFCC_GENERATED_COLLISION_TABLE_H
#define HHS_GFCC_GENERATED_COLLISION_TABLE_H
#include <stdint.h>
typedef struct hhs_gfcc_generated_correction { int64_t x_q16; int64_t y_q16; } hhs_gfcc_generated_correction;
extern const hhs_gfcc_generated_correction HHS_GFCC_REPRESENTATIVE_CORRECTION;
#endif
"""
    source = f"#include \"hhs_gfcc_collision_table.h\"\nconst hhs_gfcc_generated_correction HHS_GFCC_REPRESENTATIVE_CORRECTION = {{ {correction['x_q16']}, {correction['y_q16']} }};\n"
    return [
        _write(out_dir / "hhs_gfcc_collision_table.h", header),
        _write(out_dir / "hhs_gfcc_collision_table.c", source),
    ]


def generate_all(workload: Mapping[str, Any], root: Path) -> dict[str, Any]:
    out_dir = root / "generated" / "c"
    records: list[dict[str, Any]] = []
    records.extend(generate_parameters(workload, out_dir))
    records.extend(generate_tables(workload, out_dir))
    records.extend(generate_vm81_map(workload, out_dir))
    records.extend(generate_hash_maps(workload, out_dir))
    records.extend(generate_collision_table(workload, out_dir))
    manifest = {
        "schema": "HHS_GFCC_GENERATED_C_MANIFEST_V1",
        "source_spec_digest": digest256(workload["spec"]),
        "canonical_result_digest": workload["canonical_result_digest"],
        "generator": "python.hhs_gfcc.codegen_c.generate_all",
        "records": records,
    }
    manifest["manifest_digest"] = digest256(manifest)
    write_json(root / "manifest" / "generated_c_manifest.json", manifest)
    return manifest


__all__ = ["generate_all"]
