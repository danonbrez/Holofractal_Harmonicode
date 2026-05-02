from __future__ import annotations

from typing import Any

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import AuditedRunner
from hhs_runtime.core_sandbox.hhs_qgu_metric_harmonic_operator_v1 import qgu_metric_harmonic_operator


QGU_OPERATION_NAME = "QGU_METRIC_HARMONIC"


def register_qgu_metric_harmonic_operator(runner: AuditedRunner) -> AuditedRunner:
    """
    Register QGU as a native AuditedRunner operation.

    This does not execute QGU directly. It only binds the operator into the
    existing runtime registry so calls must pass through:
      AuditedRunner.execute -> KernelGateAdapter.audit_value -> Hash72 receipt.
    """
    runner.registry.register(QGU_OPERATION_NAME, qgu_metric_harmonic_operator)
    return runner


class QGUAuditedRunner(AuditedRunner):
    """
    AuditedRunner with QGU registered at construction time.

    QGU execution remains kernel-routed because callers still invoke:
      runner.execute("QGU_METRIC_HARMONIC", payload)
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        register_qgu_metric_harmonic_operator(self)


def execute_qgu_through_kernel(payload: dict[str, Any], *, runner: AuditedRunner | None = None) -> dict[str, Any]:
    """
    Convenience entrypoint that refuses direct operator execution.

    It creates or receives an AuditedRunner, registers QGU, then executes through
    the runtime gate/receipt path. The raw qgu_metric_harmonic_operator is not
    called from this function except through runner.execute dispatch.
    """
    active_runner = runner if runner is not None else QGUAuditedRunner()
    register_qgu_metric_harmonic_operator(active_runner)
    return active_runner.execute(QGU_OPERATION_NAME, payload, input_payload=payload)
