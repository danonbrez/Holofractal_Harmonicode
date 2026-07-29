from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
import re

from hhs_installer.canonical import hash216, stable


@dataclass(frozen=True)
class RequirementClause:
    requirement_id: str
    pass_number: int
    section: str
    line_start: int
    line_end: int
    text: str
    text_hash: str
    normative_terms: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class RequirementScanner:
    NORMATIVE = ("SHALL", "SHALL NOT", "MUST", "MUST NOT", "MAY", "MAY NOT", "REQUIRED")

    def scan(self, path: str | Path, *, pass_number: int) -> tuple[RequirementClause, ...]:
        source = Path(path)
        lines = source.read_text(encoding="utf-8").splitlines()
        clauses: list[RequirementClause] = []
        current_section = "unsectioned"
        buffer: list[str] = []
        start_line = 1

        def flush(end_line: int) -> None:
            nonlocal buffer, start_line
            text = " ".join(part.strip() for part in buffer if part.strip()).strip()
            buffer = []
            if not text:
                return
            terms = tuple(term for term in self.NORMATIVE if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE))
            if not terms:
                return
            normalized = re.sub(r"\s+", " ", text)
            text_hash = hash216(normalized, domain=f"HHS-P{pass_number}-REQUIREMENT-TEXT-V1")
            requirement_id = f"P{pass_number}-R-{len(clauses) + 1:04d}-{text_hash[:12]}"
            clauses.append(
                RequirementClause(
                    requirement_id=requirement_id,
                    pass_number=pass_number,
                    section=current_section,
                    line_start=start_line,
                    line_end=end_line,
                    text=normalized,
                    text_hash=text_hash,
                    normative_terms=terms,
                )
            )

        in_code_block = False
        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                flush(line_number - 1)
                in_code_block = not in_code_block
                start_line = line_number + 1
                continue
            if not in_code_block and stripped.startswith("#"):
                flush(line_number - 1)
                current_section = stripped.lstrip("#").strip()
                start_line = line_number + 1
                continue
            if not stripped:
                flush(line_number - 1)
                start_line = line_number + 1
                continue
            if not buffer:
                start_line = line_number
            buffer.append(stripped)
            if stripped.endswith((".", ":", ";")) and not in_code_block:
                flush(line_number)
                start_line = line_number + 1
        flush(len(lines))
        return tuple(clauses)

    def scan_pair(self, pass172: str | Path, pass173: str | Path) -> dict[str, Any]:
        clauses172 = self.scan(pass172, pass_number=172)
        clauses173 = self.scan(pass173, pass_number=173)
        payload = {
            "schema": "HHS_PASS_173_REQUIREMENT_SCAN_V1",
            "pass172": [clause.to_dict() for clause in clauses172],
            "pass173": [clause.to_dict() for clause in clauses173],
            "counts": {"pass172": len(clauses172), "pass173": len(clauses173), "total": len(clauses172) + len(clauses173)},
        }
        payload["scan_identity"] = hash216(payload, domain="HHS-P173-REQUIREMENT-SCAN-V1")
        return payload
