from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from hhs_runtime.hhs_pass220_python_rna_class_registration_v1 import (
    MEMBER_CONSTRUCTOR,
    MEMBER_FIELD,
    MEMBER_METHOD,
    PythonClassMemberSpec,
    PythonRNAClassRegistrationError,
    PythonRNAClassRegistry,
    python2_rna_class_registration_contract,
)

ROOT = Path(__file__).resolve().parents[2]
EXACT_C = ROOT / "hhs_runtime" / "c" / "hhs_runtime_exact_abi.c"
INCLUDE = ROOT / "hhs_runtime" / "include"


@pytest.fixture()
def exact_abi_library(tmp_path: Path) -> Path:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    shared = tmp_path / "libhhs_runtime_exact_abi.so"
    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-fPIC",
            "-shared",
            f"-I{INCLUDE}",
            str(EXACT_C),
            "-o",
            str(shared),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return shared


def _members():
    return (
        PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, 1),
        PythonClassMemberSpec("value", MEMBER_FIELD, 1, 1, 0),
        PythonClassMemberSpec("render", MEMBER_METHOD, 2, 0, 2),
    )


def test_python2_registers_one_class_into_pass219_rna_cell_wall(
    exact_abi_library: Path,
) -> None:
    registry = PythonRNAClassRegistry(exact_abi_library)
    registration = registry.register(
        module_name="hhs.examples",
        class_name="Widget",
        source_text=(
            "class Widget:\n"
            "    def __init__(self, value): self.value = value\n"
            "    def render(self): return self.value\n"
        ),
        members=_members(),
    )
    assert registration.schema == "HHS_PASS_220_PYTHON2_RNA_CLASS_REGISTRATION_V1"
    assert registration.rna_cell_wall_bound is True
    assert registration.registration_only is True
    assert registration.strand_id == registration.class_id
    assert registration.strand_domain_ids[0] == registration.class_id
    assert registration.strand_domain_ids[1:] == registration.member_ids
    assert registration.program_rule_count == 0
    assert len(registration.class_identity_hash216) == 216
    assert len(registration.source_sha256) == 64
    assert registration.registration_fingerprint64 != 0
    assert registration.vm81_mutation_authority is False
    assert registration.hash72_commit_authority is False
    assert registration.hash216_persistence_authority is False
    assert registration.floating_point_authority is False


def test_python2_registration_replays_identically(
    exact_abi_library: Path,
) -> None:
    registry = PythonRNAClassRegistry(exact_abi_library)
    kwargs = dict(
        module_name="hhs.examples",
        class_name="Widget",
        source_text="class Widget: pass\n",
        members=_members(),
    )
    first = registry.register(**kwargs)
    second = registry.register(**kwargs)
    assert first.class_identity_hash216 == second.class_identity_hash216
    assert first.registration_fingerprint64 == second.registration_fingerprint64
    assert first.member_ids == second.member_ids
    assert first.strand_domain_ids == second.strand_domain_ids


def test_python2_source_or_member_change_changes_registration_identity(
    exact_abi_library: Path,
) -> None:
    registry = PythonRNAClassRegistry(exact_abi_library)
    base = registry.register(
        module_name="hhs.examples",
        class_name="Widget",
        source_text="class Widget: pass\n",
        members=_members(),
    )
    changed_source = registry.register(
        module_name="hhs.examples",
        class_name="Widget",
        source_text="class Widget:\n    marker = 1\n",
        members=_members(),
    )
    changed_member = registry.register(
        module_name="hhs.examples",
        class_name="Widget",
        source_text="class Widget: pass\n",
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, 1),
            PythonClassMemberSpec("value", MEMBER_FIELD, 1, 1, 0),
            PythonClassMemberSpec("execute", MEMBER_METHOD, 2, 0, 2),
        ),
    )
    assert base.class_identity_hash216 != changed_source.class_identity_hash216
    assert base.registration_fingerprint64 != changed_source.registration_fingerprint64
    assert base.class_identity_hash216 != changed_member.class_identity_hash216


def test_python2_requires_exactly_one_constructor(
    exact_abi_library: Path,
) -> None:
    registry = PythonRNAClassRegistry(exact_abi_library)
    with pytest.raises(
        PythonRNAClassRegistrationError,
        match="EXACTLY_ONE_CONSTRUCTOR",
    ):
        registry.register(
            module_name="hhs.examples",
            class_name="Invalid",
            source_text="class Invalid: pass\n",
            members=(
                PythonClassMemberSpec("value", MEMBER_FIELD, 1),
            ),
        )


def test_python2_contract_preserves_single_vm81_authority() -> None:
    contract = python2_rna_class_registration_contract()
    assert contract["pass219_rna_rule_grammar"] == "1.11"
    assert contract["pass219_rna_admission_lowering"] == "1.12"
    assert contract["native_cpp_cell_wall_class"] == (
        "hhs::rna::PythonClassRegistration"
    )
    assert contract["registration_program_executes_state_transition"] is False
    assert contract["instance_transition_requires_rna_admission"] is True
    assert contract["vm81_mutation_authority"] is False
    assert contract["hash72_commit_authority"] is False
    assert contract["hash216_persistence_authority"] is False
    assert contract["mojo_future_binding_uses_same_class_identity"] is True
