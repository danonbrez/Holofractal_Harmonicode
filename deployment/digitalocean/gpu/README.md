# DigitalOcean GPU Deployment for HHS Pass 208

This deployment enables the Pass 207 C11/OpenCL driver and the Pass 208 neural branch-expansion manifold on a physical DigitalOcean GPU Droplet.

The GPU remains inside the inherited VM81 bytecode hydration lattice:

```text
one committed parent snapshot
+ one committed constraint/bytecode root
+ N ordered candidate deltas
+ exact q=243s+g hydration addresses
→ N parallel 5,184-lane GPU branches
→ exact CPU/VM5184 equality for every branch
→ stable integer ranking
→ one selected ordered delta
→ existing singleton VM81 advance
→ parent-bound Hash216/Hash72 receipt and persistence
```

The GPU cannot commit Hash72, persist a canonical snapshot, create an alternate kernel, or bypass VM81 admission.

## 1. Provision a GPU Droplet

A standard CPU Droplet does not gain a physical GPU by installing packages. Create a DigitalOcean GPU Droplet and migrate the HHS deployment to it.

DigitalOcean recommends its AI/ML-ready images because the vendor drivers and GPU software are preinstalled:

- NVIDIA single GPU image: `gpu-h100x1-base`
- NVIDIA eight GPU image: `gpu-h100x8-base`
- AMD GPU image: `gpu-amd-base`

The single-GPU NVIDIA image slug is used for all single-GPU NVIDIA plans, not only H100 plans.

Discover plans and regions before provisioning:

```bash
doctl compute size list --format Slug,Description,Memory,VCPUs,PriceHourly,Regions
doctl compute region list
```

Create the GPU Droplet with the selected size, region, image, and SSH keys:

```bash
export GPU_NAME=hhs-production-gpu-01
export GPU_SIZE='<available-gpu-size-slug>'
export GPU_REGION='<available-region>'
export GPU_IMAGE=gpu-h100x1-base
export SSH_KEYS='<ssh-key-id-or-fingerprint>'

doctl compute droplet create "$GPU_NAME" \
  --size "$GPU_SIZE" \
  --image "$GPU_IMAGE" \
  --region "$GPU_REGION" \
  --ssh-keys "$SSH_KEYS" \
  --enable-monitoring \
  --enable-backups \
  --tag-names hhs-production,hhs-gpu \
  --wait
```

Use the control panel instead when the required GPU plan is contract-provisioned or unavailable through the self-service size list.

## 2. Restore HHS onto the GPU host

Install or restore the existing production layout:

```text
/opt/hhs/app       repository checkout
/opt/hhs/venv      Python virtual environment
/var/lib/hhs       durable HHS state
/etc/hhs           service environment
hhs.service        production systemd service
```

Copy the 23-file JSON specification package to a stable path. The default documented path is:

```text
/opt/hhs/app/specifications/hhs-runtime-json-package
```

The package is required before physical GPU enablement. Pass 208 validates:

- exactly 23 JSON files;
- one package manifest;
- manifest file references and SHA-256 checksums;
- local JSON Schema references;
- at least four schema-linked example objects;
- conformance-vector presence;
- all declared HHS specification domains.

## 3. Install physical GPU integration

On the GPU Droplet:

```bash
cd /opt/hhs/app
git fetch origin main
git checkout main
git pull --ff-only origin main

sudo HHS_JSON_SPEC_PACKAGE_ROOT=/opt/hhs/app/specifications/hhs-runtime-json-package \
  bash deployment/digitalocean/gpu/install.sh
```

The installer:

1. requires an operational NVIDIA or AMD GPU runtime;
2. installs the OpenCL ICD loader and `clinfo`;
3. builds `libhhs_pass207_gpu_driver.so`;
4. validates the 23-file JSON package;
5. installs `/etc/hhs/pass208-gpu.env`;
6. installs a fail-closed `hhs.service` preflight;
7. enables the guarded updater's GPU validation and rebuild hook;
8. restarts HHS;
9. verifies the hosted GPU-manifold status endpoint.

