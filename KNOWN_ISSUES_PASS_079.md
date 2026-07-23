# Known Issues — Pass 079

- Pass 079 resolves bounded invocation eligibility but intentionally performs no native dispatch; Pass 080 owns membrane admission and execution interposition.
- The 15 `hhs_vm_*` declarations remain explicitly typed unresolved and unavailable to the opcode registry.
- Input/output contracts remain conservative where the frozen ABI does not prove richer ownership or buffer semantics.
