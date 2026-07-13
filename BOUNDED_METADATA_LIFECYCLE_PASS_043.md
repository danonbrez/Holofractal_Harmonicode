# Pass 043 — Bounded Metadata Lifecycle

Expanded validation metadata now moves through a declared lifecycle: validated → compacted residue → persisted as root or decayed deletion witness.

- ok: `True`
- persisted mode: `ROOT_PLUS_RECONSTRUCTION_RECIPE_ONLY`
- expanded payload retained in persisted record: `False`
