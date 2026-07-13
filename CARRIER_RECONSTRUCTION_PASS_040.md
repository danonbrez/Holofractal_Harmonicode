# Pass 040 — Carrier Reconstruction and Validation Residue Compression

Pass 040 closes the carrier read/write/reconstruction layer and prevents validation expansion residue from becoming an accumulating shadow memory artifact.

## Added

```text
hhs_runtime/hhs_validation_residue_compressor_v1.py
hhs_runtime/hhs_hhfs_carrier_adapter_v1.py
hhs_runtime/hhs_hhfs_reconstruction_protocol_v1.py

tests/test_hhs_validation_residue_compressor_v1.py
tests/test_hhs_hhfs_carrier_adapter_v1.py
tests/test_hhs_hhfs_reconstruction_protocol_v1.py

docs/HHS_VALIDATION_RESIDUE_COMPRESSION_PASS_040.md
docs/HHS_CARRIER_RECONSTRUCTION_PROTOCOL_PASS_040.md
docs/HHS_INVARIANT_DERIVED_ADAPTER_EXECUTION_PASS_040.md
```

## Doctrine lock

```text
Validation expansion cache residue must compress into the u^72/Hash72 previous-state-receipt chain.

Carrier read/write/repair is a witnessed transformation surface.

Reconstruction is never silent.
```

## Runtime services

```text
validation_residue_compressor.self_test
hhfs_carrier_adapter.self_test
hhfs_reconstruction_protocol.self_test
```

## Make targets

```text
make validation-residue-compressor
make hhfs-carrier-adapter
make hhfs-reconstruction-protocol
make hhfs-carrier-reconstruction-tests
```
