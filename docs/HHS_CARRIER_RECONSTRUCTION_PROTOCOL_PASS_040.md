# HHS Carrier Reconstruction Protocol — Pass 040

## Normative purpose

Carrier reconstruction is not a convenience repair path. It is a witnessed transformation surface.

A reconstruction operation must:

1. validate the UDFP frame,
2. verify the HHFS carrier capsule and metadata enhancement block,
3. require bounded ECC if payload repair is claimed,
4. reject silent repair,
5. emit a transformation receipt when reconstruction occurs,
6. compress validation residue into the Hash72 previous-state-receipt chain.

## Reconstruction states

```text
carrier_intact -> RECONSTRUCTION_NOT_REQUIRED
payload_corrupted_ecc_recoverable -> RECONSTRUCTED_WITH_WITNESS
payload_corrupted_ecc_unrecoverable -> WITNESS_INTACT_PAYLOAD_CORRUPTED
witness_corrupted -> RECONSTRUCTION_REJECTED_WITNESS_CORRUPTED
```

## Prohibited behavior

```text
silent repair
duplicate payload storage
repair without transformation receipt
recoverable corruption without ECC root
witness-corrupt reconstruction
```

## Adapter binding

Repair routes through `hhs_hhfs_carrier_adapter_v1` so that reconstruction remains a normal HHS derivation:

```text
carrier frame -> adapter operation -> transformation record -> reconstruction receipt
```
