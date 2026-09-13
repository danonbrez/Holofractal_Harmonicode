from __future__ import annotations

import sys
from pathlib import Path

from hhs_backend.runtime.hhs_pass219_five_lane_bigint_address_v1 import (
    Pass219I11AddressError,
    decode_framed_address,
    frame_native_address,
)
from hhs_runtime.canonical import bigint_to_bytes
from hhs_runtime.palindromic_ecc import (
    PalindromicCarrier,
    decode_palindromic_carrier,
    protect_encrypted_bigint,
)


def validate_native_hex(hex_text: str) -> dict[str, int | str]:
    raw = bytes.fromhex(hex_text.strip())
    assert raw
    assert raw[0] != 0
    assert len(raw) <= 384

    source = int.from_bytes(raw, "big", signed=False)
    assert source > 0
    assert bigint_to_bytes(source) == raw

    protected = protect_encrypted_bigint(source)
    assert protected["status"] == "PALINDROMIC_ECC_BIGINT_RECONSTRUCTION_VERIFIED"
    carrier = PalindromicCarrier.from_bigint(int(protected["carrier_bigint_hex"], 16))
    decoded133 = decode_palindromic_carrier(carrier)
    assert int(decoded133["ciphertext_hex"], 16) == source

    framed = frame_native_address(raw)
    assert framed.source_byte_length == len(raw)
    assert framed.source_bit_length == source.bit_length()
    assert framed.source_hex == hex(source)
    assert framed.pass211_shard_count >= 1
    assert framed.pass211_carrier_byte_length > len(raw)
    assert decode_framed_address(framed.package) == raw

    repeated = frame_native_address(raw)
    assert repeated.to_dict() == framed.to_dict()

    try:
        frame_native_address(b"\x00" + raw)
    except Pass219I11AddressError as exc:
        assert "NONCANONICAL_LEADING_ZERO" in str(exc)
    else:
        raise AssertionError("leading-zero I11 address was not rejected")

    return {
        "address_bytes": len(raw),
        "address_bits": source.bit_length(),
        "pass211_shards": framed.pass211_shard_count,
        "pass211_carrier_bytes": framed.pass211_carrier_byte_length,
        "package_root216": framed.pass211_package_root216,
        "package_receipt_hash72": framed.pass211_package_receipt_hash72,
    }


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/pass219_i11_address.hex")
    receipt = validate_native_hex(path.read_text(encoding="utf-8"))
    print(
        "lane5_i11_pass133_211=PASS "
        f"address_bytes={receipt['address_bytes']} "
        f"address_bits={receipt['address_bits']} "
        f"pass211_shards={receipt['pass211_shards']} "
        f"pass211_carrier_bytes={receipt['pass211_carrier_bytes']} "
        f"package_root216={receipt['package_root216']} "
        f"package_receipt_hash72={receipt['package_receipt_hash72']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
