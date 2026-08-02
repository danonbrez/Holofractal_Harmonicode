#!/usr/bin/env python3
"""Repository-native authoritative DNS gate for the host-local HHS service zone."""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import signal
import socket
import socketserver
import struct
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

TYPE_A = 1
TYPE_NS = 2
TYPE_SOA = 6
TYPE_PTR = 12
TYPE_TXT = 16
TYPE_AAAA = 28
TYPE_SRV = 33
CLASS_IN = 1
RCODE_NOERROR = 0
RCODE_FORMERR = 1
RCODE_NXDOMAIN = 3
RCODE_NOTIMP = 4
RCODE_REFUSED = 5


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def hash72(value: Any) -> str:
    return hashlib.sha512(canonical_json(value).encode("utf-8")).hexdigest()[:72]


def normalize_name(value: str) -> str:
    name = value.strip().lower().rstrip(".")
    if not name or any(not label or len(label) > 63 for label in name.split(".")):
        raise ValueError(f"invalid DNS name: {value!r}")
    if len(name) > 253:
        raise ValueError("DNS name exceeds 253 octets")
    return name


def encode_name(name: str) -> bytes:
    normalized = normalize_name(name)
    out = bytearray()
    for label in normalized.split("."):
        raw = label.encode("ascii")
        out.append(len(raw))
        out.extend(raw)
    out.append(0)
    return bytes(out)


def decode_name(message: bytes, offset: int, *, depth: int = 0) -> tuple[str, int]:
    if depth > 16:
        raise ValueError("DNS compression pointer recursion exceeded")
    labels: list[str] = []
    cursor = offset
    next_offset: int | None = None
    while True:
        if cursor >= len(message):
            raise ValueError("truncated DNS name")
        length = message[cursor]
        if length & 0xC0 == 0xC0:
            if cursor + 1 >= len(message):
                raise ValueError("truncated DNS pointer")
            pointer = ((length & 0x3F) << 8) | message[cursor + 1]
            if pointer >= len(message):
                raise ValueError("invalid DNS pointer")
            suffix, _ = decode_name(message, pointer, depth=depth + 1)
            if suffix:
                labels.extend(suffix.split("."))
            next_offset = cursor + 2
            break
        if length & 0xC0:
            raise ValueError("unsupported DNS label encoding")
        cursor += 1
        if length == 0:
            if next_offset is None:
                next_offset = cursor
            break
        if cursor + length > len(message):
            raise ValueError("truncated DNS label")
        labels.append(message[cursor:cursor + length].decode("ascii").lower())
        cursor += length
    return ".".join(labels), next_offset


def rr(name: str, rtype: int, ttl: int, rdata: bytes) -> bytes:
    return encode_name(name) + struct.pack("!HHIH", rtype, CLASS_IN, ttl, len(rdata)) + rdata


def a_rdata(address: str) -> bytes:
    return ipaddress.IPv4Address(address).packed


def txt_rdata(values: Iterable[str]) -> bytes:
    out = bytearray()
    for value in values:
        raw = value.encode("utf-8")
        if len(raw) > 255:
            raise ValueError("TXT segment exceeds 255 bytes")
        out.append(len(raw))
        out.extend(raw)
    return bytes(out)


def srv_rdata(port: int, target: str) -> bytes:
    return struct.pack("!HHH", 0, 0, port) + encode_name(target)


def soa_rdata(zone: str, serial: int) -> bytes:
    return (
        encode_name(f"dns-gate.{zone}")
        + encode_name(f"hostmaster.{zone}")
        + struct.pack("!IIIII", serial, 60, 30, 3600, 30)
    )


def reverse_name(address: str) -> str:
    return ipaddress.ip_address(address).reverse_pointer


@dataclass(frozen=True)
class Service:
    service_id: str
    name: str
    aliases: tuple[str, ...]
    address: str
    port: int
    protocol: str


