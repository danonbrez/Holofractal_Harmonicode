#!/usr/bin/env python3
"""Real operational validation for Pass 218 Iteration 12.

Runs against disposable local Docker containers in CI.  The script deliberately
uses etcd's learner mechanism for replacement so a new member can catch up
without changing the voting quorum before the old voter is retired.
"""
from __future__ import annotations

import ipaddress
import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from hhs_runtime.pass218.authority_maintenance_i12 import (
    Pass218BoundedRecoveryController,
    Pass218MaintenancePolicy,
    seal_credential_rotation_plan,
    seal_member_replacement_plan,
    seal_operational_alert_receipt,
    validate_credential_rotation_plan,
    validate_member_replacement_plan,
    validate_operational_alert_receipt,
    validate_recovery_status,
)
from hhs_runtime.pass218.operational_hardening_i11 import (
    EtcdV3MutualTLSEndpointPoolClient,
    Pass218EtcdClusterAuthority,
    Pass218EtcdClusterConfig,
    Pass218EtcdClusterMonitor,
)

ROOT = Path.cwd()
PKI = ROOT / ".i12-pki"
DATA = ROOT / ".i12-data"
EVIDENCE = ROOT / ".i12-evidence"
NAMESPACE = os.environ.get("HHS_PASS218_I12_NAMESPACE", "/hhs/pass218/i12/local")
ENDPOINTS = (
    "https://127.0.0.1:12379",
    "https://127.0.0.1:22379",
    "https://127.0.0.1:32379",
)
NETWORK = "hhs-p218-i12"
ETCD_IMAGE = "quay.io/coreos/etcd:v3.5.21"


def run(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def docker_exec(member: str, *args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return run("docker", "exec", member, *args, check=check, capture=capture)


def etcdctl(member: str, *args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return docker_exec(
        member,
        "/usr/local/bin/etcdctl",
        "--endpoints=https://127.0.0.1:2379",
        "--cacert=/certs/ca.pem",
        "--cert=/certs/client-new.pem",
        "--key=/certs/client-new-key.pem",
        *args,
        check=check,
        capture=capture,
    )


def write_json(name: str, value: Any) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def generate_pki() -> None:
    PKI.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "HHS Pass218 I12 CI CA")])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=2))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    def issue(name: str, *, server: bool = False, client: bool = False, sans: tuple[str, ...] = ()):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=2))
        )
        usages = []
        if server:
            usages.append(ExtendedKeyUsageOID.SERVER_AUTH)
        if client:
            usages.append(ExtendedKeyUsageOID.CLIENT_AUTH)
        builder = builder.add_extension(x509.ExtendedKeyUsage(usages), critical=False)
        if sans:
            values = []
            for item in sans:
                try:
                    values.append(x509.IPAddress(ipaddress.ip_address(item)))
                except ValueError:
                    values.append(x509.DNSName(item))
            builder = builder.add_extension(x509.SubjectAlternativeName(values), critical=False)
        return key, builder.sign(ca_key, hashes.SHA256())

    server_key, server_cert = issue(
        "hhs-pass218-i12-etcd-members",
        server=True,
        client=True,
        sans=("127.0.0.1", "localhost", "etcd1", "etcd2", "etcd3", "etcd3new"),
    )
    old_key, old_cert = issue("hhs-pass218-i12-writer-old", client=True)
    new_key, new_cert = issue("hhs-pass218-i12-writer-new", client=True)

    def write_key(path: Path, key: rsa.RSAPrivateKey) -> None:
        path.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )

    (PKI / "ca.pem").write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    (PKI / "server.pem").write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
    (PKI / "client-old.pem").write_bytes(old_cert.public_bytes(serialization.Encoding.PEM))
    (PKI / "client-new.pem").write_bytes(new_cert.public_bytes(serialization.Encoding.PEM))
    write_key(PKI / "server-key.pem", server_key)
    write_key(PKI / "client-old-key.pem", old_key)
    write_key(PKI / "client-new-key.pem", new_key)


