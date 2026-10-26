"""Pass220 ingress/egress transcription membrane over inherited 5184 addresses.

Candidate adapter only: canonical VM81 admission and Hash216 identity are
provided by the existing native RNA/C kernel, never minted here.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Callable

WIDTH = 5184
SLOTS = ("p", "pP", "pq", "P", "Pp", "Pq", "q", "qp")


def _bigint(text: str) -> int:
    if not isinstance(text, str) or not text or text.startswith("+"):
        raise ValueError("NONCANONICAL_BIGINT")
    try:
        value = int(text, 10)
    except (TypeError, ValueError) as exc:
        raise ValueError("NONCANONICAL_BIGINT") from exc
    if str(value) != text or not text.isascii():
        raise ValueError("NONCANONICAL_BIGINT")
    return value


def transcribe_candidate(
    p_serialized: str, *, index5184: int,
    encode: Callable[[bytes], bytes], decode: Callable[[bytes], bytes],
) -> dict:
    """Derive typed address/operand metadata and prove external byte fidelity.

    Does not equate ordered pP/Pp, evaluate native slash, or claim signed closure.
    """
    p_value = _bigint(p_serialized)
    if type(index5184) is not int or not 0 <= index5184 < WIDTH:
        raise ValueError("ADDRESS_OUT_OF_RANGE")
    if not callable(encode) or not callable(decode):
        raise ValueError("TRANSCODER_REQUIRED")
    original = p_serialized.encode("ascii")
    encoded = encode(original)
    if not isinstance(encoded, bytes):
        raise ValueError("ENCODE_BYTES_REQUIRED")
    recovered = decode(encoded)
    if not isinstance(recovered, bytes) or recovered != original:
        raise ValueError("TRANSCRIPTION_NOT_REVERSIBLE")
    _bigint(recovered.decode("ascii"))
    slot_values = (str(p_value-1), "pP", "pq", p_serialized,
                   "Pp", "Pq", str(p_value+1), "qp")
    # Exact integer-window projection is derived locally, without evaluating
    # the native rank-1 slash operator or commuting ordered products.
    window = {"p": str(p_value - 1), "P": p_serialized,
              "q": str(p_value + 1), "difference_of_squares": "1"}
    proof_payload = {
        "schema": "HHS_PASS220_BIGINT_WINDOW_ADDRESS_PROOF_V1",
        "index5184": index5184, "window": window,
        "ordered_slots": list(SLOTS),
        "native_gate_source": "P²-(q=P+1)(p=P-1)==P²((p+q)/P(p-q))-(pq)",
        "native_slash_is_rank1": True,
    }
    window_proof_digest = sha256(json.dumps(
        proof_payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    return {
        "window_proof": proof_payload,
        "window_proof_sha256": window_proof_digest,
        "schema": "HHS_PASS220_TRANSCRIPTION_HYDRATION_MEMBRANE_V1",
        "candidate_only": True,
        "state_bigint_decimal": p_serialized,
        "index5184": index5184,
        "cell81": index5184 // 64,
        "operation64": index5184 % 64,
        "hash72_major": index5184 // 72,
        "hash72_minor": index5184 % 72,
        "ordered_register": [
            {"slot": i, "operator": SLOTS[i], "operand": slot_values[i]}
            for i in range(8)
        ],
        "encoded_length": len(encoded),
        "ingress_sha256": sha256(original).hexdigest(),
        "encoded_sha256": sha256(encoded).hexdigest(),
        "egress_sha256": sha256(recovered).hexdigest(),
        "byte_round_trip_verified": True,
        "native_rank1_constraint_proven": False,
        "native_phase_gear_proven": False,
        "signed_hash216_admission_verified": False,
        "canonical_mint_authority": False,
    }


def verify_transcription_candidate(record: dict, *,
                                   encode: Callable[[bytes], bytes],
                                   decode: Callable[[bytes], bytes]) -> dict:
    """Replay native-address candidate derivation; never attest VM81 closure."""
    if not isinstance(record, dict):
        raise ValueError("TRANSCRIPTION_RECORD_REQUIRED")
    replay = transcribe_candidate(record.get("state_bigint_decimal"),
                                  index5184=record.get("index5184"),
                                  encode=encode, decode=decode)
    if replay != record:
        raise ValueError("TRANSCRIPTION_PROOF_REPLAY_MISMATCH")
    return replay