## 4. Verify production state

```bash
nvidia-smi -L             # NVIDIA
# or
rocminfo                   # AMD

clinfo -l

sudo systemctl status hhs.service --no-pager --full
sudo journalctl -u hhs.service -n 200 --no-pager

curl -fsS http://127.0.0.1:8080/api/runtime/gpu-manifold/status \
  | python3 -m json.tool

sudo cat /var/lib/hhs/pass208/PASS208_GPU_PREFLIGHT_RECEIPT.json
sudo cat /var/lib/hhs/pass208/PASS208_JSON_SPEC_VALIDATION_RECEIPT.json
```

Required hosted status fields:

```text
enabled = true
require_physical_gpu = true
driver.driver.physical_gpu = true
driver.driver.backend_name = OPENCL_GPU
driver.driver.logical_hyperthreads_per_cell = 64
driver.driver.logical_lanes_per_batch = 5184
driver.driver.stable_lane_identity = true
driver.driver.disjoint_lane_writes = true
driver.driver.canonical_reduction_order = true
```

## 5. Expand a branch manifold

Each branch shares one committed parent and one committed bytecode/constraint root.

```bash
curl -fsS -X POST \
  http://127.0.0.1:8080/api/runtime/gpu-manifold/expand \
  -H 'content-type: application/json' \
  -d @branch-expansion-request.json \
  | python3 -m json.tool
```

Example request shape:

```json
{
  "parent_root216": "<216-symbol committed continuation root>",
  "bytecode_hydration_lattice_root216": "<same 216-symbol parent constraint root>",
  "branches": [
    {
      "events": [
        {"cell": 0, "control_g": 7, "xor_mask": 1}
      ]
    },
    {
      "events": [
        {"cell": 0, "control_g": 7, "xor_mask": 2}
      ]
    }
  ]
}
```

This endpoint expands and ranks candidates but performs no canonical mutation.

## 6. Expand and commit through VM81

```bash
curl -fsS -X POST \
  http://127.0.0.1:8080/api/runtime/gpu-manifold/expand-and-commit \
  -H 'content-type: application/json' \
  -d @branch-commit-request.json \
  | python3 -m json.tool
```

The selected branch is recomputed by the existing Pass 205 singleton VM81 authority. The commit is rejected if state, projection, dependency frontier, parent receipt, hydration identity, or branch roots diverge.

## 7. Guarded deployment behavior

When `/etc/hhs/guarded-update.env` exists, the installer sets:

```text
HHS_VALIDATE_GPU=1
HHS_POST_MERGE_COMMAND=/usr/local/lib/hhs-gpu/post-merge.sh
HHS_ROLLBACK_COMMAND=/usr/local/lib/hhs-gpu/post-merge.sh
```

Every accepted update must rebuild the native GPU library and pass physical-GPU and JSON-package preflight before `hhs.service` can restart successfully.

## 8. Disable physical GPU mode

Disabling GPU execution is explicit:

```bash
sudo sed -i 's/^HHS_PASS208_GPU_ENABLED=.*/HHS_PASS208_GPU_ENABLED=0/' \
  /etc/hhs/pass208-gpu.env
sudo systemctl daemon-reload
sudo systemctl restart hhs.service
```

Remove the systemd drop-in only when returning the host to a CPU-only deployment:

```bash
sudo rm -f /etc/systemd/system/hhs.service.d/40-pass208-gpu.conf
sudo systemctl daemon-reload
sudo systemctl restart hhs.service
```

## Official DigitalOcean references

- GPU Droplets: `https://docs.digitalocean.com/products/gpu-droplets/`
- GPU creation: `https://docs.digitalocean.com/products/droplets/how-to/gpu/create/`
- Recommended GPU images and drivers: `https://docs.digitalocean.com/products/droplets/getting-started/recommended-gpu-setup/`
- GPU availability: `https://docs.digitalocean.com/products/droplets/details/gpu-availability/`
- `doctl compute droplet create`: `https://docs.digitalocean.com/reference/doctl/reference/compute/droplet/create/`