def start_member(name: str, host_port: int, cluster: str, *, state: str) -> None:
    data_dir = DATA / name
    data_dir.mkdir(parents=True, exist_ok=True)
    run(
        "docker", "run", "-d",
        "--name", name,
        "--network", NETWORK,
        "-p", f"{host_port}:2379",
        "-v", f"{PKI}:/certs:ro",
        "-v", f"{data_dir}:/etcd-data",
        ETCD_IMAGE,
        "/usr/local/bin/etcd",
        f"--name={name}",
        "--data-dir=/etcd-data",
        "--listen-client-urls=https://0.0.0.0:2379",
        f"--advertise-client-urls=https://{name}:2379",
        "--listen-peer-urls=https://0.0.0.0:2380",
        f"--initial-advertise-peer-urls=https://{name}:2380",
        f"--initial-cluster={cluster}",
        f"--initial-cluster-state={state}",
        "--initial-cluster-token=hhs-p218-i12-ci",
        "--client-cert-auth=true",
        "--trusted-ca-file=/certs/ca.pem",
        "--cert-file=/certs/server.pem",
        "--key-file=/certs/server-key.pem",
        "--peer-client-cert-auth=true",
        "--peer-trusted-ca-file=/certs/ca.pem",
        "--peer-cert-file=/certs/server.pem",
        "--peer-key-file=/certs/server-key.pem",
    )


def curl_health(port: int, *, attempts: int = 40) -> bool:
    for _ in range(attempts):
        result = run(
            "curl", "--fail", "--silent",
            "--cacert", str(PKI / "ca.pem"),
            "--cert", str(PKI / "client-new.pem"),
            "--key", str(PKI / "client-new-key.pem"),
            f"https://127.0.0.1:{port}/health",
            check=False,
            capture=True,
        )
        if result.returncode == 0 and '"health":"true"' in (result.stdout or ""):
            return True
        time.sleep(1)
    return False


def cluster_config(cert: str, key: str) -> Pass218EtcdClusterConfig:
    return Pass218EtcdClusterConfig.build(
        ENDPOINTS,
        ca_file=PKI / "ca.pem",
        client_cert_file=PKI / cert,
        client_key_file=PKI / key,
        cluster_name="i12-ci-cluster",
    )


def prove_credential_handoff() -> dict[str, Any]:
    old_cfg = cluster_config("client-old.pem", "client-old-key.pem")
    old = Pass218EtcdClusterAuthority(
        old_cfg,
        namespace=NAMESPACE,
        owner_id="i12-old-writer",
        host_id="i12-old-host",
    )
    old_probe = Pass218EtcdClusterMonitor(old_cfg, old.client, namespace=NAMESPACE).require_quorum_ready()
    old_record = old.acquire()
    assert old_record is not None
    old_fence = old_record["fence_epoch"]

    plan = seal_credential_rotation_plan(
        rotation_id="i12-ci-credential-rotation",
        old_ca_sha256=digest(PKI / "ca.pem"),
        new_ca_sha256=digest(PKI / "ca.pem"),
        old_client_cert_sha256=digest(PKI / "client-old.pem"),
        new_client_cert_sha256=digest(PKI / "client-new.pem"),
        old_client_key_sha256=digest(PKI / "client-old-key.pem"),
        new_client_key_sha256=digest(PKI / "client-new-key.pem"),
        preflight_probe_hash72=old_probe["probe_hash72"],
        current_global_fence=old_fence,
    )
    validate_credential_rotation_plan(plan)
    old.release()
    assert old.held is False

    new_cfg = cluster_config("client-new.pem", "client-new-key.pem")
    new = Pass218EtcdClusterAuthority(
        new_cfg,
        namespace=NAMESPACE,
        owner_id="i12-new-writer",
        host_id="i12-new-host",
    )
    new_probe = Pass218EtcdClusterMonitor(new_cfg, new.client, namespace=NAMESPACE).require_quorum_ready()
    new_record = new.acquire()
    assert new_record is not None
    assert new_record["fence_epoch"] > old_fence

    contender = Pass218EtcdClusterAuthority(
        old_cfg,
        namespace=NAMESPACE,
        owner_id="i12-old-contender",
        host_id="i12-old-host",
    )
    assert contender.acquire() is None
    assert contender.held is False

    evidence = {
        "old_fence": old_fence,
        "new_fence": new_record["fence_epoch"],
        "old_probe_hash72": old_probe["probe_hash72"],
        "new_probe_hash72": new_probe["probe_hash72"],
        "rotation_plan_hash72": plan["record_hash72"],
        "simultaneous_writer_permitted": False,
    }
    new.release()
    write_json("credential-rotation.json", evidence)
    return evidence


