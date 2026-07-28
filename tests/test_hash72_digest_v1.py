from hhs_runtime.core.hash72_digest_v1 import (
    hash72_digest,
    projection_receipt_hash72,
    verify_hash72,
    verify_projection_receipt_hash72,
)
from hhs_runtime.core.hash72_validator_v1 import (
    HASH72_ALPHABET,
    validate_closure,
    validate_hash72,
)


def test_phase_closure_repaired():
    receipt = hash72_digest({}, bytes(648))
    assert len(receipt) == 72
    assert validate_closure(receipt)
    assert validate_hash72(receipt)


def test_digest_deterministic_and_domain_sensitive():
    first = hash72_digest({"k": 1}, b"state")
    assert first == hash72_digest({"k": 1}, b"state")
    assert first != hash72_digest({"k": 2}, b"state")
    assert first != hash72_digest({"k": 1}, b"state2")


def test_digest_verification_and_tamper_rejection():
    receipt = hash72_digest({"k": 1}, b"state")
    assert verify_hash72(receipt, {"k": 1}, b"state")
    replacement = HASH72_ALPHABET[
        (HASH72_ALPHABET.index(receipt[0]) + 1) % 72
    ]
    tampered = replacement + receipt[1:]
    assert not verify_hash72(tampered, {"k": 1}, b"state")
    assert not validate_hash72(receipt[:-1])
    assert not validate_hash72("~" + receipt[1:])


def test_projection_receipt_bridge_valid_missing_and_mismatch():
    root = "ab" * 32
    other = "cd" * 32
    receipt = projection_receipt_hash72(root)
    assert verify_projection_receipt_hash72(receipt, root)
    assert not verify_projection_receipt_hash72(receipt, other)
    assert not verify_projection_receipt_hash72("", root)
