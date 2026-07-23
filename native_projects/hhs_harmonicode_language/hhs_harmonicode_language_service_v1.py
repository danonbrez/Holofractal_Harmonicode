"""Repository-native Harmonicode language service for Pass 075."""
from __future__ import annotations

from typing import Any, Dict, Mapping

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable

from .hhs_harmonicode_parser_v1 import PARSER_VERSION, normalize_source, parse_source
from .hhs_pass075_contracts_v1 import LANGUAGE_DOCUMENT_SCHEMA, source_commitment
from .hhs_typed_ir_v1 import build_typed_ir, validate_typed_ir

LANGUAGE_SERVICE_VERSION = "HHS_HARMONICODE_LANGUAGE_SERVICE_PASS_075_V1"


class HarmonicodeLanguageService:
    def parse(
        self, source: str, *, document_id: str, ir_id: str, source_ref: str,
        source_kind: str, source_root_hash72: str, parent_ir_ref: str = "",
    ) -> Dict[str, Any]:
        normalized = normalize_source(source)
        commitment = source_commitment(normalized)
        ast = parse_source(normalized)
        document = {
            "schema": LANGUAGE_DOCUMENT_SCHEMA,
            "version": LANGUAGE_SERVICE_VERSION,
            "document_id": document_id,
            "source_ref": source_ref,
            "source_kind": source_kind,
            "source_sha256": commitment["sha256"],
            "source_root_hash72": source_root_hash72 or commitment["product_root_hash72"],
            "normalized_source": normalized,
            "parser_version": PARSER_VERSION,
            "ast": ast,
            "derived_projection_not_canonical_source": True,
            "program_effects_executed": False,
        }
        document["document_root_hash72"] = product_root("pass075_language_document", document)
        typed_ir = build_typed_ir(
            ast,
            ir_id=ir_id,
            source_ref=source_ref,
            source_kind=source_kind,
            source_root_hash72=document["source_root_hash72"],
            source_sha256=document["source_sha256"],
            parent_ir_ref=parent_ir_ref,
        )
        validation = validate_typed_ir(typed_ir, source_text=normalized)
        return stable({"document": document, "typed_ir": typed_ir, "validation": validation})

    def validate(self, typed_ir: Mapping[str, Any], *, source_text: str = "") -> Dict[str, Any]:
        return validate_typed_ir(typed_ir, source_text=source_text)

    def symbols(self, typed_ir: Mapping[str, Any]) -> Dict[str, Any]:
        result = {
            "schema": "HHS_HARMONICODE_SYMBOL_INDEX_V1",
            "ir_id": typed_ir.get("ir_id"),
            "symbols": stable(typed_ir.get("symbol_table", [])),
            "symbol_count": len(typed_ir.get("symbol_table", [])),
            "symbol_identity_preserved": True,
        }
        result["symbol_index_root_hash72"] = product_root("pass075_symbol_index", result)
        return stable(result)
