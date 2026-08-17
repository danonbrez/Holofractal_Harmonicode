"""Pass 218 Iteration 2 exact structural grammar compiler.

The compiler consumes the inherited grammar-correction corpus, but promoted
records retain only structural edit evidence. Original ungrammatical and
corrected statements are never stored in the rule set.
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from hashlib import sha256
import csv
import json
from pathlib import Path
import re
from typing import Any

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

PASS218_GRAMMAR_COMPILER_VERSION = "HHS-P218-GRAMMAR-COMPILER-I2-V1"
_TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+|[^\w\s]", re.UNICODE)


def _tokenize(value: str) -> tuple[str, ...]:
    return tuple(_TOKEN_RE.findall(value))


def _token_shape(token: str) -> str:
    if token.isdigit():
        return "NUMBER"
    if re.fullmatch(r"[A-Za-z]+(?:'[A-Za-z]+)?", token):
        return "CONTRACTION" if "'" in token else "WORD"
    if token in {".", ",", ";", ":", "?", "!"}:
        return "PUNCT_" + {
            ".": "PERIOD",
            ",": "COMMA",
            ";": "SEMICOLON",
            ":": "COLON",
            "?": "QUESTION",
            "!": "EXCLAMATION",
        }[token]
    return "PUNCT_OTHER"


def _common_prefix_length(left: str, right: str) -> int:
    count = 0
    for lch, rch in zip(left.casefold(), right.casefold()):
        if lch != rch:
            break
        count += 1
    return count


def _single_replace_kind(left: str, right: str) -> str:
    if left.casefold() == right.casefold():
        return "CASE_NORMALIZATION"
    if ("'" in left) != ("'" in right):
        return "CONTRACTION_FORM_CHANGE"
    shorter = min(len(left), len(right))
    common = _common_prefix_length(left, right)
    if shorter > 1 and common >= shorter - 2:
        return "MORPHOLOGICAL_FORM_CHANGE"
    return "LEXICAL_SUBSTITUTION_SHAPE"


def _boundary_shape(tokens: tuple[str, ...], index: int) -> str:
    if index < 0 or index >= len(tokens):
        return "BOUNDARY"
    return _token_shape(tokens[index])


def _edit_records(source: str, target: str) -> tuple[dict[str, Any], ...]:
    source_tokens = _tokenize(source)
    target_tokens = _tokenize(target)
    matcher = SequenceMatcher(a=source_tokens, b=target_tokens, autojunk=False)
    records: list[dict[str, Any]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        source_span = source_tokens[i1:i2]
        target_span = target_tokens[j1:j2]
        if tag == "replace" and len(source_span) == 1 and len(target_span) == 1:
            edit_kind = _single_replace_kind(source_span[0], target_span[0])
        else:
            edit_kind = {
                "replace": "SPAN_REPLACEMENT",
                "delete": "TOKEN_DELETION",
                "insert": "TOKEN_INSERTION",
            }[tag]
        record = {
            "edit_kind": edit_kind,
            "source_span_length": len(source_span),
            "target_span_length": len(target_span),
            "source_shapes": [_token_shape(token) for token in source_span],
            "target_shapes": [_token_shape(token) for token in target_span],
            "left_context_shape": _boundary_shape(source_tokens, i1 - 1),
            "right_context_shape": _boundary_shape(source_tokens, i2),
        }
        record["edit_signature_hash72"] = hash72_digest(
            {"domain": "HHS-P218-GRAMMAR-EDIT-SIGNATURE-I2-V1"}, record
        )
        records.append(record)
    return tuple(records)


@dataclass(frozen=True)
class GrammarRule:
    error_type: str
    edit_kind: str
    source_span_length: int
    target_span_length: int
    source_shapes: tuple[str, ...]
    target_shapes: tuple[str, ...]
    left_context_shape: str
    right_context_shape: str
    support_count: int
    source_asset_sha256: str
    rule_hash72: str

    def to_record(self) -> dict[str, Any]:
        return {
            "error_type": self.error_type,
            "edit_kind": self.edit_kind,
            "source_span_length": self.source_span_length,
            "target_span_length": self.target_span_length,
            "source_shapes": list(self.source_shapes),
            "target_shapes": list(self.target_shapes),
            "left_context_shape": self.left_context_shape,
            "right_context_shape": self.right_context_shape,
            "support_count": self.support_count,
            "source_asset_sha256": self.source_asset_sha256,
            "rule_hash72": self.rule_hash72,
            "revisable_prior": True,
            "verbatim_examples_retained": False,
        }


@dataclass(frozen=True)
class GrammarRuleSet:
    source_asset_sha256: str
    source_row_count: int
    rules: tuple[GrammarRule, ...]
    compiler_version: str
    rule_set_hash72: str
    validation_hash72: str

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "HHS-P218-GRAMMAR-RULE-SET-I2-V1",
            "compiler_version": self.compiler_version,
            "source_asset_sha256": self.source_asset_sha256,
            "source_row_count": self.source_row_count,
            "rules": [rule.to_record() for rule in self.rules],
            "rule_set_hash72": self.rule_set_hash72,
            "validation_hash72": self.validation_hash72,
            "verbatim_examples_retained": False,
            "authoritative_float_weights": False,
            "rule_semantics": "STRUCTURAL_REVISABLE_PRIOR",
        }


def compile_grammar_rules(
    path: str | Path,
    *,
    compiler_version: str = PASS218_GRAMMAR_COMPILER_VERSION,
) -> GrammarRuleSet:
    grammar_path = Path(path)
    raw = grammar_path.read_bytes()
    asset_sha256 = sha256(raw).hexdigest()
    aggregates: dict[tuple[Any, ...], int] = {}
    row_count = 0

    with grammar_path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            error_type = str(row.get("Error Type", "")).strip()
            source = str(row.get("Ungrammatical Statement", ""))
            target = str(row.get("Standard English", ""))
            if not error_type or not source or not target:
                continue
            row_count += 1
            for edit in _edit_records(source, target):
                key = (
                    error_type,
                    edit["edit_kind"],
                    edit["source_span_length"],
                    edit["target_span_length"],
                    tuple(edit["source_shapes"]),
                    tuple(edit["target_shapes"]),
                    edit["left_context_shape"],
                    edit["right_context_shape"],
                )
                aggregates[key] = aggregates.get(key, 0) + 1

    if row_count == 0:
        raise ValueError("P218_GRAMMAR_SOURCE_EMPTY")
    if not aggregates:
        raise ValueError("P218_GRAMMAR_NO_STRUCTURAL_EDITS")

    rules: list[GrammarRule] = []
    for key in sorted(aggregates, key=lambda item: tuple(str(part) for part in item)):
        (
            error_type,
            edit_kind,
            source_span_length,
            target_span_length,
            source_shapes,
            target_shapes,
            left_context_shape,
            right_context_shape,
        ) = key
        support_count = aggregates[key]
        payload = {
            "schema": "HHS-P218-GRAMMAR-RULE-I2-V1",
            "compiler_version": compiler_version,
            "error_type": error_type,
            "edit_kind": edit_kind,
            "source_span_length": source_span_length,
            "target_span_length": target_span_length,
            "source_shapes": list(source_shapes),
            "target_shapes": list(target_shapes),
            "left_context_shape": left_context_shape,
            "right_context_shape": right_context_shape,
            "support_count": support_count,
            "source_asset_sha256": asset_sha256,
            "verbatim_examples_retained": False,
            "revisable_prior": True,
        }
        rule_hash72 = hash72_digest({"domain": "HHS-P218-GRAMMAR-RULE-I2-V1"}, payload)
        rules.append(
            GrammarRule(
                error_type=error_type,
                edit_kind=edit_kind,
                source_span_length=source_span_length,
                target_span_length=target_span_length,
                source_shapes=tuple(source_shapes),
                target_shapes=tuple(target_shapes),
                left_context_shape=left_context_shape,
                right_context_shape=right_context_shape,
                support_count=support_count,
                source_asset_sha256=asset_sha256,
                rule_hash72=rule_hash72,
            )
        )

    rule_payload = {
        "schema": "HHS-P218-GRAMMAR-RULE-SET-I2-V1",
        "compiler_version": compiler_version,
        "source_asset_sha256": asset_sha256,
        "source_row_count": row_count,
        "rules": [rule.to_record() for rule in rules],
        "verbatim_examples_retained": False,
        "authoritative_float_weights": False,
    }
    rule_set_hash72 = hash72_digest(
        {"domain": "HHS-P218-GRAMMAR-RULE-SET-I2-V1"}, rule_payload
    )
    validation_payload = {
        "schema": "HHS-P218-GRAMMAR-VALIDATION-I2-V1",
        "rule_set_hash72": rule_set_hash72,
        "source_row_count": row_count,
        "rule_count": len(rules),
        "all_rules_nonverbatim": all(
            rule.to_record()["verbatim_examples_retained"] is False for rule in rules
        ),
        "all_support_counts_positive": all(rule.support_count > 0 for rule in rules),
        "authoritative_float_weights": False,
    }
    validation_hash72 = hash72_digest(
        {"domain": "HHS-P218-GRAMMAR-VALIDATION-I2-V1"}, validation_payload
    )
    return GrammarRuleSet(
        source_asset_sha256=asset_sha256,
        source_row_count=row_count,
        rules=tuple(rules),
        compiler_version=compiler_version,
        rule_set_hash72=rule_set_hash72,
        validation_hash72=validation_hash72,
    )
