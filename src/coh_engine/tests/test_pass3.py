"""The shared Pass-3/4 fold divisor — filter (ignore) + cap behaviour.

``fold_divisor`` is the single implementation both the character ``Totals.EndUse``
(base_totals toggle arm) and the per-power ``statistics`` arm route through, so they
cannot diverge on the fold order, the ignore gate, or the recharge cap.
"""

from coh_engine.maths import f32
from coh_engine.pass3 import fold_divisor


def test_fold_is_aggregate_plus_global_plus_one() -> None:
    """The divisor is ((aggregate + global) + 1) in float32."""
    assert fold_divisor(0.9908, 0.0, aspect="RechargeTime") == f32(f32(0.9908 + 0.0) + 1.0)
    assert fold_divisor(0.0, 0.425, aspect="RechargeTime") == f32(1.425)


def test_ignored_aspect_skips_the_fold() -> None:
    """An aspect in ignored_aspects yields divisor 1.0 — the scalar stays at base."""
    assert fold_divisor(5.0, 3.0, aspect="RechargeTime", ignored_aspects=("RechargeTime",)) == 1.0
    # a different ignored aspect does not suppress this one
    assert fold_divisor(0.0, 0.425, aspect="RechargeTime", ignored_aspects=("Range",)) == f32(1.425)


def test_cap_clamps_the_multiplier() -> None:
    """A cap clamps the divisor (the AT recharge cap applied before the divide)."""
    assert fold_divisor(9.0, 0.0, aspect="RechargeTime", cap=5.0) == 5.0  # (9+0)+1 = 10 -> clamp 5
    assert fold_divisor(0.9908, 0.0, aspect="RechargeTime", cap=5.0) == f32(1.9908)  # under cap, unchanged


def test_ignored_aspect_ignores_the_cap_too() -> None:
    """When the aspect is ignored the result is 1.0 regardless of a supplied cap."""
    assert fold_divisor(9.0, 3.0, aspect="RechargeTime", ignored_aspects=("RechargeTime",), cap=5.0) == 1.0
