"""Pass 219 diagnostic proof of canonical admission for the typed BigInt VM81 carrier.

The preceding cycle proved that one exact depth-72 BigInt/phase-qudit state can
be represented as an 81 x 64 VM81 frame and routed through the existing C++ RNA
candidate ABI without mutation authority.  This probe advances only the already
validated frame through the repository's sole public post-219 mutation surface:

    hhs_exact_pass219_vm81_environment_admit_signed

The native helper is intentionally external to the runtime.  It installs the
same deterministic test root used by the inherited PQC boundary tests, builds a
repository-valid UQCEL input, obtains and verifies the genesis Hash216 parent,
and invokes the signed environmental boundary under an OpenSSL provider that
actually supplies ML-DSA-65.

A successful case must return the exact input frame as the committed frame,
verify parent and child Hash216 identities, and show that canonical receipt
ownership remains with the inherited RNA authority.  Environment, firewall,
and signature wrappers may authenticate and gate the transition but must not
self-assign canonical authority.

Negative cases are isolated in fresh native processes and must write an all-zero
committed frame while reporting no canonical receipt ownership.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Mapping

from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    VM81_FRAME_BYTES,
    build_execution_cases,
    raw_le_to_words,
    unpack_vm81_binding_words,
)

PASS = 219
ITERATION = "VM81_RNA_BIGINT_ENVIRONMENT_ADMISSION_PROBE_1_0"
SCHEMA = "HHS_PASS219_VM81_RNA_BIGINT_ENVIRONMENT_ADMISSION_PROBE_V1"
NEGATIVE_MODES = ("constraint", "bad-parent", "missing-input", "bad-pass")


class VM81RNABigIntEnvironmentAdmissionProbeError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise VM81RNABigIntEnvironmentAdmissionProbeError(
            f"FLOAT_ADMISSION_AUTHORITY_FORBIDDEN:{path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _parse_native_output(stdout: str) -> dict[str, int]:
    tokens = stdout.strip().split()
    if not tokens:
        raise VM81RNABigIntEnvironmentAdmissionProbeError("NATIVE_ADMISSION_EMPTY_OUTPUT")
    parsed: dict[str, int] = {}
    for token in tokens:
        if "=" not in token:
            raise VM81RNABigIntEnvironmentAdmissionProbeError("NATIVE_ADMISSION_TOKEN_INVALID")
        key, value = token.split("=", 1)
        if not key or not value:
            raise VM81RNABigIntEnvironmentAdmissionProbeError("NATIVE_ADMISSION_TOKEN_INVALID")
        parsed[key] = int(value)
    return parsed


def run_native_admission(raw: bytes, native_probe: str, mode: str) -> dict[str, Any]:
    probe = Path(native_probe)
    if not probe.is_file():
        raise VM81RNABigIntEnvironmentAdmissionProbeError("NATIVE_ADMISSION_EXECUTABLE_REQUIRED")
    if not isinstance(raw, (bytes, bytearray)) or len(raw) != VM81_FRAME_BYTES:
        raise VM81RNABigIntEnvironmentAdmissionProbeError("RAW_VM5184_MUST_BE_648_BYTES")
    with tempfile.TemporaryDirectory(prefix="hhs-p219-env-admission-") as directory:
        source = Path(directory) / "candidate.bin"
        committed = Path(directory) / "committed.bin"
        source.write_bytes(bytes(raw))
        completed = subprocess.run(
            [str(probe), mode, str(source), str(committed)],
            check=True,
            capture_output=True,
            text=True,
        )
        if not committed.is_file():
            raise VM81RNABigIntEnvironmentAdmissionProbeError("NATIVE_ADMISSION_COMMITTED_FRAME_MISSING")
        committed_raw = committed.read_bytes()
    if len(committed_raw) != VM81_FRAME_BYTES:
        raise VM81RNABigIntEnvironmentAdmissionProbeError("NATIVE_ADMISSION_COMMITTED_FRAME_LENGTH")
    return {
        "native": _parse_native_output(completed.stdout),
        "committed_raw": committed_raw,
    }


def vm81_rna_bigint_environment_admission_probe(
    native_probe: str | None = None,
) -> dict[str, Any]:
    cases = build_execution_cases()
    bigint = int(cases[0]["bigint"])
    positive_rows: list[dict[str, Any]] = []
    negative_rows: list[dict[str, Any]] = []

    if native_probe is not None:
        for case in cases:
            result = run_native_admission(case["raw_bytes"], native_probe, "commit")
            native = result["native"]
            committed_raw = result["committed_raw"]
            restored = unpack_vm81_binding_words(raw_le_to_words(committed_raw))
            positive_rows.append(
                {
                    "opcode": case["opcode"],
                    "lane": case["lane"],
                    "direction": case["direction"],
                    "status": native["status"],
                    "provider_available": native["provider_available"] == 1,
                    "committed_exact": native["committed_exact"] == 1,
                    "committed_bytes_equal_source": committed_raw == case["raw_bytes"],
                    "committed_raw_sha256": sha256(committed_raw).hexdigest(),
                    "reencoded_bigint_exact": restored["bigint"] == bigint,
                    "reencoded_metadata_exact": restored["metadata"]
                    == {
                        "opcode": case["opcode"],
                        "lane": case["lane"],
                        "direction": case["direction"],
                        "source": case["source"],
                        "target": case["target"],
                    },
                    "parent_hash216_verified": native["parent_hash216_verified"] == 1,
                    "child_hash216_verified": native["child_hash216_verified"] == 1,
                    "inherited_rna_authority_invoked": native["inherited_rna_authority_invoked"] == 1,
                    "canonical_receipt_minted": native["canonical_receipt_minted"] == 1,
                    "transition_verified": native["transition_verified"] == 1,
                    "child_identity_matches": native["child_identity_matches"] == 1,
                    "signature_verified": native["signature_verified"] == 1,
                    "environment_verified": native["environment_verified"] == 1,
                    "authority_handoff_exact": native["authority_handoff_exact"] == 1,
                    "environment_witness_sequence": native["environment_witness_sequence"],
                    "signature_length": native["signature_length"],
                }
            )

        reference_raw = cases[0]["raw_bytes"]
        for mode in NEGATIVE_MODES:
            result = run_native_admission(reference_raw, native_probe, mode)
            native = result["native"]
            committed_raw = result["committed_raw"]
            negative_rows.append(
                {
                    "mode": mode,
                    "case": native["case"],
                    "status": native["status"],
                    "failed_closed": native["status"] != 0,
                    "committed_frame_zero": committed_raw == bytes(VM81_FRAME_BYTES),
                    "canonical_receipt_minted": native["canonical_receipt_minted"] == 1,
                    "firewall_decision": native["firewall_decision"],
                    "firewall_halted": native["firewall_halted"] == 1,
                }
            )

    positive_green = bool(positive_rows) and all(
        row["status"] == 0
        and row["provider_available"]
        and row["committed_exact"]
        and row["committed_bytes_equal_source"]
        and row["reencoded_bigint_exact"]
        and row["reencoded_metadata_exact"]
        and row["parent_hash216_verified"]
        and row["child_hash216_verified"]
        and row["inherited_rna_authority_invoked"]
        and row["canonical_receipt_minted"]
        and row["transition_verified"]
        and row["child_identity_matches"]
        and row["signature_verified"]
        and row["environment_verified"]
        and row["authority_handoff_exact"]
        and row["signature_length"] > 0
        for row in positive_rows
    )
    negative_green = bool(negative_rows) and all(
        row["failed_closed"]
        and row["committed_frame_zero"]
        and not row["canonical_receipt_minted"]
        for row in negative_rows
    )

    report = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "input_identity": {
            "bigint": bigint,
            "case_count": len(cases),
            "same_bigint_across_twelve_directional_views": len({case["bigint"] for case in cases}) == 1,
            "all_candidate_frames_distinct": len({case["raw_sha256"] for case in cases}) == len(cases),
        },
        "canonical_admission": {
            "native_probe_supplied": native_probe is not None,
            "positive_case_count": len(positive_rows),
            "all_twelve_signed_environmental_commits_exact": positive_green,
            "committed_frames_reencode_same_bigint": positive_green,
            "typed_pq_qp_metadata_survives_canonical_commit": positive_green,
            "parent_and_child_hash216_verified": positive_green,
            "canonical_receipt_owned_by_inherited_rna_authority": positive_green,
            "environment_and_signature_wrappers_do_not_self_mint_canonical_receipts": positive_green,
            "rows": positive_rows,
        },
        "negative_admission": {
            "case_count": len(negative_rows),
            "all_invalid_prerequisites_fail_closed": negative_green,
            "no_invalid_case_commits_vm81": negative_green,
            "no_invalid_case_mints_canonical_receipt": negative_green,
            "rows": negative_rows,
        },
        "promotion_result": {
            "candidate_to_signed_environmental_admission_bound": positive_green,
            "decode_admit_commit_reencode_exact": positive_green,
            "canonical_vm81_commit_observed_only_through_existing_public_boundary": positive_green,
            "canonical_hash216_receipt_verified": positive_green,
            "tampered_or_incomplete_prerequisites_rejected": negative_green,
            "new_runtime_mutation_primitive_required": False,
            "new_receipt_primitive_required": False,
        },
        "authority": {
            "diagnostic_only": True,
            "existing_environmental_mutator_reused": True,
            "new_canonical_mutation_authority": False,
            "new_canonical_receipt_authority": False,
            "hash72_minting_authority_added": False,
            "hash216_persistence_authority_added": False,
            "floating_point_authority": False,
            "ordered_pq_qp_collapse": False,
        },
    }
    report["report_sha256"] = _digest(report)
    return report


def main() -> None:
    native_probe = os.environ.get("HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE")
    print(
        json.dumps(
            vm81_rna_bigint_environment_admission_probe(native_probe),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
