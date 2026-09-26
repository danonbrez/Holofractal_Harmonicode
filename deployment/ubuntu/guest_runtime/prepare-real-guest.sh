#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

SOURCE_ROOT="${SOURCE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
TARGET_SHA="${TARGET_SHA:?TARGET_SHA is required}"
MANIFEST="${HHS_GUEST_IMAGE_MANIFEST:-$SOURCE_ROOT/deployment/ubuntu/guest_runtime/ubuntu-24.04-amd64-image.json}"
ROOT="${HHS_GUEST_INTEGRATION_ROOT:-/var/lib/hhs/ubuntu-guest}"
RELEASE_ROOT="$ROOT/releases"
STATE_ROOT="$RELEASE_ROOT/$TARGET_SHA"
PERSISTENT_VM="${HHS_GUEST_PERSISTENT_VM:-0}"
RUNTIME_STATE_ROOT="$STATE_ROOT"
if [[ "$PERSISTENT_VM" == "1" ]]; then
  RUNTIME_STATE_ROOT="$ROOT/machine"
fi
IMAGE_ROOT="$ROOT/images"
KEY_ROOT="$RUNTIME_STATE_ROOT/keys"
SEED_ROOT="$RUNTIME_STATE_ROOT/seed"
SSH_PORT="${HHS_GUEST_SSH_PORT:-2222}"
RUNTIME_HTTP_PORT="${HHS_GUEST_RUNTIME_HTTP_PORT:-18080}"
GUEST_RUNTIME_HTTP_PORT="${HHS_GUEST_RUNTIME_GUEST_PORT:-8080}"
APPLICATION_API_PORT="${HHS_GUEST_APPLICATION_API_PORT:-18720}"
GUEST_APPLICATION_API_PORT="${HHS_GUEST_APPLICATION_API_GUEST_PORT:-8720}"
MEMORY_MIB="${HHS_GUEST_MEMORY_MIB:-2048}"
CPUS="${HHS_GUEST_CPUS:-2}"
REPO_URL="${HHS_GUEST_REPOSITORY_URL:-https://github.com/danonbrez/Holofractal_Harmonicode.git}"

fail() {
  printf 'HHS_I044_GUEST_PREPARE_FAILED: %s\n' "$*" >&2
  exit 2
}

[[ $EUID -eq 0 ]] || fail "root is required"
[[ "$TARGET_SHA" =~ ^[0-9a-f]{40}$ ]] || fail "TARGET_SHA must be a 40-character lowercase git SHA"
[[ -r "$MANIFEST" ]] || fail "guest image manifest missing: $MANIFEST"

for tool in python3 curl ssh-keygen; do
  command -v "$tool" >/dev/null 2>&1 || fail "required tool missing: $tool"
done

readarray -t IMAGE_FIELDS < <(python3 - "$MANIFEST" <<'PY'
import json, sys
from pathlib import Path
payload=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["schema"] == "HHS_PASS_220_I044_UBUNTU_GUEST_IMAGE_V1"
assert payload["architecture"] == "amd64"
assert payload["format"] == "qcow2"
assert payload["authority"]["canonical_hhs_state_authority"] is False
print(payload["url"])
print(payload["sha256"])
print(payload["filename"])
PY
)
IMAGE_URL="${IMAGE_FIELDS[0]}"
IMAGE_SHA256="${IMAGE_FIELDS[1]}"
IMAGE_FILENAME="${IMAGE_FIELDS[2]}"
[[ "$IMAGE_SHA256" =~ ^[0-9a-f]{64}$ ]] || fail "manifest SHA-256 is invalid"

MISSING_PACKAGES=()
command -v qemu-system-x86_64 >/dev/null 2>&1 || MISSING_PACKAGES+=(qemu-system-x86)
command -v qemu-img >/dev/null 2>&1 || MISSING_PACKAGES+=(qemu-utils)
command -v cloud-localds >/dev/null 2>&1 || MISSING_PACKAGES+=(cloud-image-utils)
command -v ssh >/dev/null 2>&1 || MISSING_PACKAGES+=(openssh-client)
if (("${#MISSING_PACKAGES[@]}" > 0)); then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y "${MISSING_PACKAGES[@]}"
fi

for tool in qemu-system-x86_64 qemu-img cloud-localds ssh; do
  command -v "$tool" >/dev/null 2>&1 || fail "required runtime tool missing after install: $tool"
done

install -d -m 0750 "$ROOT" "$RELEASE_ROOT" "$IMAGE_ROOT"
install -d -m 0700 "$STATE_ROOT" "$RUNTIME_STATE_ROOT" "$KEY_ROOT" "$SEED_ROOT"

