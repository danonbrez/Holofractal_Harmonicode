from hhs_runtime.hhs_pass220_ordered_antipodal_phase72_v1 import (
    phase72_transport_witness, SOURCE_TERMINAL, SOURCE_ORIENTATION,
)
from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import Phase72

def test_antipodal_full_cycle():
    assert Phase72(-36) == Phase72(36)
    assert Phase72(-36) * Phase72(-36) == Phase72(0)
    assert Phase72(72) == Phase72(0)
    assert Phase72(35) != Phase72(0)
    assert Phase72(71) != Phase72(0)

def test_sectors_complete_bijective():
    witness = phase72_transport_witness()
    groups = witness["sectors_mod6"]
    assert len(groups) == 6
    assert all(len(s) == 12 for s in groups)
    assert len(set(v for sector in groups for v in sector)) == 72
    assert all(all(k % 6 == idx for k in sector) for idx,sector in enumerate(groups))

def test_ordered_channels_survive_without_scalar_commutation():
    witness = phase72_transport_witness()
    assert witness["ordered_terminal_source"] == SOURCE_TERMINAL
    assert witness["ordered_orientation_source"] == SOURCE_ORIENTATION
    assert witness["ordered_channel_pairs"] == (("xy","yx"),("AB","BA"))
    assert witness["denominator_constraint"] == "Delta=1"
    assert witness["native_terminal_closure_proven"] is False
    assert witness["e6_octonion_map_proven"] is False
    assert all(witness[field] is False for field in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_mint_authority",
        "canonical_hash216_persistence_authority",
    ))
    assert len(witness["candidate_receipt_sha256"]) == 64
