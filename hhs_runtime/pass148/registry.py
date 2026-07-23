from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from hhs_runtime.pass145.canonical import hash72

PASS_ID = "HHS-P148-NSAM"
VERSION = "148.1.0"
SEMANTIC_REGISTRY_VERSION = "HHS_NATIVE_SEMANTIC_REGISTRY_148.1.0"
INTERPRETATION_VERSION = "HHS_P148_INTERPRETATION_1.0.0"

PRIMARY_CLASSES = {
    "DECLARED_SYSTEM_LAW",
    "DERIVABLE_CONSEQUENCE",
    "CONTROL_PROJECTION",
    "UNRESOLVED_EXPRESSION",
    "NARRATIVE_EXTRAPOLATION",
}
CONSEQUENCE_CLASSES = {
    "NECESSARY",
    "CONDITIONAL",
    "LANE_LOCAL",
    "GATE_LOCAL",
    "NORMALIZATION_LOCAL",
    "INVARIANT",
    "EXCLUDED",
    "UNDETERMINED",
}
AUTHORITY_LEVELS = {"A1", "A2", "A3", "A4"}
SOURCE_TYPES = {
    "contract", "runtime", "documentation", "user_declaration", "model_output",
    "fiction", "control_engine",
}

# The registry identifies operator contracts. It does not execute hidden fallback
# arithmetic. A missing entry must remain unresolved.
OPERATORS: dict[str, dict[str, Any]] = {
    "HHS_GATE_EQ": {
        "operator_id": "HHS_GATE_EQ", "glyphs": ["=="], "forbidden_aliases": ["="],
        "arity": 2, "precedence": 10, "associativity": "NON_ASSOCIATIVE",
        "commutative": False, "lane_applicability": ["DECLARED_BY_CONTEXT"],
        "semantics": "admission/equivalence gate; not ordinary scalar equality",
        "cancellation_rules": [], "inverse_rules": [], "projection_permissions": ["EXPLICIT_CONTROL_ONLY"],
        "source_authority": "HHS-P081+ inherited typed dispatch",
    },
    "HHS_DECLARATIVE_RELATION": {
        "operator_id": "HHS_DECLARATIVE_RELATION", "glyphs": ["="], "forbidden_aliases": ["=="],
        "arity": 2, "precedence": 10, "associativity": "NON_ASSOCIATIVE",
        "commutative": False, "lane_applicability": ["DECLARATION", "PROJECTION_BY_PROFILE"],
        "semantics": "declared relation spelling; interpretation depends on source authority and profile",
        "cancellation_rules": [], "inverse_rules": [], "projection_permissions": ["PROFILE_DECLARED"],
        "source_authority": "HHS-P148-NSAM",
    },
    "HHS_DISTINCT_FROM": {
        "operator_id": "HHS_DISTINCT_FROM", "glyphs": ["≠", "\\neq", "!="], "forbidden_aliases": [],
        "arity": 2, "precedence": 10, "associativity": "NON_ASSOCIATIVE",
        "commutative": True, "lane_applicability": ["ALL_DECLARED_SCOPES"],
        "semantics": "typed identity distinction",
        "cancellation_rules": [], "inverse_rules": [], "projection_permissions": ["IDENTITY_PRESERVING"],
        "source_authority": "HHS-P148 Ω148.9",
    },
    "HHS_PROJECTION_PLUS": {
        "operator_id": "HHS_PROJECTION_PLUS", "glyphs": ["+"], "forbidden_aliases": [],
        "arity": 2, "precedence": 30, "associativity": "ORDERED_LEFT",
        "commutative": False, "lane_applicability": ["TYPED_BY_CONTEXT"],
        "semantics": "secondary projection/composition operator; no conventional fallback",
        "cancellation_rules": [], "inverse_rules": [], "projection_permissions": ["EXPLICIT_CONTROL_ONLY"],
        "source_authority": "Inherited HHS operator contract",
    },
    "HHS_RESIDUAL_MINUS": {
        "operator_id": "HHS_RESIDUAL_MINUS", "glyphs": ["-"], "forbidden_aliases": [],
        "arity": 2, "precedence": 30, "associativity": "ORDERED_LEFT",
        "commutative": False, "lane_applicability": ["TYPED_BY_CONTEXT"],
        "semantics": "ordered residual/cancellation projection; x-x is not automatically zero",
        "cancellation_rules": [], "inverse_rules": [], "projection_permissions": ["EXPLICIT_CONTROL_ONLY"],
        "source_authority": "HHS-P148 Ω148.7 and Δ residual law",
    },
    "HHS_ORDERED_COMPOSITION": {
        "operator_id": "HHS_ORDERED_COMPOSITION", "glyphs": ["*", "·", "IMPLICIT"], "forbidden_aliases": [],
        "arity": 2, "precedence": 50, "associativity": "ORDERED_LEFT",
        "commutative": False, "lane_applicability": ["TYPED_BY_CONTEXT"],
        "semantics": "ordered composition/phase transport; AB and BA retain order",
        "cancellation_rules": [], "inverse_rules": [], "projection_permissions": ["EXPLICIT_CONTROL_ONLY"],
        "source_authority": "HHS noncommutative typed runtime",
    },
    "HHS_TYPED_FRACTION": {
        "operator_id": "HHS_TYPED_FRACTION", "glyphs": ["/", "\\frac"], "forbidden_aliases": [],
        "arity": 2, "precedence": 50, "associativity": "ORDERED_LEFT",
        "commutative": False, "lane_applicability": ["TYPED_BY_CONTEXT"],
        "semantics": "typed normalization/fraction constructor; not automatic field division",
        "cancellation_rules": ["ONLY_WHEN_EXPLICIT_RULE_MATCHES"], "inverse_rules": ["TYPED_BY_CONTEXT"],
        "projection_permissions": ["EXPLICIT_CONTROL_ONLY"],
        "source_authority": "HHS-P148 Ω148.7 and Ω148.10",
    },
    "HHS_PHASE_EXPONENT": {
        "operator_id": "HHS_PHASE_EXPONENT", "glyphs": ["^"], "forbidden_aliases": [],
        "arity": 2, "precedence": 70, "associativity": "ORDERED_RIGHT",
        "commutative": False, "lane_applicability": ["TYPED_BY_CONTEXT"],
        "semantics": "typed exponent/phase transport; not presumed repeated scalar multiplication",
        "cancellation_rules": [], "inverse_rules": ["PROFILE_DECLARED"],
        "projection_permissions": ["EXPLICIT_CONTROL_ONLY"],
        "source_authority": "HHS native symbolic runtime",
    },
    "HHS_SYMBOLIC_ROOT": {
        "operator_id": "HHS_SYMBOLIC_ROOT", "glyphs": ["√", "\\sqrt"], "forbidden_aliases": [],
        "arity": 1, "precedence": 80, "associativity": "PREFIX",
        "commutative": False, "lane_applicability": ["TYPED_BY_CONTEXT"],
        "semantics": "symbolic root object; branch and movement rules require explicit authority",
        "cancellation_rules": [], "inverse_rules": [], "projection_permissions": ["PROFILE_DECLARED"],
        "source_authority": "HHS exact symbolic-root substrate",
    },
}

