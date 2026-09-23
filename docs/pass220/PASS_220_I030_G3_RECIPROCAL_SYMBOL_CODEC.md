# Pass 220 I030 — G³ Reciprocal Symbol-String Codec

Date: 2026-09-22

## Scope

I030 formalizes and implements the constructor-level statement that an exact
symbol string can traverse the G³ reciprocal phase surface without losing its
source spelling when ingress and return are the same operation evaluated at
reciprocal phases.

Canonical local definitions:

~~~text
A = ProofCell("123321.111")

Zx = ODiv(OProd(Phase[x], Phase[y], A), Phase[x])
Zy = ODiv(OProd(Phase[y], Phase[x], A), Phase[y])

return phase: y=1/x
~~~

No ordered factor is commuted or cancelled.

## Implemented

- opaque `123321.111` proof-cell token;
- exact 3x3 G³ ordered proof tensor;
- x/y and z/w reciprocal phase involution;
- digit `1..9` scaled proof-cell lifts;
- digit `0` phase-locked forward/return cell;
- UTF-8 exact symbol carrier with forward and reverse byte paths;
- one public reciprocal transform satisfying `T(T(s)) == s` on admitted
  strings;
- preservation of leading zeroes and representation spelling;
- binary and IEEE-like textual representations without numeric parsing;
- SHA-256-bound bounded repair when exactly one redundant byte path survives;
- fail-closed rejection when both paths or symbol provenance are invalid;
- registered read-only service surface;
- Wolfram 17/17 constructor-level proof;
- dedicated white paper and exact-head workflow.

## Wolfram result

~~~text
HHS_PASS_220_I030_G3_RECIPROCAL_SYMBOL_CODEC_WOLFRAM_20260922_V1
PASS
17 / 17
~~~

## Authority

I030 remains read-only. It has no canonical VM81 mutation, Hash72 mint,
Hash216 mint, external persistence, or floating-point authority.

It composes with the inherited I015/I028 proof/runtime surfaces and does not
create a direct bypass around the Lane 5 / RNA / Holo4 / PQC membranes.

## Files

- `hhs_runtime/hhs_pass220_g3_reciprocal_symbol_codec_v1.py`
- `tests/pass220/test_hhs_pass220_g3_reciprocal_symbol_codec_v1.py`
- `hhs_runtime/hhs_service_registry_v1.py`
- `evidence/pass220/i030_g3_reciprocal_symbol_codec_wolfram_20260922_v1.wl`
- `evidence/pass220/i030_g3_reciprocal_symbol_codec_wolfram_20260922_v1.output.json`
- `evidence/pass220/i030_g3_reciprocal_symbol_codec_wolfram_20260922_v1.receipt.json`
- `docs/whitepapers/HARMONICODE_G3_RECIPROCAL_SYMBOL_STRING_CODEC_THEOREM.md`
- `.github/workflows/pass220-i030-g3-reciprocal-symbol-codec.yml`
- restart checkpoint for this cycle.