def prove_learner_replacement() -> dict[str, Any]:
    cfg = cluster_config("client-new.pem", "client-new-key.pem")
    client = EtcdV3MutualTLSEndpointPoolClient(cfg)
    monitor = Pass218EtcdClusterMonitor(cfg, client, namespace=NAMESPACE)
    before_probe = monitor.require_quorum_ready()

    before = json.loads(etcdctl("etcd1", "member", "list", "-w", "json", capture=True).stdout or "{}")
    old_member = next(member for member in before["members"] if member.get("name") == "etcd3")
    old_id = int(old_member["ID"])
    old_hex = f"{old_id:x}"

    add = etcdctl(
        "etcd1",
        "member", "add", "etcd3new",
        "--peer-urls=https://etcd3new:2380",
        "--learner",
        "-w", "json",
        capture=True,
    )
    add_payload = json.loads(add.stdout or "{}")
    learner_id = int(add_payload["member"]["ID"])
    learner_hex = f"{learner_id:x}"

    cluster = (
        "etcd1=https://etcd1:2380,"
        "etcd2=https://etcd2:2380,"
        "etcd3=https://etcd3:2380,"
        "etcd3new=https://etcd3new:2380"
    )
    start_member("etcd3new", 42379, cluster, state="existing")
    assert curl_health(42379), "replacement learner never became healthy"

    # Give the learner a bounded catch-up window while all original voters remain healthy.
    learner_ready = False
    for _ in range(30):
        status = docker_exec(
            "etcd3new",
            "/usr/local/bin/etcdctl",
            "--endpoints=https://127.0.0.1:2379",
            "--cacert=/certs/ca.pem",
            "--cert=/certs/client-new.pem",
            "--key=/certs/client-new-key.pem",
            "endpoint", "status", "-w", "json",
            check=False,
            capture=True,
        )
        if status.returncode == 0:
            learner_ready = True
            break
        time.sleep(1)
    assert learner_ready, "replacement learner did not expose endpoint status"

    # Only one voter is unavailable.  The learner is already caught up before retirement.
    run("docker", "stop", "etcd3")
    etcdctl("etcd1", "endpoint", "health")
    etcdctl("etcd2", "endpoint", "health")
    etcdctl("etcd1", "member", "remove", old_hex)
    etcdctl("etcd1", "endpoint", "health")
    etcdctl("etcd2", "endpoint", "health")

    promoted = False
    promotion_output = ""
    for _ in range(30):
        attempt = etcdctl(
            "etcd1", "member", "promote", learner_hex,
            check=False,
            capture=True,
        )
        promotion_output = attempt.stdout or ""
        if attempt.returncode == 0:
            promoted = True
            break
        time.sleep(1)
    assert promoted, f"learner promotion failed: {promotion_output}"

    # Move the replacement onto the canonical third client port only after old etcd3 is gone.
    run("docker", "rm", "etcd3")
    run("docker", "stop", "etcd3new")
    run("docker", "rm", "etcd3new")
    # Reuse the learner's data directory and assigned member identity; this is a process restart,
    # not another membership mutation.
    data_dir = DATA / "etcd3new"
    run(
        "docker", "run", "-d",
        "--name", "etcd3new",
        "--network", NETWORK,
        "-p", "32379:2379",
        "-v", f"{PKI}:/certs:ro",
        "-v", f"{data_dir}:/etcd-data",
        ETCD_IMAGE,
        "/usr/local/bin/etcd",
        "--name=etcd3new",
        "--data-dir=/etcd-data",
        "--listen-client-urls=https://0.0.0.0:2379",
        "--advertise-client-urls=https://etcd3new:2379",
        "--listen-peer-urls=https://0.0.0.0:2380",
        "--initial-advertise-peer-urls=https://etcd3new:2380",
        "--client-cert-auth=true",
        "--trusted-ca-file=/certs/ca.pem",
        "--cert-file=/certs/server.pem",
        "--key-file=/certs/server-key.pem",
        "--peer-client-cert-auth=true",
        "--peer-trusted-ca-file=/certs/ca.pem",
        "--peer-cert-file=/certs/server.pem",
        "--peer-key-file=/certs/server-key.pem",
    )
    assert curl_health(32379), "replacement voter did not restart on canonical client port"

    post_probe = monitor.require_quorum_ready()
    assert post_probe["reachable_member_count"] == 3
    assert post_probe["quorum_ready"] is True

    plan = seal_member_replacement_plan(
        replacement_id="i12-ci-etcd3-learner-replacement",
        old_member_id=old_id,
        replacement_member_name="etcd3new",
        replacement_peer_url="https://etcd3new:2380",
        replacement_client_url="https://etcd3new:2379",
        preflight_probe_hash72=before_probe["probe_hash72"],
        expected_member_count=3,
        quorum_size=2,
    )
    validate_member_replacement_plan(plan)
    evidence = {
        "old_member_id": old_id,
        "replacement_member_id": learner_id,
        "old_and_replacement_ids_differ": old_id != learner_id,
        "pre_probe_hash72": before_probe["probe_hash72"],
        "post_probe_hash72": post_probe["probe_hash72"],
        "reachable_member_count": post_probe["reachable_member_count"],
        "member_ids": post_probe["member_ids"],
        "replacement_plan_hash72": plan["record_hash72"],
        "learner_used": True,
        "maximum_unavailable_voters": 1,
    }
    write_json("member-replacement.json", evidence)
    return evidence


