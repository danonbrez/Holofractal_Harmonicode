"""Descriptor-first lazy population for the canonical HHS service registry.

The inherited default registry imports every service module while constructing
an emulator. That makes kernel boot depend on every optional service import.
This adapter preserves the complete registered descriptor surface and the
existing conformance interposer, but resolves each callable only when that
service is dispatched.

Pass 217 restoration rule: production lazy dispatch is not permitted to jump
from registration directly to the service handler. Every dispatched service
must traverse the inherited Pass 043 kernel-derived runtime composer first.
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
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload

VERSION = "HHS_DESCRIPTOR_FIRST_LAZY_SERVICE_REGISTRY_V1"
_BUILD_LOCK = threading.RLock()


class HHSLazyServiceRegistry(HHSServiceRegistry):
    """Registry whose descriptors are validated now and callables resolve later."""

    def __init__(self, controller: Optional[HHSRuntimeController] = None):
        super().__init__(controller=controller)
        self._composition_decision_cache: Dict[str, Dict[str, Any]] = {}

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

    def _composition_surface(self, service_name: str) -> Dict[str, Any]:
        spec = self._services[service_name]
        surface = spec.to_dict()
        surface.update(
            {
                "surface_id": f"service:{service_name}",
                "surface_type": "SERVICE",
                "symbol": spec.function,
                "declared_operations": sorted({service_name, spec.function}),
                "derivation_complete": bool(
                    spec.conformance_decision.get("derivation_complete")
                ),
            }
        )
        return surface

    @staticmethod
    def _compact_preflight(preflight: Mapping[str, Any]) -> Dict[str, Any]:
        plan = dict(preflight.get("composition_plan") or {})
        pipeline = dict(plan.get("pipeline") or {})
        witness = dict(plan.get("witness") or {})
        cache = dict(preflight.get("cache") or {})
        return {
            "schema": "HHS_LIVE_SERVICE_COMPOSITION_PREFLIGHT_SUMMARY_V1",
            "ok": bool(preflight.get("ok")),
            "status": preflight.get("status"),
            "surface_id": preflight.get("surface_id"),
            "operation": preflight.get("operation"),
            "conformance_root_hash72": preflight.get("conformance_root_hash72"),
            "pipeline_root_hash72": pipeline.get("pipeline_root_hash72"),
            "composition_root_hash72": witness.get("composition_root_hash72"),
            "cache_hit": bool(cache.get("cache_hit")),
            "expanded_metadata_persisted": bool(
                preflight.get("expanded_metadata_persisted")
            ),
            "compact_residue": preflight.get("compact_residue"),
        }

    def dispatch(
        self,
        service_name: str,
        payload: Optional[Mapping[str, Any]] = None,
        *,
        zero_bypass_interposition_token: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Dispatch only after the inherited Pass 043 composer admits the path."""

        if service_name not in self._services:
            raise HHSServiceRegistryError(f"unknown service: {service_name}")

        spec = self._services[service_name]
        surface = self._composition_surface(service_name)
        operation = spec.function or service_name
        preflight = execute_surface_preflight(
            surface,
            operation=operation,
            cache=self._composition_decision_cache,
        )
        preflight_summary = self._compact_preflight(preflight)
        if not preflight.get("ok"):
            return {
                "schema": "HHS_SERVICE_DISPATCH_COMPOSITION_REJECTION_V1",
                "service": spec.to_dict(),
                "payload": dict(payload or {}),
                "kernel_runtime_composition_preflight": preflight_summary,
                "propagation_allowed": False,
                "execution_allowed": False,
                "bypass_attempt": True,
                "reason": "REJECT_SERVICE_HANDLER_WITHOUT_KERNEL_DERIVED_COMPOSITION",
            }

        record = super().dispatch(
            service_name,
            payload,
            zero_bypass_interposition_token=zero_bypass_interposition_token,
        )
        record["kernel_runtime_composition_preflight"] = preflight_summary

        if record.get("execution_allowed") is False:
            return record

        previous_tip = (record.get("unified_ledger") or {}).get("tip_hash72")
        binding_payload = {
            "schema": "HHS_CUMULATIVE_COMPOSITION_BINDING_V1",
            "service_name": service_name,
            "surface_id": preflight_summary.get("surface_id"),
            "operation": operation,
            "conformance_root_hash72": preflight_summary.get(
                "conformance_root_hash72"
            ),
            "pipeline_root_hash72": preflight_summary.get("pipeline_root_hash72"),
            "composition_root_hash72": preflight_summary.get(
                "composition_root_hash72"
            ),
            "service_dispatch_tip_hash72": previous_tip,
            "expanded_metadata_persisted": False,
        }
        ledger = append_payload(
            "RUNTIME_COMPOSITION",
            f"HHSLazyServiceRegistry.dispatch.{service_name}",
            binding_payload,
        )
        record["composition_ledger_binding"] = {
            "schema": "HHS_CUMULATIVE_COMPOSITION_LEDGER_BINDING_V1",
            "entry_count": ledger.get("entry_count"),
            "tip_hash72": ledger.get("tip_hash72"),
            "ledger_hash72": ledger.get("ledger_hash72"),
            "prior_service_dispatch_tip_hash72": previous_tip,
            "composition_root_hash72": preflight_summary.get(
                "composition_root_hash72"
            ),
        }
        return record


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
