"""Exact read-only Lane 5 dyadic virtual-register candidates.

No VM81 admission, Hash72 mint, Hash216 persistence or canonical mutation.
Exact Fraction identities are projections, never OP_11 constitutive receipts.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

RADIX = 72
WIDTH = 72
VM5184 = 5184

def _integer(value: int, name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} requires an exact integer")
    return value

def dyadic(exponent: int) -> Fraction:
    n = _integer(exponent, "exponent")
    return Fraction(1 << n, 1) if n >= 0 else Fraction(1, 1 << -n)

def shell(depth: int) -> tuple[tuple[int, Fraction], ...]:
    n = _integer(depth, "depth")
    if n < 0:
        raise ValueError("negative shell depth")
    return tuple((k, dyadic(k)) for k in range(-n, n + 1))

def reciprocal_witness(exponent: int) -> bool:
    return dyadic(exponent) * dyadic(-exponent) == Fraction(1)

def encode_address(digits: tuple[int, ...]) -> int:
    if not isinstance(digits, tuple) or len(digits) != WIDTH:
        raise ValueError("expected 72 ordered radix-72 digits")
    result = 0
    for digit in reversed(digits):
        v = _integer(digit, "address digit")
        if not 0 <= v < RADIX:
            raise ValueError("radix-72 digit outside 0..71")
        result = result * RADIX + v
    return result

def decode_address(index: int) -> tuple[int, ...]:
    value = _integer(index, "address")
    if not 0 <= value < RADIX ** WIDTH:
        raise ValueError("address outside 72**72")
    result = []
    for _ in range(WIDTH):
        value, digit = divmod(value, RADIX)
        result.append(digit)
    return tuple(result)

def hydration_address(row: int, column: int) -> int:
    i = _integer(row, "row")
    j = _integer(column, "column")
    if not 0 <= i < RADIX or not 0 <= j < RADIX:
        raise ValueError("hydration coordinate outside 72x72")
    return RADIX * i + j

@dataclass(frozen=True)
class VirtualRegister:
    address: tuple[int, ...]
    exponent: int
    phase: str
    cell_type: str
    constructor: str
    provenance: str

    def __post_init__(self) -> None:
        encode_address(self.address)
        _integer(self.exponent, "exponent")
        for key in ("phase", "cell_type", "constructor", "provenance"):
            if not isinstance(getattr(self, key), str) or not getattr(self, key):
                raise ValueError(f"{key} must be a nonempty provenance-bearing string")

    @property
    def index(self) -> int:
        return encode_address(self.address)

    @property
    def quantization(self) -> Fraction:
        return dyadic(self.exponent)

def symmetric_witness(center: Fraction, exponent: int) -> dict[str, object]:
    """Rational projection where sqrt(2**n) is rational, else symbolic."""
    if type(center) is not Fraction:
        raise TypeError("center must be an exact Fraction")
    n = _integer(exponent, "exponent")
    delta = dyadic(n)
    if n % 2:
        return {"center": center, "delta": delta,
                "displacement": ("sqrt", delta),
                "p": None, "q": None,
                "pq": center * center - delta,
                "sum": 2 * center, "status": "SYMBOLIC_UNADMITTED"}
    d = dyadic(n // 2)
    p, q = center - d, center + d
    assert p + q == 2 * center and center * center - p * q == delta
    return {"center": center, "delta": delta, "displacement": d,
            "p": p, "q": q, "pq": p * q,
            "sum": p + q, "status": "EXACT_PROJECTION_UNADMITTED"}

def prime_center_witness(prime: int) -> dict[str, int]:
    """Candidate unit-defect witness with exact primality guard."""
    p = _integer(prime, "prime")
    if p < 3 or p % 2 == 0:
        raise ValueError("odd prime center required")
    for d in range(3, isqrt(p) + 1, 2):
        if p % d == 0:
            raise ValueError("center is composite")
    left, right = p - 1, p + 1
    assert p * p - left * right == 1
    return {"P": p, "p": left, "q": right, "modulus": left * right,
            "square": p * p, "defect": 1}


def symbolic_reciprocal_pair(exponent: int) -> dict[str, object]:
    """Typed exact two-radical candidate; never numerically collapses branches.

    For delta=2**n choose P=sqrt(1+delta), d=sqrt(delta).
    The conjugate product is one by polynomial identity, with distinct
    ordered operands. This is a symbolic projection, not OP_11 admission.
    """
    n = _integer(exponent, "exponent")
    delta = dyadic(n)
    center_squared = Fraction(1) + delta
    return {
        "schema": "HHS_LANE5_DYADIC_RECIPROCAL_PAIR_CANDIDATE_V1",
        "exponent": n,
        "delta": delta,
        "P": ("POSITIVE_SQRT", center_squared),
        "d": ("POSITIVE_SQRT", delta),
        "p": ("ORDERED_SUBTRACT", "P", "d"),
        "q": ("ORDERED_ADD", "P", "d"),
        "p_plus_q": ("TWICE", "P"),
        "p_times_q": Fraction(1),
        "difference_of_squares": center_squared - delta,
        "identities": ("P2_MINUS_PQ_EQUALS_DELTA", "P_PLUS_PQ_SYMMETRY", "PQ_EQUALS_ONE"),
        "operator_semantics": "TYPED_CONSTITUTIVE_UNRESOLVED",
        "admission": "CANDIDATE_ONLY",
    }


def prepare_lane5_hydration_candidate(
    register: VirtualRegister, *, witness: dict[str, object] | None = None
) -> dict[str, object]:
    """Build a read-only Lane 5 proposal, without side effects or receipts.

    Gate operator semantics are inherited from Pass148; they are not
    implemented here. The resulting proposal must be submitted through
    the existing VM81 admission and Hash72-before-Hash216 authority path.
    """
    if not isinstance(register, VirtualRegister):
        raise TypeError("exact VirtualRegister required")
    from hhs_runtime.pass148.registry import OPERATORS
    gate = OPERATORS["HHS_GATE_EQ"]
    if gate["commutative"] or gate["operator_id"] != "HHS_GATE_EQ":
        raise RuntimeError("inherited gate definition drift")
    if witness is None:
        witness = symbolic_reciprocal_pair(register.exponent)
    if not isinstance(witness, dict) or witness.get("exponent") != register.exponent:
        raise ValueError("symbolic witness exponent/address mismatch")
    if witness.get("admission") != "CANDIDATE_ONLY":
        raise ValueError("unverified witness cannot claim admission")
    # Reject edited, substituted, or incomplete proof terms. A candidate's
    # own assertion of exactness never supplies a native receipt.
    expected = symbolic_reciprocal_pair(register.exponent)
    if set(witness) != set(expected) or any(
        type(witness[key]) is not type(value) or witness[key] != value
        for key, value in expected.items()
    ):
        raise ValueError("symbolic reciprocal witness drift")
    return {
        "schema": "HHS_LANE5_DYADIC_VIRTUAL_HYDRATION_PROPOSAL_V1",
        "virtual_address": register.index,
        "radix72_address": register.address,
        "signed_exponent": register.exponent,
        "quantization": register.quantization,
        "phase": register.phase,
        "cell_type": register.cell_type,
        "constructor": register.constructor,
        "provenance": register.provenance,
        "inherited_gate_id": gate["operator_id"],
        "inherited_gate_semantics": gate["semantics"],
        "witness": dict(witness),
        "candidate_only": True,
        "requires": ("NATIVE_CPLUSPLUS_CELL_WALL", "SINGLETON_VM81_ADMISSION",
                     "HASH72_RECEIPT", "HASH216_LINEAGE", "REPLAY"),
        "canonical_hash_mutation": None,
    }


def bind_existing_pass159_provenance(
    register: VirtualRegister,
    provenance: dict[str, object],
    *,
    root: str | None = None,
) -> dict[str, object]:
    """Read-only handoff to the inherited Pass219 I157 source/VMIR contract.

    The returned fields describe independently supplied provenance metadata.
    They never claim that this module executed a frontend or VM81 admission.
    """
    if not isinstance(register, VirtualRegister):
        raise TypeError("exact VirtualRegister required")
    if not isinstance(provenance, dict):
        raise TypeError("Pass159 provenance mapping required")
    from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
        normalize_pass159_provenance,
        verify_frozen_source_identity,
    )
    # Verify the actual frozen source bytes in the checked-out repository.
    source_receipt = verify_frozen_source_identity(root)
    normalized = normalize_pass159_provenance(provenance)
    binding = normalized["provenance_binding_sha256"]
    if register.provenance != binding:
        raise ValueError("register provenance differs from Pass159 source/VMIR binding")
    proposal = prepare_lane5_hydration_candidate(register)
    return {
        "schema": "HHS_LANE5_DYADIC_PASS159_CANDIDATE_BINDING_V1",
        "proposal": proposal,
        "pass159_source_identity": source_receipt,
        "pass159_provenance": normalized,
        "provenance_binding_sha256": binding,
        "pass159_metadata_validated": True,
        "frontend_executed_here": False,
        "vm81_admitted": False,
        "hash72_minted": False,
        "hash216_persisted": False,
        "canonical_hash_mutation": None,
    }


def attach_existing_i157_typed_graph(
    bound_candidate: dict[str, object],
    graph: dict[str, object],
) -> dict[str, object]:
    """Attach *existing* I157 graph lineage without asserting dyadic proof.

    Pass219 I157's snapshot P is an exact positive integer. The dyadic
    proposal's symbolic irrational P is an independent typed field, never
    coerced into that integer snapshot or the fifteen source terms.
    """
    if not isinstance(bound_candidate, dict) or not isinstance(graph, dict):
        raise TypeError("typed candidate and Pass219 I157 graph mappings required")
    from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
        SCHEMA as I157_SCHEMA,
        _sha256 as inherited_diagnostic_sha256,
    )
    if bound_candidate.get("schema") != "HHS_LANE5_DYADIC_PASS159_CANDIDATE_BINDING_V1":
        raise ValueError("candidate binding schema mismatch")
    if bound_candidate.get("vm81_admitted") is not False or bound_candidate.get("canonical_hash_mutation") is not None:
        raise ValueError("candidate authority escalation")
    proposal = bound_candidate.get("proposal")
    if not isinstance(proposal, dict) or proposal.get("candidate_only") is not True:
        raise ValueError("unadmitted dyadic proposal required")
    if graph.get("schema") != I157_SCHEMA:
        raise ValueError("Pass219 typed graph schema mismatch")
    actual_root = graph.get("typed_value_graph_sha256")
    core = {key: value for key, value in graph.items() if key != "typed_value_graph_sha256"}
    if actual_root != inherited_diagnostic_sha256(core):
        raise ValueError("Pass219 typed graph diagnostic root mismatch")
    provenance = graph.get("pass159_provenance")
    if not isinstance(provenance, dict) or provenance != bound_candidate.get("pass159_provenance"):
        raise ValueError("Pass159 source-to-VMIR graph lineage mismatch")
    if provenance.get("provenance_binding_sha256") != bound_candidate.get("provenance_binding_sha256"):
        raise ValueError("candidate provenance binding mismatch")
    if graph.get("source_identity") != bound_candidate.get("pass159_source_identity"):
        raise ValueError("frozen source identity mismatch")
    snapshot = graph.get("snapshot")
    if not isinstance(snapshot, dict) or type(snapshot.get("P")) is not int or snapshot["P"] < 1:
        raise ValueError("I157 integer-snapshot P required")
    if snapshot.get("hydration_bits") != 5184:
        raise ValueError("I157 5184 hydration scope drift")
    authority = graph.get("authority")
    if not isinstance(authority, dict) or any(
        authority.get(k) is not False for k in (
            "canonical_monolithic_proof", "vm81_execution_verified",
            "vm81_mutation_authority", "hash72_execution_receipt_verified",
            "hash72_mint_authority", "hash216_persistence_authority",
            "deterministic_replay_verified", "floating_point_authority",
        )
    ):
        raise ValueError("I157 graph authority escalation")
    return {
        "schema": "HHS_LANE5_DYADIC_I157_TYPED_GRAPH_ATTACHMENT_V1",
        "candidate": bound_candidate,
        "inherited_graph_root_sha256": actual_root,
        "inherited_graph_snapshot_binding_sha256": snapshot.get("snapshot_binding_sha256"),
        "inherited_graph_candidate_binding_sha256": graph.get("candidate_binding_sha256"),
        "typed_graph_term_count": graph.get("counts", {}).get("term_count") if isinstance(graph.get("counts"), dict) else None,
        "i157_integer_snapshot_P": snapshot["P"],
        "dyadic_symbolic_P": proposal.get("witness", {}).get("P"),
        "separate_P_type_domains": True,
        "native_full_master_equation_executed": False,
        "vm81_admitted": False,
        "hash72_minted": False,
        "hash216_persisted": False,
        "canonical_hash_mutation": None,
    }


def lower_attached_candidate_to_native_abi(
    attachment: dict[str, object],
) -> dict[str, object]:
    """Fail-closed data lowering for the existing native candidate-only route.

    This is not an admission request: the caller still must provide genuine
    Pass219 I028 frame/predecessor/constructor witnesses to the native C ABI.
    Python's unlimited exponents are never silently truncated to int64.
    """
    if not isinstance(attachment, dict) or attachment.get("schema") != (
        "HHS_LANE5_DYADIC_I157_TYPED_GRAPH_ATTACHMENT_V1"
    ):
        raise ValueError("typed I157 attachment required")
    if attachment.get("separate_P_type_domains") is not True:
        raise ValueError("separate typed centers required")
    for field in ("native_full_master_equation_executed", "vm81_admitted",
                  "hash72_minted", "hash216_persisted"):
        if attachment.get(field) is not False:
            raise ValueError("unadmitted authority flags required")
    if attachment.get("canonical_hash_mutation") is not None:
        raise ValueError("canonical mutation forbidden")
    bound = attachment.get("candidate")
    if not isinstance(bound, dict) or bound.get("schema") != (
        "HHS_LANE5_DYADIC_PASS159_CANDIDATE_BINDING_V1"
    ):
        raise ValueError("Pass159 candidate binding required")
    if bound.get("vm81_admitted") is not False or bound.get(
        "canonical_hash_mutation", object()
    ) is not None:
        raise ValueError("unadmitted source binding required")
    proposal = bound.get("proposal")
    if not isinstance(proposal, dict) or proposal.get("schema") != (
        "HHS_LANE5_DYADIC_VIRTUAL_HYDRATION_PROPOSAL_V1"
    ) or proposal.get("candidate_only") is not True:
        raise ValueError("native candidate proposal required")
    exponent = _integer(proposal.get("signed_exponent"), "signed_exponent")
    if not -(1 << 63) < exponent < (1 << 63):
        raise ValueError("signed exponent unrepresentable in native int64 ABI")
    digits = proposal.get("radix72_address")
    if type(digits) is not tuple:
        raise ValueError("ordered radix-72 tuple required")
    if proposal.get("virtual_address") != encode_address(digits):
        raise ValueError("radix-72 address/index mismatch")
    if proposal.get("quantization") != dyadic(exponent):
        raise ValueError("exact dyadic quantization drift")
    if proposal.get("witness") != symbolic_reciprocal_pair(exponent):
        raise ValueError("symbolic dyadic witness drift")
    phase_text = proposal.get("phase")
    if (type(phase_text) is not str or not phase_text.isascii() or
        not phase_text.isdecimal() or
        (len(phase_text) > 1 and phase_text.startswith("0"))):
        raise ValueError("native phase requires canonical ASCII decimal 0..71")
    phase = int(phase_text)
    if not 0 <= phase < 72:
        raise ValueError("native phase coordinate 0..71 required")
    binding = bound.get("provenance_binding_sha256")
    if (type(binding) is not str or len(binding) != 64 or
        not all(ch in "0123456789abcdef" for ch in binding)):
        raise ValueError("normalized lowercase Pass159 SHA256 required")
    if proposal.get("provenance") != binding:
        raise ValueError("Pass159 source binding mismatch")
    provenance = bound.get("pass159_provenance")
    if not isinstance(provenance, dict) or provenance.get(
        "provenance_binding_sha256"
    ) != binding:
        raise ValueError("normalized Pass159 provenance mismatch")
    if attachment.get("dyadic_symbolic_P") != proposal["witness"]["P"]:
        raise ValueError("dyadic center identity mismatch")
    return {
        "schema": "HHS_LANE5_DYADIC_NATIVE_CANDIDATE_ABI_FIELDS_V1",
        "radix72_address": tuple(digits),
        "signed_dyadic_exponent_int64": exponent,
        "phase_coordinate72": phase,
        "pass159_binding_sha256": binding,
        "requires_inherited_i028_input": True,
        "requires_inherited_i028_vm81_frame": True,
        "requires_inherited_i028_predecessor": True,
        "requires_inherited_i028_constructor_witness": True,
        "requires_signed_environmental_vm81": True,
        "candidate_only": True,
        "vm81_admitted": False,
        "canonical_hash_mutation": None,
    }
