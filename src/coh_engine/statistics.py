"""Derived per-power statistics (``Core/Statistics.cs`` + the Pass-3 global fold).

``compute_base_totals`` produces character ``Totals`` only; goal scoring (CP7) and
attack-chain analysis need per-power numbers. This module computes the buffed
per-power scalars — final recharge time, endurance cost, interrupt time — and the
endurance-per-second rate, from the base scalars, the slotted enhancement (via
:func:`~coh_engine.enh_pipeline.aggregate_and_ed`), and the global ``_selfEnhance``
terms (:class:`~coh_engine.base_totals.GlobalEnhance`).

The per-power scalar fold generalises ``GBPA_Pass3_EnhancePostED`` (clsToonX.cs:1924)
beyond the CP5 toggle-EndUse arm: the buffed value is ``base / (( ED(sum slotted) +
global ) + 1)``. Two per-power hard limits from ``GBPA_ApplyArchetypeCaps``
(clsToonX.cs:1275) apply: the recharge multiplier is clamped to the AT recharge cap
before the divide, and a power that ignores an aspect (``Power.IgnoreEnh`` /
``IgnoreEnhancement``) skips that fold entirely (its modifiable base is zero) — e.g. One
with the Shield keeps its recharge at base 360.

**Damage / DPS are deferred.** Faithful damage-per-activation is ``Power.FXGetDamageValue``
(Power.cs:856), which applies Scrapper critical mechanics and ``ValidateConditional`` /
``CanInclude`` per-effect filtering — the same conditional subsystem unported since CP3
(a plain BuffedMag sum overcounts ~2x). :func:`compute_power_dps` fails loud (``E15``)
rather than return a wrong number; perma-Hasten / perma-Dom scoring depends only on the
recharge times this module does produce.

Spec: docs/engine/mids-port-spec.md § gbpa-pass-pipeline (Pass 3).
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from coh_engine.archetypes import ArchetypeDb
from coh_engine.attribmod import AttribMods
from coh_engine.base_totals import EngineConfig, GlobalEnhance
from coh_engine.effect import Power
from coh_engine.enh_pipeline import aggregate_and_ed
from coh_engine.enhancement import EnhancementRecord, SlotRef
from coh_engine.maths import MathTables, f32

# eEnhance aspect names (Power.IgnoreEnh entries) the per-power scalar fold keys on.
_ASPECT_RECHARGE = "RechargeTime"
_ASPECT_END = "EnduranceDiscount"
_ASPECT_INTERRUPT = "Interrupt"


@dataclass(frozen=True, slots=True)
class StatsContext:
    """The shared inputs every per-power derived-stat computation needs.

    ``global_enhance`` carries the build's global ``_selfEnhance`` scalar terms (from
    :func:`~coh_engine.base_totals.compute_base_totals`); ``recharge_cap`` is the
    archetype's recharge-multiplier cap. ``force_level`` comes from ``config``.
    """

    mods: AttribMods
    classes: ArchetypeDb
    archetype_index: int
    config: EngineConfig
    tables: MathTables
    enh_db: Mapping[int, EnhancementRecord]
    global_enhance: GlobalEnhance
    recharge_cap: float


@dataclass(frozen=True, slots=True)
class PowerStats:
    """One power's derived scalars and the endurance rate derived from them."""

    full_name: str
    recharge_time: float
    end_cost: float
    interrupt_time: float
    end_per_sec: float


def _aggregate(power_slots: Sequence[SlotRef], aspect: str, ctx: StatsContext) -> float:
    """``ED(sum slotted <aspect>)`` over the power's in-gate slots."""
    return aggregate_and_ed(
        power_slots, aspect=aspect, enh_db=ctx.enh_db, force_level=ctx.config.force_level, tables=ctx.tables
    )


def _fold_divisor(
    power: Power, power_slots: Sequence[SlotRef], aspect: str, global_term: float, ctx: StatsContext
) -> float:
    """The Pass 3/4 multiplier ``(ED(sum slotted) + global) + 1``, or 1 if the aspect is ignored.

    ``Power.IgnoreEnh`` (``IgnoreEnhancement``) zeroes the modifiable base for an
    ignored aspect, so neither the slotted nor the global term applies and the buffed
    scalar stays at base.
    """
    if aspect in power.ignore_enh:
        return 1.0
    return f32(f32(_aggregate(power_slots, aspect, ctx) + global_term) + 1.0)


def _buffed_recharge(power: Power, power_slots: Sequence[SlotRef], ctx: StatsContext) -> float:
    """Buffed recharge = base / clamp((ED(sum rech) + global) + 1, recharge cap), 0 if base is 0."""
    if power.recharge_time <= 0.0:
        return 0.0
    multiplier = min(
        _fold_divisor(power, power_slots, _ASPECT_RECHARGE, ctx.global_enhance.recharge, ctx), ctx.recharge_cap
    )
    return f32(power.recharge_time / multiplier)


def compute_power_stats(power: Power, power_slots: Sequence[SlotRef], ctx: StatsContext) -> PowerStats:
    """The derived scalars + endurance/sec for one power (see the module docstring)."""
    recharge = _buffed_recharge(power, power_slots, ctx)
    end_cost = f32(
        power.end_cost / _fold_divisor(power, power_slots, _ASPECT_END, ctx.global_enhance.end_discount, ctx)
    )
    interrupt = f32(
        power.interrupt_time / _fold_divisor(power, power_slots, _ASPECT_INTERRUPT, ctx.global_enhance.interrupt, ctx)
    )

    if power.power_type == "Toggle" and power.activate_period > 0.0:
        end_per_sec = f32(end_cost / power.activate_period)
    else:
        cadence = f32(recharge + f32(power.cast_time + interrupt))
        end_per_sec = f32(end_cost / cadence) if cadence > 0.0 else 0.0

    return PowerStats(
        full_name=power.full_name,
        recharge_time=recharge,
        end_cost=end_cost,
        interrupt_time=interrupt,
        end_per_sec=end_per_sec,
    )


def compute_build_stats(
    powers: Sequence[Power], slots: Mapping[int, Sequence[SlotRef]], ctx: StatsContext
) -> list[PowerStats]:
    """Derived stats for every build power, in build order."""
    return [compute_power_stats(power, slots.get(power.build_index, ()), ctx) for power in powers]


def compute_power_dps(power: Power, power_slots: Sequence[SlotRef], ctx: StatsContext) -> float:
    """Damage-per-activation / DPS — deferred (``E15``).

    Faithful damage is ``Power.FXGetDamageValue``: it applies Scrapper critical
    mechanics and ``ValidateConditional`` / ``CanInclude`` per-effect filtering (Smite's
    DPA is base + one conditional tick, not the full BuffedMag sum, which overcounts
    ~2x). That conditional subsystem is unported (deferred since CP3), so this fails
    loud rather than return a wrong figure.

    Raises:
        NotImplementedError: ``E15`` always — port ``FXGetDamageValue`` + the
            conditional/critical machinery against a validated fixture first.
    """
    raise NotImplementedError(
        f"E15: DPS for {power.full_name} requires the FXGetDamageValue critical/conditional port "
        "(deferred; a plain buffed-damage sum overcounts). Slots supplied: "
        f"{len([s for s in power_slots if s.enh >= 0])}"
    )
