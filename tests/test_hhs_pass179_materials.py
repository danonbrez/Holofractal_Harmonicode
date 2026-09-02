from hhs_runtime.pass179.materials import GradientStop, phase_color, sample_gradient
from hhs_runtime.pass179.types import RGBA16


def test_phase_palette_and_gradient_are_exact_integer_only():
    assert phase_color(0) == phase_color(0)
    left = GradientStop(0, RGBA16(0, 0, 0, 65535))
    right = GradientStop(65536, RGBA16(65535, 32768, 0, 65535))
    mid = sample_gradient([left, right], 32768)
    assert mid.r in {32767, 32768}
    assert mid.g == 16384
    assert mid.a == 65535