# Canonical source expressions are paired with explicit authority records.
# Variants are normalized only at the spelling layer; source text is never replaced.
DECLARED_LAWS: list[dict[str, Any]] = [
    {"rule_id": "HHS_O_DISTINCT_PI_V1", "expressions": ["O≠π", "O\\neq\\pi", "O != π"], "consequence_class": "INVARIANT", "scope": {"global": True}, "statement": "O is a distinct HHS operator and is not the circular constant π.", "source_authority": "HHS-P148 Ω148.9 and inherited O ≠ π rule"},
    {"rule_id": "HHS_DELTA_NORMALIZATION_V1", "expressions": ["n/Δ=n", "\\frac{n}{\\Delta}=n", "\\frac n\\Delta=n"], "consequence_class": "NORMALIZATION_LOCAL", "scope": {"normalization_lane": True}, "statement": "n normalized through Δ returns n in the declared typed normalization lane.", "source_authority": "HHS-P148 Ω148.10"},
    {"rule_id": "HHS_DELTA_IDEMPOTENT_EXPONENT_V1", "expressions": ["Δ^n=Δ", "\\Delta^n=\\Delta"], "consequence_class": "NORMALIZATION_LOCAL", "scope": {"normalization_lane": True}, "statement": "Declared typed Δ exponent normalization.", "source_authority": "HHS-P148 Ω148.10"},
    {"rule_id": "HHS_DELTA_RESIDUAL_V1", "expressions": ["Δ-Δ=x+y", "\\Delta-\\Delta=x+y"], "consequence_class": "NORMALIZATION_LOCAL", "scope": {"residual_lane": True}, "statement": "Δ residual subtraction yields x+y in the declared lane; ordinary cancellation is unauthorized.", "source_authority": "HHS-P148 §13.2"},
    {"rule_id": "HHS_INFINITY_NEG_DELTA_EXPONENT_V1", "expressions": ["∞^{-Δ}=Δ", "\\infty^{-\\Delta}=\\Delta"], "consequence_class": "GATE_LOCAL", "scope": {"infinite_boundary": True}, "statement": "Typed exponent boundary law.", "source_authority": "HHS-P148 §13.3"},
    {"rule_id": "HHS_DELTA_INFINITY_COMPOSITION_V1", "expressions": ["Δ∞=∞", "\\Delta\\infty=\\infty"], "consequence_class": "GATE_LOCAL", "scope": {"infinite_boundary": True}, "statement": "Ordered Δ-infinity composition boundary law.", "source_authority": "HHS-P148 §13.3"},
    {"rule_id": "HHS_INFINITY_MINUS_DELTA_V1", "expressions": ["∞-Δ=∞", "\\infty-\\Delta=\\infty"], "consequence_class": "GATE_LOCAL", "scope": {"infinite_boundary": True}, "statement": "Typed residual infinite boundary law.", "source_authority": "HHS-P148 §13.3"},
    {"rule_id": "HHS_INFINITY_PLUS_DELTA_V1", "expressions": ["∞+Δ=∞", "\\infty+\\Delta=\\infty"], "consequence_class": "GATE_LOCAL", "scope": {"infinite_boundary": True}, "statement": "Typed projection infinite boundary law.", "source_authority": "HHS-P148 §13.3"},
    {"rule_id": "HHS_NEGATIVE_INFINITY_EMPTY_EXPONENT_V1", "expressions": ["-∞=∅^{-Δ}", "-\\infty=\\varnothing^{-\\Delta}"], "consequence_class": "GATE_LOCAL", "scope": {"infinite_boundary": True}, "statement": "Typed negative-infinity/empty-boundary relation.", "source_authority": "HHS-P148 §13.3"},
]