class Registry:
    def __init__(self, payload: dict[str, Any]):
        if payload.get("schema") != "HHS_NATIVE_DNS_GATE_REGISTRY_V1":
            raise ValueError("unsupported registry schema")
        self.registry_hash72 = hash72(payload)
        self.zone = normalize_name(str(payload["zone"]))
        self.ttl = int(payload.get("ttl", 30))
        if not 1 <= self.ttl <= 86400:
            raise ValueError("ttl outside supported range")
        dns = dict(payload["dns"])
        self.dns_name = normalize_name(str(dns["name"]))
        self.dns_address = str(ipaddress.IPv4Address(str(dns["address"])))
        self.dns_port = int(dns["port"])
        if not 1 <= self.dns_port <= 65535:
            raise ValueError("invalid DNS port")
        self.services: list[Service] = []
        self.by_id: dict[str, Service] = {}
        self.addresses: dict[str, str] = {self.dns_name: self.dns_address}
        self.srv: dict[str, tuple[int, str]] = {
            normalize_name(f"_dns._udp.{self.dns_name}"): (self.dns_port, self.dns_name),
            normalize_name(f"_dns._tcp.{self.dns_name}"): (self.dns_port, self.dns_name),
        }
        self.ptr: dict[str, str] = {reverse_name(self.dns_address): self.dns_name}
        service_ids: set[str] = set()
        endpoints: set[tuple[str, int]] = set()
        for item in payload.get("services", []):
            service_id = str(item["service_id"]).strip()
            if not service_id or service_id in service_ids:
                raise ValueError("duplicate or empty service_id")
            service_ids.add(service_id)
            name = normalize_name(str(item["name"]))
            aliases = tuple(normalize_name(str(v)) for v in item.get("aliases", []))
            address = str(ipaddress.IPv4Address(str(item["address"])))
            port = int(item["port"])
            protocol = str(item.get("protocol", "http")).strip().lower()
            if not name.endswith("." + self.zone):
                raise ValueError(f"service outside zone: {name}")
            if not ipaddress.IPv4Address(address).is_loopback:
                raise ValueError(f"service address is not loopback: {address}")
            if not 1 <= port <= 65535:
                raise ValueError(f"invalid service port: {port}")
            endpoint = (address, port)
            if endpoint in endpoints:
                raise ValueError(f"duplicate address/port endpoint: {endpoint}")
            endpoints.add(endpoint)
            service = Service(service_id, name, aliases, address, port, protocol)
            self.services.append(service)
            self.by_id[service_id] = service
            for hostname in (name, *aliases):
                if hostname in self.addresses:
                    raise ValueError(f"duplicate DNS name: {hostname}")
                self.addresses[hostname] = address
                self.srv[normalize_name(f"_{protocol}._tcp.{hostname}")] = (port, name)
            self.ptr[reverse_name(address)] = name
        self.serial = int(payload.get("serial", 1))
        self.txt = {
            normalize_name(f"_gate.{self.zone}"): (
                "schema=HHS_NATIVE_DNS_GATE_REGISTRY_V1",
                f"zone={self.zone}",
                f"services={len(self.services)}",
                "scope=host-loopback-only",
                f"registry_hash72={self.registry_hash72}",
            )
        }

    @classmethod
    def load(cls, path: str | Path) -> "Registry":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_NATIVE_DNS_GATE_STATUS_V1",
            "zone": self.zone,
            "dns": {"name": self.dns_name, "address": self.dns_address, "port": self.dns_port},
            "service_count": len(self.services),
            "services": [service.__dict__ for service in self.services],
            "conflict_resolved": (
                self.by_id["pass189.iteration2"].port == self.by_id["pass190.runtime"].port == 8190
                and self.by_id["pass189.iteration2"].address != self.by_id["pass190.runtime"].address
            ),
            "canonical_shared_port": 8190,
            "registry_hash72": self.registry_hash72,
            "conflict_resolution_hash72": hash72({
                "pass189": self.by_id["pass189.iteration2"].__dict__,
                "pass190": self.by_id["pass190.runtime"].__dict__,
            }),
        }


