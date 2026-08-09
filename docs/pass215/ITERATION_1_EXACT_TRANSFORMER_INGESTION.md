# Pass 215 Iteration 1 — Exact Quantized Transformer Ingestion and Admission Incidence

Pass 215 inherits the full pre-pass foundation, Passes 001–214, the cumulative-main Pass 214 benchmark authority, and the frozen Pass 215 benchmark profile. Iteration 1 begins empirical execution without redefining that instrument.

## Authority boundary

The frozen profile remains byte-for-byte unchanged at Git blob `b458d674a75a4cfc64a32b9203dd693e3603576e`. Its historical `PREDECLARED_BY_PASS214_NOT_YET_AUTHORIZED` field is not rewritten; authorization is supplied by the Pass 214 terminal authority:

- Pass 214 cumulative-main closure commit: `063bcc1426b5bba106e139cb7dba1c540df090df`
- Pass 214 authority root: `c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8`
- frozen Pass 215 profile root: `a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e`
- Pass 213 gate-preservation root: `214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092`

Benchmark authority is promoted. Runtime mutation authority and canonical mutation remain false.

## Iteration 1 measurement

The runtime ingests a deterministic manifest of quantized tensor byte ranges. Canonical metadata forbids floating-point values. Supported layouts in this iteration are packed signed/unsigned 4-bit and 8/16/32-bit integer tensors.

Each tensor is measured independently. Every complete `6,298,560`-byte window is passed through the inherited Pass 212 full-hydration encoder and then decoded immediately. The window is counted only after exact byte reconstruction succeeds.

Admission tiers are:

1. `TIER_1_GENERATOR_SEED_EXACT` — inherited affine generator codec, zero exceptions.
2. `TIER_2_GENERATOR_PLUS_EXCEPTIONS` — inherited affine generator codec plus exact sparse XOR exceptions.
3. `TIER_3_RAW_FALLBACK` — inherited raw fallback or an incomplete hydration tail.

Incomplete tails are never zero padded for incidence measurement. They remain raw fallback. This makes the incidence result conservative for tensors smaller than one full hydration window and prevents synthetic padding from inflating compression.

## Measurements

Evidence records integer-only values for source bytes, tier bytes, admitted bytes, compressed codec payload bytes, physically protected storage bytes, generator-seed units, sparse exception units, raw fallback units, exact incidence fractions, exact physical ratios, per-window roots/receipts, and aggregate Hash216/Hash72 identities.

The physical storage count for complete windows uses Pass 212's parity-protected storage measurement, not merely compressed payload length. Raw incomplete tails are counted at their literal byte size because Iteration 1 does not invent a padded Pass 212 package for them.

## Manifest surface

`HHS_PASS_215_QUANTIZED_TRANSFORMER_MANIFEST_V1` accepts ordered tensor records with:

- tensor name;
- quantized dtype;
- exact shape;
- source path;
- byte offset;
- exact byte length;
- optional SHA-256 source digest.

Paths are resolved under the caller-supplied base directory and traversal outside that root is rejected.

## What Iteration 1 does not claim

Iteration 1 establishes the measurement machinery and validates it against deterministic transformer-shaped controls. It does not yet claim that a real open transformer has been measured, does not claim 50B-on-desktop feasibility, does not replace dense forward execution, and does not yet implement exact nonlinear transformer operators.

Those are subsequent Pass 215 empirical stages. This iteration makes their first measurement—admission incidence—runnable, exact, profile-bound, and fail-closed.