DERIVATION_RULES: dict[str, dict[str, Any]] = {
    "HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1": {
        "rule_id": "HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1",
        "requires_declared_rule": "HHS_DELTA_NORMALIZATION_V1",
        "input_pattern": "n/Δ=n",
        "substitution": {"n": "Δ"},
        "output_expression": "Δ/Δ=Δ",
        "operator_types": ["HHS_TYPED_FRACTION", "HHS_DECLARATIVE_RELATION"],
        "scope": {"normalization_lane": True},
        "conditions": ["substitution n:=Δ is explicitly admitted", "HHS_DELTA_NORMALIZATION_V1 is authoritative"],
        "consequence_class": "NORMALIZATION_LOCAL",
        "authority_ceiling": "A3",
    },
    "HHS_IDENTITY_PRESERVING_RESTATEMENT_V1": {
        "rule_id": "HHS_IDENTITY_PRESERVING_RESTATEMENT_V1",
        "input_pattern": "ANY_DECLARED_LAW",
        "operator_types": [],
        "scope": {"same_as_input": True},
        "conditions": ["source expression and AST are unchanged"],
        "consequence_class": "NECESSARY",
        "authority_ceiling": "A3",
    },
}

PROJECTION_PROFILES: dict[str, dict[str, Any]] = {
    "HHS_NATIVE_TYPED_V1": {
        "profile_id": "HHS_NATIVE_TYPED_V1", "native": True,
        "type_domain": "typed HHS symbolic objects", "equality_semantics": "registry-defined",
        "branch_rules": "registry-defined", "commutation_permissions": [], "cancellation_permissions": [],
        "numerical_representation": "exact symbolic/integer/rational/prime-exponent", "authority_ceiling": "A4",
        "allowed_output_classes": ["DECLARED_SYSTEM_LAW", "DERIVABLE_CONSEQUENCE", "UNRESOLVED_EXPRESSION"],
        "prohibited_native_state_mutations": [],
    },
    "COMMUTATIVE_FIELD_CONTROL_V1": {
        "profile_id": "COMMUTATIVE_FIELD_CONTROL_V1", "native": False,
        "type_domain": "commutative field with explicitly nonzero denominators", "equality_semantics": "ordinary field equality",
        "branch_rules": "conventional", "commutation_permissions": ["MULTIPLICATION"],
        "cancellation_permissions": ["NONZERO_COMMON_FACTOR"], "numerical_representation": "exact symbolic field",
        "authority_ceiling": "A1", "allowed_output_classes": ["CONTROL_PROJECTION"],
        "prohibited_native_state_mutations": ["ALL"],
    },
    "EXACT_RATIONAL_CONTROL_V1": {
        "profile_id": "EXACT_RATIONAL_CONTROL_V1", "native": False,
        "type_domain": "Q", "equality_semantics": "rational equality", "branch_rules": "not applicable",
        "commutation_permissions": ["ADDITION", "MULTIPLICATION"], "cancellation_permissions": ["NONZERO_COMMON_FACTOR"],
        "numerical_representation": "integer numerator/denominator", "authority_ceiling": "A1",
        "allowed_output_classes": ["CONTROL_PROJECTION"], "prohibited_native_state_mutations": ["ALL"],
    },
    "IEEE754_BINARY64_CONTROL_V1": {
        "profile_id": "IEEE754_BINARY64_CONTROL_V1", "native": False,
        "type_domain": "IEEE-754 binary64", "equality_semantics": "binary64 comparison", "branch_rules": "IEEE-754",
        "commutation_permissions": ["CONTROL_PROFILE_ONLY"], "cancellation_permissions": ["CONTROL_PROFILE_ONLY"],
        "numerical_representation": "binary64 approximate", "authority_ceiling": "A1",
        "allowed_output_classes": ["CONTROL_PROJECTION"], "prohibited_native_state_mutations": ["ALL"],
    },
    "STANDARD_COMPLEX_CONTROL_V1": {
        "profile_id": "STANDARD_COMPLEX_CONTROL_V1", "native": False,
        "type_domain": "C", "equality_semantics": "standard complex equality", "branch_rules": "principal unless declared",
        "commutation_permissions": ["ADDITION", "MULTIPLICATION"], "cancellation_permissions": ["NONZERO_COMMON_FACTOR"],
        "numerical_representation": "exact/approximate as declared", "authority_ceiling": "A1",
        "allowed_output_classes": ["CONTROL_PROJECTION"], "prohibited_native_state_mutations": ["ALL"],
    },
    "STANDARD_REAL_ANALYSIS_CONTROL_V1": {
        "profile_id": "STANDARD_REAL_ANALYSIS_CONTROL_V1", "native": False,
        "type_domain": "R and standard extended-real conventions only when declared", "equality_semantics": "standard real equality",
        "branch_rules": "standard real analysis", "commutation_permissions": ["ADDITION", "MULTIPLICATION"],
        "cancellation_permissions": ["NONZERO_COMMON_FACTOR"], "numerical_representation": "exact/approximate as declared",
        "authority_ceiling": "A1", "allowed_output_classes": ["CONTROL_PROJECTION"],
        "prohibited_native_state_mutations": ["ALL"],
    },
    "SYMBOLIC_CAS_CONTROL_V1": {
        "profile_id": "SYMBOLIC_CAS_CONTROL_V1", "native": False,
        "type_domain": "CAS-defined symbolic domain", "equality_semantics": "CAS profile",
        "branch_rules": "CAS-specific and recorded", "commutation_permissions": ["CAS_DECLARED"],
        "cancellation_permissions": ["CAS_DECLARED"], "numerical_representation": "CAS-specific",
        "authority_ceiling": "A1", "allowed_output_classes": ["CONTROL_PROJECTION"],
        "prohibited_native_state_mutations": ["ALL"],
    },
    "NARRATIVE_WORLD_MODEL_V1": {
        "profile_id": "NARRATIVE_WORLD_MODEL_V1", "native": False,
        "type_domain": "narrative propositions", "equality_semantics": "story-local consistency only",
        "branch_rules": "narrative", "commutation_permissions": [], "cancellation_permissions": [],
        "numerical_representation": "not authoritative", "authority_ceiling": "A1",
        "allowed_output_classes": ["NARRATIVE_EXTRAPOLATION"], "prohibited_native_state_mutations": ["ALL"],
    },
}

