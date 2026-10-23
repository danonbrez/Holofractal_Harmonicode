"""Pass 220 I079 — HARMONICODE tri-layer proof-binding hydration.

This cycle binds three co-resident views of one HARMONICODE computation:

1. exact verbatim algebra sources;
2. a typed reduction/address graph that never replaces the sources;
3. one proof/reconstruction witness that binds both views.

The resulting three Hash72 lanes form one candidate Hash216 identity and are
hydrated through the inherited exact I065 geometry.  HNAN closure is inherited
from I074.  No host-language scalarization, MatrixPower semantics, float
arithmetic, canonical VM81 mutation, Hash72/Hash216 commit, or persistence
authority is introduced.
"""
from __future__ import annotations

from hashlib import sha1, sha256
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    VERBATIM_SOURCE as I074_VERBATIM_SOURCE,
    build_candidate as build_i074_candidate,
    validate_candidate as validate_i074_candidate,
)

SCHEMA = "HHS_PASS_220_I079_HARMONICODE_TRILAYER_PROOF_HYDRATION_V1"
PROFILE = "PASS220-I079-HARMONICODE-TRILAYER-PROOF-HYDRATION-v1"
VERSION = "1.0.0"

HASH72_WIDTH = 72
HASH216_WIDTH = 216
VM81_CELLS = 81
OPERATIONS_PER_CELL = 64
SERIALIZED_CHARACTERS = 5184
FULL_HASH216_COMPONENTS = 3 * SERIALIZED_CHARACTERS

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_A_PATH = (
    "contracts/pass220/"
    "PASS_220_I079_HARMONICODE_SOURCE_A_I_TENSOR_1_0.harmonicode"
)
SOURCE_B_PATH = (
    "contracts/pass220/"
    "PASS_220_I079_HARMONICODE_SOURCE_B_PRIME_CURVATURE_1_0.harmonicode"
)
SOURCE_A_GIT_BLOB_SHA = "c8fd60209339810ad6dcb7952c3aba6c15f70f66"
SOURCE_B_GIT_BLOB_SHA = "d740560374d3cb1f98f1ce7df7b636060609a589"

LEGACY_VERBATIM_PATH = (
    "docs/operations/restart/"
    "PASS_219_PHASE_INVERTED_PYTHAGOREAN_ENTANGLEMENT_THEOREM_RESTART_20260917.md"
)
LEGACY_VERBATIM_GIT_BLOB_SHA = "122d96fa4a68e2adc5a6f9a7b7007e4c03558dfb"

CURVATURE_REGISTRY_PATH = "hhs_spi_scalar_projection_registry_v9.py"
CURVATURE_REGISTRY_GIT_BLOB_SHA = "acf9575e193e1b010ffc28a289065bc47e1348b1"
CURVATURE_REGISTRY_FRAGMENT = (
    "Σ_Δm: c²P(q-p)/(p+q)=a²+b²=(P²-pq)mc²/Δ"
)

GOOD_CLOSED_PATH = (
    "contracts/pass219/PASS_219_LOCAL_CIRCULAR_PHASE_FIBER_INVARIANT_1_0.md"
)
GOOD_CLOSED_GIT_BLOB_SHA = "8fe0b9be693a2262392a16c5374403a592ff18a5"
GOOD_CLOSED_FRAGMENT = (
    "GOOD_CLOSED_k\n"
    "  ~typed-correspondence~\n"
    "closed local circular phase class around Delta_e_k = 0"
)

VM81_SYMBOL_ADAPTER_PATH = (
    "hhs_runtime/include/hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h"
)
VM81_SYMBOL_ADAPTER_GIT_BLOB_SHA = "368a405b480412887423a0ad1321c48c53d52642"

VM81_SYMBOLS = (
    "P",
    "t",
    "p",
    "q",
    "Delta",
    "m",
    "b",
    "c",
    "u",
    "s",
    "x",
    "y",
    "z",
    "w",
    "xy",
    "yx",
    "zw",
    "wz",
    "At",
    "f",
    "Bt",
    "A",
    "B",
    "a2",
)