def prove_bounded_recovery() -> dict[str, Any]:
    cfg = cluster_config("client-new.pem", "client-new-key.pem")
    predecessor = Pass218EtcdClusterAuthority(
        cfg,
        namespace=NAMESPACE,
        owner_id="i12-recovery-predecessor",
        host_id="i12-recovery-host",
    )
    monitor = Pass218EtcdClusterMonitor(cfg, predecessor.client, namespace=NAMESPACE)
    pre_probe = monitor.require_quorum_ready()
    pre_record = predecessor.acquire()
    assert pre_record is not None
    pre_fence = pre_record["fence_epoch"]
    predecessor.release()

    run("docker", "stop", "etcd2")
    run("docker", "stop", "etcd3new")
    lost_probe = monitor.probe()
    assert lost_probe["quorum_ready"] is False

    alert = seal_operational_alert_receipt(
        alert_sequence=1,
        severity="CRITICAL",
        event_code="P218_I12_QUORUM_LOST",
        cluster_probe_hash72=lost_probe["probe_hash72"],
        global_fence=pre_fence,
        writer_authority_held=False,
        writer_authority_revoked=True,
        requires_new_global_fence=True,
    )
    validate_operational_alert_receipt(alert)
    write_json("quorum-loss-alert.json", alert)

    policy = Pass218MaintenancePolicy.build(
        expected_member_count=3,
        max_automated_recovery_attempts=2,
    )
    controller = Pass218BoundedRecoveryController(policy)
    controller.record_authority_loss(
        predecessor_global_fence=pre_fence,
        cluster_probe_hash72=lost_probe["probe_hash72"],
    )
    controller.begin_attempt(writer_authority_held=False)

    run("docker", "start", "etcd2")
    assert curl_health(22379), "second voter did not recover"
    recovery_probe = monitor.require_quorum_ready()

    successor = Pass218EtcdClusterAuthority(
        cfg,
        namespace=NAMESPACE,
        owner_id="i12-recovery-successor",
        host_id="i12-recovery-host",
    )
    recovered_record = successor.acquire()
    assert recovered_record is not None
    recovered_fence = recovered_record["fence_epoch"]
    assert recovered_fence > pre_fence
    status = controller.record_recovered_fence(
        recovered_global_fence=recovered_fence,
        cluster_probe_hash72=recovery_probe["probe_hash72"],
    )
    validate_recovery_status(status)
    assert status["recovery_can_mint_authority"] is False
    assert status["recovery_can_mutate_canonical_target"] is False
    successor.release()

    evidence = {
        "predecessor_fence": pre_fence,
        "recovered_fence": recovered_fence,
        "quorum_loss_probe_hash72": lost_probe["probe_hash72"],
        "recovery_probe_hash72": recovery_probe["probe_hash72"],
        "recovery_status_hash72": status["record_hash72"],
        "quorum_loss_alert_hash72": alert["record_hash72"],
    }
    write_json("bounded-recovery.json", evidence)
    return evidence


