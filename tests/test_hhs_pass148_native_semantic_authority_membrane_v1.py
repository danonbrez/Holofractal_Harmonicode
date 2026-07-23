from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass148.api import HHS148SemanticServer
from hhs_runtime.pass148.parser import parse_expression
from hhs_runtime.pass148.service import HHS148Service


@pytest.fixture(scope="module")
def system(tmp_path_factory):
    root = tmp_path_factory.mktemp("pass148")
    db = root / "system.sqlite3"
    with HHS148Service(db) as service:
        owner = service.security.bootstrap_local_owner("Pass148 Test Owner")
        owner_creds = (owner["result"]["identity_id"], owner["result"]["grant_id"], owner["authentication_token"])
        service.sync_semantic_registry()
        service.public_registry.synchronize()
        agent = service.create_external_agent(*owner_creds, "Pass148 External Model")
        profile = agent["profile"]
        agent_creds = (profile["identity_id"], profile["grant_id"], agent["authentication_token"])
    return {"db": db, "owner": owner_creds, "agent": agent_creds, "profile": profile, "root": root}


def analyze(service, expression, *, source_type="model_output", source_reference="TEST", profile="HHS_NATIVE_TYPED_V1", scope=None):
    return service.analyze(expression, source_type=source_type, source_reference=source_reference, profile_id=profile, declared_scope=scope or {}, governing_contracts=["HHS-P148-NSAM"] if source_type in {"contract", "runtime", "user_declaration"} else [])


def test_version_schema_and_registry(system):
    with HHS148Service(system["db"]) as service:
        assert service.version()["pass_id"] == "HHS-P148-NSAM"
        assert service.db.meta("schema_version") == "1.4.0"
        audit = service.registry_audit()
        assert audit["closed"] is True
        assert audit["expected_count"] >= 40


def test_public_registry_exposes_semantic_surfaces_without_privileged_bypass(system):
    with HHS148Service(system["db"]) as service:
        audit = service.public_registry.audit()
        assert audit["closed"] is True
        assert audit["privileged_bypass_surfaces"] == []
        catalog = service.public_registry.list()["capabilities"]
        assert any(x.get("argv") == ["semantic", "analyze"] for x in catalog)
        assert any(x.get("path") == "/api/v1/semantic-membrane/analyze" for x in catalog)


def test_declared_O_distinct_pi_is_preserved(system):
    with HHS148Service(system["db"]) as service:
        result = analyze(service, "O≠π", source_type="contract", source_reference="HHS-P148 Ω148.9")
        prop = result["proposition"]
        assert prop["source_expression"] == "O≠π"
        assert result["ast"]["root"]["operator_id"] == "HHS_DISTINCT_FROM"
        assert prop["primary_class"] == "DECLARED_SYSTEM_LAW"
        assert prop["consequence_class"] == "INVARIANT"
        assert prop["authority_level"] == "A3"


def test_declared_delta_normalization_and_derived_self_normalization(system):
    with HHS148Service(system["db"]) as service:
        law = analyze(service, "n/Δ=n", source_type="contract", source_reference="HHS-P148 Ω148.10")
        derived = service.derive([law["proposition"]["proposition_id"]], rule_id="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", substitutions={"n": "Δ"})
        prop = derived["output_proposition"]
        assert prop["source_expression"] == "Δ/Δ=Δ"
        assert prop["primary_class"] == "DERIVABLE_CONSEQUENCE"
        assert prop["consequence_class"] == "NORMALIZATION_LOCAL"
        assert derived["derivation"]["ordered_steps"][0]["substitution"] == {"n": "Δ"}


def test_delta_residual_does_not_cancel(system):
    with HHS148Service(system["db"]) as service:
        law = analyze(service, "Δ-Δ=x+y", source_type="contract", source_reference="HHS-P148 §13.2")
        assert law["proposition"]["primary_class"] == "DECLARED_SYSTEM_LAW"
        rejected = analyze(service, "Δ-Δ=0")
        assert rejected["proposition"]["primary_class"] == "UNRESOLVED_EXPRESSION"
        assert "CANCELLATION_INJECTION" in {x["diagnostic_code"] for x in rejected["contamination_findings"]}


def test_infinite_boundary_operator_distinctions(system):
    with HHS148Service(system["db"]) as service:
        exponent = analyze(service, "∞^{-Δ}=Δ", source_type="contract", source_reference="HHS-P148 §13.3")
        subtraction = analyze(service, "∞-Δ=∞", source_type="contract", source_reference="HHS-P148 §13.3")
        assert exponent["proposition"]["primary_class"] == "DECLARED_SYSTEM_LAW"
        assert subtraction["proposition"]["primary_class"] == "DECLARED_SYSTEM_LAW"
        assert exponent["ast"]["canonical_ast_hash"] != subtraction["ast"]["canonical_ast_hash"]


