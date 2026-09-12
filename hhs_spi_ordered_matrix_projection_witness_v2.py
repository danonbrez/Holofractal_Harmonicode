"""Pass 219 SPI O2 ordered-matrix projection witness v2.

Additive successor to O2 witness v1.  It retains the source-bound matrix-defined
scalar projection ``a² -> 1`` and adds the HARMONICODE symmetric unit-product
surface rule.  Once the derived 3x3 magnitude surface is proven symmetric and
all nine projected cells close to unit, it emits a new projection layer
``a²=xy=1``.

The layer is projection-only.  It does not assert native ``a² ≡ xy``, commute
``xy/yx``, or replace the native ordered matrix/tensor surface.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from hhs_spi_ordered_matrix_projection_witness_v1 import (
    AUDITED_MAIN_SHA,
    PROJECTION_SOURCE,
    ordered_matrix_projection_witness,
)
from hhs_spi_symmetric_unit_product_projection_rule_v1 import (
    PROFILE as SYMMETRIC_UNIT_PROFILE,
    symmetric_unit_product_projection,
)

FORMAT = "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_WITNESS_V2"
VERSION = "2.0.0"
SCHEMA = "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_WITNESS_V2"
PASS129_REPORT_PATH = "PASS_129_PROOF_TESTING_ANALYSIS_REPORT.json"
PASS129_XY_UNIT_CLAIM = "the three-way membrane closes at residue 1 when xy=zw=1 and x+y+z+w=0"
DERIVED_ALL_ONES_SURFACE = "((1,1,1),(1,1,1),(1,1,1))"


class SPIO2MatrixProjectionV2Error(ValueError):
    pass


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parent


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _pass129_xy_unit_precedent(repo_root: Path) -> Dict[str, Any]:
    path = repo_root / PASS129_REPORT_PATH
    source = path.read_text(encoding="utf-8")
    if PASS129_XY_UNIT_CLAIM not in source:
        raise SPIO2MatrixProjectionV2Error("Pass129 xy=1 projection precedent drifted")
    return {
        "path": PASS129_REPORT_PATH,
        "source_sha256": sha256(source.encode("utf-8")).hexdigest(),
        "claim": PASS129_XY_UNIT_CLAIM,
        "xy_projection_unit": 1,
        "native_xy_yx_identity_claimed": False,
    }


def _symmetric_unit_layer(v1: Mapping[str, Any], repo_root: Path) -> Dict[str, Any]:
    topology = v1["ordered_matrix_topology"]
    if topology["outer_cell_count"] != 8 or topology["outer_phase_alignment_exact"] is not True:
        raise SPIO2MatrixProjectionV2Error("O2 outer unit topology is incomplete")
    if topology["all_nine_topology_cells_witnessed"] is not True:
        raise SPIO2MatrixProjectionV2Error("O2 nine-cell topology is incomplete")
    center = topology["center"]
    if center["native_closure"] != "0/0=u^0 mod(u^72)=1":
        raise SPIO2MatrixProjectionV2Error("O2 center unit closure drifted")
    if center["ordinary_zero_division_executed"] is not False:
        raise SPIO2MatrixProjectionV2Error("O2 center attempted ordinary 0/0 division")

    # After the eight exact unit perimeter projections and the separately typed
    # unit center closure, the magnitude projection is the exact all-ones 3x3
    # surface.  Standard transpose symmetry supplies six complete involution
    # orbits covering all nine cells exactly once.
    orbits = (
        {"orbit_id": "diag-00", "members": ("00",), "product": 1, "involution_closed": True},
        {"orbit_id": "diag-11", "members": ("11",), "product": 1, "involution_closed": True},
        {"orbit_id": "diag-22", "members": ("22",), "product": 1, "involution_closed": True},
        {"orbit_id": "transpose-01", "members": ("01", "10"), "product": 1, "involution_closed": True},
        {"orbit_id": "transpose-02", "members": ("02", "20"), "product": 1, "involution_closed": True},
        {"orbit_id": "transpose-12", "members": ("12", "21"), "product": 1, "involution_closed": True},
    )
    layer = symmetric_unit_product_projection(
        surface_id="HHCQ:E_a2:O2:DERIVED_MAGNITUDE_3X3",
        surface_source=DERIVED_ALL_ONES_SURFACE,
        symmetry_orbits=orbits,
        total_component_count=9,
        profile_id=SYMMETRIC_UNIT_PROFILE,
    )
    return {
        "projection_source": PROJECTION_SOURCE,
        "derived_unit_surface": DERIVED_ALL_ONES_SURFACE,
        "derivation": [
            "eight ordered perimeter phase correspondences project exactly to unit",
            "native center constraint intersection projects separately to unit without ordinary 0/0 division",
            "therefore the complete 3x3 magnitude projection contains nine exact unit cells",
            "the all-ones 3x3 projection is symmetric under transpose",
            "all six transpose/fixed-point symmetry orbit products are exactly 1",
            "emit the new scalar projection layer a²=xy=1",
        ],
        "pass129_xy_unit_precedent": _pass129_xy_unit_precedent(repo_root),
        "unit_layer_receipt": layer,
    }


def ordered_matrix_projection_witness_v2(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = _repo_root(repo_root)
    v1 = ordered_matrix_projection_witness(root)
    exact_one = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    if v1["result"]["matrix_branch_projection"] != exact_one:
        raise SPIO2MatrixProjectionV2Error("O2 v1 matrix-defined scalar projection is not unit")

    symmetric = _symmetric_unit_layer(v1, root)
    unit_layer = symmetric["unit_layer_receipt"]
    if unit_layer["projection_layer"]["relation"] != "a²=xy=1":
        raise SPIO2MatrixProjectionV2Error("symmetric unit layer relation drifted")
    if unit_layer["native_a2_xy_identity_authorized"] is not False:
        raise SPIO2MatrixProjectionV2Error("symmetric unit layer promoted projection equality to native identity")
    if unit_layer["xy_yx_commutation_authorized"] is not False:
        raise SPIO2MatrixProjectionV2Error("symmetric unit layer commuted xy/yx")

    witness: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_witness_sha256": v1["witness_sha256"],
        "matrix_defined_scalar_projection": v1["defined_scalar_projection"],
        "symmetric_unit_product_surface": symmetric,
        "projection_layers": [
            {
                "layer_id": "O2:a²-defined-scalar",
                "relation": "a²=1",
                "basis": "source-bound matrix/tensor definition edge",
            },
            {
                "layer_id": "O2:symmetric-unit-product",
                "relation": "a²=xy=1",
                "basis": SYMMETRIC_UNIT_PROFILE,
            },
        ],
        "result": {
            "a²": exact_one,
            "xy": exact_one,
            "relation": "a²=xy=1",
            "relation_kind": "SCALAR_PROJECTION_LAYER_ONLY",
        },
        "generic_matrix_tensor_scalarization_authorized": False,
        "symmetry_plus_all_unit_products_required": True,
        "native_a2_xy_identity_authorized": False,
        "xy_yx_commutation_authorized": False,
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    witness["witness_sha256"] = _digest(witness)
    return witness


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors = []
    try:
        witness = ordered_matrix_projection_witness_v2(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_VALIDATION_V2",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }
    unit = witness["symmetric_unit_product_surface"]["unit_layer_receipt"]
    if unit["symmetry_complete"] is not True or unit["all_orbit_products_unit"] is not True:
        errors.append("symmetric unit-product surface did not close")
    if unit["covered_component_count"] != 9:
        errors.append("symmetric unit-product coverage is not nine cells")
    if witness["result"]["relation"] != "a²=xy=1":
        errors.append("unit projection layer relation is incorrect")
    if witness["native_a2_xy_identity_authorized"] or witness["xy_yx_commutation_authorized"]:
        errors.append("projection layer leaked into native identity/order authority")
    return {
        "schema": "HHS_SPI_O2_ORDERED_MATRIX_PROJECTION_VALIDATION_V2",
        "ok": not errors,
        "witness_sha256": witness["witness_sha256"],
        "projection_relation": witness["result"]["relation"],
        "symmetric_unit_profile": SYMMETRIC_UNIT_PROFILE,
        "canonical_admission_authority": False,
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--manifest", action="store_true")
    args = parser.parse_args(argv)
    if args.validate:
        report = validation_report()
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if report["ok"] else 1
    print(json.dumps(ordered_matrix_projection_witness_v2(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
