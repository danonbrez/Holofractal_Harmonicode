#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass145.canonical import canonical_json, hash72
from hhs_runtime.pass148.public import Pass148PublicSurfaceRegistry, SCHEMAS, SEMANTIC_API_SURFACES
from hhs_runtime.pass148.registry import (
    AUTHORITY_LEVELS, CONSEQUENCE_CLASSES, PRIMARY_CLASSES, SOURCE_TYPES,
    contamination_registry, full_registry, projection_profile_registry,
)


def write_json(name: str, payload: dict) -> None:
    (ROOT / name).write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


CONTRACT = r'''# HHS PASS 148 — NATIVE SEMANTIC AUTHORITY MEMBRANE

## Mathematical Consequence Classification, Interpretation Isolation, and Narrative Non-Promotion Contract

**Contract ID:** HHS-P148-NSAM  
**Status:** Normative implementation contract  
**Parent:** Complete authoritative Pass 147 nucleus  
**Governance:** HHS-I132 CEUAC, Pass 134 RFACC, and all binding inherited HHS contracts

## 0. Declaration

Pass 148 implements a native semantic authority membrane around HHS mathematical expressions. Representation may vary, but native semantic authority must not drift. Analysis, restatement, control projection, narrative construction, and model proposals are permitted; none becomes native truth without an admitted authority transition.

The five primary semantic classes are:

1. `DECLARED_SYSTEM_LAW`
2. `DERIVABLE_CONSEQUENCE`
3. `CONTROL_PROJECTION`
4. `UNRESOLVED_EXPRESSION`
5. `NARRATIVE_EXTRAPOLATION`

Exactly one primary class and one secondary consequence class are assigned to every persisted proposition. The secondary classes are `NECESSARY`, `CONDITIONAL`, `LANE_LOCAL`, `GATE_LOCAL`, `NORMALIZATION_LOCAL`, `INVARIANT`, `EXCLUDED`, and `UNDETERMINED`.

## 1. Inheritance

The release is the complete inherited nucleus: `N148 = N147 ∪ Δ148`. Every inherited non-cache file and binding obligation remains present. The Pass 147 external-agent opacity architecture and Pass 146 boundary-construction architecture remain authoritative. Pass 148 is additive and may not expose a private semantic shortcut.

## 2. Implementation rule

Authorization requires a functioning, callable, persisted, tested, replayable membrane. Prose, prompts, regular-expression labels, unconnected libraries, mock evaluators, and hard-coded success responses are insufficient. Real expressions must produce ordered ASTs, classifications, scope records, diagnostics, derivations, decisions, and receipts through public surfaces.

## 3. Problem boundary

Conventional glyph priors do not authorize conventional semantics. The membrane rejects silent mappings including `==→=`, commutative `+`, scalar subtraction, repeated-multiplication exponentiation, field division, `Δ→1`, `O→π`, lane-local→global, and narrative event→verified physical consequence.

## 4. Core invariants

- **Ω148.1 Identity:** source spelling, operand order, grouping, operator spelling/type, scope, and provenance are immutable evidence.
- **Ω148.2 Native priority:** glyph identity, operator identity, and contextual result remain distinct.
- **Ω148.3 Promotion:** classification promotion requires a witnessed source, target, rule, dependency set, scope, verifier, authority, receipt, and replay witness.
- **Ω148.4 Narrative:** fiction cannot legislate mathematics.
- **Ω148.5 Projection:** IEEE, conventional field, real, complex, CAS, and numerical outputs remain isolated controls and cannot mutate native state.
- **Ω148.6 Unresolved:** absent semantic authority yields `UNRESOLVED_EXPRESSION`, not forced closure.
- **Ω148.7 Order:** no commutation, reassociation, cancellation, distribution, inversion, or branch exchange without an applicable rule.
- **Ω148.8 Scope:** lane-, gate-, branch-, normalization-, and projection-local results cannot silently become global.
- **Ω148.9 Symbol identity:** `O ≠ π` is absolute.
- **Ω148.10 Delta:** `n/Δ=n` and `Δ^n=Δ` are typed HHS laws and do not imply scalar `Δ=1`.
- **Ω148.11 Evidence independence:** evidence is immutable; interpretations are append-only and versioned.
- **Ω148.12 External agent:** model proposals have zero native semantic commit authority.

## 5. Authority

Every result carries CEUAC authority A1, A2, A3, or A4. A1 records execution; A2 records public black-box capability; A3 records contract conformance; A4 is reserved for an identified formal proof artifact. A1–A3 may not be relabeled as universal impossibility or formal proof.

## 6. Objects

The canonical proposition retains source expression, AST hash, source type/reference, both classifications, authority, operator profile, lane/gate/branch scope, dependencies, assumptions, prohibited promotions, interpretation version/hash, Hash72 identity, and timestamp. Derivations retain every ordered rule step, before/after expression, operator types, conditions, scope, authority, unresolved dependencies, contamination state, promotion state, and receipt.

## 7. Projection profiles

Required profiles are `HHS_NATIVE_TYPED_V1`, `COMMUTATIVE_FIELD_CONTROL_V1`, `EXACT_RATIONAL_CONTROL_V1`, `IEEE754_BINARY64_CONTROL_V1`, `STANDARD_COMPLEX_CONTROL_V1`, `STANDARD_REAL_ANALYSIS_CONTROL_V1`, `SYMBOLIC_CAS_CONTROL_V1`, and `NARRATIVE_WORLD_MODEL_V1`. Each declares domain, equality, branch, simplification, commutation, cancellation, representation, authority ceiling, output classes, and mutation prohibition.

## 8. Contamination

The membrane detects scalarization, operator aliasing, equality flattening, commutativity injection, cancellation injection, scope inflation, narrative promotion, physical-ontology promotion, consciousness promotion, proof-language inflation, order collapse, hidden dependencies, source mutation, and control/native repair contamination. Each finding is structured and receipted.

## 9. Native registry

The registry is queryable and versioned. It contains operator IDs, glyph aliases/forbidden aliases, signatures, lane/gate scope, precedence, associativity, commutativity, inverse/cancellation/normalization/branch rules, projection permissions, examples, counterexamples, source authority, version, and Hash72 witness. Missing entries remain unresolved; conventional fallback is prohibited.

## 10. Required boundary cases

The implementation preserves `O≠π`, `n/Δ=n`, `Δ^n=Δ`, `Δ-Δ=x+y`, the declared infinity relations, and ordered meta-constraints. It derives `Δ/Δ=Δ` only from the admitted normalization law with explicit substitution. It isolates commutative reduction of `AB/B²` as a control with nonzero assumptions. It does not infer `Δ=1`, `∞=1`, `P=√2`, global prime exclusion, Lo Shu closure from resemblance, physical ontology, or consciousness without separate authority.

## 11. Mixed documents

Documents containing exposition, equations, dialogue, fiction, appendices, speculation, conventional calculations, and native declarations are segmented with exact source spans. Each proposition is classified independently. A title, fictional speaker, technical style, repetition, or appendix placement confers no authority. Original bytes remain reconstructable.

## 12. Public surfaces

The public CLI provides `hhs semantic analyze`, `analyze-document`, `derive`, `project`, `classify`, `promotion-request`, `promotion-evaluate`, `rule show`, `replay`, `audit`, and registry operations. The loopback API provides expression/document analysis, derivation, projection, promotion request/evaluation, proposition/derivation/rule retrieval, replay, and audit. Every operation is boundary-constructed. Promotion evaluation and registry mutation require separate `SEMANTIC_AUTHORITY_ADMIN`; external agents never receive it.

## 13. Persistence and replay

Raw source, AST, proposition, interpretation, derivation, projection, diagnostics, promotion requests/decisions, semantic replays, and CEUAC evidence are persisted transactionally. Repeated execution under the same source, registry, profile, contracts, and scope reproduces the same AST, proposition identity, classifications, findings, unresolved set, derivation graph, and deterministic semantic receipt. Occurrence-specific transaction receipts remain separate.

## 14. Testing and CEUAC

Positive and adversarial tests execute real service, CLI, and API surfaces. The black-box Actor uses only public CLI/API, schemas, documentation, sandbox files, and public rule retrieval. It cannot inspect source code, SQLite, private registries, or nucleus state. Evidence preserves A1, A2, A3, and any A4 artifacts separately.

## 15. Terminal rule

The semantic closure condition requires source identity, native isolation, witnessed classification, scope preservation, projection separation, narrative non-promotion, deterministic replay, and external privilege zero. The system may analyze everything exposed to it, but nothing becomes native truth without authority.
'''


