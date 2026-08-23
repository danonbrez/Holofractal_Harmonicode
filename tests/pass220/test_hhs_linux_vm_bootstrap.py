from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from native_projects.hhs_pass220_linux_vm.hhs_linux_vm import (
    AUTHORITY_PATH,
    CANONICAL_HASH72_AUTHORITY,
    CANONICAL_MUTATION_AUTHORITY,
    CANONICAL_PERSISTENCE_AUTHORITY,
    CONFIG_SCHEMA,
    PROMOTION_STATUS,
    VMConfig,
    build_qemu_argv,
    build_vm_plan,
    canonical_config_bytes,
    config_identity,
    load_config,
    resolve_acceleration,
)


DEFAULT_CONFIG = ROOT / "native_projects/hhs_pass220_linux_vm/config/hhs-vm.default.json"


class LinuxVMBootstrapTests(unittest.TestCase):
    def test_default_config_identity_is_stable(self) -> None:
        config = load_config(DEFAULT_CONFIG)
        self.assertEqual(config.schema, CONFIG_SCHEMA)
        self.assertEqual(
            config_identity(config),
            "d5e5e1b6e0aa43bb492383d343453145e8c09b8f2cae2c544700e8b951149b31",
        )
        reordered = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        reordered = dict(reversed(list(reordered.items())))
        self.assertEqual(
            canonical_config_bytes(VMConfig(**reordered)),
            canonical_config_bytes(config),
        )

    def test_auto_acceleration_prefers_kvm_then_tcg(self) -> None:
        config = load_config(DEFAULT_CONFIG)
        self.assertEqual(resolve_acceleration(config, {"kvm_usable": True}), "kvm")
        self.assertEqual(resolve_acceleration(config, {"kvm_usable": False}), "tcg")
        with self.assertRaises(RuntimeError):
            resolve_acceleration(replace(config, acceleration="kvm"), {"kvm_usable": False})

    def test_tcg_plan_is_deterministic_and_projection_only(self) -> None:
        config = replace(load_config(DEFAULT_CONFIG), acceleration="tcg")
        probe = {
            "linux_host": True,
            "qemu_available": True,
            "qemu_binary": "/usr/bin/qemu-system-x86_64",
            "kvm_usable": False,
        }
        first = build_vm_plan(config, host_probe=probe)
        second = build_vm_plan(config, host_probe=probe)
        self.assertEqual(first, second)
        self.assertEqual(first["promotion_status"], PROMOTION_STATUS)
        self.assertEqual(first["authority_path"], AUTHORITY_PATH)
        self.assertFalse(first["guest_is_canonical_authority"])
        self.assertFalse(first["canonical_mutation_authority"])
        self.assertFalse(first["canonical_persistence_authority"])
        self.assertFalse(first["canonical_hash72_authority"])
        self.assertEqual(first["web_frontend_status"], "DEPRECATED_COMPATIBILITY_ONLY")
        self.assertEqual(first["guest_api_endpoint"], "http://10.0.2.2:8080")
        self.assertIn("q35,accel=tcg", first["qemu_argv"])
        self.assertIn("max", first["qemu_argv"])
        self.assertIn("user,id=hhsnet", first["qemu_argv"])
        self.assertIn("virtio-net-pci,netdev=hhsnet", first["qemu_argv"])

    def test_no_network_and_headless_are_explicit(self) -> None:
        config = replace(
            load_config(DEFAULT_CONFIG),
            acceleration="tcg",
            network="none",
            display="none",
        )
        argv = build_qemu_argv(
            config,
            host_probe={"kvm_usable": False, "qemu_binary": "qemu-system-x86_64"},
        )
        self.assertIn("-nographic", argv)
        self.assertIn("-nic", argv)
        self.assertIn("none", argv)
        self.assertNotIn("user,id=hhsnet", argv)

    def test_invalid_config_is_rejected(self) -> None:
        base = load_config(DEFAULT_CONFIG)
        for invalid in (
            replace(base, vcpus=0),
            replace(base, memory_mib=0),
            replace(base, architecture="aarch64"),
            replace(base, acceleration="unknown"),
            replace(base, network="bridge"),
            replace(base, display="browser"),
            replace(base, api_port=0),
        ):
            with self.assertRaises(ValueError):
                invalid.validate()

    def test_authority_constants_are_zero(self) -> None:
        self.assertFalse(CANONICAL_MUTATION_AUTHORITY)
        self.assertFalse(CANONICAL_PERSISTENCE_AUTHORITY)
        self.assertFalse(CANONICAL_HASH72_AUTHORITY)


if __name__ == "__main__":
    unittest.main()
