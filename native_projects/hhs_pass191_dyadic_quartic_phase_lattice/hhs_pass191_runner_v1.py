"""Execution shim for the Pass 191 artifact generator.

Keeps the published implementation module stable while correcting the
DYADIC_UNIT nested PHASE_SQUARE arity before authoritative macro execution.
"""

from __future__ import annotations

from native_projects.hhs_pass191_dyadic_quartic_phase_lattice import hhs_pass191_phase_lattice_v1 as implementation


implementation.REQUESTED_MACROS = (
    "DEF DYADIC_UNIT() := PHASE_SQUARE(1,0)==2",
    *implementation.REQUESTED_MACROS[1:],
)


def main() -> int:
    return implementation.main()


if __name__ == "__main__":
    raise SystemExit(main())
