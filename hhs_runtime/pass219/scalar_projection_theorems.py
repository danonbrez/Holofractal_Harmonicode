"""Pass 219 exhaustive HARMONICODE scalar-projection theorem registry.

The registry annotates native source expressions with fixed, parameterized,
multibranch, symbolic, unsupported, or typed-nonscalar projection semantics.
It does not parse/evaluate HARMONICODE independently and has no canonical
mutation, Hash72 mint, or Hash216 persistence authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass219.scalar_projection_proofs import (
    CANONICAL_SOURCE_BYTES,
    CANONICAL_SOURCE_PATH,
    CANONICAL_SOURCE_SHA256,
    PROOF_BY_ID,
    verify_canonical_source,
)

SCHEMA = "HHS_PASS219_SCALAR_PROJECTION_THEOREM_REGISTRY_V1"
CONTRACT_ID = "HHS-P219-SCALAR-PROJECTION-THEOREM-REGISTRY-1.1"

FIXED = "FIXED_SCALAR"
PARAMETERIZED = "PARAMETERIZED_SCALAR"
MULTIBRANCH = "MULTIBRANCH_SCALAR"
SYMBOLIC = "SYMBOLIC_SCALAR"
UNSUPPORTED = "UNSUPPORTED_DOMAIN"
TYPED_NONSCALAR = "TYPED_NONSCALAR"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True)
class ProjectionTheorem:
    theorem_id: str
    native_expression: str
    projection_class: str
    projection_id: str
    domain: str
    result_expression: str | None
    premises: tuple[str, ...] = ()
    derivation: tuple[str, ...] = ()
    fixed_proof_id: str | None = None
    source_needles: tuple[str, ...] = ()
    source_scope: str = "PASS169_OR_REGISTERED_PASS219"
    reverse_lift_rule: str = "NONE"
    lost_information: tuple[str, ...] = ("native_expression_identity",)

    def to_dict(self) -> dict[str, object]:
        if self.fixed_proof_id is not None and self.fixed_proof_id not in PROOF_BY_ID:
            raise ValueError(f"UNKNOWN_FIXED_PROOF:{self.theorem_id}:{self.fixed_proof_id}")
        body: dict[str, object] = {
            "theorem_id": self.theorem_id,
            "claim_type": "PROJECTION_THEOREM",
            "native_expression": self.native_expression,
            "projection_class": self.projection_class,
            "projection_id": self.projection_id,
            "domain": self.domain,
            "result_expression": self.result_expression,
            "premises": list(self.premises),
            "derivation": list(self.derivation),
            "fixed_proof_id": self.fixed_proof_id,
            "source_needles": list(self.source_needles),
            "source_scope": self.source_scope,
            "reverse_lift_rule": self.reverse_lift_rule,
            "lost_information": list(self.lost_information),
            "projection_equality_implies_native_identity": False,
            "source_rewrite_authorized": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_persistence_authority": False,
            "floating_point_canonical_authority": False,
        }
        body["theorem_sha256"] = sha256(_canonical_json(body).encode("utf-8")).hexdigest()
        body["theorem_receipt_hash72"] = hash72_digest(
            {"domain": "HHS-P219-SCALAR-PROJECTION-THEOREM-V1", "theorem_id": self.theorem_id},
            body,
        )
        return body


def _t(
    tid: str,
    expr: str,
    kind: str,
    result: str | None,
    *steps: str,
    projection_id: str = "PI-SCALAR-ORDINARY-v1",
    domain: str = "EXACT_TYPED_PROJECTION",
    premises: Iterable[str] = (),
    fixed_proof_id: str | None = None,
    source_needles: Iterable[str] = (),
    source_scope: str = "PASS169_OR_REGISTERED_PASS219",
    reverse_lift_rule: str = "NONE",
) -> ProjectionTheorem:
    return ProjectionTheorem(
        tid,
        expr,
        kind,
        projection_id,
        domain,
        result,
        tuple(premises),
        tuple(steps),
        fixed_proof_id,
        tuple(source_needles),
        source_scope,
        reverse_lift_rule,
    )


# Multiple records for one symbol are intentional when separate registered
# projection domains expose different scalar views. A view never overwrites
# the native source object or another projection domain.
THEOREMS: tuple[ProjectionTheorem, ...] = (
    _t("SPT001", "a^2", FIXED, "1", "delegate to SPP001", fixed_proof_id="SPP001", source_scope="REGISTERED_PASS169_SYMBOL_REGISTRY"),
    _t("SPT002", "b^2", FIXED, "2", "delegate to SPP002", fixed_proof_id="SPP002", source_needles=("b^2",)),
    _t("SPT003", "c^2", FIXED, "3", "delegate to SPP003", fixed_proof_id="SPP003", source_needles=("c^2",)),
    _t("SPT004", "b^4", FIXED, "4", "delegate to SPP008", fixed_proof_id="SPP008", source_needles=("b^4",)),
    _t("SPT005", "c^4", FIXED, "9", "delegate to SPP009", fixed_proof_id="SPP009", source_needles=("c^4",)),
    _t("SPT006", "b^6", FIXED, "8", "delegate to SPP010", fixed_proof_id="SPP010", source_needles=("b^6",)),
    _t("SPT007", "b^2*c^2", FIXED, "6", "delegate to SPP011", fixed_proof_id="SPP011", source_needles=("b^2c^2",)),
    _t("SPT008", "b^2+c^2", FIXED, "5", "delegate to SPP012", fixed_proof_id="SPP012", source_scope="REGISTERED_LOSHU_PROJECTION"),
    _t("SPT009", "b^4+c^2", FIXED, "7", "delegate to SPP013", fixed_proof_id="SPP013", source_needles=("b^4+c^2",)),
    _t("SPT010", "c^2-b^2", FIXED, "1", "delegate to SPP015", fixed_proof_id="SPP015", source_needles=("c^2-b^2",)),
    _t("SPT011", "2*c^2+b^2", FIXED, "8", "delegate to SPP017", fixed_proof_id="SPP017", source_needles=("(2c^2)+b^2",)),
    _t("SPT012", "2/b^2", FIXED, "1", "delegate to SPP018", fixed_proof_id="SPP018", source_needles=("2/b^2",)),
    _t("SPT013", "b^6*c^4", FIXED, "72", "delegate to SPP025", fixed_proof_id="SPP025", source_needles=("72",)),

    _t("SPT014", "a", MULTIBRANCH, "{+1,-1}",
       "c^4-b^2*c^2-b^4+b^2 -> 1", "c^2-b^2 -> 1", "a is represented by the explicit +/- radical branches",
       projection_id="PI-HHCQ-A-RADICAL-BRANCH-v1", domain="REGISTERED_EXACT_RADICAL_BRANCH",
       premises=("a^2=1",), source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT015", "b", SYMBOLIC, "root_of(X^2-2)",
       "b^2 projects to 2 but no global sign/root branch is chosen",
       projection_id="PI-ALGEBRAIC-ROOT-v1", domain="SYMBOLIC_ALGEBRAIC_ROOT", premises=("b^2=2",)),
    _t("SPT016", "c", SYMBOLIC, "root_of(X^2-3)",
       "c^2 projects to 3 but no global sign/root branch is chosen",
       projection_id="PI-ALGEBRAIC-ROOT-v1", domain="SYMBOLIC_ALGEBRAIC_ROOT", premises=("c^2=3",)),
    _t("SPT017", "P", PARAMETERIZED, "P", "P is an exact candidate coordinate, not a fixed numeral",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="POSITIVE_BIGINT_INPUT", source_needles=("P^2",)),
    _t("SPT018", "p", PARAMETERIZED, "p", "p is an exact candidate coordinate",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="POSITIVE_ODD_BIGINT_INPUT", source_needles=("pq",)),
    _t("SPT019", "q", PARAMETERIZED, "q", "q is an exact candidate coordinate",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="POSITIVE_ODD_BIGINT_INPUT", source_needles=("pq",)),
    _t("SPT020", "Delta", PARAMETERIZED, "Delta", "Delta is an exact nonnegative candidate residue in UCE",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="NONNEGATIVE_BIGINT_INPUT", source_needles=("∆",)),

    _t("SPT021", "Delta", FIXED, "1", "delegate to SPP032", fixed_proof_id="SPP032",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL"),
    _t("SPT022", "p", PARAMETERIZED, "P-Delta", "q-P=Delta and P-p=Delta", "therefore p=P-Delta",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL", premises=("P-p=Delta",)),
    _t("SPT023", "q", PARAMETERIZED, "P+Delta", "q-P=Delta", "therefore q=P+Delta",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL", premises=("q-P=Delta",)),
    _t("SPT024", "p+q", PARAMETERIZED, "2P", "(P-Delta)+(P+Delta)=2P",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL"),
    _t("SPT025", "q-p", PARAMETERIZED, "2Delta", "(P+Delta)-(P-Delta)=2Delta",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL"),
    _t("SPT026", "p*q", PARAMETERIZED, "P^2-Delta^2", "(P-Delta)(P+Delta)=P^2-Delta^2",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL", source_needles=("pq",)),
    _t("SPT027", "P^2-p*q", FIXED, "1", "delegate to SPP033", fixed_proof_id="SPP033",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL", source_needles=("P²-pq",)),
    _t("SPT028", "t^3-t", PARAMETERIZED, "Delta",
       "Pass129 binds the rational projection residue t^3-t to Delta without solving t",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_RATIONAL_RESIDUE_ONLY",
       premises=("t^3-t=Delta",), source_needles=("t^3-t",)),
    _t("SPT029", "m^2-m", PARAMETERIZED, "Delta",
       "Pass129 binds the rational projection residue m^2-m to Delta without solving m",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_RATIONAL_RESIDUE_ONLY",
       premises=("m^2-m=Delta",), source_needles=("m^2-m",)),
    _t("SPT030", "xy", PARAMETERIZED, "Delta",
       "Pass129 binds the scalar residue projection of ordered xy to Delta while retaining native order",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_ORDERED_PHASE_RESIDUE",
       premises=("xy=Delta",), source_needles=("xy",)),
    _t("SPT031", "zw", FIXED, "1", "Pass129 three-way membrane uses zw=1 on the declared witness branch",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_DECLARED_MEMBRANE_WITNESS",
       premises=("Delta=1", "xy=1", "zw=1")),
    _t("SPT032", "x+y+z+w", FIXED, "0", "Pass129 declared membrane witness carries x+y+z+w=0",
       projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_DECLARED_MEMBRANE_WITNESS",
       premises=("x+y+z+w=0",), source_needles=("x+y+z+w",)),

    _t("SPT033", "x", PARAMETERIZED, "x_int", "Phase11 native phase coordinate x is represented as an exact integer",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="EXACT_INTEGER_PHASE_COORDINATE", source_needles=("x",)),
    _t("SPT034", "y", PARAMETERIZED, "y_int", "Phase11 native phase coordinate y is represented as an exact integer",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="EXACT_INTEGER_PHASE_COORDINATE", source_needles=("y",)),
    _t("SPT035", "z", PARAMETERIZED, "z_int", "Phase11 native phase coordinate z is represented as an exact integer",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="EXACT_INTEGER_PHASE_COORDINATE", source_needles=("z",)),
    _t("SPT036", "w", PARAMETERIZED, "w_int", "Phase11 native phase coordinate w is represented as an exact integer",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="EXACT_INTEGER_PHASE_COORDINATE", source_needles=("w",)),
    _t("SPT037", "xy", PARAMETERIZED, "ordered_product(x,y)", "ordered xy retains x then y provenance",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="ORDERED_EXACT_PHASE_PRODUCT", source_needles=("xy",)),
    _t("SPT038", "yx", PARAMETERIZED, "ordered_product(y,x)", "ordered yx retains y then x provenance",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="ORDERED_EXACT_PHASE_PRODUCT"),
    _t("SPT039", "zw", PARAMETERIZED, "ordered_product(z,w)", "ordered zw retains z then w provenance",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="ORDERED_EXACT_PHASE_PRODUCT"),
    _t("SPT040", "wz", PARAMETERIZED, "ordered_product(w,z)", "ordered wz retains w then z provenance",
       projection_id="PI-HHCQ-8BASIS-INTEGER-v1", domain="ORDERED_EXACT_PHASE_PRODUCT"),
    _t("SPT041", "Phi8=x+y+z+w+xy+yx+zw+wz", PARAMETERIZED, "b^2*P-(p+q)",
       "Phase11 macro/micro equilibrium binds Phi8 to b^2*P-(p+q)",
       projection_id="PI-HHCQ-8BASIS-EQUILIBRIUM-v1", domain="EXACT_RATIONAL_MACRO_MICRO_EQUILIBRIUM",
       premises=("b^2*P-(p+q)=Phi8",), source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT042", "P", PARAMETERIZED, "(Phi8+p+q)/2", "b^2=2", "2P-(p+q)=Phi8", "P=(Phi8+p+q)/2",
       projection_id="PI-HHCQ-8BASIS-EQUILIBRIUM-v1", domain="EXACT_RATIONAL_MACRO_MICRO_EQUILIBRIUM",
       premises=("b^2=2", "b^2*P-(p+q)=Phi8"), source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT043", "Phi8", FIXED, "0",
       "on the compatible Pass129 zero-residue branch p+q=2P and b^2=2", "therefore Phi8=0",
       projection_id="PI-HHCQ-P129-COMPAT-v1", domain="PASS129_ZERO_EQUILIBRIUM_BRANCH",
       premises=("p+q=2P", "b^2=2")),

    _t("SPT044", "P^2", PARAMETERIZED, "p*q+Delta", "UCE exact integer/symmetric constraint P^2=p*q+Delta",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="EXACT_BIGINT_UCE", source_needles=("P^2",)),
    _t("SPT045", "A", PARAMETERIZED, "P^2", "UCE symmetric projection A=P^2",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="EXACT_BIGINT_UCE", premises=("A=P^2",), source_needles=("AB",)),
    _t("SPT046", "B", PARAMETERIZED, "P^2", "UCE symmetric projection B=P^2",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="EXACT_BIGINT_UCE", premises=("B=P^2",), source_needles=("AB",)),
    _t("SPT047", "A*B", PARAMETERIZED, "P^4", "A=P^2 and B=P^2", "A*B=P^4",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="EXACT_BIGINT_UCE",
       premises=("A=P^2", "B=P^2"), source_needles=("AB",)),
    _t("SPT048", "Sqrt(A*B)", PARAMETERIZED, "P^2", "A*B=P^4", "for positive UCE P, principal exact Sqrt(P^4)=P^2",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="POSITIVE_EXACT_RADICAL_UCE", source_needles=("Sqrt[AB]",)),
    _t("SPT049", "A", PARAMETERIZED, "P^2*(p/q)", "Phase10 prime-rational constructor",
       projection_id="PI-HHCQ-PRIME-RATIONAL-v1", domain="EXACT_PRIME_RATIONAL", premises=("p,q distinct prime seeds",)),
    _t("SPT050", "B", PARAMETERIZED, "P^2*(q/p)", "Phase10 prime-rational constructor",
       projection_id="PI-HHCQ-PRIME-RATIONAL-v1", domain="EXACT_PRIME_RATIONAL", premises=("p,q distinct prime seeds",)),
    _t("SPT051", "A/B", PARAMETERIZED, "p^2/q^2", "[P^2(p/q)]/[P^2(q/p)]=p^2/q^2",
       projection_id="PI-HHCQ-PRIME-RATIONAL-v1", domain="EXACT_PRIME_RATIONAL"),
    _t("SPT052", "B/A", PARAMETERIZED, "q^2/p^2", "[P^2(q/p)]/[P^2(p/q)]=q^2/p^2",
       projection_id="PI-HHCQ-PRIME-RATIONAL-v1", domain="EXACT_PRIME_RATIONAL"),
    _t("SPT053", "(A/B)*(B/A)", FIXED, "1", "delegate to SPP034", fixed_proof_id="SPP034",
       projection_id="PI-HHCQ-PRIME-RATIONAL-v1", domain="EXACT_NONZERO_RECIPROCAL"),
    _t("SPT054", "AB/P^2", PARAMETERIZED, "P^2", "AB=P^4", "P!=0 on positive UCE domain", "P^4/P^2=P^2",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="POSITIVE_EXACT_BIGINT_UCE", source_needles=("AB/P^2",)),
    _t("SPT055", "AB/(pq+Delta)-P^2", FIXED, "0",
       "pq+Delta=P^2", "AB=P^4", "AB/(pq+Delta)=P^2", "P^2-P^2=0",
       projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="POSITIVE_EXACT_BIGINT_UCE",
       premises=("P^2=pq+Delta", "AB=P^4"), source_needles=("AB/(pq+∆)-P^2",)),

    _t("SPT056", "u", TYPED_NONSCALAR, None,
       "native u has type-distinct u_phase and u_q projections and no global scalar alias",
       projection_id="PI-U-MULTIPROJECTION-v1", domain="NATIVE_U_SOURCE", source_needles=("u^72",)),
    _t("SPT057", "u_phase^72", FIXED, "1", "delegate to SPP030", fixed_proof_id="SPP030",
       projection_id="PI-U-PHASE-v1", domain="REGISTERED_U72_PHASE"),
    _t("SPT058", "c^2-u_phase^72", FIXED, "2", "c^2->3", "u_phase^72->1", "3-1=2",
       projection_id="PI-U-PHASE-v1", domain="REGISTERED_U72_PHASE",
       premises=("c^2=3", "u_phase^72=1"), source_needles=("c^2-u^72",)),
    _t("SPT059", "pq+xy", PARAMETERIZED, "P^2", "Pass129: pq=P^2-1", "Pass129 scalar residue xy=1", "pq+xy=P^2",
       projection_id="PI-HHCQ-P129-COMPAT-v1", domain="PASS129_ORDERED_PHASE_RESIDUE", source_needles=("pq+xy",)),
    _t("SPT060", "72*(pq+xy)", PARAMETERIZED, "72*P^2", "b^6*c^4->72", "pq+xy->P^2",
       projection_id="PI-HHCQ-P129-COMPAT-v1", domain="PASS129_ORDERED_PHASE_RESIDUE", source_needles=("72*(pq+xy)",)),
    _t("SPT061", "b^6-xy", FIXED, "7", "b^6->8", "Pass129 scalar residue xy->1", "8-1=7",
       projection_id="PI-HHCQ-P129-COMPAT-v1", domain="PASS129_ORDERED_PHASE_RESIDUE", source_needles=("b^6-(xy)",)),

    _t("SPT062", "c^2-a^2", FIXED, "2", "c^2->3", "a^2->1", "3-1=2",
       projection_id="PI-HHCQ-B2-U72-v1", domain="EXACT_BASIS_NUMERAL", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT063", "(c^2-a^2)^2", FIXED, "4", "c^2-a^2->2", "2^2=4",
       projection_id="PI-HHCQ-B2-U72-v1", domain="EXACT_BASIS_NUMERAL", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT064", "(c^2-a^2)^2/(2*u_phase^72)", FIXED, "2", "numerator->4", "u_phase^72->1", "4/(2*1)=2",
       projection_id="PI-HHCQ-B2-U72-v1", domain="REGISTERED_U72_PHASE", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT065", "Pi-b^2+b^4-Pi", FIXED, "2",
       "identical symbolic Pi terms cancel only inside this scalar projection", "-2+4=2",
       projection_id="PI-HHCQ-SYMBOLIC-SCALAR-v1", domain="EXACT_SYMBOLIC_ADDITIVE_PROJECTION",
       source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT066", "(Pi-b^2+b^4-Pi)/(c^2-b^2)", FIXED, "2", "numerator->2", "c^2-b^2->1", "2/1=2",
       projection_id="PI-HHCQ-SYMBOLIC-SCALAR-v1", domain="EXACT_SYMBOLIC_ADDITIVE_PROJECTION",
       source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT067", "u_phase^0", FIXED, "1", "phase zero is the identity/origin phase",
       projection_id="PI-U-PHASE-v1", domain="REGISTERED_U72_PHASE", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT068", "b^4*c^2", FIXED, "12", "b^4->4", "c^2->3", "4*3=12",
       projection_id="PI-HHCQ-U0-REALSURD-v1", domain="EXACT_BASIS_NUMERAL", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT069", "RealSurd(b^2,b^4*c^2)", SYMBOLIC, "RealSurd(2,12)",
       "b^2->2", "b^4*c^2->12", "retain exact real algebraic root rather than IEEE approximation",
       projection_id="PI-HHCQ-U0-REALSURD-v1", domain="EXACT_ALGEBRAIC_ROOT", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT070", "Power(RealSurd(b^2,b^4*c^2),a^2)", SYMBOLIC, "RealSurd(2,12)",
       "a^2->1", "Power(root,1)=root in the registered exact algebraic projection",
       projection_id="PI-HHCQ-U0-REALSURD-v1", domain="EXACT_ALGEBRAIC_ROOT", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT071", "Power(RealSurd(b^2,b^4*c^2),a^2)^(b^6*c^4)", FIXED, "64",
       "RealSurd(2,12) is the exact real 12th root of 2", "b^6*c^4->72", "(2^(1/12))^72=2^6=64",
       projection_id="PI-HHCQ-U0-REALSURD-v1", domain="POSITIVE_EXACT_ALGEBRAIC_ROOT", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT072", "(b^6)^2", FIXED, "64", "b^6->8", "8^2=64",
       projection_id="PI-HHCQ-U0-REALSURD-v1", domain="EXACT_BASIS_NUMERAL", source_scope="REGISTERED_PASS219_HHCQ"),
    _t("SPT073", "Power(RealSurd(b^2,b^4*c^2),a^2)^(b^6*c^4)/(b^6)^2", FIXED, "1",
       "numerator->64", "denominator->64", "64/64=1",
       projection_id="PI-HHCQ-U0-REALSURD-v1", domain="POSITIVE_EXACT_ALGEBRAIC_ROOT",
       premises=("denominator != 0",), source_scope="REGISTERED_PASS219_HHCQ"),

    _t("SPT074", "I", TYPED_NONSCALAR, None,
       "I is a registered phase/complex basis object, not an ordinary real scalar",
       projection_id="PI-COMPLEX-COMPAT-v1", domain="REGISTERED_PHASE_BASIS", source_needles=("I^3",)),
    _t("SPT075", "I^4", FIXED, "1", "delegate to SPP031", fixed_proof_id="SPP031",
       projection_id="PI-COMPLEX-COMPAT-v1", domain="REGISTERED_PHASE_PROJECTION", source_needles=("I^4",)),
    _t("SPT076", "Pi", SYMBOLIC, "Pi", "Pi remains exact symbolic and is not silently replaced by a decimal literal",
       projection_id="PI-SYMBOLIC-CONSTANT-v1", domain="EXACT_SYMBOLIC_CONSTANT", source_scope="REGISTERED_PASS169_SYMBOL_REGISTRY"),
    _t("SPT077", "O", SYMBOLIC, "O", "O remains a distinct exact symbolic HARMONICODE symbol; O!=Pi",
       projection_id="PI-SYMBOLIC-CONSTANT-v1", domain="EXACT_SYMBOLIC_CONSTANT", source_scope="REGISTERED_PASS169_SYMBOL_REGISTRY"),
    _t("SPT078", "E", SYMBOLIC, "E", "E remains exact symbolic and is not silently replaced by 2.71828182846",
       projection_id="PI-SYMBOLIC-CONSTANT-v1", domain="EXACT_SYMBOLIC_CONSTANT", source_scope="REGISTERED_PASS169_SYMBOL_REGISTRY"),

    _t("SPT079", "t", UNSUPPORTED, None, "full-symbolic UCE does not solve native t",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="T_M_HARMONIC_RESIDUAL", source_needles=("t^3-t",)),
    _t("SPT080", "m", UNSUPPORTED, None, "full-symbolic UCE does not solve native m",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="T_M_HARMONIC_RESIDUAL", source_needles=("m^2-m",)),
    _t("SPT081", "s", UNSUPPORTED, None, "nested s tensor remains a registered full-symbolic residual",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="TENSOR_S_F_AT_BT_RESIDUAL", source_needles=("s==",)),
    _t("SPT082", "f", UNSUPPORTED, None, "f/At/Bt substitution chain remains a registered full-symbolic residual",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="TENSOR_S_F_AT_BT_RESIDUAL", source_needles=("f/u",)),
    _t("SPT083", "At", UNSUPPORTED, None, "At remains a registered source-bound correspondence node",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="TENSOR_S_F_AT_BT_RESIDUAL", source_needles=("/At",)),
    _t("SPT084", "Bt", UNSUPPORTED, None, "Bt remains a registered source-bound correspondence node",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="TENSOR_S_F_AT_BT_RESIDUAL", source_needles=("/Bt",)),
    _t("SPT085", "Mod(f/u,72*(pq+xy))", UNSUPPORTED, None,
       "modular substitution clause remains full-symbolic residual until exact adapter proves it",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="MOD_F_U_RESIDUAL", source_needles=("Mod(f/u,(72*(pq+xy)))",)),
    _t("SPT086", "Delta/P=Sqrt(pq+u^72)^x^2", UNSUPPORTED, None,
       "root/phase geometry remains full-symbolic residual in UCE 1.8",
       projection_id="PI-UCE-FULL-SYMBOLIC-v1", domain="DELTA_P_ROOT_RESIDUAL", source_needles=("∆/P=√(pq+u⁷²)^x²",)),
    _t("SPT087", "NcalcMatrixPower(...,4)", SYMBOLIC, "exact_ordered_matrix_power_object",
       "matrix order and source identity are preserved; no fixed scalar is asserted without exact matrix evaluator",
       projection_id="PI-HARMONICODE-MATRIX-v1", domain="ORDERED_SYMBOLIC_MATRIX", source_needles=("NcalcMatrixPower",)),
)

THEOREM_BY_ID = {theorem.theorem_id: theorem for theorem in THEOREMS}
THEOREMS_BY_EXPRESSION: dict[str, tuple[ProjectionTheorem, ...]] = {}
for _theorem in THEOREMS:
    THEOREMS_BY_EXPRESSION[_theorem.native_expression] = (*THEOREMS_BY_EXPRESSION.get(_theorem.native_expression, ()), _theorem)


def validate_theorem_registry() -> None:
    ids: set[str] = set()
    for theorem in THEOREMS:
        if theorem.theorem_id in ids:
            raise ValueError(f"DUPLICATE_THEOREM_ID:{theorem.theorem_id}")
        ids.add(theorem.theorem_id)
        theorem.to_dict()
        if theorem.projection_class in {FIXED, PARAMETERIZED, MULTIBRANCH, SYMBOLIC} and theorem.result_expression is None:
            raise ValueError(f"MISSING_RESULT_EXPRESSION:{theorem.theorem_id}")
        if theorem.projection_class in {UNSUPPORTED, TYPED_NONSCALAR} and theorem.fixed_proof_id is not None:
            raise ValueError(f"NONSCALAR_HAS_FIXED_PROOF:{theorem.theorem_id}")


def source_bound_occurrences(source: bytes | str) -> list[dict[str, object]]:
    identity = verify_canonical_source(source)
    if not identity["verified"]:
        raise ValueError("CANONICAL_SOURCE_IDENTITY_MISMATCH")
    text = source.decode("utf-8") if isinstance(source, (bytes, bytearray)) else source
    records: list[dict[str, object]] = []
    for theorem in THEOREMS:
        if not theorem.source_needles:
            continue
        for needle in theorem.source_needles:
            start = 0
            found = False
            while True:
                index = text.find(needle, start)
                if index < 0:
                    break
                found = True
                records.append({
                    "theorem_id": theorem.theorem_id,
                    "needle": needle,
                    "start": index,
                    "end": index + len(needle),
                    "span_sha256": sha256(text[index:index + len(needle)].encode("utf-8")).hexdigest(),
                })
                start = index + 1
            if not found and theorem.source_scope == "PASS169_OR_REGISTERED_PASS219":
                raise ValueError(f"SOURCE_NEEDLE_NOT_FOUND:{theorem.theorem_id}:{needle}")
    return records


def build_theorem_manifest(source: bytes | str) -> dict[str, object]:
    validate_theorem_registry()
    identity = verify_canonical_source(source)
    if not identity["verified"]:
        raise ValueError("CANONICAL_SOURCE_IDENTITY_MISMATCH")
    occurrences = source_bound_occurrences(source)
    classes: dict[str, int] = {}
    for theorem in THEOREMS:
        classes[theorem.projection_class] = classes.get(theorem.projection_class, 0) + 1
    source_bound_ids = {record["theorem_id"] for record in occurrences}
    manifest: dict[str, object] = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "canonical_source": {"path": CANONICAL_SOURCE_PATH, "bytes": CANONICAL_SOURCE_BYTES, "sha256": CANONICAL_SOURCE_SHA256},
        "theorem_count": len(THEOREMS),
        "class_counts": classes,
        "theorems": [theorem.to_dict() for theorem in THEOREMS],
        "pass169_source_occurrences": occurrences,
        "pass169_source_bound_theorem_count": len(source_bound_ids),
        "semantic_invariants": {
            "projection_equality_implies_native_identity": False,
            "same_native_symbol_may_have_multiple_registered_projections": True,
            "unresolved_projection_may_be_approximated": False,
            "source_rewrite_authorized": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_persistence_authority": False,
            "floating_point_canonical_authority": False,
        },
    }
    manifest["manifest_sha256"] = sha256(_canonical_json(manifest).encode("utf-8")).hexdigest()
    manifest["manifest_receipt_hash72"] = hash72_digest({"domain": "HHS-P219-SCALAR-PROJECTION-THEOREM-MANIFEST-V1"}, manifest)
    return manifest


def explain_projection(native_expression: str) -> tuple[dict[str, object], ...]:
    records = THEOREMS_BY_EXPRESSION.get(native_expression)
    if not records:
        raise KeyError(f"NO_PROJECTION_THEOREM:{native_expression}")
    return tuple(record.to_dict() for record in records)