def proposition_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "hhs://schemas/pass148/proposition",
        "title": "HHS Pass 148 Proposition",
        "type": "object",
        "additionalProperties": True,
        "required": [
            "proposition_id", "source_expression", "canonical_ast_hash", "source_type", "source_reference",
            "primary_class", "consequence_class", "authority_level", "operator_profile", "lane_scope",
            "gate_scope", "branch_conditions", "dependencies", "assumptions", "prohibited_promotions",
            "interpretation_version", "interpretation_hash", "hash72_identity", "timestamp",
        ],
        "properties": {
            "proposition_id": {"type": "string", "minLength": 1},
            "source_expression": {"type": "string"},
            "canonical_ast_hash": {"type": "string", "minLength": 1},
            "source_type": {"enum": list(SOURCE_TYPES)},
            "source_reference": {"type": "string", "minLength": 1},
            "primary_class": {"enum": list(PRIMARY_CLASSES)},
            "consequence_class": {"enum": list(CONSEQUENCE_CLASSES)},
            "authority_level": {"enum": list(AUTHORITY_LEVELS)},
            "operator_profile": {"type": "string", "minLength": 1},
            "lane_scope": {"type": "array"}, "gate_scope": {"type": "array"},
            "branch_conditions": {"type": "array"}, "dependencies": {"type": "array"},
            "assumptions": {"type": "array"}, "prohibited_promotions": {"type": "array"},
            "interpretation_version": {"type": "string", "minLength": 1},
            "interpretation_hash": {"type": "string", "minLength": 1},
            "hash72_identity": {"type": "string", "minLength": 1},
            "timestamp": {"type": ["string", "null"]},
        },
    }


