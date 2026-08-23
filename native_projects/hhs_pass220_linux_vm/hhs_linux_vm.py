#!/usr/bin/env python3
"""Pass 220 non-promotional Linux VM bootstrap.

This module builds and launches a deterministic QEMU/KVM guest plan. The guest
is an execution and interface container only: canonical HHS mutation remains
behind the inherited backend and singleton VM81/kernel authority path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path
import platform
import shutil
import sys
from typing import Any, Mapping, Sequence

SCHEMA = "HHS_P220_LINUX_VM_BOOTSTRAP_V0"
CONFIG_SCHEMA = "HHS_P220_LINUX_VM_CONFIG_V0"
PROMOTION_STATUS = "NON_PROMOTIONAL_PREIMPLEMENTATION"
AUTHORITY_PATH = "INHERITED_HHS_API_TO_SINGLETON_VM81_KERNEL"
CANONICAL_MUTATION_AUTHORITY = False
CANONICAL_PERSISTENCE_AUTHORITY = False
CANONICAL_HASH72_AUTHORITY = False
SUPPORTED_ARCHITECTURES = ("x86_64",)
SUPPORTED_ACCELERATION = ("auto", "kvm", "tcg")
SUPPORTED_DISPLAYS = ("gtk", "none")
SUPPORTED_NETWORKS = ("user", "none")
SUPPORTED_DISK_FORMATS = ("qcow2", "raw")


@dataclass(frozen=True)
class VMConfig:
    schema: str = CONFIG_SCHEMA
    guest_name: str = "HHS-Linux-VM"
    architecture: str = "x86_64"
    machine: str = "q35"
    acceleration: str = "auto"
    vcpus: int = 4
    memory_mib: int = 4096
    disk_image: str = ".hhs/vm/hhs-linux.qcow2"
    disk_format: str = "qcow2"
    display: str = "gtk"
    network: str = "user"
    api_host: str = "10.0.2.2"
    api_port: int = 8080

    def validate(self) -> None:
        if self.schema != CONFIG_SCHEMA:
            raise ValueError(f"unsupported config schema: {self.schema!r}")
        if self.architecture not in SUPPORTED_ARCHITECTURES:
            raise ValueError(f"unsupported architecture: {self.architecture!r}")
        if self.acceleration not in SUPPORTED_ACCELERATION:
            raise ValueError(f"unsupported acceleration: {self.acceleration!r}")
        if self.display not in SUPPORTED_DISPLAYS:
            raise ValueError(f"unsupported display: {self.display!r}")
        if self.network not in SUPPORTED_NETWORKS:
            raise ValueError(f"unsupported network: {self.network!r}")
        if self.disk_format not in SUPPORTED_DISK_FORMATS:
            raise ValueError(f"unsupported disk format: {self.disk_format!r}")
        if not self.guest_name or not self.machine or not self.disk_image:
            raise ValueError("guest_name, machine, and disk_image must be non-empty")
        if isinstance(self.vcpus, bool) or not isinstance(self.vcpus, int) or self.vcpus <= 0:
            raise ValueError("vcpus must be a positive integer")
        if isinstance(self.memory_mib, bool) or not isinstance(self.memory_mib, int) or self.memory_mib <= 0:
            raise ValueError("memory_mib must be a positive integer")
        if isinstance(self.api_port, bool) or not isinstance(self.api_port, int) or not (1 <= self.api_port <= 65535):
            raise ValueError("api_port must be an integer in 1..65535")
        if not self.api_host:
            raise ValueError("api_host must be non-empty")


def canonical_config_bytes(config: VMConfig) -> bytes:
    config.validate()
    return json.dumps(
        asdict(config),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def config_identity(config: VMConfig) -> str:
    return hashlib.sha256(canonical_config_bytes(config)).hexdigest()


def load_config(path: str | os.PathLike[str]) -> VMConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("VM config must be a JSON object")
    allowed = set(VMConfig.__dataclass_fields__)
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"unknown config keys: {unknown}")
    config = VMConfig(**payload)
    config.validate()
    return config


def probe_host(qemu_binary: str | None = None) -> dict[str, Any]:
    system = platform.system()
    machine = platform.machine()
    qemu = qemu_binary or shutil.which("qemu-system-x86_64")
    kvm_path = Path("/dev/kvm")
    kvm_exists = kvm_path.exists()
    kvm_readable = os.access(kvm_path, os.R_OK) if kvm_exists else False
    kvm_writable = os.access(kvm_path, os.W_OK) if kvm_exists else False
    kvm_usable = system == "Linux" and kvm_exists and kvm_readable and kvm_writable
    return {
        "schema": "HHS_P220_LINUX_VM_HOST_PROBE_V0",
        "promotion_status": PROMOTION_STATUS,
        "host_system": system,
        "host_machine": machine,
        "linux_host": system == "Linux",
        "qemu_binary": qemu,
        "qemu_available": bool(qemu),
        "kvm_device": str(kvm_path),
        "kvm_exists": kvm_exists,
        "kvm_readable": kvm_readable,
        "kvm_writable": kvm_writable,
        "kvm_usable": kvm_usable,
        "canonical_mutation_authority": CANONICAL_MUTATION_AUTHORITY,
        "canonical_persistence_authority": CANONICAL_PERSISTENCE_AUTHORITY,
        "canonical_hash72_authority": CANONICAL_HASH72_AUTHORITY,
    }


def resolve_acceleration(config: VMConfig, host_probe: Mapping[str, Any]) -> str:
    config.validate()
    if config.acceleration == "auto":
        return "kvm" if bool(host_probe.get("kvm_usable")) else "tcg"
    if config.acceleration == "kvm" and not bool(host_probe.get("kvm_usable")):
        raise RuntimeError("KVM was required but /dev/kvm is not usable")
    return config.acceleration


def build_qemu_argv(
    config: VMConfig,
    *,
    host_probe: Mapping[str, Any] | None = None,
    qemu_binary: str | None = None,
) -> list[str]:
    config.validate()
    probe = dict(host_probe or probe_host(qemu_binary=qemu_binary))
    qemu = qemu_binary or probe.get("qemu_binary") or "qemu-system-x86_64"
    acceleration = resolve_acceleration(config, probe)
    cpu = "host" if acceleration == "kvm" else "max"

    argv = [
        str(qemu),
        "-name", config.guest_name,
        "-machine", f"{config.machine},accel={acceleration}",
        "-cpu", cpu,
        "-smp", str(config.vcpus),
        "-m", str(config.memory_mib),
        "-drive", f"file={config.disk_image},if=virtio,format={config.disk_format}",
        "-device", "virtio-rng-pci",
        "-device", "virtio-balloon-pci",
    ]

    if config.display == "gtk":
        argv.extend(["-display", "gtk", "-device", "virtio-vga"])
    else:
        argv.append("-nographic")

    if config.network == "user":
        argv.extend([
            "-netdev", "user,id=hhsnet",
            "-device", "virtio-net-pci,netdev=hhsnet",
        ])
    else:
        argv.extend(["-nic", "none"])
    return argv


def build_vm_plan(
    config: VMConfig,
    *,
    host_probe: Mapping[str, Any] | None = None,
    qemu_binary: str | None = None,
) -> dict[str, Any]:
    config.validate()
    probe = dict(host_probe or probe_host(qemu_binary=qemu_binary))
    acceleration = resolve_acceleration(config, probe)
    argv = build_qemu_argv(config, host_probe=probe, qemu_binary=qemu_binary)
    return {
        "schema": SCHEMA,
        "promotion_status": PROMOTION_STATUS,
        "config_identity_sha256": config_identity(config),
        "guest_name": config.guest_name,
        "architecture": config.architecture,
        "resolved_acceleration": acceleration,
        "qemu_argv": argv,
        "guest_api_endpoint": f"http://{config.api_host}:{config.api_port}",
        "network_boundary": (
            "QEMU_USER_MODE_HOST_ACCESS_ONLY_BY_DEFAULT"
            if config.network == "user"
            else "NO_GUEST_NETWORK"
        ),
        "authority_path": AUTHORITY_PATH,
        "guest_is_canonical_authority": False,
        "canonical_mutation_authority": CANONICAL_MUTATION_AUTHORITY,
        "canonical_persistence_authority": CANONICAL_PERSISTENCE_AUTHORITY,
        "canonical_hash72_authority": CANONICAL_HASH72_AUTHORITY,
        "web_frontend_status": "DEPRECATED_COMPATIBILITY_ONLY",
        "host_probe": probe,
    }


def _json_dump(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True, indent=2))


def _config_from_args(args: argparse.Namespace) -> VMConfig:
    config = load_config(args.config)
    if args.disk:
        config = replace(config, disk_image=args.disk)
    if args.acceleration:
        config = replace(config, acceleration=args.acceleration)
    if args.display:
        config = replace(config, display=args.display)
    if args.network:
        config = replace(config, network=args.network)
    config.validate()
    return config


def _run(config: VMConfig, *, dry_run: bool) -> int:
    probe = probe_host()
    plan = build_vm_plan(config, host_probe=probe)
    if dry_run:
        _json_dump(plan)
        return 0
    if not probe["linux_host"]:
        raise RuntimeError("Pass 220 VM bootstrap currently requires a Linux host")
    if not probe["qemu_available"]:
        raise RuntimeError("qemu-system-x86_64 is not installed or not on PATH")
    disk_path = Path(config.disk_image)
    if not disk_path.is_file():
        raise RuntimeError(f"guest disk image does not exist: {disk_path}")
    argv = plan["qemu_argv"]
    os.execv(str(argv[0]), argv)
    return 0


def build_parser() -> argparse.ArgumentParser:
    default_config = Path(__file__).with_name("config") / "hhs-vm.default.json"
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    probe_parser = sub.add_parser("probe", help="inspect host QEMU/KVM capability")
    probe_parser.add_argument("--qemu-binary")

    for command in ("plan", "run"):
        item = sub.add_parser(command, help=f"{command} the HHS Linux VM bootstrap")
        item.add_argument("--config", default=str(default_config))
        item.add_argument("--disk")
        item.add_argument("--acceleration", choices=SUPPORTED_ACCELERATION)
        item.add_argument("--display", choices=SUPPORTED_DISPLAYS)
        item.add_argument("--network", choices=SUPPORTED_NETWORKS)
        if command == "run":
            item.add_argument("--dry-run", action="store_true")

    sub.add_parser("manifest", help="emit immutable authority/deprecation metadata")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "probe":
            _json_dump(probe_host(qemu_binary=args.qemu_binary))
            return 0
        if args.command == "manifest":
            _json_dump({
                "schema": SCHEMA,
                "promotion_status": PROMOTION_STATUS,
                "authority_path": AUTHORITY_PATH,
                "canonical_mutation_authority": CANONICAL_MUTATION_AUTHORITY,
                "canonical_persistence_authority": CANONICAL_PERSISTENCE_AUTHORITY,
                "canonical_hash72_authority": CANONICAL_HASH72_AUTHORITY,
                "web_frontend_status": "DEPRECATED_COMPATIBILITY_ONLY",
                "preferred_local_interface": "HHS_PASS220_NATIVE_LINUX_VM",
            })
            return 0
        config = _config_from_args(args)
        if args.command == "plan":
            _json_dump(build_vm_plan(config))
            return 0
        if args.command == "run":
            return _run(config, dry_run=bool(args.dry_run))
        raise RuntimeError(f"unhandled command: {args.command}")
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"hhs-linux-vm: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
