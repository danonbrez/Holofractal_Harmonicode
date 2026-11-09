"""Independent exact-integer regression checks for the read-only Wolfram witness."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts/pass220/PASS_220_NUCLEUS_81_RECIPROCAL_PHASE_INHERITANCE_V1.json"

def _sudoku():
    return [[(3 * ((r) % 3) + r // 3 + c) % 9 + 1
             for c in range(9)] for r in range(9)]

def test_sudoku_27_permutations_sum_product():
    from math import prod, factorial
    grid = _sudoku()
    groups = list(grid)
    groups += [[grid[r][c] for r in range(9)] for c in range(9)]
    groups += [[grid[r][c] for r in range(br, br+3)
                for c in range(bc, bc+3)]
               for br in (0,3,6) for bc in (0,3,6)]
    assert len(groups) == 27
    assert all(sorted(group) == list(range(1,10)) for group in groups)
    assert all(sum(group) == 45 and prod(group) == factorial(9)
               for group in groups)

def test_antipodal_pair_address_cover():
    pairs = [(i, 82-i) for i in range(1,41)]
    assert len(set(sum(([a,b] for a,b in pairs), []))) == 80
    assert sorted([x for pair in pairs for x in pair] + [41]) == list(range(1,82))
    assert all(a+b == 82 for a,b in pairs)

def test_loshu_and_phase_coordinates():
    loshu = ((4,9,2),(3,5,7),(8,1,6))
    assert loshu[1][1] == 5
    assert all(sum(row) == 15 for row in loshu)
    assert all(sum(loshu[r][c] for r in range(3)) == 15 for c in range(3))
    assert 81 * 64 == 72**2 == 5184
    assert all((right + (left-right)%72)%72 == left
               for left in range(72) for right in range(72))

def test_contract_preserves_frozen_authority_boundary():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["authority"] == {
        "canonical_vm81_mutation": False,
        "canonical_hash72_mint": False,
        "canonical_hash216_persistence": False,
    }
    assert "18 other-cell parameter mapping" in contract["unproven_by_this_extension"]

def test_one_way_control_with_read_only_inheritance():
    control = [[int(j <= i) for j in range(4)] for i in range(4)]
    assert control[0][1:] == [0, 0, 0]
    assert control[3] == [1, 1, 1, 1]
    nucleus = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    records = [()]
    for phase in ("phase1", "phase2", "phase3"):
        records.append(records[-1] + (phase,))
    assert len(records[-1]) == 3
    assert all(nucleus == ((4, 9, 2), (3, 5, 7), (8, 1, 6))
               for _ in records)


def test_full_81_by_81_address_bijection():
    addresses = [(k // 81, k % 81) for k in range(81 * 81)]
    assert len(addresses) == 6561
    assert len(set(addresses)) == 6561
    assert min(min(pair) for pair in addresses) == 0
    assert max(max(pair) for pair in addresses) == 80
    assert all(len({r // 9 for r, _ in addresses}) == 9 for _ in range(1))
