"""Pass 220 I049 native Mathlib relations/order and exact-rational slice."""
from __future__ import annotations

from hhs_runtime.hhs_pass220_i048_native_mathlib_v1 import MathlibNativeClassSpec
from hhs_runtime.hhs_pass220_python_rna_class_registration_v1 import (
    MEMBER_CONSTRUCTOR,
    MEMBER_METHOD,
    ROLE_HAIRPIN,
    ROLE_TOEHOLD,
    PythonClassMemberSpec,
)

SCHEMA = "HHS_PASS_220_I049_NATIVE_MATHLIB_ORDER_RAT_V1"

ORDER_RAT_CLASSES: tuple[MathlibNativeClassSpec, ...] = (
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Data.Rat.Defs",
        native_module="HHS.Mathlib.Data.Rat.Defs",
        class_name="Rat",
        source_text=(
            "class Rat:\n"
            "    def __init__(self, numerator, denominator): "
            "self.numerator, self.denominator = numerator, denominator\n"
            "    def add(self, rhs): "
            "return Rat(self.numerator*rhs.denominator+rhs.numerator*self.denominator,"
            "self.denominator*rhs.denominator)\n"
            "    def sub(self, rhs): "
            "return Rat(self.numerator*rhs.denominator-rhs.numerator*self.denominator,"
            "self.denominator*rhs.denominator)\n"
            "    def mul(self, rhs): "
            "return Rat(self.numerator*rhs.numerator,self.denominator*rhs.denominator)\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("add", MEMBER_METHOD, 1, 0, 0),
            PythonClassMemberSpec("sub", MEMBER_METHOD, 2, 1, 0),
            PythonClassMemberSpec("mul", MEMBER_METHOD, 3, 0, ROLE_HAIRPIN),
        ),
    ),
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Order.Defs.Unbundled",
        native_module="HHS.Mathlib.Order.Defs.Unbundled",
        class_name="LT",
        source_text=(
            "class LT:\n"
            "    def compare(self, lhs, rhs): "
            "return lhs.numerator*rhs.denominator-rhs.numerator*lhs.denominator\n"
        ),
        members=(
            PythonClassMemberSpec("compare", MEMBER_METHOD, 4, 0, ROLE_HAIRPIN),
        ),
    ),
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Order.Defs.Unbundled",
        native_module="HHS.Mathlib.Order.Defs.Unbundled",
        class_name="LE",
        source_text=(
            "class LE:\n"
            "    def compare(self, lhs, rhs): "
            "return lhs.numerator*rhs.denominator-rhs.numerator*lhs.denominator\n"
        ),
        members=(
            PythonClassMemberSpec("compare", MEMBER_METHOD, 1, 1, ROLE_HAIRPIN),
        ),
    ),
)


def native_order_rat_contract() -> dict:
    return {
        "schema": SCHEMA,
        "coverage": "RELATIONS_ORDER_EXACT_RATIONAL_SLICE",
        "complete_mathlib_rebuild_claimed": False,
        "representation": "ORDERED_NUMERATOR_POSITIVE_DENOMINATOR_PAIR",
        "canonical_reduction_required": False,
        "zero_denominator_admitted": False,
        "negative_denominator_admitted": False,
        "equivalence": "a.num*b.den == b.num*a.den",
        "strict_order": "a.num*b.den < b.num*a.den",
        "non_strict_order": "strict_order OR equivalence",
        "arithmetic_authority": "PYTHON1_C11_5184_DIGIT_EXACT_BIGINT",
        "comparison_authority": "PYTHON1_CROSS_PRODUCT_DELTA_SIGN",
        "host_float_authority": False,
        "host_integer_comparison_authority": False,
        "native_cpp_class": "hhs::mathlib::NativeRat",
        "lean_module": "HHS.Mathlib.OrderRat",
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "ORDER_RAT_CLASSES",
    "SCHEMA",
    "native_order_rat_contract",
]
