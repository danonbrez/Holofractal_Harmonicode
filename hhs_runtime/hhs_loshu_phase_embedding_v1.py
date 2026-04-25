"""
HHS Lo Shu Phase Embedding v1
================================

Closed positional/state embedding adapter for the Holofractal Harmonicode
runtime.  This module replaces the transformer sinusoidal base 10000 with the
integer phase anchor P=179971 and projects position/dimension pairs into:

    position -> u^72 phase -> 81-cell Lo Shu address -> xyzw DNA -> Hash72 receipt

Design rules preserved here:

* no floating point state in the core path
* no commutation of ordered carriers
* position deterministically implies phase/address/DNA/receipt metadata
* scalar/vector projections are optional shadow exports only

The module is intentionally dependency-free and can run before the full HHS
runtime bundle is hydrated into the repository.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Iterable, List, Sequence, Tuple


PHASE_BASE: int = 179_971
PHASE_PREDECESSOR: int = PHASE_BASE - 1
PHASE_SUCCESSOR: int = PHASE_BASE + 1
TORUS_ORDER: int = 72
LO_SHU_CELLS: int = 81
LO_SHU_SIDE: int = 9
PALINDROMIC_RESONANCE = Fraction(179_971_179_971, 1_000_000)

# 72 symbols: 10 digits + 26 lowercase + 26 uppercase + 10 operators.
HASH72_ALPHABET: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()^√=≠"

# Canonical 3x3 Lo Shu seed, lifted/tiled into 9x9 addressing.
LO_SHU_3X3: Tuple[Tuple[int, int, int], ...] = (
    (4, 9, 2),
    (3, 5, 7),
    (8, 1, 6),
)

DNA_SYMBOLS: Tuple[str, str, str, str] = ("x", "y", "z", "w")
DNA_COMPLEMENT: Dict[str, str] = {"x": "w", "w": "x", "y": "z", "z": "y"}
FORBIDDEN_ADJACENCIES = {("x", "z"), ("z", "x"), ("y", "w"), ("w", "y")}


@dataclass(frozen=True)
class LoShuAddress:
    """Expanded 9x9 Lo Shu cell address."""

    cell_index: int
    row: int
    col: int
    lo_shu_value: int
    tile_row: int
    tile_col: int


@dataclass(frozen=True)
class PhaseEmbeddingState:
    """Fully qualified HHS positional embedding state."""

    token: str
    position: int
    dimension: int
    d_model: int
    phase_base: int
    phase_index: int
    reciprocal_phase_index: int
    carrier: str
    reciprocal_carrier: str
    lo_shu: LoShuAddress
    xyzw_dna: str
    hash72: str
    receipt_hash72: str
    invariants: Dict[str, bool]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class EmbeddingReceipt:
    """Batch receipt for a token sequence."""

    module: str
    phase_base: int
    torus_order: int
    lo_shu_cells: int
    palindromic_resonance: str
    adjacency_identity_ok: bool
    states: List[PhaseEmbeddingState]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def adjacency_identity_ok() -> bool:
    """Verify P^2 - (P-1)(P+1) = 1 for the 179971 anchor."""

    return PHASE_BASE * PHASE_BASE - PHASE_PREDECESSOR * PHASE_SUCCESSOR == 1


def _base72_digits(value: int, width: int = 1) -> str:
    """Encode a non-negative integer into HASH72 alphabet symbols."""

    if value < 0:
        raise ValueError("Hash72 digit encoding expects a non-negative integer")
    if len(HASH72_ALPHABET) != TORUS_ORDER:
        raise RuntimeError("HASH72_ALPHABET must contain exactly 72 symbols")

    digits: List[str] = []
    n = value
    if n == 0:
        digits.append(HASH72_ALPHABET[0])
    while n:
        n, r = divmod(n, TORUS_ORDER)
        digits.append(HASH72_ALPHABET[r])
    encoded = "".join(reversed(digits))
    if width > len(encoded):
        encoded = HASH72_ALPHABET[0] * (width - len(encoded)) + encoded
    return encoded


def hash72_digest(parts: Iterable[object], width: int = 18) -> str:
    """
    Deterministic HASH72-native digest.

    This is not SHA and is not a cryptographic claim. It is a lightweight
    repository-local receipt constructor that keeps all emitted symbols in the
    72-character HHS alphabet until the full Hash72 authority is present.
    """

    modulus = TORUS_ORDER ** width
    state = PHASE_BASE % modulus
    for part in parts:
        text = str(part)
        for ch in text:
            state = (state * PHASE_BASE + ord(ch) + 1) % modulus
            state ^= (state << 7) % modulus
            state %= modulus
    return _base72_digits(state, width=width)[-width:]


def phase_frequency(dimension: int, d_model: int) -> int:
    """
    Dimension-specific closed phase gear.

    Standard transformers use 10000^(2i/d_model), which introduces fractional
    powers/floats.  The HHS core instead derives an exact gear from P=179971 in
    Z_72.  The dimension and model width both participate so every coordinate is
    position-derived but model-shape aware.
    """

    if dimension < 0:
        raise ValueError("dimension must be non-negative")
    if d_model <= 0:
        raise ValueError("d_model must be positive")

    exponent = 2 * dimension + 1
    base_gear = pow(PHASE_BASE, exponent, TORUS_ORDER)
    width_gate = (d_model % TORUS_ORDER) or TORUS_ORDER
    gear = (base_gear + width_gate + dimension) % TORUS_ORDER
    return gear or 1


def phase_index(position: int, dimension: int, d_model: int) -> int:
    """Map a position/dimension pair into the closed u^72 phase ring."""

    gear = phase_frequency(dimension, d_model)
    return (position * gear + dimension * dimension + PHASE_BASE) % TORUS_ORDER


def carrier_symbol(n: int) -> str:
    """Return formal carrier u^n."""

    return f"u^{n % TORUS_ORDER}"


def lo_shu_address(phase_n: int, dimension: int = 0) -> LoShuAddress:
    """
    Lift a phase index into the 81-cell Lo Shu qudit address space.

    Phase alone covers 72 states.  Dimension supplies the remaining address
    spread without breaking determinism: position/dimension -> cell is unique
    and replayable.
    """

    cell_index = (phase_n + 9 * (dimension % 9)) % LO_SHU_CELLS
    row, col = divmod(cell_index, LO_SHU_SIDE)
    tile_row, local_row = divmod(row, 3)
    tile_col, local_col = divmod(col, 3)
    return LoShuAddress(
        cell_index=cell_index,
        row=row,
        col=col,
        lo_shu_value=LO_SHU_3X3[local_row][local_col],
        tile_row=tile_row,
        tile_col=tile_col,
    )


def _repair_pair(left: str, right: str) -> Tuple[str, str]:
    """Repair forbidden local adjacency while preserving complement closure."""

    if (left, right) not in FORBIDDEN_ADJACENCIES:
        return left, right
    # Rotate the right symbol to the next legal DNA symbol, then recompute the
    # eventual reverse complement in xyzw_dna().
    idx = (DNA_SYMBOLS.index(right) + 1) % len(DNA_SYMBOLS)
    candidate = DNA_SYMBOLS[idx]
    while (left, candidate) in FORBIDDEN_ADJACENCIES:
        idx = (idx + 1) % len(DNA_SYMBOLS)
        candidate = DNA_SYMBOLS[idx]
    return left, candidate


def xyzw_dna(phase_n: int, address: LoShuAddress, length: int = 8) -> str:
    """
    Serialize phase/address into ordered xyzw digital DNA.

    The emitted strand is reverse-complement sealed:
        first x -> last w, first y -> last z, etc.
    Forbidden adjacent pairs x-z and y-w are repaired locally before sealing.
    """

    if length < 4 or length % 2:
        raise ValueError("xyzw DNA length must be an even integer >= 4")

    seed = phase_n + address.cell_index + 5 * address.lo_shu_value + 13 * address.row + 17 * address.col
    half: List[str] = []
    n = seed
    for i in range(length // 2):
        symbol = DNA_SYMBOLS[n % 4]
        if half:
            prev, symbol = _repair_pair(half[-1], symbol)
            half[-1] = prev
        half.append(symbol)
        n = (n * PHASE_BASE + i + address.lo_shu_value) % (4 ** 8)

    mirror = [DNA_COMPLEMENT[ch] for ch in reversed(half)]
    strand = "".join(half + mirror)

    for left, right in zip(strand, strand[1:]):
        if (left, right) in FORBIDDEN_ADJACENCIES:
            raise RuntimeError(f"forbidden xyzw adjacency survived repair: {left}{right}")
    return strand


def state_invariants(phase_n: int, reciprocal_n: int, dna: str, address: LoShuAddress) -> Dict[str, bool]:
    """Runtime guard surface for one positional state."""

    complement_ok = all(DNA_COMPLEMENT[dna[i]] == dna[-i - 1] for i in range(len(dna) // 2))
    adjacency_ok = all((a, b) not in FORBIDDEN_ADJACENCIES for a, b in zip(dna, dna[1:]))
    return {
        "phase_base_adjacency_identity": adjacency_identity_ok(),
        "u72_reciprocal_closure": (phase_n + reciprocal_n) % TORUS_ORDER == 0,
        "lo_shu_address_in_range": 0 <= address.cell_index < LO_SHU_CELLS,
        "xyzw_reverse_complement": complement_ok,
        "xyzw_forbidden_adjacency_clear": adjacency_ok,
        "theta15_shadow_ok": sum(sum(row) for row in LO_SHU_3X3) == 45,
    }


def embed_token(token: str, position: int, dimension: int, d_model: int) -> PhaseEmbeddingState:
    """Build one fully qualified Lo Shu phase embedding state."""

    if position < 0:
        raise ValueError("position must be non-negative")

    n = phase_index(position, dimension, d_model)
    reciprocal_n = (-n) % TORUS_ORDER
    address = lo_shu_address(n, dimension)
    dna = xyzw_dna(n, address)
    state_hash = hash72_digest((token, position, dimension, d_model, n, reciprocal_n, address, dna))
    invariants = state_invariants(n, reciprocal_n, dna, address)
    receipt_hash = hash72_digest((state_hash, sorted(invariants.items())))

    return PhaseEmbeddingState(
        token=token,
        position=position,
        dimension=dimension,
        d_model=d_model,
        phase_base=PHASE_BASE,
        phase_index=n,
        reciprocal_phase_index=reciprocal_n,
        carrier=carrier_symbol(n),
        reciprocal_carrier=carrier_symbol(reciprocal_n),
        lo_shu=address,
        xyzw_dna=dna,
        hash72=state_hash,
        receipt_hash72=receipt_hash,
        invariants=invariants,
    )


def embed_sequence(tokens: Sequence[str], d_model: int = 72, dimensions: int | None = None) -> EmbeddingReceipt:
    """Embed a token sequence into Lo Shu addressable phase states."""

    if dimensions is None:
        dimensions = min(d_model, TORUS_ORDER)
    if dimensions <= 0:
        raise ValueError("dimensions must be positive")

    states: List[PhaseEmbeddingState] = []
    for position, token in enumerate(tokens):
        for dimension in range(dimensions):
            states.append(embed_token(token, position, dimension, d_model))

    receipt_hash = hash72_digest(state.receipt_hash72 for state in states)
    return EmbeddingReceipt(
        module="hhs_loshu_phase_embedding_v1",
        phase_base=PHASE_BASE,
        torus_order=TORUS_ORDER,
        lo_shu_cells=LO_SHU_CELLS,
        palindromic_resonance=f"{PALINDROMIC_RESONANCE.numerator}/{PALINDROMIC_RESONANCE.denominator}",
        adjacency_identity_ok=adjacency_identity_ok(),
        states=states,
        receipt_hash72=receipt_hash,
    )


def shadow_float_projection(state: PhaseEmbeddingState) -> Tuple[float, float]:
    """
    Optional transformer-compatible shadow projection.

    The core state is exact.  This function is only for legacy vector consumers
    that still expect sin/cos-like float pairs.
    """

    import math

    theta = 2.0 * math.pi * state.phase_index / TORUS_ORDER
    return math.sin(theta), math.cos(theta)


def demo() -> Dict[str, object]:
    """Small deterministic demo report."""

    receipt = embed_sequence(["HHS", "Hash72", "LoShu", "xyzw"], d_model=72, dimensions=4)
    return receipt.to_dict()


if __name__ == "__main__":
    import json

    print(json.dumps(demo(), indent=2, sort_keys=True))
