from .core import ExactRational


def build_transform(*, x_q16: int, y_q16: int, stage_ratio: ExactRational, phase: int, shell_depth: int) -> dict:
    if not 0 <= phase < 72:
        raise ValueError("HHS_GFCC_INVALID_GEOMETRY:phase outside 0..71")
    return {
        "translation_q16": [int(x_q16), int(y_q16)],
        "golden_stage_ratio": stage_ratio.to_dict(),
        "inverse_diagonal_symbol": "ETA:2*eta^2=1:positive",
        "phase": int(phase),
        "shell_depth": int(shell_depth),
        "canonical_numeric_authority": "EXACT_FIXED_POINT_AND_RATIONAL",
    }


__all__ = ["build_transform"]
