from __future__ import annotations

import re
from copy import deepcopy
from fractions import Fraction
from typing import Any, Mapping, Sequence

from hhs_runtime.pass145.canonical import canonical_json, hash72, stable_id
from hhs_runtime.pass145.errors import Pass145Error
from .parser import ast_semantic_key, parse_expression, render_ast, walk_ast
from .registry import (
    AUTHORITY_LEVELS,
    CONSEQUENCE_CLASSES,
    CONTAMINATION_DIAGNOSTICS,
    DECLARED_LAWS,
    DERIVATION_RULES,
    INTERPRETATION_VERSION,
    PRIMARY_CLASSES,
    PROJECTION_PROFILES,
    SEMANTIC_REGISTRY_VERSION,
    SOURCE_TYPES,
    get_profile,
)


def normalized_spelling(text: str) -> str:
    value = text.strip()
    replacements = {
        "\\left": "", "\\right": "", "\\Delta": "Δ", "\\pi": "π",
        "\\infty": "∞", "\\varnothing": "∅", "\\neq": "≠",
        "\\cdot": "·", "\\times": "*",
    }
    for before, after in replacements.items():
        value = value.replace(before, after)
    # Normalize the limited declared \frac spelling without applying algebra.
    value = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)", value)
    value = re.sub(r"\\frac\s*([A-Za-zΔπ∞∅])\s*([A-Za-zΔπ∞∅])", r"(\1)/(\2)", value)
    value = value.replace("{", "(").replace("}", ")")
    value = re.sub(r"\s+", "", value)
    # Grouping at the single-symbol fraction boundary is spelling-only.
    value = value.replace("(n)/(Δ)", "n/Δ").replace("(Δ)/(Δ)", "Δ/Δ")
    return value


def declared_law_match(expression: str) -> dict[str, Any] | None:
    observed = normalized_spelling(expression)
    for law in DECLARED_LAWS:
        if any(normalized_spelling(candidate) == observed for candidate in law["expressions"]):
            return deepcopy(law)
    return None


def _diag(code: str, evidence: Mapping[str, Any], *, span: list[int] | None = None) -> dict[str, Any]:
    definition = CONTAMINATION_DIAGNOSTICS[code]
    payload = {
        "diagnostic_code": code,
        "severity": definition["severity"],
        "description": definition["description"],
        "evidence": dict(evidence),
        "source_span": span,
        "registry_version": SEMANTIC_REGISTRY_VERSION,
    }
    payload["diagnostic_hash72"] = hash72("hhs_pass148_contamination_finding_v1", payload)
    return payload