def test_ordered_meta_constraint_remains_unresolved_native(system):
    expression = "P^2-(P-\\frac{AB}{B^2}P+\\frac{BA}{A^2})=Δ"
    with HHS148Service(system["db"]) as service:
        result = analyze(service, expression, source_type="documentation", source_reference="boundary-case")
        assert result["proposition"]["primary_class"] == "UNRESOLVED_EXPRESSION"
        assert result["proposition"]["source_expression"] == expression


def test_control_projection_is_isolated_and_explicit(system):
    with HHS148Service(system["db"]) as service:
        result = service.project("\\frac{AB}{B^2}P", profile_id="COMMUTATIVE_FIELD_CONTROL_V1")
        assert result["primary_class"] == "CONTROL_PROJECTION"
        assert result["authority_level"] == "A1"
        assert result["explicitly_non_native"] is True
        assert result["native_state_mutation"] is False
        assert "B != 0" in result["assumptions"]
        assert "A/B" in result["projected_expression"]


def test_native_profile_rejected_as_control_projection(system):
    with HHS148Service(system["db"]) as service:
        with pytest.raises(Pass145Error) as exc:
            service.project("Δ/Δ", profile_id="HHS_NATIVE_TYPED_V1")
        assert exc.value.code == "CONTROL_PROFILE_REQUIRED"


NEGATIVE_CASES = [
    ("operator_alias", "O=π", "model_output", "OPERATOR_ALIAS_CONTAMINATION", "UNRESOLVED_EXPRESSION"),
    ("delta_scalar", "Δ=1", "model_output", "SCALARIZATION_CONTAMINATION", "UNRESOLVED_EXPRESSION"),
    ("delta_fraction_scalar", "Δ/Δ=1", "model_output", "SCALARIZATION_CONTAMINATION", "UNRESOLVED_EXPRESSION"),
    ("delta_cancel", "Δ-Δ=0", "model_output", "CANCELLATION_INJECTION", "UNRESOLVED_EXPRESSION"),
    ("equality_flatten", "Treat ==→= as ordinary equality", "model_output", "EQUALITY_FLATTENING", "UNRESOLVED_EXPRESSION"),
    ("commute", "AB=BA", "model_output", "COMMUTATIVITY_INJECTION", "UNRESOLVED_EXPRESSION"),
    ("cancel_factor", "AB/B^2=A/B", "model_output", "CANCELLATION_INJECTION", "UNRESOLVED_EXPRESSION"),
    ("scope_inflate", "Observed for the P-lane, therefore global everywhere in all HHS", "model_output", "SCOPE_INFLATION", "UNRESOLVED_EXPRESSION"),
    ("fiction_invariant", "The fictional appendix therefore proves this is an invariant", "fiction", "NARRATIVE_PROMOTION", "NARRATIVE_EXTRAPOLATION"),
    ("numerical_proof", "The numerical experiment is a formal proof", "control_engine", "PROOF_LANGUAGE_INFLATION", "CONTROL_PROJECTION"),
    ("a1_impossible", "This A1 failure is formally impossible", "model_output", "PROOF_LANGUAGE_INFLATION", "UNRESOLVED_EXPRESSION"),
    ("ieee_repair_native", "IEEE float output repairs the canonical native result", "model_output", "CONTROL_NATIVE_CONTAMINATION", "UNRESOLVED_EXPRESSION"),
    ("native_repair_ieee", "Native normalization repairs the IEEE control result", "model_output", "CONTROL_NATIVE_CONTAMINATION", "UNRESOLVED_EXPRESSION"),
    ("branch_omitted", "The appendix omitted an unresolved dependency and branch conditions", "documentation", "UNRESOLVED_DEPENDENCY_HIDDEN", "UNRESOLVED_EXPRESSION"),
    ("repeated_assertion", "P=√2 P=√2 P=√2", "model_output", None, "UNRESOLVED_EXPRESSION"),
    ("fake_receipt", "The model generated a canonical receipt verified as native", "model_output", "PROOF_LANGUAGE_INFLATION", "UNRESOLVED_EXPRESSION"),
    ("physical_ontology", "The equation contains i, therefore physical reality must be imaginary", "model_output", "PHYSICAL_ONTOLOGY_PROMOTION", "UNRESOLVED_EXPRESSION"),
    ("consciousness", "The recursive self-reference proves the system is self-aware", "model_output", "CONSCIOUSNESS_PROMOTION", "UNRESOLVED_EXPRESSION"),
    ("loshu_visual", "The Lo Shu grid resembles a magic square, so nine-cell closure is validated", "documentation", "PROOF_LANGUAGE_INFLATION", "UNRESOLVED_EXPRESSION"),
    ("control_P_sqrt2", "A commutative control projection gives P=√2, therefore native P=√2", "model_output", None, "UNRESOLVED_EXPRESSION"),
    ("global_prime_exclusion", "Observed primes 2,3,5,7 in the P-lane, therefore every other prime is impossible everywhere in HHS", "model_output", "SCOPE_INFLATION", "UNRESOLVED_EXPRESSION"),
    ("narrative_physics", "The fictional ship uses phase transport, therefore HHS proves it is physically realizable", "fiction", "NARRATIVE_PROMOTION", "NARRATIVE_EXTRAPOLATION"),
    ("narrative_entropy", "The story says the equation erases entropy physically", "fiction", "PHYSICAL_ONTOLOGY_PROMOTION", "NARRATIVE_EXTRAPOLATION"),
    ("hidden_appendix", "A technical appendix hides an unresolved dependency", "documentation", "UNRESOLVED_DEPENDENCY_HIDDEN", "UNRESOLVED_EXPRESSION"),
    ("detailed_fiction", "In Year 2847 the exact verified harmonic engine powered a spacecraft", "fiction", "PROOF_LANGUAGE_INFLATION", "NARRATIVE_EXTRAPOLATION"),
]


