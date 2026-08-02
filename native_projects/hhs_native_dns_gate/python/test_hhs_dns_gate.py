import json
import socket
import struct
import tempfile
import threading
import unittest
from pathlib import Path

from hhs_dns_gate import (
    CLASS_IN,
    DNSAuthority,
    RCODE_NXDOMAIN,
    RCODE_NOERROR,
    RCODE_REFUSED,
    Registry,
    TCPHandler,
    TYPE_A,
    TYPE_AAAA,
    TYPE_NS,
    TYPE_PTR,
    TYPE_SOA,
    TYPE_SRV,
    TYPE_TXT,
    ThreadingTCP,
    ThreadingUDP,
    UDPHandler,
    build_query,
    parse_first_answer,
    query_server,
    reverse_name,
)


REGISTRY = {
    "schema": "HHS_NATIVE_DNS_GATE_REGISTRY_V1",
    "zone": "hhs.internal",
    "ttl": 30,
    "dns": {"name": "dns-gate.hhs.internal", "address": "127.0.0.55", "port": 53},
    "services": [
        {"service_id": "pass189.iteration2", "name": "pass189-calibration.hhs.internal", "aliases": ["pass189-i2.hhs.internal"], "address": "127.189.0.2", "port": 8190, "protocol": "http"},
        {"service_id": "pass190.runtime", "name": "pass190-runtime.hhs.internal", "aliases": ["pass190.hhs.internal"], "address": "127.190.0.1", "port": 8190, "protocol": "http"},
    ],
}


class GateTests(unittest.TestCase):
    def setUp(self):
        self.registry = Registry(REGISTRY)
        self.authority = DNSAuthority(self.registry)

    def test_same_port_distinct_loopback_addresses(self):
        status = self.registry.status()
        self.assertTrue(status["conflict_resolved"])
        services = {item["service_id"]: item for item in status["services"]}
        self.assertEqual(services["pass189.iteration2"]["port"], 8190)
        self.assertEqual(services["pass190.runtime"]["port"], 8190)
        self.assertNotEqual(services["pass189.iteration2"]["address"], services["pass190.runtime"]["address"])

    def test_registry_and_conflict_witnesses(self):
        status = self.registry.status()
        self.assertEqual(len(status["registry_hash72"]), 72)
        self.assertEqual(len(status["conflict_resolution_hash72"]), 72)
        self.assertEqual(status["registry_hash72"], Registry(json.loads(json.dumps(REGISTRY))).status()["registry_hash72"])

    def test_a_records(self):
        left = parse_first_answer(self.authority.answer(build_query("pass189-calibration.hhs.internal", TYPE_A)))
        right = parse_first_answer(self.authority.answer(build_query("pass190-runtime.hhs.internal", TYPE_A)))
        self.assertEqual(left["address"], "127.189.0.2")
        self.assertEqual(right["address"], "127.190.0.1")

    def test_alias_record(self):
        answer = parse_first_answer(self.authority.answer(build_query("pass190.hhs.internal", TYPE_A)))
        self.assertEqual(answer["address"], "127.190.0.1")

    def test_srv_records_preserve_canonical_port(self):
        answer = parse_first_answer(self.authority.answer(build_query("_http._tcp.pass190-runtime.hhs.internal", TYPE_SRV)))
        self.assertEqual(answer["port"], 8190)
        self.assertEqual(answer["target"], "pass190-runtime.hhs.internal")

    def test_ptr_records(self):
        answer = parse_first_answer(self.authority.answer(build_query(reverse_name("127.190.0.1"), TYPE_PTR)))
        self.assertEqual(answer["target"], "pass190-runtime.hhs.internal")


    def test_ns_authority_record(self):
        answer = parse_first_answer(self.authority.answer(build_query("hhs.internal", TYPE_NS)))
        self.assertEqual(answer["target"], "dns-gate.hhs.internal")

    def test_soa_authority_record(self):
        answer = parse_first_answer(self.authority.answer(build_query("hhs.internal", TYPE_SOA)))
        self.assertEqual(answer["type"], TYPE_SOA)
        self.assertEqual(answer["answer_count"], 1)

    def test_txt_registry_record(self):
        answer = parse_first_answer(self.authority.answer(build_query("_gate.hhs.internal", TYPE_TXT)))
        self.assertEqual(answer["type"], TYPE_TXT)
        self.assertEqual(answer["answer_count"], 1)

    def test_unknown_in_zone_is_nxdomain(self):
        answer = parse_first_answer(self.authority.answer(build_query("missing.hhs.internal", TYPE_A)))
        self.assertEqual(answer["rcode"], RCODE_NXDOMAIN)

    def test_outside_zone_is_refused(self):
        answer = parse_first_answer(self.authority.answer(build_query("example.com", TYPE_A)))
        self.assertEqual(answer["rcode"], RCODE_REFUSED)

    def test_aaaa_is_empty_noerror(self):
        answer = parse_first_answer(self.authority.answer(build_query("pass190-runtime.hhs.internal", TYPE_AAAA)))
        self.assertEqual(answer["rcode"], RCODE_NOERROR)
        self.assertEqual(answer["answer_count"], 0)

    def test_duplicate_endpoint_rejected(self):
        bad = json.loads(json.dumps(REGISTRY))
        bad["services"].append({"service_id": "bad", "name": "bad.hhs.internal", "address": "127.190.0.1", "port": 8190, "protocol": "http"})
        with self.assertRaises(ValueError):
            Registry(bad)

    def test_non_loopback_rejected(self):
        bad = json.loads(json.dumps(REGISTRY))
        bad["services"][0]["address"] = "10.0.0.2"
        with self.assertRaises(ValueError):
            Registry(bad)

    def test_udp_and_tcp_servers(self):
        udp = ThreadingUDP(("127.0.0.1", 0), UDPHandler)
        port = udp.server_address[1]
        tcp = ThreadingTCP(("127.0.0.1", port), TCPHandler)
        udp.authority = self.authority
        tcp.authority = self.authority
        threads = [threading.Thread(target=udp.serve_forever, daemon=True), threading.Thread(target=tcp.serve_forever, daemon=True)]
        for thread in threads:
            thread.start()
        try:
            udp_answer = query_server("127.0.0.1", port, "pass189-i2.hhs.internal", TYPE_A)
            tcp_answer = query_server("127.0.0.1", port, "_http._tcp.pass190.hhs.internal", TYPE_SRV, tcp=True)
            self.assertEqual(udp_answer["address"], "127.189.0.2")
            self.assertEqual(tcp_answer["port"], 8190)
        finally:
            udp.shutdown(); tcp.shutdown(); udp.server_close(); tcp.server_close()


if __name__ == "__main__":
    unittest.main()
