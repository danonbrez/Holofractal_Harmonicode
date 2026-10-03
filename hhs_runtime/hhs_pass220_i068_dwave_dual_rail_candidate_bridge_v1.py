"""Pass 220 I068 D-Wave dual-rail error-aware candidate bridge.

The bridge transcribes D-Wave Leap QCDL simulator results into exact HHS
candidate evidence while preserving detected erasures and ordered control/target
geometry. It never grants canonical VM81/Hash72/Hash216 mutation authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import gcd
from typing import Any, Mapping, Sequence
import json

from python.hhs_gfcc.core import (
    HASH72_ALPHABET,
    HASH72_POSITIONS,
    inherited_hash72,
)

SCHEMA = "HHS_PASS_220_I068_DWAVE_DUAL_RAIL_CANDIDATE_BRIDGE_V1"
PROFILE = "PASS220-I068-DWAVE-DUAL-RAIL-CANDIDATE-BRIDGE-v1"
SOURCE_SURFACE = "DWAVE_LEAP_QCDL_SIMULATOR"
SDK_SURFACE = "dwave.gate.leap.LeapQCDLSimulator"
DOCUMENTED_BETA_QPUS = ("DRsim_17qubits", "DRsim_21qubits")
OUTCOME_SYMBOLS = ("0", "1", "*")
OUTCOME_CODE = {"0": 0, "1": 1, "*": 2}

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "external_simulator_source": True,
    "erasure_channel_preserved": True,
    "post_selection_for_provenance_forbidden": True,
    "exact_integer_transcription": True,
    "floating_point_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_persistence_authority": False,
    "external_egress_authority": False,
}


class Pass220I068DWaveBridgeError(ValueError):
    pass


def _exact_int(value: Any, name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I068DWaveBridgeError(f"{name} must be an exact integer")
    if minimum is not None and value < minimum:
        raise Pass220I068DWaveBridgeError(f"{name} must be >= {minimum}")
    return value


def _require_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise Pass220I068DWaveBridgeError(f"{name} must be boolean")
    return value


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I068DWaveBridgeError(
            f"floating-point value forbidden at {path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    elif hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def hash72(value: Any) -> str:
    return inherited_hash72(canonical_bytes(value))


def _validate_hash72(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH72_POSITIONS:
        raise Pass220I068DWaveBridgeError(f"{name} must be 72 HHS glyphs")
    if any(symbol not in HASH72_ALPHABET for symbol in value):
        raise Pass220I068DWaveBridgeError(
            f"{name} contains non-Hash72 glyphs"
        )
    return value


def _validate_hash216(value: Any, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 3 * HASH72_POSITIONS
    ):
        raise Pass220I068DWaveBridgeError(f"{name} must be 216 HHS glyphs")
    if any(symbol not in HASH72_ALPHABET for symbol in value):
        raise Pass220I068DWaveBridgeError(
            f"{name} contains non-Hash72 glyphs"
        )
    return value


@dataclass(frozen=True)
class OrderedGateWitness:
    operation: str
    control_qubit: str
    target_qubit: str

    def __post_init__(self) -> None:
        if not isinstance(self.operation, str) or not self.operation:
            raise Pass220I068DWaveBridgeError(
                "operation must be a non-empty string"
            )
        if not self.control_qubit or not self.target_qubit:
            raise Pass220I068DWaveBridgeError(
                "control/target qubit names are required"
            )
        if self.control_qubit == self.target_qubit:
            raise Pass220I068DWaveBridgeError(
                "control and target qubits must differ"
            )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class MCEDSignal:
    measurement_index: int
    shot_index: int
    qubit: str
    erased: int

    def __post_init__(self) -> None:
        _exact_int(
            self.measurement_index,
            "measurement_index",
            minimum=0,
        )
        _exact_int(self.shot_index, "shot_index", minimum=0)
        if not isinstance(self.qubit, str) or not self.qubit:
            raise Pass220I068DWaveBridgeError(
                "mced qubit must be non-empty"
            )
        erased = _exact_int(self.erased, "erased", minimum=0)
        if erased not in (0, 1):
            raise Pass220I068DWaveBridgeError(
                "erased must be 0 or 1"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def i027_outcome_for_symbols(
    control_symbol: str,
    target_symbol: str,
) -> int:
    if (
        control_symbol not in OUTCOME_CODE
        or target_symbol not in OUTCOME_CODE
    ):
        raise Pass220I068DWaveBridgeError(
            "dual-rail outcome must be one of 0, 1, *"
        )
    return (
        3 * OUTCOME_CODE[control_symbol]
        + OUTCOME_CODE[target_symbol]
    )


@dataclass(frozen=True)
class MeasurementRound:
    register_order: tuple[str, ...]
    counts: tuple[tuple[str, int], ...]
    shots_observed: int
    clean_shots: int
    erased_shots: int
    erasure_counts_by_register: tuple[tuple[str, int], ...]
    exact_yield_numerator: int
    exact_yield_denominator: int
    i027_outcome_histogram: tuple[tuple[int, int], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "register_order": list(self.register_order),
            "counts": [
                [key, count]
                for key, count in self.counts
            ],
            "shots_observed": self.shots_observed,
            "clean_shots": self.clean_shots,
            "erased_shots": self.erased_shots,
            "erasure_counts_by_register": [
                list(item)
                for item in self.erasure_counts_by_register
            ],
            "exact_yield": [
                self.exact_yield_numerator,
                self.exact_yield_denominator,
            ],
            "i027_outcome_histogram": [
                list(item)
                for item in self.i027_outcome_histogram
            ],
        }


@dataclass(frozen=True)
class DWaveDualRailCandidate:
    schema: str
    profile: str
    source_surface: str
    sdk_surface: str
    qpu: str
    documented_beta_qpu: bool
    noise_model: bool
    repeat_until_shots_requested: bool
    shots_requested: int
    program_hash72: str
    gate: OrderedGateWitness
    rounds: tuple[MeasurementRound, ...]
    mced_events: tuple[MCEDSignal, ...]
    config_hash72: str
    result_hash72: str
    authority_hash72: str
    receipt_hash216: str
    authority: Mapping[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "profile": self.profile,
            "source_surface": self.source_surface,
            "sdk_surface": self.sdk_surface,
            "qpu": self.qpu,
            "documented_beta_qpu": self.documented_beta_qpu,
            "noise_model": self.noise_model,
            "repeat_until_shots_requested":
                self.repeat_until_shots_requested,
            "shots_requested": self.shots_requested,
            "program_hash72": self.program_hash72,
            "gate": self.gate.to_dict(),
            "rounds": [
                round_.to_dict()
                for round_ in self.rounds
            ],
            "mced_events": [
                event.to_dict()
                for event in self.mced_events
            ],
            "config_hash72": self.config_hash72,
            "result_hash72": self.result_hash72,
            "authority_hash72": self.authority_hash72,
            "receipt_hash216": self.receipt_hash216,
            "authority": dict(self.authority),
        }


@dataclass(frozen=True)
class VM81ComparisonWitness:
    schema: str
    candidate_receipt_hash216: str
    canonical_vm81_receipt_hash216: str
    round_index: int
    candidate_histogram: tuple[tuple[int, int], ...]
    canonical_histogram: tuple[tuple[int, int], ...]
    delta_histogram: tuple[tuple[int, int], ...]
    sample_count_equal: bool
    exact_histogram_equal: bool
    comparison_hash72: str
    canonical_mutation_authority: bool = False
    hash72_commit_authority: bool = False
    hash216_commit_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_register_order(
    register_order: Sequence[str],
) -> tuple[str, ...]:
    if isinstance(register_order, (str, bytes)):
        raise Pass220I068DWaveBridgeError(
            "register_order must be a sequence of names"
        )
    names = tuple(register_order)
    if (
        not names
        or any(
            not isinstance(name, str) or not name
            for name in names
        )
    ):
        raise Pass220I068DWaveBridgeError(
            "register_order must contain non-empty names"
        )
    if len(set(names)) != len(names):
        raise Pass220I068DWaveBridgeError(
            "register_order must not contain duplicates"
        )
    return names


def _normalize_round(
    counts: Mapping[str, int],
    register_order: tuple[str, ...],
    gate: OrderedGateWitness,
) -> MeasurementRound:
    if not isinstance(counts, Mapping) or not counts:
        raise Pass220I068DWaveBridgeError(
            "counts round must be a non-empty mapping"
        )
    if (
        gate.control_qubit not in register_order
        or gate.target_qubit not in register_order
    ):
        raise Pass220I068DWaveBridgeError(
            "gate qubits must appear in register_order"
        )

    normalized: list[tuple[str, int]] = []
    for key, raw_count in counts.items():
        if (
            not isinstance(key, str)
            or len(key) != len(register_order)
        ):
            raise Pass220I068DWaveBridgeError(
                "count key width must match register_order"
            )
        if any(
            symbol not in OUTCOME_SYMBOLS
            for symbol in key
        ):
            raise Pass220I068DWaveBridgeError(
                "count keys may contain only 0, 1, *"
            )
        count = _exact_int(
            raw_count,
            f"count[{key}]",
            minimum=1,
        )
        normalized.append((key, count))
    normalized.sort()

    shots = sum(count for _, count in normalized)
    clean = sum(
        count
        for key, count in normalized
        if "*" not in key
    )
    erased = shots - clean
    divisor = gcd(clean, shots)
    yield_num = clean // divisor
    yield_den = shots // divisor

    erasures = []
    for index, name in enumerate(register_order):
        erasures.append(
            (
                name,
                sum(
                    count
                    for key, count in normalized
                    if key[index] == "*"
                ),
            )
        )

    position = {
        name: index
        for index, name in enumerate(register_order)
    }
    histogram = {index: 0 for index in range(9)}
    for key, count in normalized:
        outcome = i027_outcome_for_symbols(
            key[position[gate.control_qubit]],
            key[position[gate.target_qubit]],
        )
        histogram[outcome] += count

    return MeasurementRound(
        register_order=register_order,
        counts=tuple(normalized),
        shots_observed=shots,
        clean_shots=clean,
        erased_shots=erased,
        erasure_counts_by_register=tuple(erasures),
        exact_yield_numerator=yield_num,
        exact_yield_denominator=yield_den,
        i027_outcome_histogram=tuple(
            sorted(histogram.items())
        ),
    )


def transcribe_dwave_counts(
    *,
    counts: Mapping[str, int]
    | Sequence[Mapping[str, int]],
    register_order: Sequence[str],
    gate: OrderedGateWitness,
    qpu: str,
    noise_model: bool,
    shots_requested: int,
    program_hash72: str,
    repeat_until_shots_requested: bool = False,
    post_selected: bool = False,
    mced_events: Sequence[MCEDSignal] = (),
) -> DWaveDualRailCandidate:
    if not isinstance(qpu, str) or not qpu:
        raise Pass220I068DWaveBridgeError(
            "qpu must be a non-empty string"
        )
    _require_bool(noise_model, "noise_model")
    _require_bool(
        repeat_until_shots_requested,
        "repeat_until_shots_requested",
    )
    _require_bool(post_selected, "post_selected")
    requested = _exact_int(
        shots_requested,
        "shots_requested",
        minimum=1,
    )
    program_hash = _validate_hash72(
        program_hash72,
        "program_hash72",
    )
    if post_selected:
        raise Pass220I068DWaveBridgeError(
            "post-selected-only input is forbidden; "
            "erasure evidence must be preserved"
        )

    names = _normalize_register_order(register_order)
    if isinstance(counts, Mapping):
        rounds_source = (counts,)
    else:
        rounds_source = tuple(counts)
        if not rounds_source:
            raise Pass220I068DWaveBridgeError(
                "at least one measurement round is required"
            )
    rounds = tuple(
        _normalize_round(
            round_counts,
            names,
            gate,
        )
        for round_counts in rounds_source
    )

    observed = {
        round_.shots_observed
        for round_ in rounds
    }
    if len(observed) != 1:
        raise Pass220I068DWaveBridgeError(
            "all measurement rounds must report "
            "the same shot count"
        )
    observed_shots = next(iter(observed))
    if repeat_until_shots_requested:
        if observed_shots < requested:
            raise Pass220I068DWaveBridgeError(
                "repeat-until result cannot contain "
                "fewer executions than requested"
            )
    elif observed_shots != requested:
        raise Pass220I068DWaveBridgeError(
            "non-repeating result shot count "
            "must equal shots_requested"
        )

    if (
        not noise_model
        and any(
            round_.erased_shots
            for round_ in rounds
        )
    ):
        raise Pass220I068DWaveBridgeError(
            "ideal/noise_model=False transcript "
            "cannot contain erasure splats"
        )

    events = tuple(mced_events)
    if any(
        not isinstance(event, MCEDSignal)
        for event in events
    ):
        raise Pass220I068DWaveBridgeError(
            "mced_events must contain MCEDSignal values"
        )

    config_payload = {
        "schema": SCHEMA,
        "profile": PROFILE,
        "source_surface": SOURCE_SURFACE,
        "sdk_surface": SDK_SURFACE,
        "qpu": qpu,
        "noise_model": noise_model,
        "repeat_until_shots_requested":
            repeat_until_shots_requested,
        "shots_requested": requested,
        "program_hash72": program_hash,
        "gate": gate.to_dict(),
        "register_order": list(names),
    }
    result_payload = {
        "rounds": [
            round_.to_dict()
            for round_ in rounds
        ],
        "mced_events": [
            event.to_dict()
            for event in events
        ],
    }
    config_hash = hash72(config_payload)
    result_hash = hash72(result_payload)
    authority_hash = hash72(AUTHORITY_BOUNDARY)
    receipt = (
        config_hash
        + result_hash
        + authority_hash
    )
    _validate_hash216(receipt, "receipt_hash216")

    return DWaveDualRailCandidate(
        schema=SCHEMA,
        profile=PROFILE,
        source_surface=SOURCE_SURFACE,
        sdk_surface=SDK_SURFACE,
        qpu=qpu,
        documented_beta_qpu=(
            qpu in DOCUMENTED_BETA_QPUS
        ),
        noise_model=noise_model,
        repeat_until_shots_requested=(
            repeat_until_shots_requested
        ),
        shots_requested=requested,
        program_hash72=program_hash,
        gate=gate,
        rounds=rounds,
        mced_events=events,
        config_hash72=config_hash,
        result_hash72=result_hash,
        authority_hash72=authority_hash,
        receipt_hash216=receipt,
        authority=dict(AUTHORITY_BOUNDARY),
    )


def program_hash72(program: Any) -> str:
    if isinstance(program, Mapping):
        payload = dict(program)
    elif hasattr(program, "model_dump"):
        payload = program.model_dump(mode="json")
    else:
        raise Pass220I068DWaveBridgeError(
            "program must be a mapping or expose "
            "model_dump(mode='json')"
        )
    return hash72(
        {
            "domain":
                "HHS-P220-I068-QCDL-PROGRAM-V1",
            "program": payload,
        }
    )


def transcribe_leap_result(
    result: Any,
    *,
    gate: OrderedGateWitness,
    qpu: str,
    noise_model: bool,
    shots_requested: int,
    program_hash: str,
    repeat_until_shots_requested: bool = False,
    mced_events: Sequence[MCEDSignal] = (),
) -> DWaveDualRailCandidate:
    if (
        not hasattr(result, "get_counts")
        or not hasattr(
            result,
            "get_measurements_register",
        )
    ):
        raise Pass220I068DWaveBridgeError(
            "result does not expose the documented "
            "D-Wave Result surface"
        )
    counts = result.get_counts(post_select=False)
    register_order = result.get_measurements_register()
    return transcribe_dwave_counts(
        counts=counts,
        register_order=register_order,
        gate=gate,
        qpu=qpu,
        noise_model=noise_model,
        shots_requested=shots_requested,
        program_hash72=program_hash,
        repeat_until_shots_requested=(
            repeat_until_shots_requested
        ),
        post_selected=False,
        mced_events=mced_events,
    )


def run_leap_qcdl_candidate(
    program: Any,
    *,
    gate: OrderedGateWitness,
    shots: int,
    qpu: str = "DRsim_21qubits",
    noise_model: bool = True,
    repeat_until_shots_requested: bool = False,
    profile: str | None = None,
    label: str = (
        "HHS Pass 220 I068 dual-rail candidate"
    ),
) -> DWaveDualRailCandidate:
    try:
        from dwave.gate.leap import LeapQCDLSimulator
    except ImportError as exc:
        raise Pass220I068DWaveBridgeError(
            "dwave-gate/Ocean SDK is required "
            "only for live Leap execution"
        ) from exc

    simulator = (
        LeapQCDLSimulator()
        if profile is None
        else LeapQCDLSimulator(profile=profile)
    )
    requested = _exact_int(
        shots,
        "shots",
        minimum=1,
    )
    program_hash = program_hash72(program)
    future = simulator.run(
        program,
        qpu=qpu,
        noise_model=noise_model,
        shots=requested,
        repeat_until_shots_requested=(
            repeat_until_shots_requested
        ),
        label=label,
    )
    result = future.result().result
    return transcribe_leap_result(
        result,
        gate=gate,
        qpu=qpu,
        noise_model=noise_model,
        shots_requested=requested,
        program_hash=program_hash,
        repeat_until_shots_requested=(
            repeat_until_shots_requested
        ),
    )


def build_ordered_cz_probe(
) -> tuple[Any, OrderedGateWitness]:
    try:
        from dwave.gate.qcdl import qcdl
        from dwave.gate.qcdl.operations import (
            cz,
            h,
            measure,
        )
    except ImportError as exc:
        raise Pass220I068DWaveBridgeError(
            "dwave-gate/Ocean SDK is required "
            "only to build the live QCDL probe"
        ) from exc

    @qcdl(2)
    def ordered_cz_probe(
        q0: Any,
        q1: Any,
    ) -> None:
        h(q0)
        h(q1)
        cz(
            control_qubit=q0,
            target_qubit=q1,
        )
        measure(q0)
        measure(q1)

    return (
        ordered_cz_probe(),
        OrderedGateWitness(
            "CZ",
            "q0",
            "q1",
        ),
    )


def compare_with_vm81_histogram(
    candidate: DWaveDualRailCandidate,
    *,
    canonical_histogram: Mapping[int, int],
    canonical_vm81_receipt_hash216: str,
    round_index: int = 0,
) -> VM81ComparisonWitness:
    if not isinstance(
        candidate,
        DWaveDualRailCandidate,
    ):
        raise Pass220I068DWaveBridgeError(
            "candidate must be a "
            "DWaveDualRailCandidate"
        )
    receipt = _validate_hash216(
        canonical_vm81_receipt_hash216,
        "canonical_vm81_receipt_hash216",
    )
    index = _exact_int(
        round_index,
        "round_index",
        minimum=0,
    )
    if index >= len(candidate.rounds):
        raise Pass220I068DWaveBridgeError(
            "round_index out of range"
        )

    canonical = {
        i: 0
        for i in range(9)
    }
    for raw_key, raw_count in (
        canonical_histogram.items()
    ):
        key = _exact_int(
            raw_key,
            "canonical outcome",
            minimum=0,
        )
        if key > 8:
            raise Pass220I068DWaveBridgeError(
                "canonical outcomes must lie in 0..8"
            )
        count = _exact_int(
            raw_count,
            f"canonical_histogram[{key}]",
            minimum=0,
        )
        canonical[key] = count

    candidate_hist = dict(
        candidate.rounds[
            index
        ].i027_outcome_histogram
    )
    delta = {
        i: (
            candidate_hist[i]
            - canonical[i]
        )
        for i in range(9)
    }
    sample_count_equal = (
        sum(candidate_hist.values())
        == sum(canonical.values())
    )
    exact_equal = (
        sample_count_equal
        and all(
            value == 0
            for value in delta.values()
        )
    )
    payload = {
        "domain":
            "HHS-P220-I068-VM81-COMPARISON-V1",
        "candidate_receipt_hash216":
            candidate.receipt_hash216,
        "canonical_vm81_receipt_hash216":
            receipt,
        "round_index": index,
        "candidate_histogram":
            sorted(candidate_hist.items()),
        "canonical_histogram":
            sorted(canonical.items()),
        "delta_histogram":
            sorted(delta.items()),
        "sample_count_equal":
            sample_count_equal,
        "exact_histogram_equal":
            exact_equal,
        "authority": {
            "canonical_mutation_authority":
                False,
            "hash72_commit_authority":
                False,
            "hash216_commit_authority":
                False,
        },
    }
    return VM81ComparisonWitness(
        schema=(
            "HHS_PASS_220_I068_"
            "VM81_COMPARISON_WITNESS_V1"
        ),
        candidate_receipt_hash216=(
            candidate.receipt_hash216
        ),
        canonical_vm81_receipt_hash216=(
            receipt
        ),
        round_index=index,
        candidate_histogram=tuple(
            sorted(candidate_hist.items())
        ),
        canonical_histogram=tuple(
            sorted(canonical.items())
        ),
        delta_histogram=tuple(
            sorted(delta.items())
        ),
        sample_count_equal=(
            sample_count_equal
        ),
        exact_histogram_equal=(
            exact_equal
        ),
        comparison_hash72=hash72(payload),
    )


def self_test() -> dict[str, Any]:
    mapping = {
        i027_outcome_for_symbols(a, b)
        for a in OUTCOME_SYMBOLS
        for b in OUTCOME_SYMBOLS
    }
    gate = OrderedGateWitness(
        "CZ",
        "q0",
        "q1",
    )
    ph = hash72(
        {"program": "synthetic-i068"}
    )
    candidate = transcribe_dwave_counts(
        counts={
            "00": 3,
            "0*": 1,
            "*1": 1,
        },
        register_order=("q0", "q1"),
        gate=gate,
        qpu="DRsim_21qubits",
        noise_model=True,
        shots_requested=5,
        program_hash72=ph,
    )
    comparison = compare_with_vm81_histogram(
        candidate,
        canonical_histogram=dict(
            candidate.rounds[
                0
            ].i027_outcome_histogram
        ),
        canonical_vm81_receipt_hash216=(
            hash72("a")
            + hash72("b")
            + hash72("c")
        ),
    )
    checks = {
        "nine_state_bijection":
            mapping == set(range(9)),
        "erasure_preserved":
            candidate.rounds[0].erased_shots == 2,
        "yield_exact":
            (
                candidate.rounds[
                    0
                ].exact_yield_numerator,
                candidate.rounds[
                    0
                ].exact_yield_denominator,
            )
            == (3, 5),
        "hash216_three_lane":
            len(candidate.receipt_hash216) == 216,
        "candidate_only":
            candidate.authority["candidate_only"],
        "no_vm81_mutation_authority":
            not candidate.authority[
                "canonical_vm81_mutation_authority"
            ],
        "no_hash_commit_authority":
            (
                not candidate.authority[
                    "canonical_hash72_commit_authority"
                ]
                and not candidate.authority[
                    "canonical_hash216_commit_authority"
                ]
            ),
        "comparison_exact":
            comparison.exact_histogram_equal,
    }
    return {
        "schema":
            "HHS_PASS_220_I068_SELF_TEST_V1",
        "status":
            "PASS"
            if all(checks.values())
            else "FAIL",
        "checks": checks,
        "receipt_hash216":
            candidate.receipt_hash216,
    }


def main() -> None:
    print(
        json.dumps(
            self_test(),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
