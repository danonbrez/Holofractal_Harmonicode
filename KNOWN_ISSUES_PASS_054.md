# Known Issues — Pass 054

- Role assignments are deterministic in-process records; durable multi-session lease storage is deferred.
- Independent revalidation is structurally separate but currently executes in the same Runtime process.
- GUI surfaces are source-complete inspection panels; live API binding remains part of the broader GUI integration track.
- Distributed cryptographic identity for remote human or machine role holders is not introduced in this pass.
