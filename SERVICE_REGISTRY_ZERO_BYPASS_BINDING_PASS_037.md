# Service Registry Zero-Bypass Binding Pass 037

Pass 036 declared `service_registry.dispatch` as a mandatory interposition surface.  Pass 037 binds that declaration to the native dispatch primitive.

## Rule

```text
HHSServiceRegistry.dispatch(...)
-> requires valid service_registry.dispatch interposition token
-> otherwise returns HHS_SERVICE_DISPATCH_REJECTION_RECORD_V1
-> handler is not executed
```

## Accepted Path

```text
interpose_dispatch(service_name, payload)
-> interpose_runtime_surface(surface="service_registry.dispatch")
-> dispatch(..., zero_bypass_interposition_token=token)
-> guarded_surface_propagation(...)
-> service handler execution
-> unified ledger dispatch record
```

## Rejection Paths

```text
direct dispatch without token
-> REJECTED_MISSING_INTERPOSITION_DECISION

dispatch with wrong-surface token
-> REJECTED_SURFACE_TOKEN_MISMATCH
```

This closes the Pass 036 API-only dispatch closure gap by making the lowest-level service registry primitive enforce the same zero-bypass contract.
