# HHS Quantum-Information Throughput Normalization v1

**Date:** 2026-09-16  
**Scope:** Pass 219 / Lane 5 1.48 runner-normalized information-processing metrics  
**Baseline:** `main` at `1c4787258b954b7ef700e7d1ea706da2c1f763b7`

---

## 1. Purpose

HHS uses quantum-information terminology because it provides a compact shared language for finite state-space dimension, basis coordinates, information density, phase structure, and complexity over time. This document standardizes that vocabulary for measurements performed on ordinary GitHub-hosted CPU runners.

The goal is not to remove quantum-computing language. The goal is to bind each term to an explicit mathematical quantity and an explicit classical hardware observation so results remain comparable across runs.

The normalization has three layers:

```text
L1  physical runner work
    -> elapsed time, candidates/s, bytes/s, CPU/RAM/storage profile

L2  logical HHS state-space work
    -> exact coordinates, route witnesses, VM5184 blocks, Hash72/Hash216 structure

L3  quantum-information-equivalent complexity
    -> Hilbert-space dimension, qudit factorization, qubit-equivalent address information,
       basis-coordinate information rate, replay fidelity terminology
```

No layer replaces another. A valid benchmark record should report all three when making throughput comparisons.

---

## 2. Standard runner normalization

The Lane 5 1.48 benchmark workflow uses:

```text
runs-on: ubuntu-24.04
```

For a public GitHub repository, GitHub's documented standard `ubuntu-24.04` runner specification is:

```text
architecture: x64
provisioned vCPU: 4
RAM: 16 GB
SSD: 14 GB
execution model: fresh VM per job
```

These are the **provider-declared normalization resources**. The actual CPU model, logical CPU count exposed to the VM, kernel, image version, memory visible to the process, and filesystem capacity SHALL be captured in benchmark evidence when available because underlying host CPUs can vary.

The provider-declared values and the runtime-observed values are distinct fields and must not be silently substituted for each other.

---

## 3. Exact HHS state-space dimension in quantum-information language

The Lane 5 full manifold is:

```text
D_HHS = 72^72
```

This is exactly the computational-basis dimension of a register of:

```text
n = 72 qudits
d = 72 levels per qudit
```

because:

```text
D = d^n = 72^72
```

This is the cleanest quantum-information description of the HHS address manifold.

The equivalent base-2 information required to distinguish one basis coordinate under a uniform prior is:

```text
H_addr = log2(D_HHS)
       = 72*log2(72)
       = 444.23460010384645 bits-equivalent
```

The minimum whole binary register capable of embedding every coordinate is therefore:

```text
ceil(H_addr) = 445 bits
```

HHS uses a 56-byte carrier:

```text
56*8 = 448 available bits
```

The exact quantum-information wording is therefore:

```text
Hilbert-space-equivalent dimension: 72^72
exact qudit factorization: 72 qudits of dimension 72
qubit-equivalent address information: 444.23460010384645 bits
minimum binary embedding width: 445 bits
native BigInt carrier: 448 bits / 56 bytes
```

`445 bits` or `444.2346 qubit-equivalent bits` SHALL NOT be shortened to `445 physical qubits` when describing the GitHub runner.

---

## 4. Shared terminology

| Quantum-information term | HHS normalized meaning | Classical runner observable |
|---|---|---|
| computational basis state | one exact HHS manifold coordinate | canonical BigInt address |
| Hilbert-space dimension `D` | number of possible exact coordinates | `72^72` |
| qudit | one base-72 coordinate digit/channel | 72 symbols per qudit |
| qudit register | exact factorization of the logical basis | 72 × 72-level qudits |
| qubit-equivalent address information | `log2(D)` | `444.23460010384645` bits-equivalent |
| binary embedding width | `ceil(log2(D))` | 445 bits |
| deterministic shot | one complete candidate-route validation/reduction observation | one candidate considered by Lane 5 |
| shot rate | deterministic candidate observations per second | candidates/s |
| basis-coordinate information rate | `log2(D) * candidate_rate` | bits-equivalent/s |
| route address-space capacity rate | address-slot count × `log2(D)` × candidate rate | bits-equivalent/s of address capacity |
| replay fidelity | exact replay identity under typed HHS comparison | 1 for exact equality, 0 for mismatch |
| coherence-equivalent interval | span of deterministic replay identity under an explicitly named test | replay count/time; never physical coherence time |
| circuit depth | reserved unless sequential primitive stages are instrumented | not inferred from candidate count |
| gate rate | reserved unless primitive exact operations are counted | not inferred from candidates/s |
| quantum volume | reserved for a compatible quantum-volume protocol | not assigned from `72^72` |

