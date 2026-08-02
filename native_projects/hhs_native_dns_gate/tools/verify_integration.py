#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
registry=json.loads((ROOT/'config/service_registry.json').read_text())
services={x['service_id']:x for x in registry['services']}
expected={
'hhs-pass189.service.d':('127.189.0.1',8189),
'hhs-pass189-iteration2.service.d':('127.189.0.2',8190),
'hhs-pass189-iteration3.service.d':('127.189.0.3',8191),
'hhs-pass189-iteration4.service.d':('127.189.0.4',8192),
'hhs-pass190.service.d':('127.190.0.1',8190),
'hhs-pass196-integrated-environment.service.d':('127.196.0.1',8080),
}
seen=[]
for unit,(address,port) in expected.items():
    text=(ROOT/'deploy/overrides'/unit/'10-hhs-dns-gate.conf').read_text()
    assert 'Requires=hhs-dns-gate-resolved.service' in text
    assert f'--host {address}' in text
    assert f'--port {port}' in text
    seen.append((address,port))
assert len(seen)==len(set(seen))
assert services['pass189.iteration2']['port']==services['pass190.runtime']['port']==8190
assert services['pass189.iteration2']['address'] != services['pass190.runtime']['address']
nginx=(ROOT/'deploy/overrides/nginx.service.d'/'10-hhs-dns-gate.conf').read_text()
assert 'Requires=hhs-dns-gate-resolved.service' in nginx
resolved=(ROOT/'deploy/hhs-dns-gate-resolved.service').read_text()
assert 'resolvectl domain lo ~hhs.internal' in resolved
for reverse_zone in ('~0.189.127.in-addr.arpa','~0.190.127.in-addr.arpa','~0.196.127.in-addr.arpa','~0.0.127.in-addr.arpa'):
    assert reverse_zone in resolved
assert 'resolvectl default-route lo no' in resolved
gate=(ROOT/'deploy/hhs-dns-gate.service').read_text()
assert 'Before=systemd-resolved.service' not in gate
print('HHS_NATIVE_DNS_GATE_INTEGRATION_PASS endpoints=%d canonical_shared_port=8190' % len(seen))
