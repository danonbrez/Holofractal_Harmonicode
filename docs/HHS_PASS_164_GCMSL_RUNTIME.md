# Pass 164 GCMSL runtime guide

## Purpose

Pass 164 maps the inherited Pass 163 VMRC plane into a deterministic cluster-computation surface without multiplying canonical authorities.

```text
VM-thread coordinate: (i,t), 0 <= i < 81, 0 <= t < 64
linear index:         n = 64i + t
phase coordinate:     (a,b) = (floor(n/72), n mod 72)
```

The inverse is:

```text
n = 72a + b
i = floor(n/64)
t = n mod 64
```

## Authority path

```text
cluster candidate
-> CPU or simulated-GPU staging result
-> stable deterministic reduction
-> Δ_VM81 zero-closure gate
-> inherited Pass 163 candidate validation
-> inherited Pass 163 VM81 commit
-> inherited permanent Hash216 index
```

Clusters begin with capability zero. Registering a cluster does not authorize candidate submission. The authority must grant a bounded capability scope first.

## Python example

```python
from hhs_runtime.pass164.gcmsl import GCMSLRuntime

runtime = GCMSLRuntime()
runtime.register_cluster("cluster-a")
runtime.grant_capability("cluster-a", "GCMSL_CANDIDATE_COMPUTE")

operation = runtime.submit_operation(
    cluster_id="cluster-a",
    vm81_position=4,
    thread=7,
    phase=11,
    trit=1,
)

reduction = runtime.reduce(
    [operation["operation"]["operation_id"]],
    required_clusters=["cluster-a"],
)

receipt = runtime.commit(reduction["batch"]["batch_id"])
assert receipt["receipt"]["kernel_authorities"] == 1
```

## API sequence

```text
POST /api/runtime/gcmsl/clusters
POST /api/runtime/gcmsl/clusters/{cluster_id}/capabilities
POST /api/runtime/gcmsl/operations
POST /api/runtime/gcmsl/reduce
POST /api/runtime/gcmsl/commit
GET  /api/runtime/gcmsl/replay
POST /api/runtime/gcmsl/benchmark
```

The reducer rejects physical-arrival-order dependence, duplicate candidates, stale roots, conflicting writes, unpaired reciprocal operations, missing required participants, and unresolved invariant residuals.

## Backend status

The implemented backend comparison is between:

- an exact integer CPU reference backend;
- a deterministic simulated-GPU backend that deliberately completes operations in reverse physical order.

This proves order-independent normalization in the reference runtime. It is not evidence of physical GPU performance or driver-level equivalence.
