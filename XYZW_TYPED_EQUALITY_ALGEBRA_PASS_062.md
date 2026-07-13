# xyzw Typed Equality Algebra — Pass 062

The Runtime does not treat every `=` token as a universal identity assertion. It preserves the declared relation frame:

- `IDENTITY_EQ`
- `RELATIONAL_EQ`
- `PHASE_EQ`
- `NORMALIZED_EQ`
- `ALIAS_EQ`
- `CLOSURE_EQ`

Accordingly, normalized statements such as `xy = 1` and `yx = 1` do not erase the oriented relation `xy:yx = 1:-1` or the distinctness of `xy` and `yx`. A contradiction is introduced only by an external assumption that strips the typed equality frame.

The transport constant is retained exactly as `179971179971 / 1000000`; no floating-point authority is used.
