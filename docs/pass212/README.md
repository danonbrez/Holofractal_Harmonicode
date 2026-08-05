# Pass 212 Runtime

Pass 212 makes the complete HHS hydration—not one local 5,184-bit leaf—the compression and recovery authority.

## Exact scale

- full hydration: `50,388,480 bits` / `6,298,560 bytes`;
- local HFC leaves: `9,720`;
- local leaf: `5,184 bits` / `648 bytes`;
- strict affine seed: `19,440 bits` / `2,430 bytes`;
- raw physical layout: `9,720` data shards plus `80` parity shards.

## Runtime use

```python
from hhs_backend.runtime.hhs_pass212_full_hydration_recovery_v1 import (
    FullHydrationRecoveryRuntime,
    generate_affine_hydration,
)

runtime = FullHydrationRecoveryRuntime()
state = generate_affine_hydration(seed_bytes)  # seed_bytes is exactly 2,430 bytes
package = runtime.encode(state)

degraded = runtime.without_shards(package, ["0:data:0", "0:data:1"])
recovered_state = runtime.decode(degraded)
assert recovered_state == state
```

The same runtime accepts arbitrary 6,298,560-byte states. When the strict descriptor is not smaller, it chooses raw packed fallback and still applies physical parity recovery.

## API

- `GET /api/runtime/full-hydration-recovery/status`
- `POST /api/runtime/full-hydration-recovery/encode-affine`
- `POST /api/runtime/full-hydration-recovery/recover`

Pass 201 API federation discovers and registers the route module before the visual static mount.
