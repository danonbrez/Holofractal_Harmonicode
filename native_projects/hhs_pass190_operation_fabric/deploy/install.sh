#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
make validate
sudo install -d -o hhs -g hhs /var/lib/hhs
sudo install -m 0644 deploy/hhs-pass190.service /etc/systemd/system/hhs-pass190.service
sudo systemctl daemon-reload
sudo systemctl enable --now hhs-pass190.service
sudo systemctl --no-pager --full status hhs-pass190.service