def derivation_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "hhs://schemas/pass148/derivation",
        "title": "HHS Pass 148 Derivation",
        "type": "object", "additionalProperties": True,
        "required": ["derivation_id", "input_propositions", "output_proposition", "ordered_steps", "unresolved_dependencies", "control_contamination", "promotion_requested", "promotion_authorized", "derivation_hash72", "receipt"],
        "properties": {
            "derivation_id": {"type": "string"}, "input_propositions": {"type": "array", "items": {"type": "string"}},
            "output_proposition": {"type": "string"},
            "ordered_steps": {"type": "array", "items": {"type": "object", "required": ["step", "rule_id", "before", "after", "operator_types", "scope", "conditions", "authority"]}},
            "unresolved_dependencies": {"type": "array"}, "control_contamination": {"type": "boolean"},
            "promotion_requested": {"type": "boolean"}, "promotion_authorized": {"type": "boolean"},
            "derivation_hash72": {"type": "string"}, "receipt": {"type": ["string", "null"]},
        },
    }


def promotion_schema() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "hhs://schemas/pass148/promotion",
        "type": "object", "additionalProperties": True,
        "required": ["source_proposition_id", "source_class", "target_class", "governing_rule", "dependency_set", "scope", "requested_by_identity", "status"],
        "properties": {
            "source_proposition_id": {"type": "string"}, "source_class": {"enum": list(PRIMARY_CLASSES)},
            "target_class": {"enum": list(PRIMARY_CLASSES)}, "governing_rule": {"type": "string"},
            "dependency_set": {"type": "array", "items": {"type": "string"}}, "scope": {"type": "object"},
            "requested_by_identity": {"type": "string"}, "status": {"enum": ["REQUESTED", "AUTHORIZED", "REJECTED"]},
        },
    }


