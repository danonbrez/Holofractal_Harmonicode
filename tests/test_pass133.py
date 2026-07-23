from hashlib import sha256
from pathlib import Path

import pytest

from hhs_runtime.hash72_checkpoint import verify_parent_witness, make_hash72_witness, NativeHash72Ring
from hhs_runtime.sudoku_tensor import derive_diagonal_sudoku, validate_sudoku, pack_topology, unpack_topology, vm81_loshu_order, S9, unrank_permutation
from hhs_runtime.prime_generation import generate_distinct_primes, deterministic_mr64
from hhs_runtime.prime_magic_key_state import build_prime_magic_key_state, run_prime_magic_negative_tests
from hhs_runtime.phase_tensor import build_phase_tensor, run_phase_negative_tests
from hhs_runtime.palindromic_ecc import protect_encrypted_bigint, PalindromicCarrier, decode_palindromic_carrier, run_ecc_stress
from hhs_runtime.semantic_continuity import run_schic_self_test
from hhs_runtime.canonical import CanonicalEncodingError

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT/"parent_checkpoint"/"PASS_132_RELEASE_MANIFEST.json"
PARENT_ROOT=__import__('json').loads(PARENT.read_text())["release_manifest_root_hash72"]
SEED=sha256(b"pass133-tests").digest()


def test_parent_hash72_checkpoint_replays_exactly():
    result=verify_parent_witness(PARENT)
    assert result["ok"] is True
    assert result["alphabet_length"]==72


def test_hash72_ring_reverse_restores_genesis():
    ring=NativeHash72Ring(); before=ring.export()
    ring.rotate(5,17); ring.rotate(71,-29)
    after=ring.reverse().export()
    assert after["positions"]==before["positions"]
    assert after["zero_sum"] is True


def test_diagonal_sudoku_factoradic_round_trip_and_native_order():
    grid=derive_diagonal_sudoku(SEED)
    assert validate_sudoku(grid)["ok"] is True
    packed,_=pack_topology(grid)
    assert packed.bit_length()<=167
    assert unpack_topology(packed)==grid
    assert sorted(vm81_loshu_order())==list(range(81))


def test_factoradic_out_of_range_rejected():
    with pytest.raises(ValueError): unrank_permutation(S9)


def test_prime_generation_distinct_and_exact_width():
    primes,receipts=generate_distinct_primes(SEED,count=9,bits=32,domain="TEST")
    assert len(set(primes))==9
    assert all(p.bit_length()==32 and deterministic_mr64(p) for p in primes)
    assert all(r.sympy_isprime for r in receipts)


def test_prime_magic_key_state_closes_and_negatives_pass():
    result=build_prime_magic_key_state(SEED,prime_bits=32,parent_root=PARENT_ROOT)
    assert result["status"]=="PRIME_MAGIC_SUDOKU_BIGINT_KEY_STATE_VERIFIED"
    assert result["reconstruction"]["delta_key"]==1
    assert run_prime_magic_negative_tests(result)["status"]=="PASS"


def test_phase_tensor_forward_inverse_and_wrong_order_rejected():
    result=build_phase_tensor(SEED,prime_bits=24,parent_root=PARENT_ROOT,trace_all_steps=False)
    assert result["status"]=="PRIME_QUDIT_PHASE_CANCELLATION_KEY_STATE_VERIFIED"
    assert result["reconstruction"]["delta_rec"]==1
    assert result["reconstruction"]["trace_defect"]==0
    assert run_phase_negative_tests(SEED,result,parent_root=PARENT_ROOT,prime_bits=24)["status"]=="PASS"


def test_palindromic_ecc_corrects_single_bit_and_fails_double():
    payload=int.from_bytes(b"HHS exact encrypted BigInt payload","big")
    result=protect_encrypted_bigint(payload)
    assert result["status"]=="PALINDROMIC_ECC_BIGINT_RECONSTRUCTION_VERIFIED"
    carrier=PalindromicCarrier.from_bigint(int(result["carrier_bigint_hex"],16))
    bits=list(carrier.left_bits); bits[7]='1' if bits[7]=='0' else '0'
    corrected=decode_palindromic_carrier(PalindromicCarrier(2,''.join(bits),carrier.center,carrier.right_bits))
    assert int(corrected["ciphertext_hex"],16)==payload
    assert corrected["correction_events"]>=1
    stress=run_ecc_stress(payload,sample_limit=64)
    assert stress["status"]=="PASS"


def test_schic_preserves_declared_intent_and_rejects_invention():
    result=run_schic_self_test(PARENT_ROOT)
    assert result["status"]=="PASS"
    assert result["valid_replay"] is True
    assert result["unauthorized_substitution_detected"] is True
