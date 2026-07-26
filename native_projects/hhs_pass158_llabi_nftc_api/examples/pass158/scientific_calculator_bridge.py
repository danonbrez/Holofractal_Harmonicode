from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Translation:
    original_source: str
    parser_profile: str
    canonical_ast: tuple[tuple[str, str], ...]
    diagnostics: tuple[str, ...]


def translate(source: str, parser_profile: str = "SCIENTIFIC_CALCULATOR") -> Translation:
    diagnostics: list[str] = []
    if source.count("==") > 1:
        diagnostics.append("CHAINED_EQUALITY_REQUIRES_HHS_TOPOLOGY")
    if re.search(r"\d\.\d", source):
        diagnostics.append("IMPLICIT_DECIMAL_APPROXIMATION")
    if "O==Pi" in source or "O=Pi" in source:
        diagnostics.append("PHASE_IDENTITY_VIOLATION")
    lanes = tuple(("EQ_EDGE", lane.strip()) for lane in source.split("==") if lane.strip())
    return Translation(source, parser_profile, lanes, tuple(diagnostics))


if __name__ == "__main__":
    result = translate("A==B==C")
    print(result)
    assert result.original_source == "A==B==C"
    assert "CHAINED_EQUALITY_REQUIRES_HHS_TOPOLOGY" in result.diagnostics