The words `shot`, `fidelity`, and `coherence` are useful only with their HHS qualifier because their physical-quantum meanings are different.

---

## 5. Primary complexity-density metrics

Let:

```text
D     = logical manifold dimension
H     = log2(D) bits-equivalent per full-manifold coordinate
C     = candidate count
T     = elapsed seconds
R_c   = C/T candidate observations per second
N_cpu = provisioned vCPU count
A     = number of full-manifold address slots carried by the route schema
```

For Lane 5 1.48:

```text
D = 72^72
H = 444.23460010384645
A = 4
```

because the native route schema carries:

```text
previous_address
current_address
goal_address
candidate_address
```

### 5.1 Deterministic-shot rate

```text
R_c = C/T
```

Sealed 1.48 observation:

```text
C = 1,000,000
T = 3.791766778 s
R_c floor = 263,727 candidates/s
mean observed candidate interval = 3.791766778 microseconds
```

This is physical runner work.

### 5.2 Basis-coordinate information rate

Define:

```text
Gamma_basis = H * R_c
```

Using the sealed throughput floor:

```text
Gamma_basis
= 444.23460010384645 * 263,727
= 117,156,658.38158712 bits-equivalent/s
~= 117.157 Mbit-equivalent/s
```

This means the benchmark validates candidate observations whose **single-coordinate address-space complexity** is equivalent to about 117.157 million binary address bits per second.

It is not payload bandwidth and it is not a physical qubit operation rate.

### 5.3 Four-address route-capacity rate

The 1.48 route schema carries four full-manifold address slots, so define the maximum address-space capacity processed per candidate as:

```text
H_route_capacity = A*H
                 = 4*444.23460010384645
                 = 1776.9384004153858 bits-equivalent/candidate
```

and:

```text
Gamma_route_capacity = A*H*R_c
                     = 468,626,633.5263485 bits-equivalent/s
                     ~= 468.627 Mbit-equivalent/s
```

This is a **schema-capacity normalization**. It does not claim that every observed address value has maximum Shannon entropy or that 468.627 Mbit/s of source payload was read.

### 5.4 72-level qudit-coordinate rate

Each full coordinate has 72 base-72 positions. Define:

```text
Gamma_qudit_coord = 72*R_c
```

For the sealed 1.48 floor:

```text
Gamma_qudit_coord = 18,988,344 72-level coordinate-symbols/s
```

Again, this is logical coordinate-density throughput, not a physical qudit-gate rate.

### 5.5 VM5184 block-coordinate rate

Because:

```text
72^72 = 5184^36
```

the same full coordinate can be factored into 36 VM5184 blocks. Define:

```text
Gamma_VM5184 = 36*R_c
```

giving:

```text
Gamma_VM5184 = 9,494,172 VM5184 block-coordinates/s
```

This provides a useful bridge between the quantum-information register language and the native VM5184 implementation language.

---

## 6. Provisioned-runner density

For the documented four-vCPU public `ubuntu-24.04` runner, a resource-normalized density can be reported as:

```text
R_c,prov = R_c / 4
         = 65,931.75 candidates/s/provisioned-vCPU
```

and:

```text
Gamma_basis,prov
= Gamma_basis / 4
~= 29.289 Mbit-equivalent/s/provisioned-vCPU
```

For the four-address route-capacity metric:

