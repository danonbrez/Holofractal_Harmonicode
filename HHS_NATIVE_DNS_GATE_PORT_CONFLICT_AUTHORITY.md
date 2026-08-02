# HHS Native DNS Gate — Same-Port Loopback Authority

## 1. Normative metadata

| Field | Value |
|---|---|
| Contract | `HHS-NDG-HOST-LOCAL-DNS-SAME-PORT-AUTHORITY-V1` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Baseline | `main @ e302cca3618592a120752f9f766850ef798b6dc3` |
| Deployment authority | DigitalOcean Ubuntu, systemd, systemd-resolved, nginx |
| Internal zone | `hhs.internal` |
| DNS endpoint | `127.0.0.55:53`, UDP and TCP |
| Classification | `HHS_NATIVE_DNS_GATE_SAME_PORT_CONFLICT_RESOLVED` |
| Vercel | Excluded from authority and acceptance |

## 2. Problem

Pass 189 Iteration 2 and Pass 190 both own canonical port `8190`. Binding both to `127.0.0.1:8190` makes simultaneous co-hosted execution impossible.

DNS alone cannot map one address and port to two processes. The native gate therefore combines authoritative host-local DNS with loopback-address partitioning:

```text
pass189-calibration.hhs.internal → 127.189.0.2:8190
pass190-runtime.hhs.internal     → 127.190.0.1:8190
```

Both services retain their canonical port. The conflict is removed at the kernel socket tuple `(address, port)`.

## 3. Canonical service registry

| Service | Name | Address | Port |
|---|---|---:|---:|
| Pass 189 Iteration 1 | `pass189-runtime.hhs.internal` | `127.189.0.1` | `8189` |
| Pass 189 Iteration 2 | `pass189-calibration.hhs.internal` | `127.189.0.2` | `8190` |
| Pass 189 Iteration 3 | `pass189-adapter.hhs.internal` | `127.189.0.3` | `8191` |
| Pass 189 Iteration 4 | `pass189-provenance.hhs.internal` | `127.189.0.4` | `8192` |
| Pass 190 API | `pass190-runtime.hhs.internal` | `127.190.0.1` | `8190` |
| Pass 196 IDE | `pass196-ide.hhs.internal` | `127.196.0.1` | `8080` |

Linux reserves the complete `127.0.0.0/8` block for loopback. No service address is publicly routable.

## 4. DNS authority

The standard-library gate serves authoritative records for `hhs.internal` over UDP and TCP. It supports:

- A records for canonical names and aliases;
- PTR records for the assigned loopback addresses;
- SRV records that retain canonical ports;
- NS and SOA authority records;
- TXT registry identity and scope witnesses;
- NXDOMAIN for unknown names inside the zone;
- REFUSED for names outside the zone.

The canonical registry and the conflict-resolution pair receive deterministic Hash72 identities. The DNS gate does not recurse or forward public DNS.

## 5. Resolver membrane

`hhs-dns-gate-resolved.service` configures `systemd-resolved` with route-only domains on the loopback link:

```text
~hhs.internal
~0.189.127.in-addr.arpa
~0.190.127.in-addr.arpa
~0.196.127.in-addr.arpa
~0.0.127.in-addr.arpa
```

`default-route lo no` prevents unrelated queries from entering the gate.

## 6. Service admission

Persistent systemd drop-ins require the resolver membrane and replace only service bind addresses. Original project units retain ownership of commands, databases, users, and hardening.

Nginx also requires the resolver membrane. Pass 189 and Pass 190 upstreams use canonical `hhs.internal` names. A failed DNS gate therefore fails closed instead of silently sending traffic to the wrong process.

## 7. Installation

Both Pass 189 and Pass 190 installers invoke the native DNS-gate installer before enabling their own units. The gate installer is idempotent and installs:

```text
hhs-dns-gate.service
hhs-dns-gate-resolved.service
/etc/systemd/system/<service>.d/10-hhs-dns-gate.conf
```

Reinstalling a project base unit does not remove its persistent drop-in.

## 8. Validation

Required validation includes:

1. registry schema and loopback-only admission;
2. unique address-and-port tuples;
3. Pass 189 and Pass 190 both retaining port `8190`;
4. distinct loopback addresses for those services;
5. A, alias, PTR, SRV, NS, SOA, and TXT behavior;
6. UDP and TCP DNS operation;
7. NXDOMAIN and REFUSED behavior;
8. route-only resolver configuration;
9. systemd dependency and command overrides;
10. nginx hostname upstreams;
11. simultaneous kernel bind of both `8190` endpoints;
12. inherited Pass 189 and Pass 190 validation.

## 9. Security boundary

The DNS listener binds only `127.0.0.55`. Service identities bind only loopback addresses. No public firewall rule is authorized for DNS or application ports. The gate runs with only `CAP_NET_BIND_SERVICE`, a strict capability bounding set, and systemd filesystem, kernel, address-family, and IP restrictions.

## 10. Honest boundary

This contract establishes a single-host, host-local DNS and socket identity membrane. It does not claim distributed DNS, DNSSEC, multi-host service discovery, public-zone delegation, cross-host consensus, or hardware dispatch authority. External DigitalOcean mutation must be verified separately on the target host.