CONTAMINATION_DIAGNOSTICS: dict[str, dict[str, Any]] = {
    "SCALARIZATION_CONTAMINATION": {"severity": "REJECT_NATIVE_PROMOTION", "description": "A typed HHS object was reduced to an ordinary scalar without an authorized profile."},
    "OPERATOR_ALIAS_CONTAMINATION": {"severity": "REJECT_NATIVE_PROMOTION", "description": "Distinct HHS and external symbols/operators were aliased."},
    "EQUALITY_FLATTENING": {"severity": "REJECT_NATIVE_PROMOTION", "description": "The HHS == gate was flattened to ordinary equality."},
    "COMMUTATIVITY_INJECTION": {"severity": "REJECT_NATIVE_PROMOTION", "description": "Operand order was changed without an authorized commutation rule."},
    "CANCELLATION_INJECTION": {"severity": "REJECT_NATIVE_PROMOTION", "description": "A factor was cancelled without an authorized inverse/cancellation contract."},
    "SCOPE_INFLATION": {"severity": "REJECT_NATIVE_PROMOTION", "description": "A local observation was promoted to a broader scope."},
    "NARRATIVE_PROMOTION": {"severity": "REJECT_NATIVE_PROMOTION", "description": "Narrative content was promoted to native mathematics."},
    "PHYSICAL_ONTOLOGY_PROMOTION": {"severity": "NON_AUTHORITATIVE", "description": "Physical ontology was inferred from symbolic syntax."},
    "CONSCIOUSNESS_PROMOTION": {"severity": "NON_AUTHORITATIVE", "description": "Consciousness was inferred from recursion or self-reference."},
    "PROOF_LANGUAGE_INFLATION": {"severity": "REJECT_AUTHORITY_CLAIM", "description": "Proof-strength language exceeded the available authority or evidence."},
    "SOURCE_TEXT_MUTATION": {"severity": "CORRUPT", "description": "Normalization or interpretation changed immutable source text."},
    "ORDER_COLLAPSE": {"severity": "REJECT_NATIVE_PROMOTION", "description": "Differently ordered ASTs were treated as identical."},
    "CONTROL_NATIVE_CONTAMINATION": {"severity": "REJECT_NATIVE_PROMOTION", "description": "A control result attempted to mutate, repair, or satisfy native state."},
    "UNRESOLVED_DEPENDENCY_HIDDEN": {"severity": "REJECT_DERIVATION", "description": "A derivation omitted an unresolved dependency or condition."},
}


