# Known Issues — Pass 080

- Pass 080 validates exact recurrence polynomial residues but does not construct algebraic-number field elements for irrational roots. This is intentional: floating approximations have no authority.
- Pass 080 stops before leased native invocation. Simultaneous native execution receipts and post-state witnessing remain Pass 081 work.
- The fifteen Pass 078.1 typed-unresolved `hhs_vm_*` declarations remain unavailable and are never represented as zero or callable.
