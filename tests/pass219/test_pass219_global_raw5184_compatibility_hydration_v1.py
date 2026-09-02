from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from hhs_runtime.hhs_pass219_global_raw5184_serialization_hydration_v1 import (
    RAW_BYTES,
    descriptor,
    hydrate_raw5184_bytes,
    serialize_raw5184_bytes,
    validation_receipt,
)
from hhs_runtime.pass163.vmrc import BASE64_SYMBOLS, VMRCSnapshot
from hhs_runtime.pass166.codec import projection


ROOT = Path(__file__).resolve().parents[2]


def patterned_frame() -> bytes:
    return bytes(((index * 37 + 11) & 0xFF) for index in range(RAW_BYTES))


def test_i150_membrane_preserves_exact_raw5184_bits_and_native_hydration() -> None:
    raw = patterned_frame()
    hydrated = hydrate_raw5184_bytes(raw)
    assert serialize_raw5184_bytes(raw) == raw
    assert len(hydrated.pcm64_bits) == 81
    assert len(hydrated.quads) == 20
    assert len(hydrated.sine_pcm64) == 160

    for quad in hydrated.quads:
        q = quad.stereo_ternary
        by_basis = {channel.basis: channel.phase72 for channel in quad.channels}
        assert q.left_mono_phase72 == (
            by_basis["yx"],
            (by_basis["x"] + by_basis["y"]) % 72,
            by_basis["xy"],
        )
        assert q.right_mono_phase72 == (
            by_basis["wz"],
            (by_basis["z"] + by_basis["w"]) % 72,
            by_basis["zw"],
        )
        assert q.numerator_roles == (-1, 0, 1)
        assert q.denominator_roles == (-1, 0, 1)
        assert q.quotient_identity == (1, 1, 1)
        assert q.center_zero_over_zero_u0_mod_u72 is True
        assert q.center_xy_sum_over_zw_sum_u0 is True
        assert q.scalar_division_attempted is False
        assert q.scalar_projection_runtime_authority is False

    d = descriptor()
    assert d.raw_bits == 5184
    assert d.raw_bytes == 648
    assert d.vm81_cells == 81
    assert d.word_bits == 64
    assert d.exact_bit_identity is True
    assert d.floating_point_authority is False
    assert d.vm81_mutation_authority is False
    assert d.hash72_commit_authority is False
    assert d.hash216_commit_authority is False


def test_vmrc_ingress_egress_and_base64_inherit_i150_hydration() -> None:
    raw = patterned_frame()
    snapshot = VMRCSnapshot(raw)
    assert snapshot.to_bytes() == raw
    encoded = snapshot.base64()
    assert len(encoded) == BASE64_SYMBOLS == 864
    assert VMRCSnapshot.from_base64(encoded).to_bytes() == raw


def test_pass166_direct_projection_is_a_hydrated_raw5184_frame() -> None:
    vector = SimpleNamespace(
        source_token_b64="dGVzdA==",
        canonical_vector_digest="1" * 64,
        canonical_values=(1, -2, 3, -4),
    )
    raw = projection(vector, "2" * 64, ("test", "TEST"))
    assert len(raw) == RAW_BYTES
    assert serialize_raw5184_bytes(raw) == raw
    receipt = validation_receipt(raw)
    assert receipt["exact_bit_identity"] is True
    assert receipt["left_mono"] == ["yx", "x+y", "xy"]
    assert receipt["right_mono"] == ["wz", "z+w", "zw"]
    assert receipt["center_closure"] == "0/0=u^0 mod(u^72)=1"


def test_pass196_active_v2_snapshot_routes_through_i150_and_v1_stays_frozen() -> None:
    historical_v1 = (
        ROOT / "hhs_backend" / "runtime" /
        "hhs_pass196_integrated_environment_v1.py"
    ).read_text(encoding="utf-8")
    assert "serialize_raw5184_bytes" not in historical_v1

    active_v2 = (
        ROOT / "hhs_backend" / "runtime" /
        "hhs_pass196_integrated_environment_v2.py"
    ).read_text(encoding="utf-8")
    assert (
        "from hhs_runtime.hhs_pass219_global_raw5184_serialization_hydration_v1 "
        "import serialize_raw5184_bytes"
    ) in active_v2
    assert "return serialize_raw5184_bytes(_pass196_v1._snapshot(payload))" in active_v2


def test_vmrc_lineage_surfaces_share_the_central_snapshot_serializer() -> None:
    lineage = {
        "pass164": ROOT / "hhs_runtime" / "pass164" / "runtime_base.py",
        "pass165": ROOT / "hhs_runtime" / "pass165" / "ingestion.py",
        "pass174": ROOT / "hhs_runtime" / "pass174" / "runtime.py",
        "pass218_commit": ROOT / "hhs_runtime" / "pass218" / "commit_boundary.py",
        "pass218_persistence": ROOT / "hhs_runtime" / "pass218" / "persistence.py",
    }
    for name, path in lineage.items():
        text = path.read_text(encoding="utf-8")
        assert ".to_bytes()" in text, name

    vmrc = (ROOT / "hhs_runtime" / "pass163" / "vmrc.py").read_text(encoding="utf-8")
    assert "deserialize_raw5184_bytes(candidate)" in vmrc
    assert "serialize_raw5184_bytes(self._raw)" in vmrc


def test_standalone_kernel_serializer_is_private_raw_primitive_only() -> None:
    source = (ROOT / "hhs_runtime" / "HARMONICODE_VM_RUNTIME.c").read_text(
        encoding="utf-8"
    )
    assert "static void vm81_serialize_frame_le" in source
    assert source.count("vm81_serialize_frame_le") == 2
    assert "VM81_FRAME_BYTES" in source
    # The one call is the standalone kernel's internal address/frame self-check.
    assert "vm81_serialize_frame_le(vm, frame);" in source


def test_i150_rejects_non_648_byte_payloads() -> None:
    for size in (0, 647, 649):
        with pytest.raises(ValueError, match="I150_RAW5184_BYTE_COUNT"):
            hydrate_raw5184_bytes(bytes(size))