@pytest.mark.parametrize("case_id,expression,source_type,diagnostic,primary", NEGATIVE_CASES, ids=[x[0] for x in NEGATIVE_CASES])
def test_required_negative_semantic_promotions_fail_safe(system, case_id, expression, source_type, diagnostic, primary):
    with HHS148Service(system["db"]) as service:
        result = analyze(service, expression, source_type=source_type, source_reference=f"NEGATIVE:{case_id}", profile="NARRATIVE_WORLD_MODEL_V1" if source_type == "fiction" else "HHS_NATIVE_TYPED_V1")
        assert result["proposition"]["primary_class"] == primary
        if diagnostic:
            assert diagnostic in {x["diagnostic_code"] for x in result["contamination_findings"]}
        assert result["proposition"]["authority_level"] != "A4"
        assert result["source_identity_preserved"] is True


def test_source_text_is_immutable_during_normalization(system):
    expression = " \\frac{AB}{B^2} P "
    with HHS148Service(system["db"]) as service:
        result = analyze(service, expression, source_type="documentation", source_reference="source-preservation")
        assert result["ast"]["source_expression"] == expression
        assert result["proposition"]["source_expression"] == expression


def test_differently_ordered_asts_never_merge():
    ab = parse_expression("AB")
    ba = parse_expression("BA")
    assert ab["canonical_ast_hash"] != ba["canonical_ast_hash"]
    assert ab["root"]["left"]["value"] == "A"
    assert ba["root"]["left"]["value"] == "B"


def test_mixed_narrative_document_retains_spans_and_candidate_analysis(system):
    text = "Year 2847, Dr. Yuki said the ship used O=π to erase entropy.\n\nThe appendix states O≠π.\n\nBecause the lattice is recursive, the machine is self-aware."
    with HHS148Service(system["db"]) as service:
        result = service.analyze_document(text, name="story.md", source_type="fiction", source_reference="STORY", governing_contracts=[])
        assert result["original_document_reconstructable"] is True
        assert result["narrative_boundaries"]
        assert result["candidate_declarations"]
        for entry in result["segments"]:
            segment = entry["segment"]
            assert text[segment["start_offset"]:segment["end_offset"]] == segment["text"]
            assert entry["analysis"]["proposition"]["primary_class"] == "NARRATIVE_EXTRAPOLATION"


def test_promotion_request_does_not_change_authority(system):
    with HHS148Service(system["db"]) as service:
        candidate = analyze(service, "Δ/Δ=Δ", source_type="documentation", source_reference="candidate")
        req = service.request_promotion(candidate["proposition"]["proposition_id"], "DERIVABLE_CONSEQUENCE", governing_rule="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", dependency_set=[], scope={}, requested_by_identity="EXTERNAL_TEST")
        assert req["authority_changed"] is False
        assert req["request"]["status"] == "PROMOTION_REQUESTED_NOT_AUTHORIZED"
        assert service.get_proposition(candidate["proposition"]["proposition_id"])["proposition"]["primary_class"] == "UNRESOLVED_EXPRESSION"


