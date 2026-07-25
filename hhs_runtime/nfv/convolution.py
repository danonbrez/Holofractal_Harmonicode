from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .audio import ALL_LANES, ExactScalar, HarmonicField, ZERO
from .core import NFVError, hash216


@dataclass(frozen=True)
class ConvolutionKernel:
    lane_id: str
    coefficients: tuple[ExactScalar, ...]
    source_receipt: str
    kernel_index: str = ""

    def __post_init__(self) -> None:
        if self.lane_id not in ALL_LANES:
            raise NFVError("NFV_INVALID_CONVOLUTION_LANE", "kernel lane must be x,y,z,w, or c")
        if not self.coefficients:
            raise NFVError("NFV_EMPTY_CONVOLUTION_KERNEL", "kernel requires at least one coefficient")
        coefficients = tuple(
            value if isinstance(value, ExactScalar) else ExactScalar(*value) if isinstance(value, tuple) else ExactScalar(int(value))
            for value in self.coefficients
        )
        object.__setattr__(self, "coefficients", coefficients)
        if not self.source_receipt:
            raise NFVError("NFV_MISSING_KERNEL_RECEIPT", "kernel must bind to a source receipt")
        expected = hash216({
            "domain": "HHS-NFV-CONVOLUTION-KERNEL-V1",
            "lane_id": self.lane_id,
            "coefficients": [coefficient.to_dict() for coefficient in coefficients],
            "source_receipt": self.source_receipt,
        })
        if self.kernel_index and self.kernel_index != expected:
            raise NFVError("NFV_CONVOLUTION_KERNEL_IDENTITY_MISMATCH", "kernel index is not canonical")
        object.__setattr__(self, "kernel_index", expected)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane_id": self.lane_id,
            "coefficients": [coefficient.to_dict() for coefficient in self.coefficients],
            "source_receipt": self.source_receipt,
            "kernel_index": self.kernel_index,
        }


@dataclass(frozen=True)
class ConvolutionKernelBank:
    lane_x: ConvolutionKernel
    lane_y: ConvolutionKernel
    lane_z: ConvolutionKernel
    lane_w: ConvolutionKernel
    center: ConvolutionKernel
    source_receipt: str
    bank_index: str = ""

    def __post_init__(self) -> None:
        kernels = self.kernels
        if tuple(kernel.lane_id for kernel in kernels) != ALL_LANES:
            raise NFVError("NFV_CONVOLUTION_LANE_ORDER_MISMATCH", "kernel bank order must remain x,y,z,w,c")
        if any(kernel.source_receipt != self.source_receipt for kernel in kernels):
            raise NFVError("NFV_KERNEL_RECEIPT_MISMATCH", "all kernels must bind to the bank source receipt")
        expected = hash216({
            "domain": "HHS-NFV-CONVOLUTION-BANK-V1",
            "source_receipt": self.source_receipt,
            "kernels": [kernel.to_dict() for kernel in kernels],
        })
        if self.bank_index and self.bank_index != expected:
            raise NFVError("NFV_CONVOLUTION_BANK_IDENTITY_MISMATCH", "kernel bank index is not canonical")
        object.__setattr__(self, "bank_index", expected)

    @property
    def kernels(self) -> tuple[ConvolutionKernel, ...]:
        return self.lane_x, self.lane_y, self.lane_z, self.lane_w, self.center

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "HHS_NFV_CONVOLUTION_KERNEL_BANK_V1",
            "source_receipt": self.source_receipt,
            "kernels": [kernel.to_dict() for kernel in self.kernels],
            "bank_index": self.bank_index,
        }


def refresh_kernel_bank(
    current: ConvolutionKernelBank,
    candidate: ConvolutionKernelBank,
    *,
    vm81_authorized: bool,
) -> ConvolutionKernelBank:
    if not vm81_authorized:
        raise NFVError("NFV_VM81_KERNEL_REFRESH_REJECTED", "kernel refresh requires VM81 authorization")
    if candidate.source_receipt == current.source_receipt:
        raise NFVError("NFV_STALE_KERNEL_RECEIPT", "kernel refresh requires a new source receipt")
    return candidate


def _convolve(signal: tuple[ExactScalar, ...], kernel: tuple[ExactScalar, ...]) -> tuple[ExactScalar, ...]:
    output = [ZERO for _ in range(len(signal) + len(kernel) - 1)]
    for signal_index, sample in enumerate(signal):
        for kernel_index, coefficient in enumerate(kernel):
            output[signal_index + kernel_index] = output[signal_index + kernel_index].add(sample.multiply(coefficient))
    return tuple(output)


def render_convolution_chamber(field: HarmonicField, bank: ConvolutionKernelBank) -> tuple[ExactScalar, ...]:
    if field.source_receipt != bank.source_receipt:
        raise NFVError("NFV_INTERACTION_RECEIPT_MISMATCH", "harmonic field and kernel bank must share one receipt")
    signals = (
        field.lane_x.samples,
        field.lane_y.samples,
        field.lane_z.samples,
        field.lane_w.samples,
        field.center.samples,
    )
    rendered = [_convolve(signal, kernel.coefficients) for signal, kernel in zip(signals, bank.kernels)]
    output_length = max(len(values) for values in rendered)
    chamber = [ZERO for _ in range(output_length)]
    for values in rendered:
        for index, value in enumerate(values):
            chamber[index] = chamber[index].add(value)
    return tuple(chamber)