BASE_IMAGE="$IMAGE_ROOT/$IMAGE_FILENAME"
if [[ -f "$BASE_IMAGE" ]]; then
  ACTUAL="$(sha256sum "$BASE_IMAGE" | awk '{print $1}')"
  if [[ "$ACTUAL" != "$IMAGE_SHA256" ]]; then
    fail "existing base image digest mismatch: expected=$IMAGE_SHA256 actual=$ACTUAL"
  fi
else
  PART="$BASE_IMAGE.part"
  rm -f "$PART"
  curl --fail --location --retry 5 --retry-delay 3 --connect-timeout 20 \
    --output "$PART" "$IMAGE_URL"
  ACTUAL="$(sha256sum "$PART" | awk '{print $1}')"
  [[ "$ACTUAL" == "$IMAGE_SHA256" ]] \
    || fail "downloaded base image digest mismatch: expected=$IMAGE_SHA256 actual=$ACTUAL"
  mv "$PART" "$BASE_IMAGE"
  chmod 0444 "$BASE_IMAGE"
fi

CLIENT_KEY="$KEY_ROOT/id_ed25519"
HOST_KEY="$KEY_ROOT/ssh_host_ed25519_key"
if [[ ! -f "$CLIENT_KEY" ]]; then
  ssh-keygen -q -t ed25519 -N '' -C "hhs-i044-client-$TARGET_SHA" -f "$CLIENT_KEY"
fi
if [[ ! -f "$HOST_KEY" ]]; then
  ssh-keygen -q -t ed25519 -N '' -C "hhs-i044-host-$TARGET_SHA" -f "$HOST_KEY"
fi
chmod 0600 "$CLIENT_KEY" "$HOST_KEY"
chmod 0644 "$CLIENT_KEY.pub" "$HOST_KEY.pub"

KNOWN_HOSTS="$KEY_ROOT/known_hosts"
HOST_PUBLIC="$(cut -d' ' -f1-2 "$HOST_KEY.pub")"
printf '[127.0.0.1]:%s %s\n' "$SSH_PORT" "$HOST_PUBLIC" > "$KNOWN_HOSTS"
chmod 0600 "$KNOWN_HOSTS"

USER_DATA="$SEED_ROOT/user-data"
META_DATA="$SEED_ROOT/meta-data"
SEED_IMAGE="$SEED_ROOT/nocloud-seed.img"

python3 - "$CLIENT_KEY.pub" "$HOST_KEY" "$HOST_KEY.pub" "$USER_DATA" "$TARGET_SHA" "$REPO_URL" <<'PY'
import base64, json, shlex, sys
from pathlib import Path

client_pub=Path(sys.argv[1]).read_text(encoding="utf-8").strip()
host_private=base64.b64encode(Path(sys.argv[2]).read_bytes()).decode("ascii")
host_public=base64.b64encode(Path(sys.argv[3]).read_bytes()).decode("ascii")
output=Path(sys.argv[4])
target=sys.argv[5]
repo_url=sys.argv[6]
repo_root="/opt/holofractal-harmonicode"

def q(value: str) -> str:
    return shlex.quote(value)