class DNSAuthority:
    def __init__(self, registry: Registry):
        self.registry = registry

    def answer(self, message: bytes) -> bytes:
        txid = message[:2] if len(message) >= 2 else b"\x00\x00"
        try:
            if len(message) < 12:
                raise ValueError("truncated header")
            ident, flags, qdcount, _, _, _ = struct.unpack("!HHHHHH", message[:12])
            if flags & 0x7800:
                return self._error(ident, flags, RCODE_NOTIMP)
            if qdcount != 1:
                return self._error(ident, flags, RCODE_FORMERR)
            qname, offset = decode_name(message, 12)
            if offset + 4 > len(message):
                raise ValueError("truncated question")
            qtype, qclass = struct.unpack("!HH", message[offset:offset + 4])
            question = message[12:offset + 4]
            if qclass != CLASS_IN:
                return self._response(ident, flags, question, [], RCODE_REFUSED)
            answers, rcode = self._records(qname, qtype)
            return self._response(ident, flags, question, answers, rcode)
        except (ValueError, UnicodeError, struct.error):
            ident = struct.unpack("!H", txid)[0]
            flags = struct.unpack("!H", message[2:4])[0] if len(message) >= 4 else 0
            return self._error(ident, flags, RCODE_FORMERR)

    def _records(self, qname: str, qtype: int) -> tuple[list[bytes], int]:
        name = normalize_name(qname)
        authoritative = name == self.registry.zone or name.endswith("." + self.registry.zone)
        reverse_authoritative = name in self.registry.ptr
        if not authoritative and not reverse_authoritative:
            return [], RCODE_REFUSED
        ttl = self.registry.ttl
        records: list[bytes] = []
        exists = False
        if name in self.registry.addresses:
            exists = True
            if qtype in (TYPE_A, 255):
                records.append(rr(name, TYPE_A, ttl, a_rdata(self.registry.addresses[name])))
        if name in self.registry.srv:
            exists = True
            if qtype in (TYPE_SRV, 255):
                port, target = self.registry.srv[name]
                records.append(rr(name, TYPE_SRV, ttl, srv_rdata(port, target)))
        if name in self.registry.ptr:
            exists = True
            if qtype in (TYPE_PTR, 255):
                records.append(rr(name, TYPE_PTR, ttl, encode_name(self.registry.ptr[name])))
        if name in self.registry.txt:
            exists = True
            if qtype in (TYPE_TXT, 255):
                records.append(rr(name, TYPE_TXT, ttl, txt_rdata(self.registry.txt[name])))
        if name == self.registry.zone:
            exists = True
            if qtype in (TYPE_SOA, 255):
                records.append(rr(name, TYPE_SOA, ttl, soa_rdata(self.registry.zone, self.registry.serial)))
            if qtype in (TYPE_NS, 255):
                records.append(rr(name, TYPE_NS, ttl, encode_name(self.registry.dns_name)))
        if qtype == TYPE_AAAA and exists:
            return [], RCODE_NOERROR
        if not exists:
            return [], RCODE_NXDOMAIN
        return records, RCODE_NOERROR

    def _error(self, ident: int, request_flags: int, rcode: int) -> bytes:
        return self._response(ident, request_flags, b"", [], rcode, qdcount=0)

    def _response(
        self,
        ident: int,
        request_flags: int,
        question: bytes,
        answers: list[bytes],
        rcode: int,
        *,
        qdcount: int = 1,
    ) -> bytes:
        rd = request_flags & 0x0100
        flags = 0x8000 | 0x0400 | rd | (rcode & 0x000F)
        return struct.pack("!HHHHHH", ident, flags, qdcount, len(answers), 0, 0) + question + b"".join(answers)


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data, sock = self.request
        response = self.server.authority.answer(data)  # type: ignore[attr-defined]
        sock.sendto(response, self.client_address)


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        while True:
            header = self._recv_exact(2)
            if not header:
                return
            size = struct.unpack("!H", header)[0]
            if size == 0 or size > 65535:
                return
            payload = self._recv_exact(size)
            if payload is None:
                return
            response = self.server.authority.answer(payload)  # type: ignore[attr-defined]
            self.request.sendall(struct.pack("!H", len(response)) + response)

    def _recv_exact(self, size: int) -> bytes | None:
        data = bytearray()
        while len(data) < size:
            chunk = self.request.recv(size - len(data))
            if not chunk:
                return None if data else b""
            data.extend(chunk)
        return bytes(data)


class ThreadingUDP(socketserver.ThreadingUDPServer):
    allow_reuse_address = True
    daemon_threads = True