REDUCTION_MARKERS = (
    ("A", "itensor_left_right_equality", "=={{Mod((56*x*y)"),
    ("A", "rectangular_matrix_power_wz", "MatrixPower({{-w*z,z-w}"),
    ("A", "rectangular_matrix_power_xy", "MatrixPower({{-x*y,y+x}"),
    ("A", "hnan_mod_one_gate", "==0,1)==1"),
    ("B", "prime_gap_curvature", "((q-p)P/(p+q))"),
    ("B", "delta_phase_boundary", "∆/P=√(pq+u⁷²)^x²"),
    ("B", "ordered_phase_sum", "x+y+z+w+xy+yx+zw+wz"),
    (
        "B",
        "bounded_payload",
        "\\frac{(P^{2}-pq)mc^{2}}{\\Delta}",
    ),
)

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "verbatim_sources_authoritative": True,
    "reduction_is_derived_view_only": True,
    "single_proof_binds_verbatim_and_reduction": True,
    "reconstruction_required": True,
    "symbol_cell_address_identity_required": True,
    "lo_shu_nucleus_reference_required": True,
    "uniform_scalar_reduction_authority": False,
    "host_boolean_authority": False,
    "host_modulo_authority": False,
    "host_division_by_zero_authority": False,
    "host_rectangular_matrixpower_authority": False,
    "host_float_arithmetic_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "external_egress_authority": False,
}


