"""Pass 220 I048: I047 native-library constructor binding + interpreter bridge.

This layer consumes validated I047 training records.  It does not inspect or
execute foreign machine code.  It creates deterministic native-constructor
binding candidates, preserves the external ABI/codec/type membrane, and
interprets only source-observed reference vectors exactly.  Unseen inputs and
stateful/IO/opaque entrypoints fail closed into an explicit runtime-admission
plan rather than fabricating results.

Canonical VM81 mutation, Hash72 mint, Hash216 persistence, Lane 5 scheduling,
and generalized native-constructor execution remain downstream authorities.
"""
from __future__ import annotations

import base64
import binascii
import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_compiler_ir_v1 import build_compiled_artifact
from hhs_runtime.hhs_pass220_i047_native_library_training_dataset_v1 import (
    REFERENCE_ORIGIN,
    Pass220I047DatasetError,
    build_library_training_record,
    typed_value_from_bytes,
    validate_library_training_record,
)

SCHEMA = "HHS_PASS_220_I048_NATIVE_LIBRARY_CONSTRUCTOR_BINDING_V1"
REGISTRY_SCHEMA = "HHS_PASS_220_I048_NATIVE_LIBRARY_CONSTRUCTOR_REGISTRY_V1"
PLAN_SCHEMA = "HHS_PASS_220_I048_HARMONICODE_LIBRARY_INTERPRETER_PLAN_V1"
EQUIVALENCE_SCHEMA = "HHS_PASS_220_I048_CONSTRUCTOR_EQUIVALENCE_WITNESS_V1"
VERSION = "1.0.0"
I047_SCHEMA = "HHS_PASS_220_I047_NATIVE_LIBRARY_TRAINING_RECORD_V1"
REFERENCE_REPLAY_EFFECTS = {"PURE", "READ_ONLY"}


class Pass220I048InterpreterError(ValueError):
    pass


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _sha(value: Any) -> str:
    return sha256(_stable(value).encode("utf-8")).hexdigest()


def _binding_id(record: Mapping[str, Any], entrypoint_id: str) -> str:
    return "constructor:" + sha256(
        (
            str(record["record_sha256"])
            + ":"
            + str(entrypoint_id)
        ).encode("utf-8")
    ).hexdigest()[:32]


def _entrypoint(record: Mapping[str, Any], entrypoint_id: str) -> Mapping[str, Any]:
    for entry in record["metadata"]["entrypoints"]:
        if entry["entrypoint_id"] == entrypoint_id:
            return entry
    raise Pass220I048InterpreterError(
        f"entrypoint not declared: {entrypoint_id}"
    )