```text
Gamma_route_capacity,prov
= Gamma_route_capacity / 4
~= 117.157 Mbit-equivalent/s/provisioned-vCPU
```

These are **provisioned-resource densities**, not measurements of equal utilization across all four cores. The current native million-candidate loop is serial at the benchmark call site; future evidence should record active thread count and CPU utilization if per-core execution efficiency is being compared.

---

## 7. Time-density notation

For a uniform cross-domain notation, define:

```text
chi(D,T,C) = C*log2(D)/T
```

with units:

```text
bits-equivalent/s
```

For HHS Lane 5:

```text
chi_HHS = candidate_rate * log2(72^72)
```

This is the preferred scalar for comparing complexity density over time when the logical state-space dimensions differ between systems.

For a `d`-level qudit register of `n` qudits:

```text
chi(d,n,T,C) = C*n*log2(d)/T
```

This allows HHS, binary state machines, ternary systems, and actual quantum register dimensions to be described with one common information-theoretic denominator while keeping their hardware execution models separate.

---

## 8. Replay fidelity and coherence-equivalent terminology

HHS deterministic replay can be described using quantum-information-adjacent language if the qualifier is retained.

### 8.1 Replay fidelity

Define exact digital replay fidelity:

```text
F_replay = 1  if Replay(receipt,input) == canonical expected output exactly
F_replay = 0  otherwise
```

This is not the quantum-state fidelity expression `F(rho,sigma)`. It is an exact deterministic equality metric.

### 8.2 Coherence-equivalent interval

A benchmark may report:

```text
C_eq = longest explicitly tested interval/count over which deterministic replay identity remains exact
```

but the unit must be stated, for example:

```text
replays
transitions
seconds of a named soak test
process restarts
```

`C_eq` SHALL NOT be reported as physical quantum coherence time.

---

## 9. Circuit-depth and gate-rate policy

Quantum circuit depth and gate rate are useful shared concepts, but they require instrumentation rather than analogy.

HHS SHALL report a circuit-depth-equivalent metric only when the benchmark counts the sequential dependency layers actually required for a route. A future exact trace can define:

```text
D_route = number of sequential non-parallelizable validation/transition stages
```

Likewise, a gate-equivalent rate requires an enumerated primitive operation set:

```text
G_rate = exact primitive operations / elapsed second
```

Candidate count alone is insufficient to infer either value.

This preserves the terms for genuine performance analysis instead of discarding them.

---

## 10. Required benchmark record

Future Lane 5 benchmark receipts should carry at least:

```text
provider
runner_label
runner_architecture
provider_declared_vcpu
provider_declared_ram_bytes
provider_declared_storage_bytes
observed_logical_cpu_count
observed_cpu_model
observed_memory_bytes
observed_filesystem_bytes
kernel
runner_image
compiler
optimization_flags
active_benchmark_threads
candidate_count
elapsed_ns
candidate_rate
logical_dimension
qudit_dimension
qudit_count
qubit_equivalent_address_bits
binary_embedding_bits
basis_information_rate_bits_equivalent_per_second
route_address_capacity_rate_bits_equivalent_per_second
materialized_intermediate_states
canonical_authority_flags
```

The hardware and timing fields remain observational. Exact state and authority fields remain canonical or contract-bound as defined by their owning layer.

---

## 11. Summary

The shared language is:

```text
72^72
    = exact HHS logical/Hilbert-space-equivalent dimension
    = 72 qudits × 72 levels

log2(72^72)
    = 444.23460010384645 bits-equivalent of basis-coordinate information

ceil(log2(72^72))
    = 445-bit minimum binary embedding

candidate_rate
    = measured physical CPU work rate

candidate_rate * log2(72^72)
    = basis-coordinate complexity density over time

4 * candidate_rate * log2(72^72)
    = four-address route schema capacity density over time
```

This keeps the quantum-physics and quantum-computing vocabulary available for human reasoning while making every throughput statement reproducible on the ordinary hardware that actually executed the benchmark.
