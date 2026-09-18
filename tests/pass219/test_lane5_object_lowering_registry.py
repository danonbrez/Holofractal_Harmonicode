from __future__ import annotations

from dataclasses import dataclass

import pytest

from hhs_runtime.pass219.lane5_instruction import TARGET_LINUX
from hhs_runtime.pass219.lane5_interceptor_sandbox_cache import (
    reset_default_sandbox_for_tests,
)
from hhs_runtime.pass219.lane5_object_lowering_registry import (
    Lane5ObjectLoweringRegistry,
    Lane5ObjectRegistryError,
)


@dataclass(frozen=True)
class BaseObject:
    value: int


@dataclass(frozen=True)
class ChildObject(BaseObject):
    name: str = "child"


@pytest.fixture(autouse=True)
def _reset_sandbox() -> None:
    reset_default_sandbox_for_tests()


def test_registered_object_lowerer_is_plug_and_play() -> None:
    registry = Lane5ObjectLoweringRegistry()

    def identity_lowerer(source, instruction):
        assert source.value == 7
        return instruction

    registry.register(
        BaseObject,
        target=TARGET_LINUX,
        traffic_class="linux.kernel.abi",
        lowerer=identity_lowerer,
    )
    instruction = registry.lower(
        ChildObject(7),
        operation="inspect",
        read_only=True,
    )
    assert instruction.target == TARGET_LINUX
    assert instruction.source_object_type == "ChildObject"
    assert instruction.mandatory_optimization_dispatch is True
    assert instruction.sandbox_queue_optimized is True


def test_registered_object_cannot_override_target() -> None:
    registry = Lane5ObjectLoweringRegistry()
    registry.register(
        BaseObject,
        target=TARGET_LINUX,
        traffic_class="linux.kernel.abi",
        lowerer=lambda source, instruction: instruction,
    )
    with pytest.raises(
        Lane5ObjectRegistryError,
        match="TARGET_OVERRIDE_DENIED",
    ):
        registry.lower(
            BaseObject(1),
            operation="inspect",
            read_only=True,
            target="VM81_RUNTIME",
        )


def test_unregistered_object_requires_explicit_generic_target_and_traffic() -> None:
    registry = Lane5ObjectLoweringRegistry()
    with pytest.raises(
        Lane5ObjectRegistryError,
        match="LOWERER_NOT_REGISTERED",
    ):
        registry.lower(BaseObject(3), operation="inspect", read_only=True)

    instruction = registry.lower(
        BaseObject(3),
        operation="inspect",
        read_only=True,
        target=TARGET_LINUX,
        traffic_class="linux.kernel.abi",
    )
    assert instruction.target == TARGET_LINUX
