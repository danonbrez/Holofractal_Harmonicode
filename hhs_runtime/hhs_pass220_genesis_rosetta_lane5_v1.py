"""Additive Genesis / Lo Shu / Lane 5 Rosetta composition; candidate only.

Native tensor phases and ordered layer operators remain user/native supplied.
No VM81 admission, Hash72 receipt or Hash216 archival authority is introduced.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Sequence

LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
NUCLEUS_ORDER = tuple(k for row in LO_SHU for k in row)
WIDTH = 576
LIMIT = 5184

class RosettaBoundaryError(ValueError):
    pass

def exact(value: Any, upper: int, label: str) -> int:
    if type(value) is not int or not 0 <= value < upper:
        raise RosettaBoundaryError(f"{label} outside exact domain")
    return value

def coordinates(address: int) -> dict:
    a = exact(address, LIMIT, "address")
    g, t = divmod(a, WIDTH)
    return dict(address=a, region=g, nucleus_symbol=NUCLEUS_ORDER[g],
                local=t, vm81=divmod(a,64), hash72=divmod(a,72),
                h36=divmod(a,36), q144=divmod(a,144))

def symbol_region(symbol: int) -> int:
    if type(symbol) is not int or symbol not in NUCLEUS_ORDER:
        raise RosettaBoundaryError("invalid Lo Shu symbol")
    return NUCLEUS_ORDER.index(symbol)

@dataclass(frozen=True)
class Nucleus:
    symbol: int
    word: int
    polynomial: tuple[int, ...]
    quotient: int
    remainder: int
    region: int

    @classmethod
    def from_word(cls, symbol: int, word: int) -> "Nucleus":
        g = symbol_region(symbol)
        exact(word, 1 << 64, "64-bit word")
        q, r = divmod(word, symbol)
        n = cls(symbol, word, tuple((word >> bit) & 1 for bit in range(64)),q,r,g)
        n.validate()
        return n

    def validate(self) -> None:
        if self.region != symbol_region(self.symbol):
            raise RosettaBoundaryError("region mismatch")
        exact(self.word, 1 << 64, "word")
        if (len(self.polynomial) != 64 or
            any(type(bit) is not int or bit not in (0,1) for bit in self.polynomial) or
            sum(bit << j for j,bit in enumerate(self.polynomial)) != self.word or
            self.word != self.symbol*self.quotient+self.remainder or
            not 0 <= self.remainder < self.symbol):
            raise RosettaBoundaryError("lossless polynomial/modular boundary failed")

@dataclass(frozen=True)
class Genesis:
    nuclei: tuple[Nucleus, ...]

    @classmethod
    def from_words(cls, words: Sequence[int]) -> "Genesis":
        if len(words) != 9:
            raise RosettaBoundaryError("nine independent nucleus words required")
        return cls(tuple(Nucleus.from_word(k, word) for k,word in zip(NUCLEUS_ORDER,words)))

    def words(self) -> tuple[int,...]:
        if len(self.nuclei)!=9 or tuple(n.symbol for n in self.nuclei)!=NUCLEUS_ORDER:
            raise RosettaBoundaryError("Lo Shu order broken")
        for n in self.nuclei:
            n.validate()
        return tuple(n.word for n in self.nuclei)

    def address(self, symbol: int, local: int) -> dict:
        return coordinates(WIDTH*symbol_region(symbol)+exact(local,WIDTH,"local"))

def to_vm81_bytes(words: Sequence[int]) -> bytes:
    if len(words) != 81:
        raise RosettaBoundaryError("VM81 transport requires 81 words; no padding")
    return b"".join(exact(w,1<<64,"word").to_bytes(8,"little") for w in words)

def from_vm81_bytes(raw: bytes) -> tuple[int,...]:
    if type(raw) is not bytes or len(raw)!=648:
        raise RosettaBoundaryError("VM81 transport requires 648 bytes")
    return tuple(int.from_bytes(raw[i:i+8],"little") for i in range(0,648,8))

@dataclass(frozen=True)
class NativePhaseTensor:
    regions: tuple[Any, ...]
    source_identity: str

    def validate(self) -> None:
        if len(self.regions)!=64 or any(x is None for x in self.regions) or not self.source_identity:
            raise RosettaBoundaryError("64 native phase subregions and identity required")

@dataclass(frozen=True)
class NativeLayer:
    identifier: str
    modality_in: str
    modality_out: str
    transform: Callable[[Any, Genesis, NativePhaseTensor], Any]

def compose_candidate(*, words: Sequence[int], tensor: NativePhaseTensor,
                      input_modality: str, output_modality: str, source: Any,
                      ingress: Callable, layers: Sequence[NativeLayer],
                      egress: Callable) -> dict:
    genesis = Genesis.from_words(words)
    tensor.validate()
    if not layers or not callable(ingress) or not callable(egress):
        raise RosettaBoundaryError("native ingress/layer/egress required")
    prior = input_modality
    for layer in layers:
        if (not layer.identifier or not callable(layer.transform) or
            layer.modality_in != prior):
            raise RosettaBoundaryError("ordered native modality routing mismatch")
        prior = layer.modality_out
    if prior != output_modality:
        raise RosettaBoundaryError("egress mismatch")
    current = ingress(source)
    for layer in layers:
        current = layer.transform(current, genesis, tensor)
    return dict(candidate_output=egress(current), original_words=genesis.words(),
                ordered_layers=tuple(x.identifier for x in layers),
                tensor_identity=tensor.source_identity, candidate_only=True,
                canonical_vm81_mutation_authority=False,
                hash72_commit_authority=False, hash216_commit_authority=False)

def clock_address(frame: int, sweep: int, position: int) -> dict:
    if type(frame) is not int or frame<0:
        raise RosettaBoundaryError("negative frame")
    exact(sweep,2,"sweep")
    c = coordinates(position)
    return dict(**c, frame=frame,sweep=sweep,
                absolute_native_tick=10368*frame+5184*sweep+position,
                physical_layer=5184*sweep+position)

def inherited_conway_hash216_frame(*, occupancy: int, frame_id: int) -> dict:
    """Call existing I086→I085 bridge; no alternate clock or root."""
    exact(occupancy,1<<81,"Conway occupancy")
    if type(frame_id) is not int or frame_id<0:
        raise RosettaBoundaryError("negative frame")
    from hhs_runtime.hhs_pass220_i086_conway_life_projection_v1 import compose_conway_frame
    frame = compose_conway_frame(occupancy=occupancy,frame_id=frame_id)
    if (frame.get("candidate_only") is not True or
        frame.get("canonical_vm81_mutation_authority") is not False or
        frame.get("inherited_two_sweep_hash216_array") is not True or
        not frame.get("inherited_hash216_index_root_sha256")):
        raise RosettaBoundaryError("inherited I085/I086 witness invalid")
    return frame


# Mandatory native lowering: I073 exact palindromic IEEE/dyadic/RNA carrier
# -> public Pass219 RNA VM5184 ABI -> Pass219 C++ CoreHolographicRNACellWall
# -> inherited Lane5 Holo4/G3 candidate -> existing signed admission.
# This binding checks the *result of the real native bridge*; it is not a
# replacement Python interpreter for the cell wall or for native MatrixTimes.
NATIVE_LOWERING_SYMBOL = "hhs_exact_pass220_i028_lane5_rna_g3_route"
PALINDROMIC_INGRESS_ROOT = "PALINDROMIC_IEEE_EXACT_DYADIC_FRAME"
RNA_TRANSCRIPTION_ROOT = "ORDERED_XYZW_RNA_5184_TRANSCRIPTION"
CPP_CELL_WALL_ROOT = "PASS219_CPP_RNA_CELL_WALL"

def validate_native_cell_wall_candidate(candidate: Any) -> dict:
    """Validate the inherited C++ RNA cell-wall result; fail closed on bypass.

    The caller must invoke the real C ABI and expose its returned candidate
    flags. A dict is a transport view, not independent admission evidence.
    """
    if not isinstance(candidate, dict):
        raise RosettaBoundaryError("native cell-wall candidate record required")
    required_true = (
        "surface_linux_api_abi_ingress",
        "lane5_zero_bypass_interposer",
        "cpp_rna_cell_wall_routed",
        "holo4_evidence_equivalent",
        "pqc_firewall_required_for_canonical_admission",
        "signed_environmental_vm81_required",
    )
    required_zero = (
        "direct_environmental_opcode_canonical_authority",
        "direct_abi_canonical_authority",
        "direct_vm81_bypass_authority",
        "canonical_admission_invoked",
        "external_egress_authority",
    )
    if any(candidate.get(field) not in (True, 1) for field in required_true):
        raise RosettaBoundaryError("mandatory C++ RNA cell-wall route not proven")
    if any(candidate.get(field) not in (False, 0) for field in required_zero):
        raise RosettaBoundaryError("unapproved native admission/egress authority")
    if not candidate.get("rna_prepared") or not candidate.get("rna_decision") or not candidate.get("g3_candidate"):
        raise RosettaBoundaryError("missing inherited RNA/Holo4/G3 candidate evidence")
    return candidate

def lower_via_native_rna_cell_wall(*, genome: Genesis,
                                   phase_tensor: NativePhaseTensor,
                                   native_bridge: Callable[..., dict],
                                   native_request: Any) -> dict:
    """Require inherited native ABI invocation, not x64/VM81 emulation.

    native_bridge is the installed FFI binding of
    hhs_exact_pass220_i028_lane5_rna_g3_route. Its native_request contains
    source UQCEL input, VM81 frame, Hash216 transition, mandatory constructor
    witness and selected IEEE/P4/C4 cell positions. The FFI result MUST contain
    the C++ RNA cell-wall evidence returned by that native ABI.
    """
    genome.words()
    phase_tensor.validate()
    if not callable(native_bridge):
        raise RosettaBoundaryError("installed native C++ RNA bridge required")
    candidate = validate_native_cell_wall_candidate(native_bridge(native_request))
    return {
        "native_lowering_symbol": NATIVE_LOWERING_SYMBOL,
        "ingress_roots": (
            PALINDROMIC_INGRESS_ROOT,
            RNA_TRANSCRIPTION_ROOT,
            CPP_CELL_WALL_ROOT,
        ),
        "nucleus_symbols": NUCLEUS_ORDER,
        "native_phase_tensor_identity": phase_tensor.source_identity,
        "ordered_native_candidate": candidate,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
        "external_egress_authority": False,
    }


def inherited_palindromic_rna_transcription(
    *, decimal_text: str, offsets: Sequence[int],
    nucleus_index: int = 0, nesting_depth: int = 0,
) -> dict:
    """Execute actual I073 exact/dyadic/RNA/BigInt lowering constructor.

    The I073 81 offsets are its typed 0..8 scientific-token source, NOT
    substitutes for nine independent 64-bit Lo Shu raw polynomial nuclei.
    """
    if type(decimal_text) is not str or not decimal_text:
        raise RosettaBoundaryError("exact decimal source text required")
    if (len(offsets) != 81 or any(
        type(v) is not int or not 0 <= v <= 8 for v in offsets
    )):
        raise RosettaBoundaryError("I073 ingress requires 81 exact offsets in 0..8")
    from hhs_runtime.hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1 import (
        build_generator, validate_generator, reconstruct_serialized_state,
    )
    generator = build_generator(
        decimal_text=decimal_text, offsets=tuple(offsets),
        nucleus_index=nucleus_index, nesting_depth=nesting_depth,
    )
    if validate_generator(generator) is not True:
        raise RosettaBoundaryError("inherited I073 validation rejected")
    serialized = reconstruct_serialized_state(generator)
    if len(serialized) != LIMIT:
        raise RosettaBoundaryError("I073 exact 5184-character reconstruction failed")
    return {
        "inherited_i073_generator": generator,
        "reconstructed_5184": serialized,
        "inherited_i073_validation": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "hash216_commit_authority": False,
    }