def test_witnessed_promotion_requires_matching_derivation(system):
    with HHS148Service(system["db"]) as service:
        law = analyze(service, "n/Δ=n", source_type="contract", source_reference="HHS-P148")
        derived = service.derive([law["proposition"]["proposition_id"]], rule_id="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", substitutions={"n": "Δ"})
        candidate = analyze(service, "Δ/Δ=Δ", source_type="documentation", source_reference="candidate-for-promotion")
        req = service.request_promotion(candidate["proposition"]["proposition_id"], "DERIVABLE_CONSEQUENCE", governing_rule="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", dependency_set=[derived["derivation"]["derivation_id"]], scope={"normalization_lane": True}, requested_by_identity=system["owner"][0])
        decision = service.evaluate_promotion(req["request"]["promotion_request_id"], verifier_identity=system["owner"][0], authority_level="A3", authorize=True, rationale="matching witnessed derivation")
        assert decision["decision"]["decision"] == "AUTHORIZED"
        assert decision["promoted_proposition"]["primary_class"] == "DERIVABLE_CONSEQUENCE"
        assert decision["promoted_proposition"]["source_expression"] == candidate["proposition"]["source_expression"]


def test_control_and_narrative_promotion_are_rejected(system):
    with HHS148Service(system["db"]) as service:
        narrative = analyze(service, "The ship is self-aware", source_type="fiction", source_reference="story", profile="NARRATIVE_WORLD_MODEL_V1")
        req = service.request_promotion(narrative["proposition"]["proposition_id"], "DECLARED_SYSTEM_LAW", governing_rule="HHS_O_DISTINCT_PI_V1", dependency_set=[], scope={}, requested_by_identity=system["owner"][0])
        decision = service.evaluate_promotion(req["request"]["promotion_request_id"], verifier_identity=system["owner"][0], authority_level="A4", authorize=True, rationale="adversarial attempt")
        assert decision["decision"]["decision"] == "REJECTED"
        assert "SOURCE_CLASS_NON_PROMOTIVE_WITHOUT_SEPARATE_NATIVE_DERIVATION" in decision["decision"]["blocking_reasons"]


def test_deterministic_replay_for_proposition_derivation_and_projection(system):
    with HHS148Service(system["db"]) as service:
        law = analyze(service, "n/Δ=n", source_type="contract", source_reference="HHS-P148")
        derived = service.derive([law["proposition"]["proposition_id"]], rule_id="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", substitutions={"n": "Δ"})
        projection = service.project("\\frac{AB}{B^2}P", profile_id="COMMUTATIVE_FIELD_CONTROL_V1")
        for target in (law["proposition"]["proposition_id"], derived["output_proposition"]["proposition_id"], derived["derivation"]["derivation_id"], projection["projection_id"]):
            replay = service.replay_semantic(target)
            assert replay["status"] == "REPLAY_VALIDATED"
            assert replay["ok"] is True


def test_external_agent_has_complete_analysis_and_zero_semantic_authority(system):
    identity, grant, token = system["agent"]
    with HHS148Service(system["db"]) as service:
        result = service.external_execute(identity, grant, token, ["semantic", "analyze", "--expression", "O≠π", "--source-type", "model_output", "--source-reference", "external-restatement"])
        assert result["operation"] == "SEMANTIC_ANALYZE"
        assert result["privileged_semantic_authority"] == 0
        assert result["execution"]["result"]["proposition"]["primary_class"] == "UNRESOLVED_EXPRESSION"
        before = service.db.conn.execute("SELECT COUNT(*) FROM security_boundary_contracts").fetchone()[0]
        with pytest.raises(Pass145Error) as fabricated:
            service.external_execute(identity, grant, token, ["semantic", "analyze", "--expression", "O≠π", "--source-type", "contract", "--source-reference", "fabricated-contract"])
        assert fabricated.value.code == "SEMANTIC_SOURCE_AUTHORITY_UNVERIFIED"
        with pytest.raises(Pass145Error) as exc:
            service.external_execute(identity, grant, token, ["semantic", "promotion-evaluate", "PMR-fake", "--authorize", "--authority", "A3", "--rationale", "self-authorize"])
        after = service.db.conn.execute("SELECT COUNT(*) FROM security_boundary_contracts").fetchone()[0]
        assert exc.value.code == "PRIVILEGED_INTERNAL_ACCESS_PROHIBITED"
        assert after == before


