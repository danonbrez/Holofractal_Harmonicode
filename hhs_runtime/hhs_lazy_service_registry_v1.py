"""Descriptor-first lazy population for the canonical HHS service registry.

The inherited default registry imports every service module while constructing
an emulator. That makes kernel boot depend on every optional service import.
This adapter preserves the complete registered descriptor surface and the
existing conformance interposer, but resolves each callable only when that
service is dispatched.
"""

from __future__ import annotations

import importlib
import inspect
import threading
from typing import Any, Dict, List, Mapping, Optional

import hhs_runtime.hhs_service_registry_v1 as registry_module
from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_service_registry_v1 import (
    HHSServiceRegistry,
    HHSServiceRegistryError,
    HHSServiceSpec,
)

VERSION = "HHS_DESCRIPTOR_FIRST_LAZY_SERVICE_REGISTRY_V1"
_BUILD_LOCK = threading.RLock()


class HHSLazyServiceRegistry(HHSServiceRegistry):
    """Registry whose descriptors are validated now and callables resolve later."""

    def register_function(
        self,
        *,
        name: str,
        module: str,
        function: str,
        service_type: str = "runtime",
        description: str = "",
        requires_authority: bool = True,
        schema: Optional[Dict[str, Any]] = None,
        invariant_ids: Optional[List[str]] = None,
        contract_schemas: Optional[List[str]] = None,
        witness_schemas: Optional[List[str]] = None,
        validators: Optional[List[str]] = None,
        guards: Optional[List[str]] = None,
        rejection_codes: Optional[List[str]] = None,
        mutation_policy: str = "NO_EXTERNAL_STATE_MUTATION",
        persistence_policy: str = "NO_PERSISTENCE_MUTATION",
        boundedness_policy: str = "PASS_042_BOUNDED_CONFORMANCE_SUMMARY_V1",
        contract_exempt_reason: str = "",
    ) -> HHSServiceSpec:
        def handler(payload: Mapping[str, Any]) -> Mapping[str, Any] | Dict[str, Any]:
            try:
                imported = importlib.import_module(module)
                callable_surface = getattr(imported, function)
            except Exception as exc:
                raise HHSServiceRegistryError(
                    f"service callable resolution failed for {name}: "
                    f"{module}.{function}: {exc}"
                ) from exc

            if not callable(callable_surface):
                raise HHSServiceRegistryError(
                    f"{module}.{function} is not callable for service {name}"
                )

            signature = inspect.signature(callable_surface)
            required_parameters = [
                parameter
                for parameter in signature.parameters.values()
                if parameter.default is inspect.Parameter.empty
                and parameter.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.KEYWORD_ONLY,
                )
            ]
            result = callable_surface() if not required_parameters else callable_surface(payload)
            if isinstance(result, Mapping):
                return dict(result)
            return {"result": result}

        spec = HHSServiceSpec(
            name=name,
            module=module,
            function=function,
            service_type=service_type,
            description=description,
            requires_authority=requires_authority,
            schema=schema or {},
            invariant_ids=list(invariant_ids or []),
            contract_schemas=list(contract_schemas or []),
            witness_schemas=list(witness_schemas or []),
            validators=list(validators or []),
            guards=list(guards or []),
            rejection_codes=list(rejection_codes or []),
            mutation_policy=mutation_policy,
            persistence_policy=persistence_policy,
            boundedness_policy=boundedness_policy,
            contract_exempt_reason=contract_exempt_reason,
        )
        return self.register(spec, handler)


def make_lazy_default_service_registry(
    controller: Optional[HHSRuntimeController] = None,
) -> HHSServiceRegistry:
    """Build the complete inherited descriptor set without eager service imports."""

    with _BUILD_LOCK:
        original_registry_class = registry_module.HHSServiceRegistry
        registry_module.HHSServiceRegistry = HHSLazyServiceRegistry
        try:
            registry = registry_module.make_default_service_registry(controller)
        finally:
            registry_module.HHSServiceRegistry = original_registry_class

    setattr(registry, "population_mode", VERSION)
    return registry


__all__ = [
    "VERSION",
    "HHSLazyServiceRegistry",
    "make_lazy_default_service_registry",
]
