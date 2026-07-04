"""Enhancement Diversification (ED) and the aspect->schedule mapping.

Mirrors ``Enhancement.ApplyED`` and ``Enhancement.GetSchedule`` (MidsReborn
``Core/Enhancement.cs:424-476``). The slope literals are the exact doubles the C#
source uses; intermediate float casts are reproduced at the same points so results
track Mids bit-for-bit at single precision.
Spec: docs/engine/mids-port-spec.md § enhancement-value-pipeline.
"""

from enum import IntEnum, StrEnum

from coh_engine.maths import MathTables, f32

# Exact double literals from Enhancement.cs:467-473.
_SLOPE_2 = 0.899999976158142
_SLOPE_3 = 0.699999988079071
_SLOPE_4 = 0.150000005960464


class Schedule(IntEnum):
    """``Enums.eSchedule`` (Enums.cs:942-950)."""

    NONE = -1
    A = 0
    B = 1
    C = 2
    D = 3
    MULTIPLE = 4


class Aspect(StrEnum):
    """Enhancement aspects the value pipeline touches (subset of ``Enums.eEnhance``).

    The full eEnhance enum (with MidsReborn's integer values) lands with the CP2
    database export; until then aspects are identified by name only.
    """

    ACCURACY = "accuracy"
    DAMAGE = "damage"
    DEFENSE = "defense"
    ENDURANCE_DISCOUNT = "endurance_discount"
    HEAL = "heal"
    INTERRUPT = "interrupt"
    MEZ = "mez"
    RANGE = "range"
    RECHARGE_TIME = "recharge_time"
    RESISTANCE = "resistance"
    TO_HIT = "to_hit"


_SCHEDULE_B_ASPECTS = frozenset({Aspect.DEFENSE, Aspect.RANGE, Aspect.RESISTANCE, Aspect.TO_HIT})
_MEZ_SCHEDULE_D_SUBS = frozenset({4, 5})


def schedule_for(aspect: Aspect, mez_sub: int = -1) -> Schedule:
    """Map an enhancement aspect to its ED schedule (``Enhancement.GetSchedule``)."""
    if aspect in _SCHEDULE_B_ASPECTS:
        return Schedule.B
    if aspect is Aspect.INTERRUPT:
        return Schedule.C
    if aspect is Aspect.MEZ and mez_sub in _MEZ_SCHEDULE_D_SUBS:
        return Schedule.D
    return Schedule.A


def apply_ed(schedule: Schedule, value: float, tables: MathTables) -> float:
    """Apply Enhancement Diversification once to a per-aspect pre-ED aggregate.

    Piecewise-linear with slopes 1.0 / 0.9 / 0.7 / 0.15 over the schedule's three
    thresholds. Called exactly once per aspect on the sum across all slots — never
    per slot.
    """
    if schedule in (Schedule.NONE, Schedule.MULTIPLE):
        return 0.0
    ed = tables.mult_ed[schedule]
    value = f32(value)
    if value <= ed[0]:
        return value
    # edm mirrors Enhancement.cs:464-470 including where the float casts land.
    edm_1 = f32(ed[0] + f32((ed[1] - ed[0]) * _SLOPE_2))
    edm_2 = f32(ed[0] + (ed[1] - ed[0]) * _SLOPE_2 + (ed[2] - ed[1]) * _SLOPE_3)
    if value > ed[2]:
        return f32(edm_2 + f32((value - ed[2]) * _SLOPE_4))
    if value > ed[1]:
        return f32(edm_1 + f32((value - ed[1]) * _SLOPE_3))
    return f32(ed[0] + f32((value - ed[0]) * _SLOPE_2))
