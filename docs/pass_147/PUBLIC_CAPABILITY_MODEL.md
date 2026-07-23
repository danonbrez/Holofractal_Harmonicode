# Public Capability Model

A public capability contract declares its callable surface, parameters, classification, minimum Pass 146 capabilities, mutation behavior, reversibility class, and Hash72 identity. The registry can be rebuilt deterministically and optionally synchronized into the canonical database. Discovery uses a read-only `PUBLIC_DISCOVER` path. Synchronization uses a separate transactional `PUBLIC_REGISTRY_SYNC` path.

The capability graph contains only public primitive and boundary-capability nodes. Privileged internal edges are prohibited and audited as zero.