def contamination_findings(expression: str, ast: Mapping[str, Any], *, source_type: str, profile_id: str, declared_scope: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    compact = normalized_spelling(expression)
    lower = expression.lower()
    native = profile_id == "HHS_NATIVE_TYPED_V1"

    if native and (re.search(r"(?:Δ|\\Delta)\s*(?:=|->|⇒|↦)\s*1(?:\D|$)", expression) or re.search(r"(?:Δ|\\Delta)\s*/\s*(?:Δ|\\Delta)\s*=\s*1", expression)):
        findings.append(_diag("SCALARIZATION_CONTAMINATION", {"attempt": "Δ→1 or Δ/Δ→1", "profile": profile_id}))
    if re.search(r"O\s*(?:=|->|⇒|↦)\s*(?:π|\\pi)", expression):
        findings.append(_diag("OPERATOR_ALIAS_CONTAMINATION", {"attempt": "O→π"}))
    if ("==" in expression and re.search(r"(?:->|⇒|↦|means|as)\s*=", expression, re.I)) or "==→=" in compact:
        findings.append(_diag("EQUALITY_FLATTENING", {"attempt": "==→="}))
    if native and ("AB=BA" in compact or "AB→BA" in compact or "BA=AB" in compact):
        findings.append(_diag("COMMUTATIVITY_INJECTION", {"ordered_terms": ["AB", "BA"]}))
    cancellation_signature = ("AB" in compact and ("B^2" in compact or "B²" in compact) and "A/B" in compact)
    if native and (cancellation_signature or re.search(r"(?:Δ|\\Delta)\s*-\s*(?:Δ|\\Delta)\s*=\s*0", expression)):
        findings.append(_diag("CANCELLATION_INJECTION", {"expression": expression, "required": "explicit inverse/cancellation rule"}))
    if native and re.search(r"(?:∞|\\infty)\s*\^.{0,20}(?:=|→).{0,20}(?:∞|\\infty)\s*-", expression):
        findings.append(_diag("ORDER_COLLAPSE", {"attempt": "exponent transport conflated with residual subtraction"}))
    if re.search(r"(?:lane[- ]local|p[- ]lane|observed\s+(?:in|for).{0,20}lane).{0,80}(?:global|everywhere|all hhs)", lower):
        findings.append(_diag("SCOPE_INFLATION", {"text": expression}))
    if source_type == "fiction" and re.search(r"(?:therefore|proves?|verified|invariant|system law)", lower):
        findings.append(_diag("NARRATIVE_PROMOTION", {"source_type": source_type, "text": expression}))
    if re.search(r"(?:physical reality|physically realizable|ontology of reality|must be imaginary|powers? a spacecraft|erases? entropy)", lower):
        findings.append(_diag("PHYSICAL_ONTOLOGY_PROMOTION", {"text": expression}))
    if re.search(r"(?:self-aware|conscious|sentient)", lower) and re.search(r"(?:recursive|self-reference|ouroboros)", lower):
        findings.append(_diag("CONSCIOUSNESS_PROMOTION", {"text": expression}))
    if re.search(r"(?:lo shu|magic square).{0,80}(?:looks like|resembles|visual resemblance).{0,80}(?:closed|closure|validated)", lower):
        findings.append(_diag("PROOF_LANGUAGE_INFLATION", {"claimed_authority": "VISUAL_RESEMBLANCE_AS_CLOSURE", "source_type": source_type}))
    if re.search(r"(?:appendix|footnote).{0,80}(?:omit|hidden|assume without|unresolved dependency)", lower):
        findings.append(_diag("UNRESOLVED_DEPENDENCY_HIDDEN", {"text": expression}))
    if source_type == "model_output" and re.search(r"canonical receipt|native receipt|receipt verified", lower):
        findings.append(_diag("PROOF_LANGUAGE_INFLATION", {"claimed_authority": "FABRICATED_NATIVE_RECEIPT", "source_type": source_type}))
    if re.search(r"\b(formally impossible|proved|proof|verified|exact|global)\b", lower):
        authority_claim = "A4" if "proof" in lower or "proved" in lower or "formally impossible" in lower else "A3_OR_HIGHER"
        if source_type in {"model_output", "fiction", "control_engine", "documentation"} or ("exact" in lower and re.search(r"\d+\.\d+", expression)):
            findings.append(_diag("PROOF_LANGUAGE_INFLATION", {"claimed_authority": authority_claim, "source_type": source_type}))
    control_to_native = re.search(
        r"(?:control|ieee|float|cas).{0,100}(?:repair|satisfy|overwrite|canonical).{0,100}(?:native|hhs|result|state|gate)?",
        lower,
    )
    native_to_control = re.search(
        r"(?:native|hhs|normalization).{0,100}(?:repair|satisfy|overwrite|canonical).{0,100}(?:control|ieee|float|cas)",
        lower,
    )
    if native and (control_to_native or native_to_control):
        direction = "native_to_control" if native_to_control and not control_to_native else "control_to_native"
        findings.append(_diag("CONTROL_NATIVE_CONTAMINATION", {"direction": direction, "text": expression}))
    if declared_scope and declared_scope.get("lane_scope") and declared_scope.get("global"):
        findings.append(_diag("SCOPE_INFLATION", {"declared_scope": dict(declared_scope)}))

    unique: dict[str, dict[str, Any]] = {}
    for finding in findings:
        unique[finding["diagnostic_hash72"]] = finding
    return list(unique.values())


def _authoritative_source(source_type: str, source_reference: str, governing_contracts: Sequence[str], law: Mapping[str, Any] | None) -> bool:
    if law is None:
        return False
    if source_type in {"contract", "runtime", "user_declaration"} and bool(source_reference):
        return True
    authority = str(law.get("source_authority", ""))
    return any(contract and (contract in authority or authority in contract) for contract in governing_contracts)


def analyze_expression(
    expression: str,
    *,
    source_type: str,
    source_reference: str,
    profile_id: str = "HHS_NATIVE_TYPED_V1",
    declared_scope: Mapping[str, Any] | None = None,
    governing_contracts: Sequence[str] | None = None,
) -> dict[str, Any]:
    source_type = str(source_type)
    if source_type not in SOURCE_TYPES:
        raise Pass145Error("SEMANTIC_SOURCE_INVALID", f"unsupported source_type: {source_type}", "SEMANTIC_ANALYSIS")
    profile = get_profile(profile_id)
    if profile is None:
        raise Pass145Error("SEMANTIC_PROFILE_UNKNOWN", f"unknown operator profile: {profile_id}", "SEMANTIC_ANALYSIS")
    scope = dict(declared_scope or {})
    contracts = [str(x) for x in (governing_contracts or [])]
    ast = parse_expression(expression)
    law = declared_law_match(expression)
    findings = contamination_findings(expression, ast, source_type=source_type, profile_id=profile_id, declared_scope=scope)
    unresolved: list[dict[str, Any]] = []
    for diagnostic in ast["parse_diagnostics"]:
        unresolved.append({"reason": diagnostic["code"], "detail": diagnostic})
    for node in walk_ast(ast["root"]):
        if node.get("kind") in {"UNKNOWN", "MISSING"}:
            unresolved.append({"reason": "MISSING_OPERATOR_OR_TOKEN_DEFINITION", "source_span": node.get("span"), "source_slice": node.get("source_slice")})

    if profile_id == "NARRATIVE_WORLD_MODEL_V1" or source_type == "fiction":
        primary = "NARRATIVE_EXTRAPOLATION"
        consequence = "UNDETERMINED"
        authority = "A1"
    elif not profile["native"] or source_type == "control_engine":
        primary = "CONTROL_PROJECTION"
        consequence = "CONDITIONAL"
        authority = "A1"
    elif _authoritative_source(source_type, source_reference, contracts, law):
        primary = "DECLARED_SYSTEM_LAW"
        consequence = str(law["consequence_class"])
        authority = "A3"
        if not scope:
            scope = deepcopy(dict(law.get("scope", {})))
    else:
        primary = "UNRESOLVED_EXPRESSION"
        consequence = "UNDETERMINED"
        authority = "A1"
        if law is not None:
            unresolved.append({"reason": "ABSENT_AUTHORITY_SOURCE", "candidate_rule_id": law["rule_id"], "source_type": source_type, "source_reference": source_reference})
        elif not unresolved:
            unresolved.append({"reason": "NO_AUTHORIZED_NATIVE_REDUCTION", "profile": profile_id})

    prohibited_promotions = ["NO_PROMOTION_WITHOUT_WITNESSED_AUTHORIZATION"]
    if primary == "CONTROL_PROJECTION":
        prohibited_promotions += ["NO_NATIVE_STATE_MUTATION", "NO_NATIVE_GATE_SATISFACTION", "NO_CANONICAL_NATIVE_RECEIPT"]
    if primary == "NARRATIVE_EXTRAPOLATION":
        prohibited_promotions += ["NO_NARRATIVE_TO_NATIVE_PROMOTION"]
    if findings:
        prohibited_promotions += ["CONTAMINATION_MUST_BE_RESOLVED_BEFORE_PROMOTION"]

    interpretation_core = {
        "source_expression": expression,
        "canonical_ast_hash": ast["canonical_ast_hash"],
        "source_type": source_type,
        "source_reference": source_reference,
        "primary_class": primary,
        "consequence_class": consequence,
        "authority_level": authority,
        "operator_profile": profile_id,
        "lane_scope": list(scope.get("lane_scope", [])),
        "gate_scope": list(scope.get("gate_scope", [])),
        "branch_conditions": list(scope.get("branch_conditions", [])),
        "dependencies": [law["rule_id"]] if law else [],
        "assumptions": list(scope.get("assumptions", [])),
        "prohibited_promotions": sorted(set(prohibited_promotions)),
        "interpretation_version": INTERPRETATION_VERSION,
        "semantic_registry_version": SEMANTIC_REGISTRY_VERSION,
        "governing_contracts": contracts,
    }
    proposition_id = stable_id("PROP", "hhs_pass148_proposition_id_v1", interpretation_core)
    interpretation_hash = hash72("hhs_pass148_interpretation_v1", interpretation_core)
    hash72_identity = hash72("hhs_pass148_proposition_v1", {**interpretation_core, "proposition_id": proposition_id})
    proposition = {
        "proposition_id": proposition_id,
        **interpretation_core,
        "interpretation_hash": interpretation_hash,
        "hash72_identity": hash72_identity,
        "scope": scope,
    }
    return {
        "schema": "HHS_PASS148_EXPRESSION_ANALYSIS_V1",
        "evidence_authority": "A1",
        "ast": ast,
        "proposition": proposition,
        "declared_law": law,
        "profile": profile,
        "detected_assumptions": proposition["assumptions"],
        "unresolved_elements": unresolved,
        "contamination_findings": findings,
        "native_semantics_isolated": primary != "CONTROL_PROJECTION" or not profile["native"],
        "source_identity_preserved": ast["source_expression"] == expression,
    }


def _unwrap(node: Mapping[str, Any]) -> Mapping[str, Any]:
    while node.get("kind") == "GROUP":
        node = node["value"]
    return node


def _factor_map(node: Mapping[str, Any]) -> tuple[dict[str, int], bool]:
    node = _unwrap(node)
    kind = node.get("kind")
    if kind == "SYMBOL":
        return {str(node["value"]): 1}, True
    if kind == "NUMBER":
        return {"#" + str(node["value"]): 1}, True
    if kind == "UNARY" and node.get("operator_glyph") == "-":
        factors, ok = _factor_map(node["operand"])
        factors["#-1"] = factors.get("#-1", 0) + 1
        return factors, ok
    if kind == "BINARY" and node.get("operator_id") == "HHS_ORDERED_COMPOSITION":
        left, ok1 = _factor_map(node["left"]); right, ok2 = _factor_map(node["right"])
        out = dict(left)
        for key, value in right.items(): out[key] = out.get(key, 0) + value
        return out, ok1 and ok2
    if kind == "BINARY" and node.get("operator_id") == "HHS_PHASE_EXPONENT":
        base = _unwrap(node["left"]); exponent = _unwrap(node["right"])
        if base.get("kind") == "SYMBOL" and exponent.get("kind") == "NUMBER" and str(exponent.get("value", "")).isdigit():
            return {str(base["value"]): int(exponent["value"])}, True
    return {render_ast(dict(node)): 1}, False


def _render_factor_map(factors: Mapping[str, int]) -> str:
    pieces: list[str] = []
    for key in sorted(factors):
        exponent = factors[key]
        if exponent <= 0: continue
        display = key[1:] if key.startswith("#") else key
        pieces.append(display if exponent == 1 else f"{display}^{exponent}")
    return "*".join(pieces) or "1"


def _control_simplify(node: Mapping[str, Any], profile_id: str, assumptions: list[str]) -> str:
    node = _unwrap(node)
    kind = node.get("kind")
    if kind in {"SYMBOL", "NUMBER", "UNKNOWN", "MISSING", "EMPTY"}:
        return str(node.get("value", ""))
    if kind == "UNARY":
        op = str(node.get("operator_glyph", ""))
        return op + _control_simplify(node["operand"], profile_id, assumptions)
    if kind != "BINARY":
        return render_ast(dict(node))
    op = str(node.get("operator_glyph", ""))
    if node.get("operator_id") == "HHS_TYPED_FRACTION" and profile_id in {"COMMUTATIVE_FIELD_CONTROL_V1", "EXACT_RATIONAL_CONTROL_V1", "SYMBOLIC_CAS_CONTROL_V1"}:
        numerator, ok1 = _factor_map(node["left"]); denominator, ok2 = _factor_map(node["right"])
        if ok1 and ok2:
            remaining_num = dict(numerator); remaining_den = dict(denominator)
            for factor in sorted(set(remaining_num).intersection(remaining_den)):
                amount = min(remaining_num[factor], remaining_den[factor])
                if amount:
                    remaining_num[factor] -= amount; remaining_den[factor] -= amount
                    if not factor.startswith("#"):
                        assumptions.append(f"{factor} != 0")
            return _render_factor_map(remaining_num) + "/" + _render_factor_map(remaining_den)
    left = _control_simplify(node["left"], profile_id, assumptions)
    right = _control_simplify(node["right"], profile_id, assumptions)
    if op == "IMPLICIT": op = "*"
    return f"({left}{op}{right})"


def run_control_projection(expression: str, *, profile_id: str, assumptions: Sequence[str] | None = None) -> dict[str, Any]:
    profile = get_profile(profile_id)
    if profile is None:
        raise Pass145Error("SEMANTIC_PROFILE_UNKNOWN", f"unknown projection profile: {profile_id}", "CONTROL_PROJECTION")
    if profile["native"]:
        raise Pass145Error("CONTROL_PROFILE_REQUIRED", "native HHS profile cannot be executed as a control projection", "CONTROL_PROJECTION")
    ast = parse_expression(expression)
    inferred = [str(x) for x in (assumptions or [])]
    if profile_id == "IEEE754_BINARY64_CONTROL_V1":
        # Numeric-only binary64 evaluation. It is returned as a decimal string so
        # no float enters canonical authority.
        if any(n.get("kind") == "SYMBOL" for n in walk_ast(ast["root"])):
            projected = render_ast(ast["root"])
            inferred.append("symbolic variables remain unevaluated")
        else:
            safe = expression.replace("^", "**")
            if not re.fullmatch(r"[0-9+\-*/().\s*]+", safe):
                raise Pass145Error("CONTROL_PROJECTION_REJECTED", "binary64 projection accepts numeric expressions only", "CONTROL_PROJECTION")
            observed = float(eval(safe, {"__builtins__": {}}, {}))  # isolated numeric grammar above
            projected = format(observed, ".17g")
            inferred.append("result is IEEE-754 binary64 approximation")
    else:
        projected = _control_simplify(ast["root"], profile_id, inferred)
    core = {
        "source_expression": expression,
        "source_ast_hash": ast["canonical_ast_hash"],
        "profile_id": profile_id,
        "projected_expression": projected,
        "assumptions": sorted(set(inferred)),
        "primary_class": "CONTROL_PROJECTION",
        "consequence_class": "CONDITIONAL",
        "authority_level": "A1",
        "native_state_mutation": False,
        "namespace": f"control::{profile_id}",
        "registry_version": SEMANTIC_REGISTRY_VERSION,
    }
    projection_id = stable_id("PROJ", "hhs_pass148_projection_id_v1", core)
    return {
        "schema": "HHS_PASS148_CONTROL_PROJECTION_V1",
        "projection_id": projection_id,
        **core,
        "projection_hash72": hash72("hhs_pass148_control_projection_v1", {**core, "projection_id": projection_id}),
        "explicitly_non_native": True,
        "prohibited_promotions": ["NO_NATIVE_STATE_MUTATION", "NO_NATIVE_GATE_SATISFACTION", "NO_NATIVE_RECEIPT_SUBSTITUTION"],
        "profile": profile,
    }


def derive_consequence(input_propositions: Sequence[Mapping[str, Any]], *, rule_id: str, substitutions: Mapping[str, str] | None = None) -> dict[str, Any]:
    rule = DERIVATION_RULES.get(rule_id)
    if rule is None:
        raise Pass145Error("DERIVATION_RULE_UNAVAILABLE", f"unknown derivation rule: {rule_id}", "SEMANTIC_DERIVATION")
    if not input_propositions:
        raise Pass145Error("DERIVATION_DEPENDENCY_MISSING", "at least one input proposition is required", "SEMANTIC_DERIVATION")
    inputs = [dict(x) for x in input_propositions]
    for prop in inputs:
        if prop.get("primary_class") not in {"DECLARED_SYSTEM_LAW", "DERIVABLE_CONSEQUENCE"}:
            raise Pass145Error("DERIVATION_DEPENDENCY_UNAUTHORIZED", "derivation input lacks native semantic authority", "SEMANTIC_DERIVATION", str(prop.get("proposition_id")))
        if prop.get("operator_profile") != "HHS_NATIVE_TYPED_V1":
            raise Pass145Error("CONTROL_NATIVE_CONTAMINATION", "control projection cannot satisfy a native derivation dependency", "SEMANTIC_DERIVATION")
    steps: list[dict[str, Any]] = []
    if rule_id == "HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1":
        source = next((p for p in inputs if "HHS_DELTA_NORMALIZATION_V1" in p.get("dependencies", [])), None)
        if source is None:
            raise Pass145Error("DERIVATION_DEPENDENCY_MISSING", "HHS_DELTA_NORMALIZATION_V1 declaration is required", "SEMANTIC_DERIVATION")
        admitted = dict(substitutions or {"n": "Δ"})
        if admitted != {"n": "Δ"}:
            raise Pass145Error("DERIVATION_SUBSTITUTION_REJECTED", "this rule admits only n:=Δ", "SEMANTIC_DERIVATION")
        output_expression = "Δ/Δ=Δ"
        steps.append({"step": 1, "rule_id": rule_id, "before": source["source_expression"], "after": output_expression, "operator_types": rule["operator_types"], "scope": rule["scope"], "conditions": rule["conditions"], "authority": "A3", "substitution": admitted})
        consequence_class = rule["consequence_class"]
    else:
        source = inputs[0]
        output_expression = str(source["source_expression"])
        steps.append({"step": 1, "rule_id": rule_id, "before": output_expression, "after": output_expression, "operator_types": [], "scope": source.get("scope", {}), "conditions": rule["conditions"], "authority": "A3"})
        consequence_class = str(source.get("consequence_class", rule["consequence_class"]))
    output_analysis = analyze_expression(output_expression, source_type="runtime", source_reference=rule_id, profile_id="HHS_NATIVE_TYPED_V1", declared_scope=steps[-1]["scope"], governing_contracts=["HHS-P148-NSAM"])
    output_prop = dict(output_analysis["proposition"])
    output_prop["primary_class"] = "DERIVABLE_CONSEQUENCE"
    output_prop["consequence_class"] = consequence_class
    output_prop["authority_level"] = "A3"
    output_prop["dependencies"] = [str(p["proposition_id"]) for p in inputs] + [rule_id]
    identity_core = {k: v for k, v in output_prop.items() if k not in {"proposition_id", "interpretation_hash", "hash72_identity"}}
    output_prop["proposition_id"] = stable_id("PROP", "hhs_pass148_derived_proposition_id_v1", identity_core)
    output_prop["interpretation_hash"] = hash72("hhs_pass148_derived_interpretation_v1", identity_core)
    output_prop["hash72_identity"] = hash72("hhs_pass148_derived_proposition_v1", {**identity_core, "proposition_id": output_prop["proposition_id"]})
    derivation_core = {
        "input_propositions": [str(p["proposition_id"]) for p in inputs],
        "output_proposition": output_prop["proposition_id"],
        "ordered_steps": steps,
        "unresolved_dependencies": [],
        "control_contamination": False,
        "promotion_requested": False,
        "promotion_authorized": False,
        "registry_version": SEMANTIC_REGISTRY_VERSION,
    }
    derivation_id = stable_id("DRV", "hhs_pass148_derivation_id_v1", derivation_core)
    return {
        "schema": "HHS_PASS148_DERIVATION_V1",
        "derivation": {"derivation_id": derivation_id, **derivation_core, "derivation_hash72": hash72("hhs_pass148_derivation_v1", {"derivation_id": derivation_id, **derivation_core})},
        "output_proposition": output_prop,
        "output_ast": output_analysis["ast"],
    }


def segment_document(text: str) -> list[dict[str, Any]]:
    # Deterministic mixed-document segmentation. Fenced blocks, paragraphs, and
    # sentence boundaries retain exact byte-independent character offsets.
    segments: list[dict[str, Any]] = []
    pattern = re.compile(r"```.*?```|\$\$.*?\$\$|(?:[^\n]|\n(?!\n))+", re.S)
    index = 0
    for match in pattern.finditer(text):
        block = match.group(0)
        if not block.strip():
            continue
        block_start = match.start()
        if block.startswith("```") or block.startswith("$$"):
            parts = [(0, len(block), block)]
        else:
            parts = []
            for sentence in re.finditer(r"[^.!?\n]+(?:[.!?]+|$)", block):
                value = sentence.group(0)
                if value.strip(): parts.append((sentence.start(), sentence.end(), value))
            if not parts: parts = [(0, len(block), block)]
        for local_start, local_end, value in parts:
            start = block_start + local_start; end = block_start + local_end
            segment = {"segment_index": index, "start_offset": start, "end_offset": end, "text": value, "segment_hash72": hash72("hhs_pass148_document_segment_v1", {"start": start, "end": end, "text": value})}
            segments.append(segment); index += 1
    return segments