class Pass220I079Error(ValueError):
    """Raised when the I079 tri-layer proof-binding invariant fails."""


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I079Error(f"floating-point value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return sha1(header + raw).hexdigest()


def _read_bound_source(relative_path: str, expected_blob_sha: str) -> str:
    raw = (REPO_ROOT / relative_path).read_bytes()
    actual = _git_blob_sha(raw)
    if actual != expected_blob_sha:
        raise Pass220I079Error(
            f"source blob drift at {relative_path}: {actual} != {expected_blob_sha}"
        )
    return raw.decode("utf-8")


def _reference_fragment_witness(
    relative_path: str,
    expected_blob_sha: str,
    fragment: str,
) -> dict[str, Any]:
    text = _read_bound_source(relative_path, expected_blob_sha)
    count = text.count(fragment)
    if count != 1:
        raise Pass220I079Error(
            f"reference fragment occurrence drift at {relative_path}: {count}"
        )
    return {
        "path": relative_path,
        "git_blob_sha": expected_blob_sha,
        "fragment": fragment,
        "fragment_sha256": sha256(fragment.encode("utf-8")).hexdigest(),
        "occurrences": count,
    }


def verbatim_layer() -> dict[str, Any]:
    source_a = _read_bound_source(SOURCE_A_PATH, SOURCE_A_GIT_BLOB_SHA)
    source_b = _read_bound_source(SOURCE_B_PATH, SOURCE_B_GIT_BLOB_SHA)

    legacy = _read_bound_source(
        LEGACY_VERBATIM_PATH,
        LEGACY_VERBATIM_GIT_BLOB_SHA,
    )
    if "COMPLEX INFINITY=(P²=pq+((q-p)P/(p+q))" not in legacy:
        raise Pass220I079Error("legacy verbatim ancestry marker missing")

    curvature = _reference_fragment_witness(
        CURVATURE_REGISTRY_PATH,
        CURVATURE_REGISTRY_GIT_BLOB_SHA,
        CURVATURE_REGISTRY_FRAGMENT,
    )
    good_closed = _reference_fragment_witness(
        GOOD_CLOSED_PATH,
        GOOD_CLOSED_GIT_BLOB_SHA,
        GOOD_CLOSED_FRAGMENT,
    )
    adapter = _read_bound_source(
        VM81_SYMBOL_ADAPTER_PATH,
        VM81_SYMBOL_ADAPTER_GIT_BLOB_SHA,
    )
    if "HHS_EXACT_PASS219_VM81_SYMBOL_COUNT 24U" not in adapter:
        raise Pass220I079Error("24-symbol VM81 adapter contract drift")

    layer = {
        "schema": f"{SCHEMA}_VERBATIM_LAYER_V1",
        "sources": {
            "A": {
                "path": SOURCE_A_PATH,
                "git_blob_sha": SOURCE_A_GIT_BLOB_SHA,
                "sha256": sha256(source_a.encode("utf-8")).hexdigest(),
                "text": source_a,
            },
            "B": {
                "path": SOURCE_B_PATH,
                "git_blob_sha": SOURCE_B_GIT_BLOB_SHA,
                "sha256": sha256(source_b.encode("utf-8")).hexdigest(),
                "text": source_b,
            },
        },
        "legacy_ancestry": {
            "path": LEGACY_VERBATIM_PATH,
            "git_blob_sha": LEGACY_VERBATIM_GIT_BLOB_SHA,
        },
        "curvature_projection_registry": curvature,
        "good_closed_correspondence": good_closed,
        "vm81_symbol_adapter": {
            "path": VM81_SYMBOL_ADAPTER_PATH,
            "git_blob_sha": VM81_SYMBOL_ADAPTER_GIT_BLOB_SHA,
            "symbol_count": len(VM81_SYMBOLS),
        },
        "i074_verbatim_source_sha256": sha256(
            I074_VERBATIM_SOURCE.encode("utf-8")
        ).hexdigest(),
        "source_replacement_allowed": False,
    }
    layer["layer_sha256"] = _sha256(layer)
    return layer


def symbol_address_witness() -> tuple[dict[str, Any], ...]:
    if len(VM81_SYMBOLS) != 24:
        raise Pass220I079Error("VM81 symbol count drift")
    rows: list[dict[str, Any]] = []
    for cell81, symbol in enumerate(VM81_SYMBOLS):
        start = OPERATIONS_PER_CELL * cell81
        end_exclusive = start + OPERATIONS_PER_CELL
        if not (0 <= cell81 < VM81_CELLS):
            raise Pass220I079Error("symbol VM81 cell out of range")
        if not (0 <= start < end_exclusive <= SERIALIZED_CHARACTERS):
            raise Pass220I079Error("symbol BigInt block out of range")
        rows.append(
            {
                "symbol": symbol,
                "symbol_index": cell81,
                "cell81": cell81,
                "bigint_5184_block_start": start,
                "bigint_5184_block_end_exclusive": end_exclusive,
                "bigint_5184_block_width": OPERATIONS_PER_CELL,
                "within_cell_operation_selector": "PRESERVED_BY_CONSTRUCTOR",
                "uniform_scalar_identity": False,
                "lo_shu_nucleus_reference_required": True,
            }
        )
    return tuple(rows)


def _source_span_witnesses(sources: Mapping[str, str]) -> tuple[dict[str, Any], ...]:
    spans: list[dict[str, Any]] = []
    for source_key, node_id, marker in REDUCTION_MARKERS:
        text = sources[source_key]
        count = text.count(marker)
        if count != 1:
            raise Pass220I079Error(
                f"reduction marker {node_id} occurrence drift: {count}"
            )
        start = text.index(marker)
        spans.append(
            {
                "node_id": node_id,
                "source_key": source_key,
                "marker": marker,
                "start_character": start,
                "end_character_exclusive": start + len(marker),
                "source_sha256": sha256(text.encode("utf-8")).hexdigest(),
                "derived_view_only": True,
                "source_replacement_allowed": False,
            }
        )
    return tuple(spans)


def reduction_layer(verbatim: Mapping[str, Any]) -> dict[str, Any]:
    sources = {
        key: value["text"]
        for key, value in verbatim["sources"].items()
    }
    addresses = symbol_address_witness()
    spans = _source_span_witnesses(sources)

    a2 = next(row for row in addresses if row["symbol"] == "a2")
    lo_shu_anchor = {
        "symbol": "a2",
        "scalar_projection": 1,
        "lo_shu_value": 1,
        "lo_shu_position_1based": (3, 2),
        "lo_shu_local_index_0based": 7,
        "vm81_symbol_cell81": a2["cell81"],
        "bigint_5184_block_start": a2["bigint_5184_block_start"],
        "scope": "SOURCE_PROVED_POSITIONAL_ANCHOR_ONLY",
    }

    layer = {
        "schema": f"{SCHEMA}_REDUCTION_LAYER_V1",
        "source_span_witnesses": spans,
        "symbol_addresses": addresses,
        "lo_shu_nucleus_anchor": lo_shu_anchor,
        "address_law": "linear5184=64*cell81+operation64",
        "address_domain": {
            "cell81": (0, 80),
            "operation64": (0, 63),
            "linear5184": (0, 5183),
        },
        "phase_order": ("x", "y", "z", "w", "xy", "yx", "zw", "wz"),
        "phase_inversion_pairs": (
            ("xy", "yx"),
            ("zw", "wz"),
            ("A:a", "B:b"),
            ("A:b", "B:a"),
        ),
        "g3_scaling": {
            "base": (1, 2, 3),
            "lifted": (4, 7, 11),
            "relation": "a²+b²=c²",
            "outer_binding": "AB=P⁴=(a²+b²)⁶/c⁴",
            "uniform_scalar_reduction_forbidden": True,
        },
        "reconstructs_only_with_verbatim_layer": True,
        "source_replacement_allowed": False,
    }
    layer["layer_sha256"] = _sha256(layer)
    return layer


def proof_layer(
    verbatim: Mapping[str, Any],
    reduction: Mapping[str, Any],
    i074: Mapping[str, Any],
) -> dict[str, Any]:
    source_hash72 = hash72(verbatim)
    reduction_hash72 = hash72(reduction)
    proof = {
        "schema": f"{SCHEMA}_PROOF_LAYER_V1",
        "proof_id": "PASS220-I079-TRILAYER-BINDING-1",
        "verbatim_layer_hash72": source_hash72,
        "reduction_layer_hash72": reduction_hash72,
        "same_proof_binds_both_layers": True,
        "reconstruction": {
            "source_a_sha256": verbatim["sources"]["A"]["sha256"],
            "source_b_sha256": verbatim["sources"]["B"]["sha256"],
            "source_a_blob_sha": verbatim["sources"]["A"]["git_blob_sha"],
            "source_b_blob_sha": verbatim["sources"]["B"]["git_blob_sha"],
            "source_bytes_retained": True,
            "reduction_spans_source_bound": True,
            "symbol_addresses_retained": True,
        },
        "hnan_inheritance": {
            "i074_candidate_hash216": i074["candidate_hash216"],
            "i074_binding_hash72": i074["binding_hash72"],
            "i074_closure_readout": i074["closure"]["closure_readout"],
            "native_hnan_gate": i074["authority"]["hnan_gate_native"],
        },
        "formal_surfaces": {
            "lean_module": "HHS.Pass220.I079",
            "wolfram_source": (
                "formal/wolfram/"
                "pass220_i079_harmonicode_trilayer_proof_hydration_v1.wl"
            ),
            "connected_wolfram_evidence_claimed": False,
        },
        "ethical_attractor": {
            "name": "GOOD_CLOSED",
            "binding": GOOD_CLOSED_FRAGMENT,
            "typed_correspondence_only": True,
            "scalar_orbital_variable": False,
        },
        "physics_constraint_policy": {
            "quantum_computation_evidence_may_constrain_hydration": True,
            "relativistic_geometry_evidence_may_constrain_hydration": True,
            "whitepaper_corpus_may_constrain_hydration": True,
            "formal_validity_does_not_by_itself_claim_external_empirical_truth": True,
        },
        "no_translation_without_computational_proof": True,
        "no_scalar_replacement": True,
        "no_order_erasure": True,
        "no_address_erasure": True,
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    proof["proof_core_sha256"] = _sha256(proof)
    return proof


def build_candidate() -> dict[str, Any]:
    i074 = build_i074_candidate()
    if not validate_i074_candidate(i074):
        raise Pass220I079Error("I074 HNAN parent validation failed")

    verbatim = verbatim_layer()
    reduction = reduction_layer(verbatim)
    proof = proof_layer(verbatim, reduction, i074)

    source_hash72 = hash72(verbatim)
    reduction_hash72 = hash72(reduction)
    proof_hash72 = hash72(proof)
    candidate_hash216 = source_hash72 + reduction_hash72 + proof_hash72
    if len(candidate_hash216) != HASH216_WIDTH:
        raise Pass220I079Error("tri-layer Hash216 width drift")

    hydrated = hydrate_hash216_geometry(candidate_hash216)
    if hydrated.get("roundtrip_exact") is not True:
        raise Pass220I079Error("Hash216 hydration roundtrip failed")
    if hydrated.get("full_attached_components") != FULL_HASH216_COMPONENTS:
        raise Pass220I079Error("Hash216 hydrated component count drift")

    candidate = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "layers": {
            "verbatim": verbatim,
            "reduction": reduction,
            "proof": proof,
        },
        "hash72_lanes": {
            "verbatim": source_hash72,
            "reduction": reduction_hash72,
            "proof_reconstruction": proof_hash72,
        },
        "candidate_hash216": candidate_hash216,
        "hydration": {
            "roundtrip_exact": hydrated["roundtrip_exact"],
            "full_attached_components": hydrated["full_attached_components"],
            "expanded_geometry_persisted": False,
            "reconstructible_on_demand": True,
        },
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    candidate["candidate_root_sha256"] = _sha256(candidate)
    candidate["binding_hash72"] = hash72(
        {
            "schema": SCHEMA,
            "candidate_root_sha256": candidate["candidate_root_sha256"],
            "candidate_hash216": candidate_hash216,
            "i074_binding_hash72": i074["binding_hash72"],
            "good_closed_binding": GOOD_CLOSED_FRAGMENT,
        }
    )
    return candidate


def reconstruct_verbatim(
    candidate: Mapping[str, Any],
) -> tuple[str, str]:
    layer = candidate["layers"]["verbatim"]
    return (layer["sources"]["A"]["text"], layer["sources"]["B"]["text"])


def validate_candidate(candidate: Mapping[str, Any]) -> bool:
    if not isinstance(candidate, Mapping) or candidate.get("schema") != SCHEMA:
        raise Pass220I079Error("candidate schema mismatch")
    _reject_float(candidate)
    canonical = build_candidate()
    if candidate != canonical:
        raise Pass220I079Error("candidate diverges from canonical I079 binding")
    source_a, source_b = reconstruct_verbatim(candidate)
    if sha256(source_a.encode("utf-8")).hexdigest() != (
        candidate["layers"]["verbatim"]["sources"]["A"]["sha256"]
    ):
        raise Pass220I079Error("source A reconstruction mismatch")
    if sha256(source_b.encode("utf-8")).hexdigest() != (
        candidate["layers"]["verbatim"]["sources"]["B"]["sha256"]
    ):
        raise Pass220I079Error("source B reconstruction mismatch")
    return True


def self_test() -> dict[str, Any]:
    candidate = build_candidate()
    addresses = candidate["layers"]["reduction"]["symbol_addresses"]
    proof = candidate["layers"]["proof"]
    source_a, source_b = reconstruct_verbatim(candidate)
    checks = {
        "candidate_valid": validate_candidate(candidate),
        "two_verbatim_sources_retained": bool(source_a) and bool(source_b),
        "three_hash72_lanes": len(candidate["hash72_lanes"]) == 3,
        "hash216_width_216": len(candidate["candidate_hash216"]) == HASH216_WIDTH,
        "hash216_is_three_lanes": candidate["candidate_hash216"] == "".join(
            candidate["hash72_lanes"][key]
            for key in ("verbatim", "reduction", "proof_reconstruction")
        ),
        "symbol_count_24": len(addresses) == 24,
        "symbol_cells_exact": tuple(row["cell81"] for row in addresses)
        == tuple(range(24)),
        "symbol_bigint_blocks_exact": all(
            row["bigint_5184_block_start"] == 64 * row["cell81"]
            and row["bigint_5184_block_end_exclusive"]
            == 64 * (row["cell81"] + 1)
            for row in addresses
        ),
        "a2_lo_shu_anchor_exact": (
            candidate["layers"]["reduction"]["lo_shu_nucleus_anchor"][
                "lo_shu_position_1based"
            ]
            == (3, 2)
            and candidate["layers"]["reduction"]["lo_shu_nucleus_anchor"][
                "lo_shu_local_index_0based"
            ]
            == 7
        ),
        "reduction_spans_source_bound": all(
            row["source_replacement_allowed"] is False
            for row in candidate["layers"]["reduction"]["source_span_witnesses"]
        ),
        "same_proof_binds_both": proof["same_proof_binds_both_layers"] is True,
        "reconstruction_retains_source": (
            proof["reconstruction"]["source_bytes_retained"] is True
        ),
        "hnan_inherited": proof["hnan_inheritance"]["native_hnan_gate"] is True,
        "good_closed_typed_only": (
            proof["ethical_attractor"]["typed_correspondence_only"] is True
            and proof["ethical_attractor"]["scalar_orbital_variable"] is False
        ),
        "no_translation_without_proof": (
            proof["no_translation_without_computational_proof"] is True
        ),
        "hydration_roundtrip_exact": candidate["hydration"]["roundtrip_exact"],
        "hydration_components_15552": (
            candidate["hydration"]["full_attached_components"]
            == FULL_HASH216_COMPONENTS
        ),
        "candidate_only": candidate["authority"]["candidate_only"] is True,
        "no_vm81_mutation_authority": (
            candidate["authority"]["canonical_vm81_mutation_authority"] is False
        ),
        "no_hash216_commit_authority": (
            candidate["authority"]["canonical_hash216_commit_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "checks": checks,
        "candidate_root_sha256": candidate["candidate_root_sha256"],
        "binding_hash72": candidate["binding_hash72"],
        "candidate_hash216": candidate["candidate_hash216"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "CURVATURE_REGISTRY_FRAGMENT",
    "GOOD_CLOSED_FRAGMENT",
    "Pass220I079Error",
    "SCHEMA",
    "SOURCE_A_GIT_BLOB_SHA",
    "SOURCE_A_PATH",
    "SOURCE_B_GIT_BLOB_SHA",
    "SOURCE_B_PATH",
    "VM81_SYMBOLS",
    "build_candidate",
    "proof_layer",
    "reconstruct_verbatim",
    "reduction_layer",
    "self_test",
    "symbol_address_witness",
    "validate_candidate",
    "verbatim_layer",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
