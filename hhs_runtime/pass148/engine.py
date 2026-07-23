from __future__ import annotations

from typing import Any, Mapping

from hhs_runtime.pass145.canonical import hash72
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass146 import engine as parent_engine
from hhs_runtime.pass147.engine import HHS147BoundaryEngine
from .registry import SEMANTIC_REGISTRY_VERSION, full_registry

# Additive vocabulary. Import occurs before fresh Pass 146 owner bootstrap, so a
# new root grant receives the complete Pass 148 authority graph. Existing grants
# are never silently expanded.
parent_engine.CAPABILITIES.update({
    "SEMANTIC_READ", "SEMANTIC_ANALYZE", "SEMANTIC_DERIVE", "SEMANTIC_PROJECT",
    "SEMANTIC_PROMOTION_REQUEST", "SEMANTIC_AUTHORITY_ADMIN",
})
parent_engine.OPERATION_SPECS.update({
    "SEMANTIC_ANALYZE": {"capabilities": ["SEMANTIC_ANALYZE", "SEMANTIC_READ", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["ORDERED_AST_PARSER", "NATIVE_SEMANTIC_REGISTRY", "CONTAMINATION_DETECTOR", "SEMANTIC_DATABASE"], "mutating": True},
    "SEMANTIC_DOCUMENT_ANALYZE": {"capabilities": ["SEMANTIC_ANALYZE", "SEMANTIC_READ", "INGEST", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "CHECKPOINT_REVERSIBLE", "components": ["DOCUMENT_SEGMENTER", "ORDERED_AST_PARSER", "NARRATIVE_BOUNDARY", "SEMANTIC_DATABASE"], "mutating": True},
    "SEMANTIC_DERIVE": {"capabilities": ["SEMANTIC_DERIVE", "SEMANTIC_READ", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["DERIVATION_RULE_ENGINE", "NATIVE_SEMANTIC_REGISTRY", "SEMANTIC_DATABASE"], "mutating": True},
    "SEMANTIC_PROJECT": {"capabilities": ["SEMANTIC_PROJECT", "SEMANTIC_READ", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["CONTROL_PROJECTION_ENGINE", "PROFILE_ISOLATOR", "SEMANTIC_DATABASE"], "mutating": True},
    "SEMANTIC_PROMOTION_REQUEST": {"capabilities": ["SEMANTIC_PROMOTION_REQUEST", "SEMANTIC_READ", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["PROMOTION_REQUEST_GATE", "SEMANTIC_DATABASE"], "mutating": True},
    "SEMANTIC_PROMOTION_EVALUATE": {"capabilities": ["SEMANTIC_AUTHORITY_ADMIN", "SEMANTIC_READ", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["PROMOTION_AUTHORITY_GATE", "DERIVATION_VERIFIER", "SEMANTIC_DATABASE"], "mutating": True},
    "SEMANTIC_RETRIEVE": {"capabilities": ["SEMANTIC_READ", "DATABASE_READ", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["SEMANTIC_DATABASE"], "mutating": False},
    "SEMANTIC_RULE_READ": {"capabilities": ["SEMANTIC_READ", "DATABASE_READ", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["NATIVE_SEMANTIC_REGISTRY"], "mutating": False},
    "SEMANTIC_REPLAY": {"capabilities": ["SEMANTIC_READ", "VALIDATE", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["SEMANTIC_REPLAY_ENGINE", "SEMANTIC_DATABASE"], "mutating": True},
    "SEMANTIC_AUDIT": {"capabilities": ["SEMANTIC_READ", "DATABASE_READ", "VALIDATE", "PATH_EXECUTION"], "reversibility": "APPEND_ONLY_NONDESTRUCTIVE", "components": ["SEMANTIC_AUDITOR", "NATIVE_SEMANTIC_REGISTRY"], "mutating": False},
    "SEMANTIC_REGISTRY_SYNC": {"capabilities": ["SEMANTIC_AUTHORITY_ADMIN", "DATABASE_WRITE", "PATH_EXECUTION"], "reversibility": "TRANSACTIONALLY_REVERSIBLE", "components": ["NATIVE_SEMANTIC_REGISTRY", "SEMANTIC_DATABASE"], "mutating": True},
})


class HHS148BoundaryEngine(HHS147BoundaryEngine):
    _SEMANTIC_OPS = {name for name in parent_engine.OPERATION_SPECS if name.startswith("SEMANTIC_")}

    def _target_scope_value(self, operation: str, request: Mapping[str, Any]) -> str:
        if operation in self._SEMANTIC_OPS:
            if operation in {"SEMANTIC_RETRIEVE", "SEMANTIC_REPLAY", "SEMANTIC_PROMOTION_REQUEST", "SEMANTIC_PROMOTION_EVALUATE"}:
                return str(request.get("target_id") or request.get("proposition_id") or request.get("promotion_request_id") or "SEMANTIC_STATE")
            return "SEMANTIC_MEMBRANE"
        return super()._target_scope_value(operation, request)

    def _relevant_state_root(self, identity: Mapping[str, Any], grant: Mapping[str, Any], operation: str, request: Mapping[str, Any]) -> str:
        if operation in self._SEMANTIC_OPS:
            target: Any = None
            target_id = request.get("target_id") or request.get("proposition_id") or request.get("promotion_request_id")
            if target_id:
                for table, key in (("semantic_propositions", "proposition_id"), ("semantic_derivations", "derivation_id"), ("semantic_projections", "projection_id"), ("semantic_promotion_requests", "promotion_request_id")):
                    row = self.db.conn.execute(f"SELECT * FROM {table} WHERE {key}=?", (target_id,)).fetchone()
                    if row:
                        target = {k: row[k] for k in row.keys() if not k.endswith("_json") and k != "created_at"}; break
            relevant = {"registry_hash72": full_registry()["registry_hash72"], "registry_version": SEMANTIC_REGISTRY_VERSION, "target": target, "request_hash72": hash72("hhs_pass148_semantic_request_v1", dict(request))}
            return hash72("hhs_pass148_semantic_relevant_state_v1", {"identity": {"identity_id": identity["identity_id"], "identity_hash72": identity["identity_hash72"], "active": identity["active"]}, "grant": {"grant_id": grant["grant_id"], "grant_hash72": grant["grant_hash72"], "revoked": grant["revoked"]}, "operation": operation, "relevant": relevant})
        return super()._relevant_state_root(identity, grant, operation, request)

    def _dispatch(self, contract: Mapping[str, Any], *, identity_token: str | None = None) -> tuple[Any, dict[str, Any]]:
        operation = str(contract["operation"]); request = dict(contract["request"])
        if operation == "SEMANTIC_ANALYZE":
            return self.service.analyze(str(request["expression"]), source_type=str(request.get("source_type", "model_output")), source_reference=str(request.get("source_reference", "PUBLIC_SUBMISSION")), profile_id=str(request.get("profile_id", "HHS_NATIVE_TYPED_V1")), declared_scope=dict(request.get("declared_scope", {})), governing_contracts=[str(x) for x in request.get("governing_contracts", [])]), {}
        if operation == "SEMANTIC_DOCUMENT_ANALYZE":
            return self.service.analyze_document(str(request["text"]), name=str(request.get("name", "semantic-document.md")), source_type=str(request.get("source_type", "documentation")), source_reference=str(request.get("source_reference", "PUBLIC_DOCUMENT")), profile_id=str(request.get("profile_id", "HHS_NATIVE_TYPED_V1")), governing_contracts=[str(x) for x in request.get("governing_contracts", [])]), {}
        if operation == "SEMANTIC_DERIVE":
            return self.service.derive([str(x) for x in request.get("proposition_ids", [])], rule_id=str(request["rule_id"]), substitutions=dict(request.get("substitutions", {}))), {}
        if operation == "SEMANTIC_PROJECT":
            return self.service.project(str(request["expression"]), profile_id=str(request["profile_id"]), assumptions=[str(x) for x in request.get("assumptions", [])]), {}
        if operation == "SEMANTIC_PROMOTION_REQUEST":
            return self.service.request_promotion(str(request["proposition_id"]), str(request["target_class"]), governing_rule=str(request.get("governing_rule", "")), dependency_set=[str(x) for x in request.get("dependency_set", [])], scope=dict(request.get("scope", {})), requested_by_identity=str(contract["identity_id"])), {}
        if operation == "SEMANTIC_PROMOTION_EVALUATE":
            return self.service.evaluate_promotion(str(request["promotion_request_id"]), verifier_identity=str(contract["identity_id"]), authority_level=str(request.get("authority_level", "A3")), authorize=bool(request.get("authorize", False)), rationale=str(request.get("rationale", ""))), {}
        if operation == "SEMANTIC_RETRIEVE":
            kind = str(request.get("kind", "proposition"))
            if kind == "proposition": return self.service.get_proposition(str(request["target_id"])), {}
            if kind == "derivation": return self.service.get_derivation(str(request["target_id"])), {}
            raise Pass145Error("SEMANTIC_RETRIEVE_KIND_INVALID", f"unsupported semantic record kind: {kind}", "SEMANTIC_RETRIEVE")
        if operation == "SEMANTIC_RULE_READ":
            return self.service.get_rule_record(str(request["rule_id"])), {}
        if operation == "SEMANTIC_REPLAY":
            return self.service.replay_semantic(str(request["target_id"])), {}
        if operation == "SEMANTIC_AUDIT":
            return self.service.semantic_audit(), {}
        if operation == "SEMANTIC_REGISTRY_SYNC":
            return self.service.sync_semantic_registry(), {}
        if operation == "PUBLIC_DOC_INSTALL":
            from hhs_runtime.pass147.docs import PUBLIC_DOCUMENTS
            from .docs import PASS148_PUBLIC_DOCUMENTS
            return self.service.install_public_docs([*PUBLIC_DOCUMENTS, *PASS148_PUBLIC_DOCUMENTS]), {}
        return super()._dispatch(contract, identity_token=identity_token)
