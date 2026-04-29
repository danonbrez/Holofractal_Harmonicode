"""
HHS Grammar Rule Enforcer v1
============================

Loads a correction table with columns:
- Serial Number
- Error Type
- Ungrammatical Statement
- Standard English

Applies exact and normalized phrase-level corrections before linguistic operator
training. This module is deterministic and does not define a new language model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import csv
import json
import re

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass(frozen=True)
class GrammarRule:
    serial_number: str
    error_type: str
    source_text: str
    target_text: str
    rule_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GrammarCorrection:
    rule_hash72: str
    error_type: str
    before: str
    after: str
    applied: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GrammarEnforcementReceipt:
    input_text: str
    output_text: str
    corrections: List[GrammarCorrection]
    rules_loaded: int
    applied_count: int
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_text": self.input_text,
            "output_text": self.output_text,
            "corrections": [c.to_dict() for c in self.corrections],
            "rules_loaded": self.rules_loaded,
            "applied_count": self.applied_count,
            "receipt_hash72": self.receipt_hash72,
        }


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def load_grammar_rules(csv_path: str | Path) -> List[GrammarRule]:
    path = Path(csv_path)
    rules: List[GrammarRule] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            serial = _norm(row.get("Serial Number", ""))
            error_type = _norm(row.get("Error Type", ""))
            source = _norm(row.get("Ungrammatical Statement", ""))
            target = _norm(row.get("Standard English", ""))
            if not source or not target:
                continue
            h = hash72_digest(("hhs_grammar_rule_v1", serial, error_type, source, target), width=24)
            rules.append(GrammarRule(serial, error_type, source, target, h))
    return rules


def enforce_grammar_rules(text: str, rules: List[GrammarRule]) -> GrammarEnforcementReceipt:
    output = text
    corrections: List[GrammarCorrection] = []
    for rule in rules:
        before = output
        if rule.source_text in output:
            output = output.replace(rule.source_text, rule.target_text)
        elif _norm(output) == rule.source_text:
            output = rule.target_text
        applied = before != output
        if applied:
            corrections.append(GrammarCorrection(rule.rule_hash72, rule.error_type, before, output, True))
    receipt = hash72_digest(("hhs_grammar_enforcement_receipt_v1", text, output, [c.to_dict() for c in corrections], len(rules)), width=24)
    return GrammarEnforcementReceipt(text, output, corrections, len(rules), len(corrections), receipt)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("text")
    args = parser.parse_args()
    rules = load_grammar_rules(args.csv_path)
    receipt = enforce_grammar_rules(args.text, rules)
    print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
