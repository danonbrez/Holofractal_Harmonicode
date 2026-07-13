# Known Issues — Pass 016

1. Many legacy modules still import `hhs_loshu_phase_embedding_v1.hash72_digest` directly. These are not all immediate bypasses, but they represent a migration frontier.
2. Runtime event/dataflow and persistence surfaces should be audited next for full kernel-witness surfacing.
3. The C `u^72` ring now exists and backs critical surfaces, but Golay parity and Lo Shu tensor projection should be deepened in later kernel passes.
4. Full GUI build/typecheck still depends on installing frontend dependencies outside this ZIP.
