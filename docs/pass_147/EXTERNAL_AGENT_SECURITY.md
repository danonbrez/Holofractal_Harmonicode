# External Agent Security

The external agent is a normal authenticated external actor. It may discover and compose public primitives, but it cannot invoke hidden internals. Its default grant supports knowledge, scripts, sandboxes, LVMs, local APIs, validation, and public documentation. Security administration and network propagation require separate explicit authorization and are not included in the default agent grant.

Every agent execution returns the constructed boundary identity, minimum capability set, execution result, and closure state. `privileged_internal_access` is always reported as `0`.
