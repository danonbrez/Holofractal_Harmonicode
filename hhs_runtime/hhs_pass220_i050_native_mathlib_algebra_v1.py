"""Pass 220 I050 native Mathlib algebraic-structure compatibility slice."""
from __future__ import annotations

from hhs_runtime.hhs_pass220_i048_native_mathlib_v1 import MathlibNativeClassSpec
from hhs_runtime.hhs_pass220_python_rna_class_registration_v1 import (
    MEMBER_CONSTRUCTOR,
    MEMBER_METHOD,
    ROLE_HAIRPIN,
    ROLE_TOEHOLD,
    PythonClassMemberSpec,
)

SCHEMA = "HHS_PASS_220_I050_NATIVE_MATHLIB_ALGEBRA_V1"

ALGEBRA_CLASSES: tuple[MathlibNativeClassSpec, ...] = (
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Algebra.Group.Defs",
        native_module="HHS.Mathlib.Algebra.Group.Defs",
        class_name="AddMonoid",
        source_text=(
            "class AddMonoid:\n"
            "    def __init__(self, zero, add): self.zero, self.add = zero, add\n"
            "    def check_assoc(self, a, b, c): "
            "return self.add(self.add(a,b),c), self.add(a,self.add(b,c))\n"
            "    def check_identity(self, a): "
            "return self.add(self.zero,a), self.add(a,self.zero)\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("check_assoc", MEMBER_METHOD, 1, 0, 0),
            PythonClassMemberSpec("check_identity", MEMBER_METHOD, 2, 1, ROLE_HAIRPIN),
        ),
    ),
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Algebra.Group.Defs",
        native_module="HHS.Mathlib.Algebra.Group.Defs",
        class_name="MulMonoid",
        source_text=(
            "class MulMonoid:\n"
            "    def __init__(self, one, mul): self.one, self.mul = one, mul\n"
            "    def check_assoc(self, a, b, c): "
            "return self.mul(self.mul(a,b),c), self.mul(a,self.mul(b,c))\n"
            "    def check_identity(self, a): "
            "return self.mul(self.one,a), self.mul(a,self.one)\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 3, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("check_assoc", MEMBER_METHOD, 4, 0, 0),
            PythonClassMemberSpec("check_identity", MEMBER_METHOD, 1, 1, ROLE_HAIRPIN),
        ),
    ),
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Algebra.Ring.Defs",
        native_module="HHS.Mathlib.Algebra.Ring.Defs",
        class_name="Semiring",
        source_text=(
            "class Semiring:\n"
            "    def __init__(self, add, mul): self.add, self.mul = add, mul\n"
            "    def check_left_distrib(self, a, b, c): "
            "return self.mul(a,self.add(b,c)),self.add(self.mul(a,b),self.mul(a,c))\n"
            "    def check_right_distrib(self, a, b, c): "
            "return self.mul(self.add(a,b),c),self.add(self.mul(a,c),self.mul(b,c))\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 2, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("check_left_distrib", MEMBER_METHOD, 3, 0, 0),
            PythonClassMemberSpec("check_right_distrib", MEMBER_METHOD, 4, 1, ROLE_HAIRPIN),
        ),
    ),
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Algebra.Ring.Defs",
        native_module="HHS.Mathlib.Algebra.Ring.Defs",
        class_name="Ring",
        source_text=(
            "class Ring:\n"
            "    def __init__(self, add, sub, mul): self.add, self.sub, self.mul = add, sub, mul\n"
            "    def check_add_inverse(self, zero, a): "
            "return self.add(a,self.sub(zero,a))\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 1, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("check_add_inverse", MEMBER_METHOD, 2, 1, ROLE_HAIRPIN),
        ),
    ),
)


def native_algebra_contract() -> dict:
    return {
        "schema": SCHEMA,
        "coverage": "ALGEBRAIC_STRUCTURE_CERTIFICATE_NUCLEUS",
        "complete_mathlib_rebuild_claimed": False,
        "carriers": ("Nat", "Int", "ExactRat"),
        "structures": ("AddMonoid", "MulMonoid", "Semiring", "Ring"),
        "laws": (
            "add_assoc",
            "add_identity",
            "mul_assoc",
            "mul_identity",
            "left_distrib",
            "right_distrib",
            "add_inverse",
        ),
        "runtime_law_evidence": "EXACT_SAMPLED_CERTIFICATE",
        "universal_theorem_closure_claimed": False,
        "arithmetic_authority": "PYTHON1_C11_5184_DIGIT_EXACT_BIGINT",
        "rat_equivalence_authority": "PYTHON1_CROSS_PRODUCT_EQUIVALENCE",
        "operand_order_preserved": True,
        "implicit_commutation_authorized": False,
        "host_float_authority": False,
        "host_primitive_arithmetic_authority": False,
        "class_identity_authority": "PYTHON2_CPP_RNA_CELL_WALL",
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "ALGEBRA_CLASSES",
    "SCHEMA",
    "native_algebra_contract",
]
