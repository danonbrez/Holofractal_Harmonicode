from __future__ import annotations

import hashlib

import pytest

from hhs_runtime.pass219.lane5_nine_loop_source_attestation_1_68 import (
    Lane5NineLoopSourceAttestationError,
    attest_sample,
    compare_predictions,
    parse_manifest_sample_sha256,
    parse_sample_rows,
)


FIXTURE = """# bounded repository fixture copied from the public Cosmic9 sample format
## NONZERO WORDS
bh bh fh dh dh eh dh fh bh dh fh ah ah fh eh fh dh eh 829521918 1173913588 -105757/65536
bh bh dh fh fh bh fh ah fh dh dh dh eh eh ch dh bh fh 2081161214 222560253 -8445/8192
ah ah eh ah eh fh ah fh dh fh dh fh eh eh dh eh fh fh 1926823936 1457717236 29401/32768
## ZERO WORDS
ch bh yu dh yv yw bh ah ah ch yv yw dh yu eh ch dh dh 0 0 0
ch dh ch eh fh eh ch yw ah eh fh fh eh ah eh ah eh fh 0 0 0
"""


def test_bounded_fixture_reconstructs_exactly():
    rows = parse_sample_rows(FIXTURE)
    assert len(rows) == 5
    assert sum(not row.zero_section for row in rows) == 3
    assert sum(row.zero_section for row in rows) == 2

    digest = hashlib.sha256(FIXTURE.encode()).hexdigest()
    manifest = f"{digest}  samples/E9_sample_coefficients.txt\n"
    receipt = attest_sample(
        FIXTURE.encode(),
        manifest_text=manifest,
        require_full_contract=False,
    )
    assert receipt["manifest_member_verified"] is True
    assert receipt["raw_sha256"] == digest
    assert receipt["nonzero_rows"] == 3
    assert receipt["zero_rows"] == 2
    assert receipt["all_nonzero_rationals_exact"] is True
    assert receipt["all_zero_rows_exact"] is True
    assert receipt["floating_point_authority"] is False
    assert receipt["candidate_only"] is True


def test_manifest_sample_checksum_is_uniquely_selected():
    digest = "a1" * 32
    manifest = (
        ("b2" * 32) + "  amplitude/E9_symbol_complete_mod2147483647.npz\n"
        + digest + "  samples/E9_sample_coefficients.txt\n"
    )
    assert parse_manifest_sample_sha256(manifest) == digest


def test_residue_tamper_fails_closed():
    tampered = FIXTURE.replace("829521918 1173913588", "829521919 1173913588", 1)
    with pytest.raises(Lane5NineLoopSourceAttestationError, match="p1 rational/residue mismatch"):
        parse_sample_rows(tampered)


def test_alphabet_tamper_fails_closed():
    tampered = FIXTURE.replace(
        "bh bh fh dh dh eh dh fh bh dh fh ah ah fh eh fh dh eh",
        "zz bh fh dh dh eh dh fh bh dh fh ah ah fh eh fh dh eh",
        1,
    )
    with pytest.raises(Lane5NineLoopSourceAttestationError, match="alphabet violation"):
        parse_sample_rows(tampered)


def test_zero_section_tamper_fails_closed():
    tampered = FIXTURE.replace(
        "ch bh yu dh yv yw bh ah ah ch yv yw dh yu eh ch dh dh 0 0 0",
        "ch bh yu dh yv yw bh ah ah ch yv yw dh yu eh ch dh dh 1 0 0",
        1,
    )
    with pytest.raises(Lane5NineLoopSourceAttestationError, match="ZERO section"):
        parse_sample_rows(tampered)


def test_manifest_mismatch_fails_closed():
    manifest = ("00" * 32) + "  samples/E9_sample_coefficients.txt\n"
    with pytest.raises(Lane5NineLoopSourceAttestationError, match="MANIFEST"):
        attest_sample(
            FIXTURE.encode(),
            manifest_text=manifest,
            require_full_contract=False,
        )


def test_prediction_deviation_is_parallel_metadata():
    rows = parse_sample_rows(FIXTURE)
    predictions = {
        row.word: (row.residue_p1, row.residue_p2)
        for row in rows
    }
    exact = compare_predictions(rows, predictions)
    assert exact["matched"] == 5
    assert exact["missing"] == 0
    assert exact["mismatched"] == 0
    assert exact["exact_prediction_match"] is True
    assert exact["trinary"] == 0

    predictions.pop(rows[0].word)
    incomplete = compare_predictions(rows, predictions)
    assert incomplete["missing"] == 1
    assert incomplete["exact_prediction_match"] is False
    assert incomplete["trinary"] == -1
