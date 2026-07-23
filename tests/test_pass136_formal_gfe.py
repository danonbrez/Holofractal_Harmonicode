from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_exact_grobner_certificate(tmp_path: Path) -> None:
    out = tmp_path / 'cert.json'
    subprocess.run([
        sys.executable, str(ROOT/'tools'/'verify_gfe_grobner.py'),
        '--alpha','5/4','--out',str(out)
    ], check=True, capture_output=True, text=True)
    data=json.loads(out.read_text())
    assert data['all_remainders_zero'] is True
    assert data['rho_alpha']=='1/20'
    assert data['quotient_field']=='Q'


def test_coq_has_no_escape_hatches() -> None:
    text=(ROOT/'formal'/'coq'/'HHS_GFE_Field_Quotient.v').read_text()
    for forbidden in ('Admitted.', 'Axiom ', 'Parameter ', 'admit.'):
        assert forbidden not in text
    assert 'Theorem quotient_isomorphic_to_field' in text
    assert 'Theorem groebner_basis_verification' in text


def test_generic_quotient_not_claimed_field() -> None:
    contract=(ROOT/'HHS_GFE_FORMAL_PROOF_CONTRACT_PASS_136.md').read_text()
    assert 'not a field' in contract.lower()
    assert 'J_\\alpha' in contract