def _witness(entry: Mapping[str, Any], label: str) -> dict[str, Any]:
    out = deepcopy(dict(entry))
    out["version"] = SEMANTIC_REGISTRY_VERSION
    out["hash72_witness"] = hash72(label, out)
    return out


def operator_registry() -> list[dict[str, Any]]:
    return [_witness(OPERATORS[k], "hhs_pass148_operator_rule_v1") for k in sorted(OPERATORS)]


def declared_law_registry() -> list[dict[str, Any]]:
    return [_witness(item, "hhs_pass148_declared_law_v1") for item in DECLARED_LAWS]


def derivation_rule_registry() -> list[dict[str, Any]]:
    return [_witness(DERIVATION_RULES[k], "hhs_pass148_derivation_rule_v1") for k in sorted(DERIVATION_RULES)]


def projection_profile_registry() -> list[dict[str, Any]]:
    return [_witness(PROJECTION_PROFILES[k], "hhs_pass148_projection_profile_v1") for k in sorted(PROJECTION_PROFILES)]


def contamination_registry() -> list[dict[str, Any]]:
    return [_witness({"diagnostic_code": k, **CONTAMINATION_DIAGNOSTICS[k]}, "hhs_pass148_contamination_diagnostic_v1") for k in sorted(CONTAMINATION_DIAGNOSTICS)]


def full_registry() -> dict[str, Any]:
    payload = {
        "schema": "HHS_PASS148_NATIVE_SEMANTIC_RULE_REGISTRY_V1",
        "pass_id": PASS_ID,
        "registry_version": SEMANTIC_REGISTRY_VERSION,
        "operators": operator_registry(),
        "declared_laws": declared_law_registry(),
        "derivation_rules": derivation_rule_registry(),
        "projection_profiles": projection_profile_registry(),
        "contamination_diagnostics": contamination_registry(),
    }
    payload["registry_hash72"] = hash72("hhs_pass148_semantic_registry_v1", payload)
    return payload


def get_rule(rule_id: str) -> dict[str, Any] | None:
    for entry in operator_registry() + declared_law_registry() + derivation_rule_registry():
        if entry.get("operator_id") == rule_id or entry.get("rule_id") == rule_id:
            return entry
    return None


def get_profile(profile_id: str) -> dict[str, Any] | None:
    value = PROJECTION_PROFILES.get(profile_id)
    return None if value is None else _witness(value, "hhs_pass148_projection_profile_v1")
