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
from types import MappingProxyType

from coh_engine.archetypes import ArchetypeDb
from coh_engine.attribmod import AttribMods
from coh_engine.base_totals import EngineConfig, GlobalEnhance
from coh_engine.effect import Power
from coh_engine.enh_aspects import END, INTERRUPT, RECHARGE, AspectHandler, fold_scalar, global_term
from coh_engine.enh_pipeline import aggregate_and_ed
from coh_engine.enhancement import EnhancementRecord, SlotRef
from coh_engine.maths import MathTables, f32


@dataclass(frozen=True, slots=True)
class StatsContext:
    """The shared inputs every per-power derived-stat computation needs.

    ``global_enhance`` carries the build's global ``_selfEnhance`` scalar terms (from
    :func:`~coh_engine.base_totals.compute_base_totals`); ``recharge_cap`` is the
    archetype's recharge-multiplier cap. ``force_level`` comes from ``config``.
    ``incarnate_scalar`` maps ``(build_index, aspect)`` to the incarnate ``(pre_ed,
    post_ed)`` scalar addends (:mod:`coh_engine.incarnate`); the pre-ED term co-EDs with
    the slotted aggregate and the post-ED term is the ``fold_scalar`` post-ED seam.
    """

    mods: AttribMods
    classes: ArchetypeDb
    archetype_index: int
    config: EngineConfig
    tables: MathTables
    enh_db: Mapping[int, EnhancementRecord]
    global_enhance: GlobalEnhance
    recharge_cap: float
    incarnate_scalar: Mapping[tuple[int, str], tuple[float, float]] = MappingProxyType({})


@dataclass(frozen=True, slots=True)
class PowerStats:
    """One power's derived scalars and the endurance rate derived from them.

    ``cast_time`` is the (recharge-unreduced) activation time; ``is_attack`` flags a
    click power that deals damage — the attack-chain sequencer (CP7.1) consumes both.
    """

    full_name: str
    recharge_time: float
    end_cost: float
    interrupt_time: float
    end_per_sec: float
    cast_time: float
    is_attack: bool


def _is_attack(power: Power) -> bool:
    """A click power that deals damage — an attack-chain member (identity, not its DPS)."""
    return power.power_type == "Click" and any(fx.effect_type == "Damage" for fx in power.effects)


def _aggregate(power_slots: Sequence[SlotRef], aspect: str, ctx: StatsContext, pre_ed_addend: float = 0.0) -> float:
    """``ED(sum slotted <aspect> + incarnate pre-ED)`` over the power's in-gate slots."""
    return aggregate_and_ed(
        power_slots,
        aspect=aspect,
        enh_db=ctx.enh_db,
        force_level=ctx.config.force_level,
        tables=ctx.tables,
        pre_ed_addend=pre_ed_addend,
    )


def _scalar_fold(power: Power, power_slots: Sequence[SlotRef], handler: AspectHandler, ctx: StatsContext) -> float:
    """The Pass 3/4 fold divisor for one aspect, via the per-aspect handler registry.

    The handler (:mod:`coh_engine.enh_aspects`) supplies the aspect's global ``_selfEnhance``
    term and its cap; the power's ``ignore_enh`` set is the filter. Any incarnate scalar
    contribution for this ``(power, aspect)`` folds in as its pre-ED addend (co-ED'd with
    the slotted aggregate) and post-ED extra, reproducing the pre-ED / post-ED incarnate
    application straddling ``GBPA_Pass2_ApplyED``. The base_totals toggle-EndUse arm routes
    through the same ``fold_scalar``, so the two folds cannot diverge.
    """
    pre_ed, post_ed = ctx.incarnate_scalar.get((power.build_index, handler.aspect), (0.0, 0.0))
    aggregate = _aggregate(power_slots, handler.aspect, ctx, pre_ed)
    return fold_scalar(
        handler,
        aggregate,
        global_term(handler, ctx.global_enhance),
        ignore_enh=power.ignore_enh,
        recharge_cap=ctx.recharge_cap,
        post_ed_extra=post_ed,
    )


def _buffed_recharge(power: Power, power_slots: Sequence[SlotRef], ctx: StatsContext) -> float:
    """Buffed recharge = base / clamp((ED(sum rech) + global) + 1, recharge cap), 0 if base is 0."""
    if power.recharge_time <= 0.0:
        return 0.0
    return f32(power.recharge_time / _scalar_fold(power, power_slots, RECHARGE, ctx))


def compute_power_stats(power: Power, power_slots: Sequence[SlotRef], ctx: StatsContext) -> PowerStats:
    """The derived scalars + endurance/sec for one power (see the module docstring)."""
    recharge = _buffed_recharge(power, power_slots, ctx)
    end_cost = f32(power.end_cost / _scalar_fold(power, power_slots, END, ctx))
    interrupt = f32(power.interrupt_time / _scalar_fold(power, power_slots, INTERRUPT, ctx))

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
        cast_time=power.cast_time,
        is_attack=_is_attack(power),
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
