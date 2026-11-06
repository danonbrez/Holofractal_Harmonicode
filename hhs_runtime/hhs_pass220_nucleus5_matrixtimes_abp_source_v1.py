"""Pass 220 nucleus-5 MatrixTimes source and A/B/P parameter circuit.

The verbatim HARMONICODE source is a single ordered, typed source expression.
This module is a source-preserving ingress descriptor, NOT a replacement
solver, alternative mutation authority, or host scalar interpreter.
Native Pass 159 -> VM81 -> Lane 5 -> Hash72/Hash216 must perform execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

SCHEMA = "HHS_PASS220_NUCLEUS5_MATRIXTIMES_ABP_SOURCE_V1"
NUCLEUS_CELL = 5
VERBATIM_SOURCE = "MatrixTimes(153*x^2,({{3334608*x^6*y^4*z^4+-153*z^4*(-x+z)/(x*y),-153*z^4*(x+z)/(x*y),-153*z^4*(x+z)/(x*y),-2892672*x^6*y^4*z^4+-153*z^4*(-x+z)/(x*y)},{-153*(w+y)*z^4/(x*y),-153*(w-y)*z^4/(x*y)+3334608*x^6*y^4*z^4,(-153)*(w-y)*z^4/(x*y)-2892672*x^6*y^4*z^4,-153*(w+y)*z^4/(x*y)},{-153*z^3*(x+z)/w,(-153)*(x-z)*z^3/w-2892672*x^6*y^4*z^4,-153*(x-z)*z^3/w+3334608*x^6*y^4*z^4,-153*z^3*(x+z)/w},{(-153)*((-w)+y)*z^3/w-2892672*x^6*y^4*z^4,-153*(w+y)*z^3/w,-153*(w+y)*z^3/w,-153*(-w+y)*z^3/w+3334608*x^6*y^4*z^4}}=={{1377*(370512+17*x)/(x*y),-23409/y,-23409/y,1377*(-321408+17*x)/(x*y)},{-23409/x,1377*(370512+17*y)/(x*y),1377*(-321408+17*y)/(x*y),-23409/x},{-23409*z/(x*y),1377*(-321408+17*z)/(x*y),1377*(370512+17*z)/(x*y),-23409*z/(x*y)},{1377*(-321408+17*w)/(x*y),-23409*w/(x*y),-23409*w/(x*y),1377*(370512+17*w)/(x*y)}}==(w^4+x^4+y^4+z^4)/(w^2+x^2+y^2+z^2)==x^2))/(MatrixTimes(360/({{1,4,9,-1},{3,1,-1,2},{8,-1,1,7},{-1,1,6,1}}+2)/72,3/20))"
RECIPROCAL_SOURCE = "MatrixTimes(360/({{1,4,9,-1},{3,1,-1,2},{8,-1,1,7},{-1,1,6,1}}+2)/72,3/20)"
SOURCE_VARIABLES = ("x", "y", "z", "w", "A", "B", "P", "p", "q")
# These are native ordered proof edges, not Python equations to evaluate.
ABP_ORDERED_EDGES = (
    "p==P-1",
    "q==P+1",
    "pq==P^2-1",
    "P^2-pq==1",
    "A==P^2",
    "B==P^2",
    "A==B",
    "AB==P^4",
    "BA==-P^4",
)
# The two circuits are *not* contradictory A/B/P branch theories:
# the second includes one additional ordered successor constructor.
# P remains a typed native input, never a Python-derived free scalar.
PARAMETER_CONFIGURATIONS = (
    ("ONE_INPUT",),
    ("SUCCESSOR_INPUT", "P_next==P+3", "p_next==P_next-1",
     "q_next==P_next+1", "A_next==P_next^2", "B_next==P_next^2"),
)

@dataclass(frozen=True)
class Nucleus5Source:
    """Immutable ingress payload for the existing native source pipeline."""
    source: str = VERBATIM_SOURCE
    nucleus_cell: int = NUCLEUS_CELL
    schema: str = SCHEMA

    @property
    def exact_source_sha256(self) -> str:
        return sha256(self.source.encode("utf-8")).hexdigest()

    def parameter_edges(self, configuration: str) -> tuple[str, ...]:
        """Return ordered source relationships; do not evaluate or simplify."""
        for name, *edges in PARAMETER_CONFIGURATIONS:
            if configuration == name:
                return ABP_ORDERED_EDGES + tuple(edges)
        raise ValueError("UNKNOWN_ABP_CONFIGURATION")


    def native_compilation_source_bytes(self, configuration: str) -> bytes:
        """One ordered circuit for the existing Pass159 source/constraint pipeline.

        The original MatrixTimes source remains a verbatim, contiguous operand.
        Each ABP relation is retained as its own ordered equality occurrence;
        the mutually exclusive configuration's condition is not imposed on
        the other configuration. The result must still pass native admission.
        """
        edges = self.parameter_edges(configuration)
        # List is the existing HARMONICODE ordered circuit container.
        # No Python math, Boolean equality, or scalar substitution occurs.
        return ("List(" + self.source + "," + ",".join(edges) + ")").encode("utf-8")

    def native_source_bytes(self) -> bytes:
        """Ingress bytes for hhs159_source_open_bytes (no host coercion)."""
        return self.source.encode("utf-8")


def structural_source_checks() -> dict[str, bool]:
    """Source-integrity checks only; do not claim VM81 admission."""
    return {
        "one_outer_numerator": VERBATIM_SOURCE.startswith("MatrixTimes(153*x^2,("),
        "one_reciprocal_denominator": VERBATIM_SOURCE.endswith("/(" + RECIPROCAL_SOURCE + ")"),
        "full_chained_equalities": VERBATIM_SOURCE.count("==") == 3,
        "quartic_ratio_retained": "(w^4+x^4+y^4+z^4)/(w^2+x^2+y^2+z^2)==x^2" in VERBATIM_SOURCE,
        "four_by_four_target_start": "=={{1377*(370512+17*x)/(x*y)" in VERBATIM_SOURCE,
        "variable_four_distinct": all(v in VERBATIM_SOURCE for v in ("x", "y", "z", "w")),
        "ordered_ab_ba_distinct": ("AB==P^4" in ABP_ORDERED_EDGES and "BA==-P^4" in ABP_ORDERED_EDGES),
        "canonical_one_input_roles": all(edge in ABP_ORDERED_EDGES for edge in ("A==P^2", "B==P^2", "A==B")),
        "successor_is_extension": PARAMETER_CONFIGURATIONS[1][1] == "P_next==P+3",
    }


@dataclass(frozen=True)
class Nucleus5HNANIngress:
    """Typed source handoff; no separate VM81 or Hash216 authority."""
    source_bytes: bytes
    compilation_source_bytes: bytes
    compilation_source_sha256: str
    parameter_edge_bytes: tuple[bytes, ...]
    configuration: str
    nucleus_cell: int
    source_sha256: str
    inherited_hnan_receipt_sha256: str
    inherited_hnan_terminal_source: str
    inherited_qgu_receipt_sha256: str


def bind_inherited_hnan_ingress(configuration: str) -> Nucleus5HNANIngress:
    """Prepare the exact source for native admission using the existing HNAN gate.

    No evaluation of MatrixTimes or input/output variables occurs here.
    This binding is fail-closed on a rejected inherited HNAN/QGU receipt.
    The resulting bytes must be passed to native Pass159/VM81 admission
    before any canonical Hash72 or Hash216 state can be committed.
    """
    from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
        HNAN_CENTER_EXPRESSION,
        HNAN_TERMINAL_SOURCE,
        hnan_loshu_resolution_receipt,
    )

    source = Nucleus5Source()
    edges = source.parameter_edges(configuration)
    checks = structural_source_checks()
    if not all(checks.values()):
        raise ValueError("NUCLEUS5_SOURCE_INTEGRITY_REJECTED")

    receipt = hnan_loshu_resolution_receipt()
    transport = receipt.get("qgu_transport")
    if (
        receipt.get("status") != "PASS"
        or receipt.get("center_expression") != HNAN_CENTER_EXPRESSION
        or receipt.get("terminal_source") != HNAN_TERMINAL_SOURCE
        or not isinstance(transport, dict)
        or transport.get("status") != "PASS"
        or not isinstance(receipt.get("receipt_sha256"), str)
        or not isinstance(transport.get("receipt_sha256"), str)
    ):
        raise ValueError("INHERITED_HNAN_QGU_GATE_REJECTED")

    return Nucleus5HNANIngress(
        source_bytes=source.native_source_bytes(),
        compilation_source_bytes=source.native_compilation_source_bytes(configuration),
        compilation_source_sha256=sha256(source.native_compilation_source_bytes(configuration)).hexdigest(),
        parameter_edge_bytes=tuple(edge.encode("utf-8") for edge in edges),
        configuration=configuration,
        nucleus_cell=source.nucleus_cell,
        source_sha256=source.exact_source_sha256,
        inherited_hnan_receipt_sha256=receipt["receipt_sha256"],
        inherited_hnan_terminal_source=receipt["terminal_source"],
        inherited_qgu_receipt_sha256=transport["receipt_sha256"],
    )