class ThreadingTCP(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve(registry: Registry, host: str, port: int) -> None:
    authority = DNSAuthority(registry)
    udp = ThreadingUDP((host, port), UDPHandler)
    tcp = ThreadingTCP((host, port), TCPHandler)
    udp.authority = authority  # type: ignore[attr-defined]
    tcp.authority = authority  # type: ignore[attr-defined]
    stop = threading.Event()

    def shutdown(*_: object) -> None:
        if stop.is_set():
            return
        stop.set()
        threading.Thread(target=udp.shutdown, daemon=True).start()
        threading.Thread(target=tcp.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    threads = [
        threading.Thread(target=udp.serve_forever, name="hhs-dns-udp", daemon=True),
        threading.Thread(target=tcp.serve_forever, name="hhs-dns-tcp", daemon=True),
    ]
    for thread in threads:
        thread.start()
    print(json.dumps({**registry.status(), "status": "serving", "listen": f"{host}:{port}"}, sort_keys=True), flush=True)
    stop.wait()
    udp.server_close()
    tcp.server_close()


def build_query(name: str, qtype: int, ident: int = 0x4848) -> bytes:
    return struct.pack("!HHHHHH", ident, 0x0100, 1, 0, 0, 0) + encode_name(name) + struct.pack("!HH", qtype, CLASS_IN)


def parse_first_answer(message: bytes) -> dict[str, Any]:
    if len(message) < 12:
        raise ValueError("truncated response")
    _, flags, qdcount, ancount, _, _ = struct.unpack("!HHHHHH", message[:12])
    offset = 12
    for _ in range(qdcount):
        _, offset = decode_name(message, offset)
        offset += 4
    result: dict[str, Any] = {"rcode": flags & 0xF, "answer_count": ancount}
    if not ancount:
        return result
    name, offset = decode_name(message, offset)
    rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", message[offset:offset + 10])
    offset += 10
    rdata_offset = offset
    rdata = message[offset:offset + rdlength]
    result.update({"name": name, "type": rtype, "class": rclass, "ttl": ttl})
    if rtype == TYPE_A:
        result["address"] = str(ipaddress.IPv4Address(rdata))
    elif rtype == TYPE_SRV:
        priority, weight, port = struct.unpack("!HHH", rdata[:6])
        target, _ = decode_name(message, rdata_offset + 6)
        result.update({"priority": priority, "weight": weight, "port": port, "target": target})
    elif rtype in (TYPE_PTR, TYPE_NS):
        target, _ = decode_name(message, rdata_offset)
        result["target"] = target
    return result


def query_server(host: str, port: int, name: str, qtype: int, *, tcp: bool = False, timeout: float = 2.0) -> dict[str, Any]:
    query = build_query(name, qtype)
    if tcp:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.sendall(struct.pack("!H", len(query)) + query)
            size = struct.unpack("!H", _recv(sock, 2))[0]
            response = _recv(sock, size)
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.sendto(query, (host, port))
            response, _ = sock.recvfrom(65535)
    return parse_first_answer(response)


def _recv(sock: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("unexpected EOF")
        data.extend(chunk)
    return bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(Path(__file__).resolve().parents[1] / "config" / "service_registry.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    serve_parser = sub.add_parser("serve")
    serve_parser.add_argument("--host")
    serve_parser.add_argument("--port", type=int)
    sub.add_parser("status")
    query_parser = sub.add_parser("query")
    query_parser.add_argument("name")
    query_parser.add_argument("--type", choices=("A", "SRV", "PTR", "SOA", "NS", "TXT"), default="A")
    query_parser.add_argument("--host")
    query_parser.add_argument("--port", type=int)
    query_parser.add_argument("--tcp", action="store_true")
    args = parser.parse_args()
    registry = Registry.load(args.registry)
    if args.command == "serve":
        serve(registry, args.host or registry.dns_address, args.port or registry.dns_port)
        return 0
    if args.command == "status":
        print(json.dumps(registry.status(), indent=2, sort_keys=True))
        return 0
    qtypes = {"A": TYPE_A, "SRV": TYPE_SRV, "PTR": TYPE_PTR, "SOA": TYPE_SOA, "NS": TYPE_NS, "TXT": TYPE_TXT}
    answer = query_server(args.host or registry.dns_address, args.port or registry.dns_port, args.name, qtypes[args.type], tcp=args.tcp)
    print(json.dumps(answer, indent=2, sort_keys=True))
    return 0 if answer.get("rcode") == RCODE_NOERROR else 1


if __name__ == "__main__":
    raise SystemExit(main())
