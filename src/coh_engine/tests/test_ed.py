"""Tests for coh_engine.ed — Enhancement Diversification.

Golden values from docs/engine/mids-port-spec.md § enhancement-value-pipeline
worked assertions (oracle: MidsReborn Enhancement.ApplyED, Enhancement.cs:450-476):

- Hasten with 3x level-50 recharge IOs: pre-ED 1.272 -> 0.9908 (99.08%).
- Hasten with 2x level-50 recharge IOs: pre-ED 0.848 -> 0.8332 (83.32%).
"""

from pathlib import Path

import pytest

from coh_engine.ed import Aspect, Schedule, apply_ed, schedule_for
from coh_engine.maths import MathTables, load_maths


@pytest.fixture(scope="module")
def tables(maths_path: Path) -> MathTables:
    return load_maths(maths_path)


class TestApplyED:
    def test_none_schedule_returns_zero(self, tables: MathTables) -> None:
        assert apply_ed(Schedule.NONE, 1.0, tables) == 0.0

    def test_multiple_schedule_returns_zero(self, tables: MathTables) -> None:
        assert apply_ed(Schedule.MULTIPLE, 1.0, tables) == 0.0

    def test_below_first_threshold_unreduced(self, tables: MathTables) -> None:
        assert apply_ed(Schedule.A, 0.5, tables) == pytest.approx(0.5)

    def test_at_first_threshold_unreduced(self, tables: MathTables) -> None:
        assert apply_ed(Schedule.A, 0.7, tables) == pytest.approx(0.7)

    def test_second_band_slope_09(self, tables: MathTables) -> None:
        """0.70 < 0.848 <= 0.90: 0.70 + (0.848-0.70)*0.9 = 0.8332 — the 2-SO Hasten golden."""
        assert round(apply_ed(Schedule.A, 0.848, tables), 4) == 0.8332

    def test_third_band_slope_07(self, tables: MathTables) -> None:
        """0.90 < 0.95 <= 1.00: 0.70 + 0.20*0.9 + (0.95-0.90)*0.7 = 0.915."""
        assert apply_ed(Schedule.A, 0.95, tables) == pytest.approx(0.915, abs=1e-6)

    def test_above_third_threshold_slope_015(self, tables: MathTables) -> None:
        """1.272 > 1.00: 0.95 + (1.272-1.00)*0.15 = 0.9908 — the 3-SO Hasten golden."""
        assert round(apply_ed(Schedule.A, 1.272, tables), 4) == 0.9908

    def test_schedule_b_thresholds(self, tables: MathTables) -> None:
        """Schedule B (defense): thresholds 0.40/0.50/0.60."""
        assert apply_ed(Schedule.B, 0.40, tables) == pytest.approx(0.40)
        assert apply_ed(Schedule.B, 0.45, tables) == pytest.approx(0.445, abs=1e-6)

    def test_schedule_d_thresholds(self, tables: MathTables) -> None:
        """Schedule D: thresholds 1.20/1.50/1.80."""
        assert apply_ed(Schedule.D, 1.0, tables) == pytest.approx(1.0)
        assert apply_ed(Schedule.D, 2.0, tables) == pytest.approx(1.2 + 0.3 * 0.9 + 0.3 * 0.7 + 0.2 * 0.15, abs=1e-6)


class TestHastenGoldens:
    """End-to-end: MultIO lookup -> pre-ED sum -> ApplyED, per the spec's worked assertions."""

    def test_three_level50_recharge_ios(self, tables: MathTables) -> None:
        per_slot = tables.mult_io[49][Schedule.A]  # level-50 IO, schedule A
        pre_ed = 3 * per_slot
        assert pre_ed == pytest.approx(1.272, abs=1e-6)
        assert round(apply_ed(Schedule.A, pre_ed, tables), 4) == 0.9908

    def test_two_level50_recharge_ios(self, tables: MathTables) -> None:
        pre_ed = 2 * tables.mult_io[49][Schedule.A]
        assert pre_ed == pytest.approx(0.848, abs=1e-6)
        assert round(apply_ed(Schedule.A, pre_ed, tables), 4) == 0.8332


class TestScheduleFor:
    """Enhancement.GetSchedule aspect->schedule mapping (Enhancement.cs:424-448)."""

    @pytest.mark.parametrize(
        "aspect",
        [Aspect.DEFENSE, Aspect.RANGE, Aspect.RESISTANCE, Aspect.TO_HIT],
    )
    def test_schedule_b_aspects(self, aspect: Aspect) -> None:
        assert schedule_for(aspect) == Schedule.B

    def test_interrupt_is_schedule_c(self) -> None:
        assert schedule_for(Aspect.INTERRUPT) == Schedule.C

    def test_mez_default_is_schedule_a(self) -> None:
        assert schedule_for(Aspect.MEZ) == Schedule.A
        assert schedule_for(Aspect.MEZ, mez_sub=1) == Schedule.A

    @pytest.mark.parametrize("sub", [4, 5])
    def test_mez_sub_4_5_is_schedule_d(self, sub: int) -> None:
        assert schedule_for(Aspect.MEZ, mez_sub=sub) == Schedule.D

    @pytest.mark.parametrize(
        "aspect",
        [Aspect.ACCURACY, Aspect.DAMAGE, Aspect.ENDURANCE_DISCOUNT, Aspect.HEAL, Aspect.RECHARGE_TIME],
    )
    def test_default_is_schedule_a(self, aspect: Aspect) -> None:
        assert schedule_for(aspect) == Schedule.A