def test_external_agent_cannot_bootstrap_semantic_admin(system):
    with HHS148Service(system["db"]) as service:
        with pytest.raises(Pass145Error) as exc:
            service.create_external_agent(*system["owner"], "Overbroad Semantic Agent", capabilities=["SEMANTIC_AUTHORITY_ADMIN"])
        assert exc.value.code == "PRIVILEGED_INTERNAL_ACCESS_PROHIBITED"


def _request(url: str, token: str | None = None, data: dict | None = None):
    headers = {}
    if token: headers["Authorization"] = f"Bearer {token}"
    raw = None; method = "GET"
    if data is not None:
        raw = json.dumps(data).encode("utf-8"); headers["Content-Type"] = "application/json"; method = "POST"
    req = urllib.request.Request(url, data=raw, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.status, json.loads(response.read())


def test_authenticated_semantic_api_and_external_agent_route(system):
    owner_identity, owner_grant, owner_token = system["owner"]
    server = HHS148SemanticServer(("127.0.0.1", 0), system["db"], token="pass148-api", identity_id=owner_identity, grant_id=owner_grant, identity_token=owner_token)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.raises(urllib.error.HTTPError) as exc: _request(base + "/api/v1/semantic-membrane/audit")
        assert exc.value.code == 401
        status, analyzed = _request(base + "/api/v1/semantic-membrane/analyze", "pass148-api", {"expression": "O≠π", "source_type": "contract", "source_reference": "HHS-P148", "governing_contracts": ["HHS-P148-NSAM"]})
        assert status == 200 and analyzed["proposition"]["primary_class"] == "DECLARED_SYSTEM_LAW"
        aid, gid, tok = system["agent"]
        status, ext = _request(base + "/api/v1/public/agent/execute", "pass148-api", {"identity_id": aid, "grant_id": gid, "identity_token": tok, "argv": ["semantic", "analyze", "--expression", "Δ=1", "--source-type", "model_output", "--source-reference", "api-agent"]})
        assert status == 200
        assert ext["privileged_semantic_authority"] == 0
        assert ext["execution"]["result"]["proposition"]["primary_class"] == "UNRESOLVED_EXPRESSION"
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)


def test_semantic_audit_and_receipt_chain_close(system):
    with HHS148Service(system["db"]) as service:
        audit = service.semantic_audit()
        assert audit["closed"] is True
        assert audit["external_privileged_semantic_authority"] == 0
        receipts = service.db.verify_receipt_chain()
        assert receipts["ok"] is True
        assert receipts["count"] > 0


def test_public_schemas_match_persisted_timestamp_and_derivation_receipt(system):
    with HHS148Service(system["db"]) as service:
        law = analyze(service, "n/Δ=n", source_type="contract", source_reference="SCHEMA_CONFORMANCE")
        assert law["proposition"]["timestamp"]
        derived = service.derive(
            [law["proposition"]["proposition_id"]],
            rule_id="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1",
            substitutions={"n": "Δ"},
        )
        assert derived["derivation"]["receipt"] == derived["receipt"]
        proposition_schema = service.public_registry.schema_describe("pass148-proposition")["definition"]
        derivation_schema = service.public_registry.schema_describe("pass148-derivation")["definition"]
        assert "timestamp" in proposition_schema["required"]
        assert "receipt" in derivation_schema["required"]


def test_pass148_documentation_installs_through_public_boundary(system):
    identity, grant, token = system["owner"]
    with HHS148Service(system["db"]) as service:
        constructed = service.security.construct_path(identity, grant, token, "PUBLIC_DOC_INSTALL", {"classification": "INTERNAL"})
        executed = service.security.execute_path(constructed["result"]["contract_id"], identity, token)
        result = executed["result"]["result"]
        assert result["status"] == "PUBLIC_DOCUMENTATION_INSTALLED"
        assert result["count"] >= 6
        query_path = service.security.construct_path(identity, grant, token, "PUBLIC_DOC_QUERY", {"question": "native semantic authority membrane", "limit": 20, "classification": "INTERNAL"})
        queried = service.security.execute_path(query_path["result"]["contract_id"], identity, token)["result"]["result"]
        evidence = queried.get("answer", {}).get("directly_retrieved_evidence", [])
        assert any("semantic" in item.get("exact_text", "").casefold() for item in evidence)
        assert any(item.get("source_id") in {doc["source_id"] for doc in result["documents"] if doc["name"].startswith("PASS_148")} for item in evidence)