def _normalize_typed_input(
    value: Mapping[str, Any],
    port: Mapping[str, Any],
    *,
    index: int,
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise Pass220I048InterpreterError(
            f"input[{index}] must be a typed mapping"
        )
    try:
        encoded = str(value["payload_base64"])
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
    except (KeyError, UnicodeEncodeError, binascii.Error) as exc:
        raise Pass220I048InterpreterError(
            f"input[{index}] invalid payload_base64"
        ) from exc
    if value.get("byte_length") != len(raw):
        raise Pass220I048InterpreterError(
            f"input[{index}] byte length mismatch"
        )
    if value.get("payload_sha256") != sha256(raw).hexdigest():
        raise Pass220I048InterpreterError(
            f"input[{index}] payload hash mismatch"
        )
    if (
        value.get("data_type"),
        value.get("encoding"),
    ) != (
        port.get("data_type"),
        port.get("encoding"),
    ):
        raise Pass220I048InterpreterError(
            f"input[{index}] external type/encoding drift"
        )
    normalized = {
        "data_type": value["data_type"],
        "encoding": value["encoding"],
        "byte_length": len(raw),
        "payload_base64": base64.b64encode(raw).decode("ascii"),
        "payload_sha256": sha256(raw).hexdigest(),
    }
    if "semantic_value" in value:
        normalized["semantic_value"] = value["semantic_value"]
    return normalized


def _payload_identity(value: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        value.get("data_type"),
        value.get("encoding"),
        value.get("byte_length"),
        value.get("payload_sha256"),
        value.get("payload_base64"),
    )


def _binding_source_text(
    record: Mapping[str, Any],
    entrypoint: Mapping[str, Any],
) -> str:
    descriptor = {
        "operation": "IMPORT_NATIVE_LIBRARY_CONSTRUCTOR",
        "library_id": record["library_id"],
        "record_sha256": record["record_sha256"],
        "source_sha256": record["source"]["sha256"],
        "architecture": record["metadata"]["architecture"],
        "abi": record["metadata"]["abi"],
        "entrypoint_id": entrypoint["entrypoint_id"],
        "symbol": entrypoint["symbol"],
        "inputs": entrypoint["inputs"],
        "outputs": entrypoint["outputs"],
        "ingress_encoder_id": record["metadata"]["codec_boundary"][
            "ingress_encoder_id"
        ],
        "egress_decoder_id": record["metadata"]["codec_boundary"][
            "egress_decoder_id"
        ],
        "side_effect_class": entrypoint["side_effect_class"],
        "constructor_dependencies": entrypoint[
            "constructor_dependencies"
        ],
        "phase_relationships": entrypoint["phase_relationships"],
        "timing_constraints": entrypoint["timing_constraints"],
        "vm81_relationships": entrypoint["vm81_relationships"],
        "rna_relationships": entrypoint["rna_relationships"],
    }
    return _stable(descriptor)


def build_native_constructor_binding(
    record: Mapping[str, Any],
    entrypoint_id: str,
) -> dict[str, Any]:
    try:
        validate_library_training_record(record)
    except Pass220I047DatasetError as exc:
        raise Pass220I048InterpreterError(str(exc)) from exc
    entry = _entrypoint(record, entrypoint_id)
    artifact = build_compiled_artifact(
        f"library:{record['library_id']}:{entrypoint_id}",
        _binding_source_text(record, entry),
        "HHS_IR",
    )
    if not artifact.get("ok") or artifact.get("execution_authorized"):
        raise Pass220I048InterpreterError(
            "compiler IR boundary did not remain read-only"
        )
    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "binding_id": _binding_id(record, entrypoint_id),
        "source_i047_schema": I047_SCHEMA,
        "source_record_sha256": record["record_sha256"],
        "source_library_sha256": record["source"]["sha256"],
        "relationship_root_sha256": record["relationship_root_sha256"],
        "library_id": record["library_id"],
        "library_format": record["metadata"]["library_format"],
        "architecture": record["metadata"]["architecture"],
        "abi": record["metadata"]["abi"],
        "entrypoint_id": entry["entrypoint_id"],
        "symbol": entry["symbol"],
        "inputs": tuple(entry["inputs"]),
        "outputs": tuple(entry["outputs"]),
        "side_effect_class": entry["side_effect_class"],
        "state_boundary": entry["state_boundary"],
        "math_operator_identities": tuple(
            entry["math_operator_identities"]
        ),
        "constructor_dependencies": tuple(
            entry["constructor_dependencies"]
        ),
        "phase_relationships": tuple(entry["phase_relationships"]),
        "timing_constraints": tuple(entry["timing_constraints"]),
        "vm81_relationships": tuple(entry["vm81_relationships"]),
        "rna_relationships": tuple(entry["rna_relationships"]),
        "codec_boundary": dict(record["metadata"]["codec_boundary"]),
        "external_input_contract_preserved": True,
        "external_output_contract_preserved": True,
        "observable_result_contract_preserved": True,
        "compiler_ir_artifact": artifact,
        "lane5_role": "NATIVE_CONSTRUCTOR_BINDING_CANDIDATE",
        "lane5_hydration_required_for_generalized_execution": True,
        "reference_replay_is_generalized_equivalence_proof": False,
        "execution_authorized": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "codec_boundary_removal_authorized": False,
    }
    return {**body, "binding_sha256": _sha(body)}