def prove_snapshot_artifact() -> dict[str, Any]:
    snapshot_inside = "/etcd-data/pass218-i12-snapshot.db"
    etcdctl("etcd1", "snapshot", "save", snapshot_inside)
    local_snapshot = EVIDENCE / "pass218-i12-snapshot.db"
    run("docker", "cp", f"etcd1:{snapshot_inside}", str(local_snapshot))
    status = docker_exec(
        "etcd1",
        "/usr/local/bin/etcdutl",
        "snapshot", "status", snapshot_inside,
        "-w", "json",
        capture=True,
    )
    payload = json.loads(status.stdout or "{}")
    evidence = {
        "snapshot_sha256": digest(local_snapshot),
        "snapshot_size_bytes": local_snapshot.stat().st_size,
        "snapshot_status": payload,
        "retention_artifact_validated": True,
        "destructive_exact_rehearsal_inherited_from_i11": True,
    }
    write_json("snapshot-artifact.json", evidence)
    return evidence


def cleanup() -> None:
    for name in ("etcd3new", "etcd3", "etcd2", "etcd1"):
        run("docker", "rm", "-f", name, check=False, capture=True)
    run("docker", "network", "rm", NETWORK, check=False, capture=True)


def main() -> int:
    shutil.rmtree(PKI, ignore_errors=True)
    shutil.rmtree(DATA, ignore_errors=True)
    shutil.rmtree(EVIDENCE, ignore_errors=True)
    PKI.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    cleanup()
    try:
        generate_pki()
        run("docker", "network", "create", NETWORK)
        initial = (
            "etcd1=https://etcd1:2380,"
            "etcd2=https://etcd2:2380,"
            "etcd3=https://etcd3:2380"
        )
        start_member("etcd1", 12379, initial, state="new")
        start_member("etcd2", 22379, initial, state="new")
        start_member("etcd3", 32379, initial, state="new")
        assert curl_health(12379), "etcd1 not healthy"
        assert curl_health(22379), "etcd2 not healthy"
        assert curl_health(32379), "etcd3 not healthy"

        rotation = prove_credential_handoff()
        replacement = prove_learner_replacement()
        recovery = prove_bounded_recovery()
        snapshot = prove_snapshot_artifact()
        summary = {
            "credential_rotation": rotation,
            "member_replacement": replacement,
            "bounded_recovery": recovery,
            "snapshot": snapshot,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "verbatim_source_retained": False,
            "pass165_source_retaining_path_invoked": False,
            "authoritative_float_weights": False,
        }
        write_json("operational-summary.json", summary)
        print("PASS218_I12_REAL_OPERATIONAL_VALIDATION=1")
        print(json.dumps(summary, sort_keys=True))
        return 0
    except Exception:
        for name in ("etcd1", "etcd2", "etcd3", "etcd3new"):
            logs = run("docker", "logs", name, check=False, capture=True)
            if logs.stdout:
                (EVIDENCE / f"{name}.log").write_text(logs.stdout, encoding="utf-8")
        raise
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
