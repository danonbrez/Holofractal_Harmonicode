# Known Issues — Pass 056

- Federation transport is represented by deterministic Runtime objects; network transport security and peer discovery remain external adapters.
- Remote clock synchronization is modeled by sequence intervals rather than wall-clock consensus.
- Revocation propagation is synchronously witnessed in this pass; asynchronous partition recovery is deferred.
- Cross-domain cryptographic identity exchange remains bounded to admitted witness roots and is not a public-key infrastructure implementation.
