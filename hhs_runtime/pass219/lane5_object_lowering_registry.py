"""Object-oriented Lane 5 lowering registry.

Repository objects are plug-and-play through registered lowering adapters.
Adapters can enrich a queued Lane5Instruction with object-specific exact
evidence, but they cannot bypass the Lane5Instruction execution boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable, Generic, TypeVar

from hhs_runtime.pass219.lane5_instruction import (
    Lane5Instruction,
    Lane5InstructionError,
    lower_object_to_lane5_instruction,
    require_lane5_instruction,
)

T = TypeVar("T")
Lowerer = Callable[[T, Lane5Instruction], Lane5Instruction]


class Lane5ObjectRegistryError(RuntimeError):
    pass


@dataclass(frozen=True)
class Lane5ObjectLowererBinding:
    object_type_name: str
    target: str
    traffic_class: str
    lowerer_name: str


class Lane5ObjectLoweringRegistry:
    def __init__(self) -> None:
        self._bindings: dict[type[Any], tuple[str, str, Lowerer[Any]]] = {}
        self._lock = RLock()

    def register(
        self,
        object_type: type[T],
        *,
        target: str,
        traffic_class: str,
        lowerer: Lowerer[T],
    ) -> None:
        if not isinstance(object_type, type):
            raise Lane5ObjectRegistryError("LANE5_OBJECT_TYPE_REQUIRED")
        if not callable(lowerer):
            raise Lane5ObjectRegistryError("LANE5_OBJECT_LOWERER_CALLABLE_REQUIRED")
        with self._lock:
            self._bindings[object_type] = (
                target,
                traffic_class,
                lowerer,
            )

    def unregister(self, object_type: type[Any]) -> None:
        with self._lock:
            self._bindings.pop(object_type, None)

    def bindings(self) -> tuple[Lane5ObjectLowererBinding, ...]:
        with self._lock:
            rows = []
            for object_type, (target, traffic_class, lowerer) in sorted(
                self._bindings.items(),
                key=lambda item: item[0].__qualname__,
            ):
                rows.append(
                    Lane5ObjectLowererBinding(
                        object_type_name=object_type.__qualname__,
                        target=target,
                        traffic_class=traffic_class,
                        lowerer_name=getattr(
                            lowerer,
                            "__qualname__",
                            lowerer.__class__.__qualname__,
                        ),
                    )
                )
            return tuple(rows)

    def _resolve(
        self,
        source_object: Any,
    ) -> tuple[str, str, Lowerer[Any]] | None:
        source_type = type(source_object)
        with self._lock:
            direct = self._bindings.get(source_type)
            if direct is not None:
                return direct
            candidates: list[
                tuple[int, tuple[str, str, Lowerer[Any]]]
            ] = []
            for registered_type, binding in self._bindings.items():
                if isinstance(source_object, registered_type):
                    try:
                        distance = source_type.mro().index(registered_type)
                    except ValueError:
                        distance = 1 << 30
                    candidates.append((distance, binding))
            if not candidates:
                return None
            candidates.sort(key=lambda item: item[0])
            return candidates[0][1]

    def lower(
        self,
        source_object: Any,
        *,
        operation: str,
        read_only: bool = False,
        dependency_root: str | None = None,
        metadata: dict[str, Any] | None = None,
        target: str | None = None,
        traffic_class: str | None = None,
    ) -> Lane5Instruction:
        binding = self._resolve(source_object)
        if binding is None:
            if target is None or traffic_class is None:
                raise Lane5ObjectRegistryError(
                    "LANE5_OBJECT_LOWERER_NOT_REGISTERED:"
                    + source_object.__class__.__qualname__
                )
            base = lower_object_to_lane5_instruction(
                source_object,
                target=target,
                traffic_class=traffic_class,
                operation=operation,
                read_only=read_only,
                dependency_root=dependency_root,
                metadata=metadata,
            )
            return base

        binding_target, binding_traffic, lowerer = binding
        if target is not None and target != binding_target:
            raise Lane5ObjectRegistryError("LANE5_OBJECT_TARGET_OVERRIDE_DENIED")
        if traffic_class is not None and traffic_class != binding_traffic:
            raise Lane5ObjectRegistryError(
                "LANE5_OBJECT_TRAFFIC_CLASS_OVERRIDE_DENIED"
            )
        base = lower_object_to_lane5_instruction(
            source_object,
            target=binding_target,
            traffic_class=binding_traffic,
            operation=operation,
            read_only=read_only,
            dependency_root=dependency_root,
            metadata=metadata,
        )
        enriched = lowerer(source_object, base)
        if not isinstance(enriched, Lane5Instruction):
            raise Lane5ObjectRegistryError(
                "LANE5_OBJECT_LOWERER_MUST_RETURN_INSTRUCTION"
            )
        if enriched.source_object_digest_sha256 != base.source_object_digest_sha256:
            raise Lane5ObjectRegistryError(
                "LANE5_OBJECT_IDENTITY_CHANGED_BY_LOWERER"
            )
        if enriched.target != base.target:
            raise Lane5ObjectRegistryError(
                "LANE5_OBJECT_TARGET_CHANGED_BY_LOWERER"
            )
        if enriched.traffic_class != base.traffic_class:
            raise Lane5ObjectRegistryError(
                "LANE5_OBJECT_TRAFFIC_CHANGED_BY_LOWERER"
            )
        try:
            require_lane5_instruction(
                enriched,
                expected_target=base.target,
                require_executable=False,
            )
        except Lane5InstructionError as exc:
            raise Lane5ObjectRegistryError(str(exc)) from exc
        return enriched


_DEFAULT_REGISTRY = Lane5ObjectLoweringRegistry()


def default_object_lowering_registry() -> Lane5ObjectLoweringRegistry:
    return _DEFAULT_REGISTRY


__all__ = [
    "Lane5ObjectLowererBinding",
    "Lane5ObjectLoweringRegistry",
    "Lane5ObjectRegistryError",
    "default_object_lowering_registry",
]