def validate_native_constructor_binding(
    binding: Mapping[str, Any],
    record: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        validate_library_training_record(record)
    except Pass220I047DatasetError as exc:
        raise Pass220I048InterpreterError(str(exc)) from exc
    body = dict(binding)
    claimed = body.pop("binding_sha256", None)
    if binding.get("schema") != SCHEMA or claimed != _sha(body):
        raise Pass220I048InterpreterError("constructor binding identity mismatch")
    entry = _entrypoint(record, str(binding.get("entrypoint_id")))
    exact_fields = {
        "source_record_sha256": record["record_sha256"],
        "source_library_sha256": record["source"]["sha256"],
        "relationship_root_sha256": record["relationship_root_sha256"],
        "library_id": record["library_id"],
        "library_format": record["metadata"]["library_format"],
        "architecture": record["metadata"]["architecture"],
        "abi": record["metadata"]["abi"],
        "symbol": entry["symbol"],
        "side_effect_class": entry["side_effect_class"],
        "state_boundary": entry["state_boundary"],
    }
    for key, expected in exact_fields.items():
        if binding.get(key) != expected:
            raise Pass220I048InterpreterError(
                f"constructor binding drift: {key}"
            )
    if tuple(binding.get("inputs", ())) != tuple(entry["inputs"]):
        raise Pass220I048InterpreterError("constructor input contract drift")
    if tuple(binding.get("outputs", ())) != tuple(entry["outputs"]):
        raise Pass220I048InterpreterError("constructor output contract drift")
    if binding.get("codec_boundary") != record["metadata"]["codec_boundary"]:
        raise Pass220I048InterpreterError("constructor codec membrane drift")
    artifact = binding.get("compiler_ir_artifact") or {}
    if artifact.get("target") != "HHS_IR" or artifact.get(
        "execution_authorized"
    ) is not False:
        raise Pass220I048InterpreterError("compiler execution authority drift")
    for field in (
        "execution_authorized",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_mint_authority",
        "canonical_hash216_persistence_authority",
        "codec_boundary_removal_authorized",
    ):
        if binding.get(field) is not False:
            raise Pass220I048InterpreterError(
                f"forbidden authority escalation: {field}"
            )
    return {
        "ok": True,
        "binding_id": binding["binding_id"],
        "binding_sha256": claimed,
        "entrypoint_id": binding["entrypoint_id"],
    }


def build_constructor_registry(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not records:
        raise Pass220I048InterpreterError(
            "constructor registry requires at least one I047 record"
        )
    bindings = []
    seen = set()
    for record in records:
        try:
            validate_library_training_record(record)
        except Pass220I047DatasetError as exc:
            raise Pass220I048InterpreterError(str(exc)) from exc
        for entry in record["metadata"]["entrypoints"]:
            key = (record["library_id"], entry["entrypoint_id"])
            if key in seen:
                raise Pass220I048InterpreterError(
                    "duplicate library/entrypoint constructor identity"
                )
            seen.add(key)
            binding = build_native_constructor_binding(
                record, entry["entrypoint_id"]
            )
            validate_native_constructor_binding(binding, record)
            bindings.append(binding)
    bindings = sorted(
        bindings,
        key=lambda value: (
            value["library_id"],
            value["entrypoint_id"],
        ),
    )
    body = {
        "schema": REGISTRY_SCHEMA,
        "version": VERSION,
        "bindings": tuple(bindings),
        "binding_count": len(bindings),
        "source_record_sha256s": tuple(
            sorted(record["record_sha256"] for record in records)
        ),
        "external_contracts_preserved": True,
        "generalized_execution_authorized": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    return {**body, "registry_sha256": _sha(body)}


def _reference_match(
    record: Mapping[str, Any],
    entrypoint_id: str,
    inputs: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    wanted = tuple(_payload_identity(value) for value in inputs)
    for vector in record["reference_vectors"]:
        if vector["entrypoint_id"] != entrypoint_id:
            continue
        observed = tuple(
            _payload_identity(value) for value in vector["inputs"]
        )
        if observed == wanted:
            return vector
    return None


def interpret_library_call(
    record: Mapping[str, Any],
    entrypoint_id: str,
    inputs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    binding = build_native_constructor_binding(record, entrypoint_id)
    validate_native_constructor_binding(binding, record)
    ports = tuple(binding["inputs"])
    if len(inputs) != len(ports):
        raise Pass220I048InterpreterError("interpreter input port count drift")
    normalized_inputs = tuple(
        _normalize_typed_input(value, port, index=index)
        for index, (value, port) in enumerate(zip(inputs, ports))
    )
    vector = _reference_match(record, entrypoint_id, normalized_inputs)
    replay_allowed = binding["side_effect_class"] in REFERENCE_REPLAY_EFFECTS
    if vector is not None and replay_allowed:
        status = "REFERENCE_VECTOR_REPLAY_ADMITTED"
        outputs = tuple(vector["outputs"])
        result_origin = REFERENCE_ORIGIN
        observed_vector_id = vector["vector_id"]
        runtime_adapter_required = False
    elif vector is not None:
        status = "EXPLICIT_RUNTIME_ADMISSION_REQUIRED"
        outputs = ()
        result_origin = None
        observed_vector_id = vector["vector_id"]
        runtime_adapter_required = True
    else:
        status = "NATIVE_CONSTRUCTOR_EXECUTION_REQUIRED"
        outputs = ()
        result_origin = None
        observed_vector_id = None
        runtime_adapter_required = True
    body = {
        "schema": PLAN_SCHEMA,
        "version": VERSION,
        "binding": binding,
        "entrypoint_id": entrypoint_id,
        "inputs": normalized_inputs,
        "expected_output_contract": tuple(binding["outputs"]),
        "status": status,
        "outputs": outputs,
        "result_origin": result_origin,
        "observed_vector_id": observed_vector_id,
        "reference_vector_exact_match": vector is not None,
        "reference_replay_allowed_for_effect_class": replay_allowed,
        "runtime_adapter_required": runtime_adapter_required,
        "lane5_native_constructor_required_for_unseen_inputs": vector is None,
        "external_contract_preserved": True,
        "interpreter_fabricated_result": False,
        "generalized_constructor_equivalence_claimed": False,
        "execution_authorized": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    return {**body, "plan_sha256": _sha(body)}


def validate_interpreter_plan(
    plan: Mapping[str, Any],
    record: Mapping[str, Any],
) -> dict[str, Any]:
    body = dict(plan)
    claimed = body.pop("plan_sha256", None)
    if plan.get("schema") != PLAN_SCHEMA or claimed != _sha(body):
        raise Pass220I048InterpreterError("interpreter plan identity mismatch")
    validate_native_constructor_binding(plan["binding"], record)
    entry = _entrypoint(record, plan["entrypoint_id"])
    if tuple(plan["expected_output_contract"]) != tuple(entry["outputs"]):
        raise Pass220I048InterpreterError("interpreter output contract drift")
    if plan["status"] == "REFERENCE_VECTOR_REPLAY_ADMITTED":
        if plan["result_origin"] != REFERENCE_ORIGIN:
            raise Pass220I048InterpreterError("reference origin drift")
        if len(plan["outputs"]) != len(entry["outputs"]):
            raise Pass220I048InterpreterError("reference output count drift")
        for got, want in zip(plan["outputs"], entry["outputs"]):
            if (
                got["data_type"],
                got["encoding"],
            ) != (
                want["data_type"],
                want["encoding"],
            ):
                raise Pass220I048InterpreterError(
                    "reference output type/encoding drift"
                )
    else:
        if tuple(plan["outputs"]):
            raise Pass220I048InterpreterError(
                "unexecuted interpreter plan may not fabricate outputs"
            )
    if plan.get("interpreter_fabricated_result") is not False:
        raise Pass220I048InterpreterError("fabricated result authority drift")
    for field in (
        "execution_authorized",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_mint_authority",
        "canonical_hash216_persistence_authority",
    ):
        if plan.get(field) is not False:
            raise Pass220I048InterpreterError(
                f"forbidden interpreter authority escalation: {field}"
            )
    return {
        "ok": True,
        "status": plan["status"],
        "plan_sha256": claimed,
    }


def constructor_equivalence_witness(
    record: Mapping[str, Any],
    entrypoint_id: str,
) -> dict[str, Any]:
    binding = build_native_constructor_binding(record, entrypoint_id)
    entry = _entrypoint(record, entrypoint_id)
    vectors = [
        vector
        for vector in record["reference_vectors"]
        if vector["entrypoint_id"] == entrypoint_id
    ]
    results = []
    exact = True
    for vector in vectors:
        plan = interpret_library_call(
            record,
            entrypoint_id,
            vector["inputs"],
        )
        validate_interpreter_plan(plan, record)
        expected = tuple(vector["outputs"])
        matched = (
            plan["status"] == "REFERENCE_VECTOR_REPLAY_ADMITTED"
            and tuple(plan["outputs"]) == expected
        )
        exact = exact and matched
        results.append(
            {
                "vector_id": vector["vector_id"],
                "exact_source_observed_output_replay": matched,
                "plan_sha256": plan["plan_sha256"],
            }
        )
    replayable = entry["side_effect_class"] in REFERENCE_REPLAY_EFFECTS
    body = {
        "schema": EQUIVALENCE_SCHEMA,
        "version": VERSION,
        "binding_id": binding["binding_id"],
        "library_id": record["library_id"],
        "entrypoint_id": entrypoint_id,
        "reference_vector_count": len(vectors),
        "reference_effect_class_replayable": replayable,
        "reference_results": tuple(results),
        "all_replayable_reference_outputs_exact": exact if replayable else False,
        "external_input_contract_exact": True,
        "external_output_contract_exact": True,
        "codec_membrane_exact": True,
        "generalized_constructor_equivalence_proven": False,
        "unseen_input_execution_requires_native_constructor": True,
        "canonical_authority_claimed": False,
    }
    return {**body, "witness_sha256": _sha(body)}


def load_i047_records_jsonl(path: str | Path) -> tuple[dict[str, Any], ...]:
    records = []
    for line_number, line in enumerate(
        Path(path).read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            validate_library_training_record(record)
        except (json.JSONDecodeError, Pass220I047DatasetError) as exc:
            raise Pass220I048InterpreterError(
                f"invalid I047 record at line {line_number}"
            ) from exc
        records.append(record)
    if not records:
        raise Pass220I048InterpreterError("I047 records file is empty")
    return tuple(records)


def materialize_constructor_registry(
    records_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    registry = build_constructor_registry(load_i047_records_jsonl(records_path))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(
        json.dumps(registry, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return registry


def i048_self_test() -> dict[str, Any]:
    raw = b"I048_SYNTHETIC_LIBRARY_BYTES"
    metadata = {
        "library_id": "i048.synthetic.echo",
        "library_format": "SYNTHETIC_TEST_IMAGE",
        "architecture": "TEST",
        "abi": "I048_TEST_ABI",
        "provenance": "I048_SELF_TEST",
        "codec_boundary": {
            "ingress_encoder_id": "BYTES_IN",
            "egress_decoder_id": "BYTES_OUT",
            "preserve_external_contract": True,
        },
        "byte_regions": [
            {
                "region_id": "IMAGE",
                "start": 0,
                "length": len(raw),
                "kind": "RAW_LIBRARY_BYTES",
            }
        ],
        "entrypoints": [
            {
                "entrypoint_id": "echo",
                "symbol": "i048_echo",
                "inputs": [
                    {
                        "name": "payload",
                        "data_type": "bytes",
                        "encoding": "raw",
                    }
                ],
                "outputs": [
                    {
                        "name": "return",
                        "data_type": "bytes",
                        "encoding": "raw",
                    }
                ],
                "side_effect_class": "PURE",
            }
        ],
        "relationships": [],
    }
    value = typed_value_from_bytes(
        data_type="bytes",
        encoding="raw",
        payload=b"abc",
    )
    record = build_library_training_record(
        source_bytes=raw,
        metadata=metadata,
        reference_vectors=[
            {
                "vector_id": "echo:abc",
                "entrypoint_id": "echo",
                "reference_origin": REFERENCE_ORIGIN,
                "inputs": [value],
                "outputs": [value],
                "observation": {
                    "source_library_invoked": True,
                    "observed_output": True,
                    "captured_by": "i048-self-test-fixture",
                },
            }
        ],
    )
    binding = build_native_constructor_binding(record, "echo")
    replay = interpret_library_call(record, "echo", [value])
    unseen = typed_value_from_bytes(
        data_type="bytes",
        encoding="raw",
        payload=b"xyz",
    )
    unresolved = interpret_library_call(record, "echo", [unseen])
    witness = constructor_equivalence_witness(record, "echo")
    return {
        "schema": "HHS_PASS_220_I048_SELF_TEST_V1",
        "ok": bool(
            validate_native_constructor_binding(binding, record)["ok"]
            and validate_interpreter_plan(replay, record)["ok"]
            and replay["status"] == "REFERENCE_VECTOR_REPLAY_ADMITTED"
            and tuple(replay["outputs"]) == (value,)
            and unresolved["status"]
            == "NATIVE_CONSTRUCTOR_EXECUTION_REQUIRED"
            and not unresolved["outputs"]
            and witness["all_replayable_reference_outputs_exact"]
            and not witness["generalized_constructor_equivalence_proven"]
        ),
        "binding_sha256": binding["binding_sha256"],
        "replay_plan_sha256": replay["plan_sha256"],
        "unresolved_plan_sha256": unresolved["plan_sha256"],
        "equivalence_witness_sha256": witness["witness_sha256"],
    }


__all__ = [
    "EQUIVALENCE_SCHEMA",
    "PLAN_SCHEMA",
    "REGISTRY_SCHEMA",
    "SCHEMA",
    "Pass220I048InterpreterError",
    "build_constructor_registry",
    "build_native_constructor_binding",
    "constructor_equivalence_witness",
    "i048_self_test",
    "interpret_library_call",
    "load_i047_records_jsonl",
    "materialize_constructor_registry",
    "validate_interpreter_plan",
    "validate_native_constructor_binding",
]


if __name__ == "__main__":
    print(json.dumps(i048_self_test(), indent=2, sort_keys=True))
