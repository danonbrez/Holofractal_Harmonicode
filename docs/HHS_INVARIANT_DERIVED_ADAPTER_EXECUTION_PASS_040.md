# HHS Invariant-Derived Adapter Execution — Pass 040

## Normative purpose

Carrier adapters may not invent behavior locally. They instantiate invariant-preserving transformations derived from Pass 038 and Pass 039:

```text
Pass 038: witnessed continuity / Genesis severance
Pass 039: HHFS/UDFP carrier-compatible witness binding
Pass 040: adapter execution and reconstruction receipts
```

## Adapter classes

Observation operations:

```text
read
observe
verify
extract
```

Mutation operations:

```text
write
embed
repair
reconstruct
convert
```

## Mutation rule

Every mutating adapter operation requires a permanent transformation record.

```text
mutation adapter operation -> transformation record -> adapter receipt
```

Observation operations still emit adapter receipts, but they do not claim payload mutation.

## No parallel lane

Adapters preserve:

```text
legacy compatibility
no parallel storage
no parallel computation
no duplicate payload storage
validation residue compression
```