payload={
    "hostname": "hhs-ubuntu-guest",
    "manage_etc_hosts": True,
    "ssh_pwauth": False,
    "disable_root": True,
    "ssh_deletekeys": False,
    "users": [
        {
            "name": "hhs",
            "groups": ["adm", "sudo"],
            "sudo": "ALL=(ALL) NOPASSWD:ALL",
            "shell": "/bin/bash",
            "lock_passwd": True,
            "ssh_authorized_keys": [client_pub],
        }
    ],
    "package_update": True,
    "packages": [
        "openssh-server",
        "git",
        "curl",
        "python3-venv",
        "python3-pip",
        "build-essential",
        "binutils",
        "gzip",
        "libssl-dev",
        "iproute2",
    ],
    "write_files": [
        {
            "path": "/etc/ssh/ssh_host_ed25519_key",
            "permissions": "0600",
            "owner": "root:root",
            "encoding": "b64",
            "content": host_private,
        },
        {
            "path": "/etc/ssh/ssh_host_ed25519_key.pub",
            "permissions": "0644",
            "owner": "root:root",
            "encoding": "b64",
            "content": host_public,
        },
    ],
    "runcmd": [
        ["systemctl", "enable", "--now", "ssh"],
        ["rm", "-rf", repo_root],
        ["git", "clone", "--no-checkout", repo_url, repo_root],
        ["git", "-C", repo_root, "fetch", "--depth=1", "origin", target],
        ["git", "-C", repo_root, "checkout", "--detach", target],
        ["python3", "-m", "venv", "/opt/hhs/venv"],
        [
            "/opt/hhs/venv/bin/pip",
            "install",
            "--disable-pip-version-check",
            "fastapi",
            "uvicorn",
            "httpx",
            "pytest",
            "pyyaml",
        ],
        [
            "bash",
            "-lc",
            (
                f"REPO_ROOT={q(repo_root)} "
                "HHS_APPLICATION_VM_REQUIRE_GUI=0 "
                "HHS_APPLICATION_VM_INSTALL_GUI=0 "
                f"bash {q(repo_root + '/deployment/ubuntu/application_vm/install.sh')}"
            ),
        ],
        [
            "bash",
            "-lc",
            (
                f"REPO_ROOT={q(repo_root)} "
                f"bash {q(repo_root + '/deployment/ubuntu/guest_runtime/install-unified-guest-ide.sh')}"
            ),
        ],
        [
            "bash",
            "-lc",
            (
                "install -d -m 0755 /var/lib/hhs/guest-bootstrap && "
                f"git -C {q(repo_root)} rev-parse HEAD "
                "> /var/lib/hhs/guest-bootstrap/repository-sha && "
                "curl -fsS http://127.0.0.1:8720/health "
                "> /var/lib/hhs/guest-bootstrap/application-vm-health.json && "
                "curl -fsS http://127.0.0.1:8080/api/health "
                "> /var/lib/hhs/guest-bootstrap/guest-ide-health.json && "
                "touch /var/lib/hhs/guest-bootstrap/ready"
            ),
        ],
    ],
}
output.write_text("#cloud-config\n" + json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

INSTANCE_ID="hhs-i044-$TARGET_SHA"
if [[ "$PERSISTENT_VM" == "1" ]]; then
  INSTANCE_ID="hhs-unified-lane5-machine"
fi
cat > "$META_DATA" <<EOF
instance-id: $INSTANCE_ID
local-hostname: hhs-ubuntu-guest
EOF

rm -f "$SEED_IMAGE"
cloud-localds "$SEED_IMAGE" "$USER_DATA" "$META_DATA"
[[ -s "$SEED_IMAGE" ]] || fail "NoCloud seed image was not created"

ENV_FILE="$STATE_ROOT/runtime.env"
cat > "$ENV_FILE" <<EOF
HHS_GUEST_BASE_IMAGE=$BASE_IMAGE
HHS_GUEST_BASE_SHA256=$IMAGE_SHA256
HHS_GUEST_STATE_ROOT=$RUNTIME_STATE_ROOT
HHS_GUEST_BASE_FORMAT=qcow2
HHS_GUEST_NAME=hhs-ubuntu-unified
HHS_GUEST_MEMORY_MIB=$MEMORY_MIB
HHS_GUEST_CPUS=$CPUS
HHS_GUEST_SSH_PORT=$SSH_PORT
HHS_GUEST_RUNTIME_HTTP_PORT=$RUNTIME_HTTP_PORT
HHS_GUEST_RUNTIME_GUEST_PORT=$GUEST_RUNTIME_HTTP_PORT
HHS_GUEST_APPLICATION_API_PORT=$APPLICATION_API_PORT
HHS_GUEST_APPLICATION_API_GUEST_PORT=$GUEST_APPLICATION_API_PORT
HHS_GUEST_SSH_USER=hhs
HHS_GUEST_SSH_IDENTITY=$CLIENT_KEY
HHS_GUEST_SSH_KNOWN_HOSTS=$KNOWN_HOSTS
HHS_GUEST_SEED_IMAGE=$SEED_IMAGE
HHS_GUEST_PYTHON_BIN=python3
EOF
chmod 0600 "$ENV_FILE"

python3 - "$STATE_ROOT/preparation.receipt.json" "$TARGET_SHA" "$IMAGE_URL" "$IMAGE_SHA256" "$BASE_IMAGE" "$SEED_IMAGE" "$KNOWN_HOSTS" "$RUNTIME_STATE_ROOT" "$PERSISTENT_VM" <<'PY'
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

out=Path(sys.argv[1])
payload={
    "schema": "HHS_PASS_220_I044_REAL_GUEST_PREPARATION_RECEIPT_V1",
    "target_sha": sys.argv[2],
    "image_url": sys.argv[3],
    "base_sha256": sys.argv[4],
    "base_image": sys.argv[5],
    "seed_image": sys.argv[6],
    "known_hosts": sys.argv[7],
    "ssh_loopback_only": True,
    "guest_application_vm_required": True,
    "canonical_state_authority": False,
    "new_vm81_authority": False,
    "prepared_at": datetime.now(timezone.utc).isoformat(),
}
canonical=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
payload["receipt_sha256"]=hashlib.sha256(canonical).hexdigest()
out.write_text(json.dumps(payload, sort_keys=True, indent=2)+"\n", encoding="utf-8")
print(json.dumps(payload, sort_keys=True))
PY

printf 'HHS_I044_GUEST_ENV_FILE=%s\n' "$ENV_FILE"
printf 'HHS_I044_GUEST_STATE_ROOT=%s\n' "$STATE_ROOT"
printf 'HHS_I044_GUEST_BASE_SHA256=%s\n' "$IMAGE_SHA256"
