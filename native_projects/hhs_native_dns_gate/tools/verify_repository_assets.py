#!/usr/bin/env python3
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]

def read(relative: str) -> str:
    path = REPO / relative
    assert path.is_file(), f"missing repository integration file: {relative}"
    return path.read_text(encoding="utf-8")

p189_install = read("native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/install.sh")
assert 'hhs_native_dns_gate' in p189_install
for name in (
    'pass189-runtime.hhs.internal:8189',
    'pass189-calibration.hhs.internal:8190',
    'pass189-adapter.hhs.internal:8191',
    'pass189-provenance.hhs.internal:8192',
):
    assert name in p189_install

p189_verify = read("native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/verify.sh")
for name in ('pass189-runtime.hhs.internal', 'pass189-calibration.hhs.internal', 'pass189-adapter.hhs.internal', 'pass189-provenance.hhs.internal'):
    assert name in p189_verify

p189_nginx = read("native_projects/hhs_pass189_hqlh_runtime/deployment/digitalocean/nginx-hhs-pass189.conf")
for name in ('pass189-runtime.hhs.internal', 'pass189-calibration.hhs.internal', 'pass189-adapter.hhs.internal', 'pass189-provenance.hhs.internal'):
    assert name in p189_nginx
assert 'proxy_pass http://127.0.0.1:' not in p189_nginx

p190_install = read("native_projects/hhs_pass190_operation_fabric/deploy/install.sh")
assert 'hhs_native_dns_gate' in p190_install
p190_verify = read("native_projects/hhs_pass190_operation_fabric/deploy/verify.sh")
assert 'pass190-runtime.hhs.internal:8190' in p190_verify
p190_nginx = read("native_projects/hhs_pass190_operation_fabric/deploy/nginx-hhs-pass190.conf")
assert 'pass190-runtime.hhs.internal:8190' in p190_nginx
assert 'proxy_pass http://127.0.0.1:8190' not in p190_nginx

contract = read("HHS_NATIVE_DNS_GATE_PORT_CONFLICT_AUTHORITY.md")
assert '127.189.0.2:8190' in contract
assert '127.190.0.1:8190' in contract
assert 'DNS alone cannot map' in contract

print('HHS_NATIVE_DNS_GATE_REPOSITORY_INTEGRATION_PASS')
