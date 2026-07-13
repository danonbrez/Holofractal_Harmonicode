# Known Issues — Pass 021

## Orphan Candidates Remain

The reachability audit identifies many orphan candidates. This is expected: Pass 021 is an audit pass, not a mass-integration pass.

## Static Analysis Limits

The audit is conservative and static. Dynamic plugin loading, implicit runtime reflection, and external connector routes may require explicit manifest annotations in later passes.

## Next Risk

Some `PLUGIN_READY` candidates may be true core modules that should become guarded services. Others may be experimental modules that should be documented-only or deprecated.