def openapi() -> dict:
    paths: dict[str, dict] = {}
    for method, path, description, _mutating in SEMANTIC_API_SURFACES:
        open_path = path.replace("{id}", "{id}").replace("{rule_id}", "{rule_id}")
        operation = {"summary": description, "responses": {"200": {"description": "Boundary-admitted result"}, "400": {"description": "Structured safe rejection"}, "401": {"description": "Authentication required"}}, "security": [{"bearerAuth": []}]}
        if method == "POST": operation["requestBody"] = {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}}
        paths.setdefault(open_path, {})[method.lower()] = operation
    return {
        "openapi": "3.1.0", "info": {"title": "HHS Pass 148 Semantic Membrane API", "version": "148.1.0"},
        "servers": [{"url": "http://127.0.0.1:8878", "description": "Authenticated loopback only"}],
        "paths": paths,
        "components": {"securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}, "schemas": {"Proposition": proposition_schema(), "Derivation": derivation_schema(), "Promotion": promotion_schema()}},
    }


def main() -> int:
    (ROOT / "contracts/pass148").mkdir(parents=True, exist_ok=True)
    (ROOT / "schemas/pass148").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/pass148").mkdir(parents=True, exist_ok=True)
    (ROOT / "HHS_PASS_148_NATIVE_SEMANTIC_AUTHORITY_MEMBRANE_CONTRACT.md").write_text(CONTRACT, encoding="utf-8")
    (ROOT / "contracts/pass148/HHS-P148_NATIVE_SEMANTIC_AUTHORITY_MEMBRANE.md").write_text(CONTRACT, encoding="utf-8")

    registry = full_registry()
    write_json("HHS_PASS_148_SEMANTIC_RULE_REGISTRY.json", registry)
    write_json("HHS_PASS_148_PROJECTION_PROFILE_REGISTRY.json", {"schema": "HHS_PASS148_PROJECTION_PROFILE_REGISTRY_V1", "registry_version": registry["registry_version"], "profiles": projection_profile_registry(), "registry_hash72": hash72("hhs_pass148_projection_profile_registry_artifact_v1", projection_profile_registry())})
    write_json("HHS_PASS_148_CONTAMINATION_DIAGNOSTICS.json", {"schema": "HHS_PASS148_CONTAMINATION_DIAGNOSTICS_V1", "diagnostics": contamination_registry(), "registry_hash72": hash72("hhs_pass148_contamination_artifact_v1", contamination_registry())})
    prop = proposition_schema(); drv = derivation_schema(); promo = promotion_schema()
    write_json("HHS_PASS_148_PROPOSITION_SCHEMA.json", prop); write_json("HHS_PASS_148_DERIVATION_SCHEMA.json", drv); write_json("HHS_PASS_148_PROMOTION_SCHEMA.json", promo)
    write_json("schemas/pass148/proposition.schema.json", prop); write_json("schemas/pass148/derivation.schema.json", drv); write_json("schemas/pass148/promotion.schema.json", promo)
    api = openapi(); write_json("HHS_PASS_148_API_OPENAPI.json", api); write_json("schemas/pass148/openapi.json", api)

    cli_ref = '''# HHS Pass 148 CLI Reference\n\nAll operations are boundary-constructed and support global `--db` and `--format json|jsonl|text|markdown`.\n\n- `hhs semantic analyze --expression EXPR --source-type TYPE --source-reference REF`\n- `hhs semantic analyze-document PATH --source-type TYPE`\n- `hhs semantic derive --proposition ID --rule RULE --substitutions JSON`\n- `hhs semantic project --profile PROFILE --expression EXPR`\n- `hhs semantic classify --proposition ID`\n- `hhs semantic proposition ID`\n- `hhs semantic derivation ID`\n- `hhs semantic promotion-request --source ID --target CLASS --governing-rule RULE`\n- `hhs semantic promotion-evaluate REQUEST --authorize|--reject --authority A3|A4 --rationale TEXT`\n- `hhs semantic rule show RULE_ID`\n- `hhs semantic replay TARGET_ID`\n- `hhs semantic audit --dependency-scope pass148`\n- `hhs semantic registry sync|audit`\n- `hhs semantic serve --host 127.0.0.1 --port 8878 --token TOKEN`\n\nExternal-agent profiles may use all analytical operations except `promotion-evaluate` and `registry sync`. They cannot claim `contract`, `runtime`, or `user_declaration` source authority through request fields.\n'''
    (ROOT / "HHS_PASS_148_CLI_REFERENCE.md").write_text(cli_ref, encoding="utf-8")
    (ROOT / "docs/pass148/CLI_REFERENCE.md").write_text(cli_ref, encoding="utf-8")

    implementation = f'''# HHS Pass 148 Implementation Report\n\nPass 148 is implemented as an additive service over Pass 147 public opacity and Pass 146 boundary construction.\n\n## Implemented components\n\n- ordered Pratt parser with exact source spans and no algebraic simplification;\n- native semantic, derivation, projection, and contamination registries;\n- five primary and eight secondary classifications;\n- immutable source/AST identity and versioned interpretation identity;\n- transactional SQLite schema 1.4.0 for semantic evidence and interpretations;\n- witnessed derivation graph and authorized promotion decision path;\n- isolated control projections with native mutation disabled;\n- mixed narrative/document segmentation;\n- deterministic semantic replay;\n- authenticated CLI and loopback API;\n- Pass 147 public capability, schema, rule, and documentation discovery;\n- external-agent source-authority anti-forgery and zero semantic commit authority.\n\n## Registry\n\nRegistry version: `{registry['registry_version']}`. Operators: {len(registry['operators'])}; declared laws: {len(registry['declared_laws'])}; derivation rules: {len(registry['derivation_rules'])}; projection profiles: {len(registry['projection_profiles'])}; diagnostics: {len(registry['contamination_diagnostics'])}.\n\n## Authority boundary\n\nExternal actors can analyze, segment, derive from admitted propositions, project controls, retrieve rules and records, request promotion, audit, and replay. They cannot synchronize the native registry, evaluate promotion, fabricate authoritative source type, inspect SQLite, or bypass Pass 146 pathways.\n'''
    (ROOT / "HHS_PASS_148_IMPLEMENTATION_REPORT.md").write_text(implementation, encoding="utf-8")

    # Static catalog generation does not require persistence or privileged access.
    class CatalogDB:
        pass
    # PublicSurfaceRegistry only requires a DB for synchronize/audit, not build_catalog.
    catalog = Pass148PublicSurfaceRegistry.__new__(Pass148PublicSurfaceRegistry).build_catalog()
    semantic = [x for x in catalog if (x.get("argv") or [""])[0:1] == ["semantic"] or str(x.get("path", "")).startswith("/api/v1/semantic-membrane")]
    capability = {
        "schema": "HHS_PASS148_CAPABILITY_MANIFEST_V1", "pass_id": "HHS-P148-NSAM",
        "semantic_public_surface_count": len(semantic), "semantic_public_surfaces": semantic,
        "primary_classes": list(PRIMARY_CLASSES), "consequence_classes": list(CONSEQUENCE_CLASSES),
        "authority_levels": list(AUTHORITY_LEVELS), "projection_profiles": [x["profile_id"] for x in projection_profile_registry()],
        "privileged_internal_access": 0, "privileged_semantic_authority_external": 0,
    }
    capability["manifest_hash72"] = hash72("hhs_pass148_capability_manifest_v1", capability)
    write_json("HHS_PASS_148_CAPABILITY_MANIFEST.json", capability)
    print(json.dumps({"registry_entries": sum(len(registry[k]) for k in ("operators", "declared_laws", "derivation_rules", "projection_profiles", "contamination_diagnostics")), "semantic_public_surfaces": len(semantic)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
