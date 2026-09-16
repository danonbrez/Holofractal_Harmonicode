# HHS Quantum-Information Throughput Normalization v1 — Evidence

Date: 2026-09-16  
Status: **EXECUTED / OBSERVATIONAL / RUNNER-NORMALIZED / CANDIDATE-ONLY**

## Delivery identity

```text
normalization implementation PR: #470
substantive validated head: ae44056fb2fab3bec73b5c8dde73f6301b429799
workflow: HHS Quantum Information Throughput Normalization v1
workflow run: 35086761604
workflow conclusion: success
artifact name: hhs-qinfo-throughput-normalization-v1
artifact id: 10441758898
artifact ZIP SHA-256: c4be664dcf3ed3618910b29d105f0e7a7e5a6bfafed6075b62317e06df3b8e09
merged main containing the normalization implementation: ff4ba47de90995d66d529db937288762a64aadd0
```

The validation run executed the implementation before the final restart-record-only branch update. The tested executable/script/workflow surfaces are the same substantive implementation merged by PR #470.

## Runner identity

Provider-declared standard public runner class:

```text
provider: GitHub Actions
runner label: ubuntu-24.04
architecture: x64
provisioned vCPU: 4
provisioned RAM: 16 GB
provisioned SSD: 14 GB
```

Observed by the executed workflow:

```text
runner image: ubuntu-24.04
runner image version: 20260907.300.1
operating system: Ubuntu 24.04.5 LTS
kernel: 6.17.0-1022-azure
platform: Linux-6.17.0-1022-azure-x86_64-with-glibc2.39
Azure region: centralus
observed logical CPUs: 4
observed CPU model: Intel(R) Xeon(R) 6973P-C
observed memory: 16,372,436 KiB
observed filesystem total: 154,894,188,544 bytes
observed filesystem free: 91,802,185,728 bytes
compiler: cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
active benchmark threads at call site: 1
```

The provider-declared 14 GB SSD value is the standardized runner class specification. The observed filesystem total is the filesystem exposed during this particular VM execution and is recorded separately rather than substituted for the provider specification.

## Exact logical state-space normalization

```text
D_HHS = 72^72

D_HHS =
53449019547361999534025300140057538544940601393106611570269540644280818850419033099696863861289188541180498511377339362341642322313216
```

Exact qudit factorization:

```text
D_HHS = d^n

d = 72 levels
n = 72 qudits
```

Qubit-equivalent address information:

```text
H_addr = log2(D_HHS)
       = 444.23460010384649012933840792848557726141327470771727270562838225391814480238763 bits-equivalent
```

Minimum whole binary embedding:

```text
ceil(H_addr) = 445 bits
```

Native exact carrier:

```text
56 bytes = 448 available bits
```

VM5184 factorization:

```text
72^72 = 5184^36
```

## Physical runner observation

The native Lane 5 1.48 million-candidate loop reported:

```text
result: PASS
candidate count: 1,000,000
elapsed: 3,090,640,549 ns
candidate-rate floor: 323,557 candidates/s
mean candidate interval: 3,090.640549 ns
materialized intermediate states: 0
```

The observed rate is runner- and run-specific. It is not a canonical constant.

## Quantum-information-equivalent complexity density

Using the measured floor:

```text
R_c = 323,557 candidates/s
H_addr = 444.23460010384649012933840792848557726141327470771727270562838225391814480238763 bits-equivalent
```

### Basis-coordinate information rate

```text
Gamma_basis = R_c * H_addr

Gamma_basis =
143,735,214.50580025880677834725411700792197109492460487760481500247693099317782613
bits-equivalent/s

~= 143.735 Mbit-equivalent/s
```

### Four-address route-capacity rate

The route schema carries four full-manifold address slots:

```text
previous_address
current_address
goal_address
candidate_address
```

Therefore:

```text
H_route_capacity = 4 * H_addr
                 = 1776.9384004153859605173536317139423090456530988308690908225135290156725792095505
                   bits-equivalent/candidate
```

and:

```text
Gamma_route_capacity = R_c * H_route_capacity

Gamma_route_capacity =
574,940,858.02320103522711338901646803168788437969841951041926000990772397271130453
bits-equivalent/s

~= 574.941 Mbit-equivalent/s
```

This is schema address-space capacity density, not source-payload bandwidth.

### Qudit-coordinate density

```text
Gamma_qudit = 72 * R_c
            = 23,296,104 72-level coordinate-symbols/s
```

### VM5184 block-coordinate density

```text
Gamma_VM5184 = 36 * R_c
             = 11,648,052 VM5184 block-coordinates/s
```

### Provisioned-resource density

For four provisioned vCPUs:

```text
candidate rate / provisioned vCPU
= 80,889.25 candidates/s/provisioned-vCPU

basis-coordinate information rate / provisioned vCPU
= 35,933,803.626450064701694586813529251980492773731151219401203750619232748294456532
  bits-equivalent/s/provisioned-vCPU

~= 35.934 Mbit-equivalent/s/provisioned-vCPU

four-address route-capacity rate / provisioned vCPU
= 143,735,214.50580025880677834725411700792197109492460487760481500247693099317782613
  bits-equivalent/s/provisioned-vCPU

~= 143.735 Mbit-equivalent/s/provisioned-vCPU
```

These are resource-normalized densities, not evidence that all four vCPUs were equally utilized. The benchmark call site was serial and records one active benchmark thread.

## Shared-language interpretation

The following quantum-information terms are active comparative vocabulary:

```text
computational basis state
Hilbert-space dimension
qudit / qudit register
qubit-equivalent address information
deterministic shot / shot rate
replay fidelity
coherence-equivalent interval
circuit depth
gate rate
quantum volume
```

Their use is governed as follows:

- `computational basis`, `Hilbert-space dimension`, `qudit`, and `qubit-equivalent address information` are directly normalized from the exact finite HHS manifold;
- `deterministic shot` denotes one complete candidate-route validation/reduction observation;
- `replay fidelity` denotes exact typed deterministic equality unless an explicitly quantum-state fidelity protocol is being used;
- `coherence-equivalent interval` denotes a named deterministic replay interval and is not physical coherence time;
- `circuit depth` requires instrumentation of sequential non-parallelizable HHS primitive stages;
- `gate rate` requires an enumerated exact primitive operation count;
- `quantum volume` remains reserved for a compatible quantum-volume benchmark protocol.

The standard quantum-physics equations retained by the equation compendium are therefore not discarded. Their `REFERENCE_ONLY` label concerns canonical state authority. They remain part of the shared mathematical vocabulary used to relate state evolution, information density, uncertainty, fidelity, and complexity over time across different computing substrates.

## Authority membrane

The executed normalizer verified:

```text
observational_only = true
physical_quantum_hardware_claim = false
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
requires_signed_environmental_vm81_admission = true
```

Thus the normalization translates measured CPU execution into quantum-information-equivalent complexity language without changing the authoritative VM81 / Hash72 / Hash216 transition path.

## Result

```text
HHS_QINFO_THROUGHPUT_NORMALIZATION_V1_PASS
```
