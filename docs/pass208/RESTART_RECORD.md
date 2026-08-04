# Pass 208 Restart Record

## Scope

Configure the DigitalOcean production deployment to use a physical GPU as a neural-network branch-tree expansion manifold inside the existing VM81/VM5184 kernel bytecode hydration lattice.

The implementation must preserve one VM81 mutation authority, one Hash72 commit stream, exact `s=64c+o` and `q=243s+g` addressing, Pass 207 GPU-versus-CPU equality, parent-bound Hash216 lineage, and the 23-file JSON specification package.

## Base and branch

- Base: authoritative `main` after Pass 207 merge
- Working branch: `agent/pass208-digitalocean-gpu-manifold`
- Merge target: `main`

## Implemented files

- `contracts/pass208/PASS_208_CONTRACT.json`
- `hhs_backend/runtime/hhs_pass208_gpu_branch_manifold_v1.py`
- `hhs_backend/api/pass208_gpu_manifold_routes.py`
- `deployment/digitalocean/gpu/install.sh`
- `deployment/digitalocean/gpu/hhs-gpu-preflight.sh`
- `deployment/digitalocean/gpu/post-merge.sh`
- `deployment/digitalocean/gpu/validate-candidate.sh`
- `deployment/digitalocean/gpu/validate-json-spec-package.py`
- `deployment/digitalocean/gpu/pass208-gpu.env.example`
- `deployment/digitalocean/gpu/README.md`
- `tests/test_hhs_pass208_gpu_branch_manifold_v1.py`
- `tests/test_hhs_pass208_digitalocean_gpu_deployment_v1.py`
- `.github/workflows/pass208-digitalocean-gpu-manifold.yml`
- `docs/pass208/RESTART_RECORD.md`

## Runtime behavior

- A branch expansion shares one committed parent state, parent receipt, and constraint/bytecode root.
- All branch deltas are packed into one Pass 207 SoA/CSR batch.
- Every branch executes through 5,184 stable logical lanes.
- Every physical GPU result must equal the exact CPU VM5184 oracle.
- Stable ranking uses objective distance, branch candidate root, and source ordinal.
- Expansion alone cannot mutate canonical state.
- `expand-and-commit` sends only the selected ordered delta to the existing Pass 205 `advance` path.
- Pass 205 recomputes state, projection, learning, token, receipt, and persistence under singleton VM81 authority.
- The committed content, projection, and dependency roots must equal the selected GPU candidate roots.

## DigitalOcean behavior

The installer requires an actual GPU Droplet. It does not claim that packages can turn a standard CPU Droplet into a GPU host.

Production enablement requires:

- operational `nvidia-smi` or `rocminfo`;
- an OpenCL platform and device visible through `clinfo`;
- a 64-work-item-capable device accepted by the Pass 207 driver;
- a freshly built `libhhs_pass207_gpu_driver.so`;
- `HHS_PASS207_REQUIRE_PHYSICAL_GPU=1`;
- the 23-file JSON package at `HHS_JSON_SPEC_PACKAGE_ROOT`;
- schema, checksum, example, conformance-vector, and domain validation;
- a green systemd `ExecStartPre` receipt.

## JSON package integration

The repository did not contain an indexed copy of the newly created 23-file package when this branch was started. Deployment therefore accepts its exact host path through:

```text
HHS_JSON_SPEC_PACKAGE_ROOT
HHS_JSON_SPEC_MANIFEST
```

The validator expects 23 JSON files and at least four schema-linked example objects. The package must be copied or committed before the production installer can succeed.

## Validation implemented

- strict Python compilation;
- shell syntax for install, preflight, post-merge, and guarded candidate scripts;
- Pass 205 native ABI build;
- Pass 207 native GPU ABI build;
- Pass 207 inherited tests;
- Pass 208 multi-branch expansion and selected-branch VM81 commit equivalence;
- alternate bytecode-lattice root rejection;
- default-disabled behavior;
- synthetic 23-file package validation;
- checksum drift rejection;
- route-surface verification;
- dedicated GitHub workflow.

## Remaining validation

- exact branch GitHub Actions result;
- physical OpenCL execution on the target DigitalOcean GPU Droplet;
- validation against the user's actual 23-file package rather than the synthetic conformance fixture;
- migration or restoration of `/opt/hhs/app`, `/opt/hhs/venv`, `/var/lib/hhs`, nginx, TLS, and DNS onto the GPU Droplet;
- installer execution as root on that host;
- hosted `/api/runtime/gpu-manifold/status` verification;
- a real multi-branch expansion and selected VM81 commit;
- authoritative `main` merge and post-merge verification.

## Next action

Run the Pass 208 workflow. Repair any failures without weakening physical-GPU, package-validation, lattice-root, CPU-equivalence, or singleton-VM81 gates. After merge, provision or select the DigitalOcean GPU Droplet, place the actual JSON package, run `deployment/digitalocean/gpu/install.sh`, and record the physical preflight receipts.
