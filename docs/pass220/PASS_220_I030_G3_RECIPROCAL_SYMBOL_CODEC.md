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


## Nine-character IEEE text windows through the nine-cell phase tensor

The reciprocal symbol encoder is windowed at exactly nine Unicode characters:

~~~text
SYMBOL_WINDOW_WIDTH = 9
~~~

Each complete string window binds its nine characters, in order, to the nine
row-major cells of the existing 3x3 x/y/z/w G3 phase tensor. Every occupied
cell retains both its forward phase expression and reciprocal return expression
simultaneously; no host floating-point arithmetic is required for this symbolic
transport.

Examples such as:

~~~text
1.00e+000
1000.0001
~~~

are each one complete nine-character window. The raw IEEE storage word remains
owned by I031/I032, where the same nine-cell phase tensor carries exact IEEE
bits through the forward/return operation. Thus textual IEEE spelling and raw
IEEE storage are distinct co-resident views, not replacements for one another.

Longer source strings use consecutive non-overlapping nine-character windows.
A final short tail is preserved exactly and records its unused tensor slots;
the codec never pads or invents source characters.

The corrected expanded projection fixture is:

~~~text
1000.0001=(1,0,0,0,0,0,0,0,1)=(-4,-3,-2,-1,0,+1,+2,+3,+4)=(4,9,2,3,5,7,8,1,6)=123321.111+111.123321=246642.246642=369963.369963
~~~

The Lo Shu values are distinct `3,5` cells. The earlier `35` spelling was
a transcription error and is not an admitted fixture.
