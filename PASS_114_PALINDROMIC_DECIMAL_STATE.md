# Pass 114 — Exact Palindromic Decimal State

Implemented over the real Pass 113 archive surface.

## Runtime service

`runtime.palindromic_decimal_state.pass114`

## Implemented boundary

- canonical Pass 113 archive JSON is encoded byte-for-byte as fixed-width three-digit decimal tokens;
- one fixed forward frame stores magic, version, source byte length, archive root, payload checksum, and payload;
- the mantissa is materialized as `forward.reverse(forward)` with one central `.` separator;
- the coefficient is represented as an arbitrary-precision decimal integer string with exact scale and exponent;
- digit chunks are ordered and individually Hash72-rooted;
- forward and right-to-left recovery independently reconstruct the same Pass 113 archive;
- Pass 113 then recovers and validates the underlying Pass 112 state;
- recovery work, memory, total digits, and chunk size are contract bounded;
- stored authority is revalidated before recovery.

No IEEE floating-point value has canonical authority.
