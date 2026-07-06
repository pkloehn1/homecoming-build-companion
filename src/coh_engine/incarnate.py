"""Incarnate (Alpha-slot) enhancement — the GrantPower-delivered per-power fold.

An incarnate's real enhancement is **GrantPower-delivered**: the raw
``Incarnate.Alpha.*`` power carries only ``GrantPower``/``RevokePower``/``LevelShift``/
``SetMode``, and the actual Accuracy/RechargeTime/Defense/… enhancement lives on the
hidden granted sub-powers (``Effect.Summon`` / ``nSummon`` → ``db.Power[nSummon]``). The
harness resolves those sub-powers and dumps their ``Enhancement``/``DamageBuff`` effects
plus each sub-power's accept-gate class list as ``incarnates.json`` (see
``tools/mids-dump`` ``DumpBuildIncarnates``); this module applies them per target power,
reproducing ``GBPA_ApplyIncarnateEnhancements`` (clsToonX.cs:1393) **without** porting the
GrantPower absorption subsystem.

The apply, per target power ``powerMath`` and per granted sub-power ``sub``:

- **Accept-gate** (clsToonX.cs:1458): ``powerMath.Enhancements ∩ sub.Enhancements`` must be
    non-empty. The gate is the SUB-power's class list, not the Alpha's (which is empty).
- **Scalar aspects** (clsToonX.cs:1470-1495): ``ETModifies`` of Accuracy / EnduranceDiscount
    / RechargeTime (each gated by the target's ``IgnoreEnhancement``) and InterruptTime /
    Range (always) add the effect's magnitude to that per-power scalar's fold — the pre-ED
    term where ``IgnoreED`` is false, the post-ED term where true.
- **Effect-borne aspects** (``HandleDefaultIncarnateEnh``, clsToonX.cs:1291): every other
    ``ETModifies`` (Defense, Recovery, Endurance, …) adds the magnitude to each Buffable
    target effect whose ``EffectType == ETModifies`` (and ``DamageType`` matches, for
    Damage/Defense), as the same pre-ED / post-ED split folded into that effect's Math_Mag
    multiplier.

The ED-bypass the Alpha headline describes **is** the ``IgnoreED`` split: the DB stores each
aspect twice — an ``IgnoreED == false`` effect crushed together with slotted enhancement
(pre-ED) and an ``IgnoreED == true`` effect added at full value after ED (post-ED).

This module produces two addend maps; the numeric core (``statistics``, ``base_totals``)
looks them up and stays a literal Mids transcription (check-registry.md fidelity boundary):

- ``scalar[(build_index, aspect)] = (pre_ed, post_ed)`` — the recharge/end/interrupt/acc/
    range per-power scalar fold (``pre_ed`` co-EDs with slotted enhancement, ``post_ed`` is
    the ``fold_scalar`` ``post_ed_extra`` seam).
- ``effect[(build_index, effect_index)] = ED(pre_ed) + post_ed`` — the effect-mag addend
    added onto ``1 + ED(Σ slotted)`` for that effect.

Scope boundary: the recharge-Alpha parity fixture has **empty slots**, so a target effect
never carries both slotted enhancement and an incarnate effect addend for the same aspect.
Co-slotting the two on one effect would need them co-ED'd (one ``ApplyED`` over the summed
pre-ED terms); :func:`resolve_incarnates` refuses that case loudly (``E19``) rather than
apply the two ED passes separately and diverge from Mids.

Spec: docs/engine/mids-port-spec.md § gbpa-pass-pipeline; .claude/rules/check-registry.md.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from coh_engine.archetypes import ArchetypeDb
from coh_engine.attribmod import AttribMods
from coh_engine.ed import apply_ed
from coh_engine.effect import Effect, Power, effect_mag
from coh_engine.enh_pipeline import schedule_for_enhance
from coh_engine.maths import MathTables, f32

# The scalar-aspect switch of GBPA_ApplyIncarnateEnhancements (clsToonX.cs:1470-1495):
# ETModifies -> (the eEnhance handler aspect name, whether the target's IgnoreEnhancement
# gate applies). Accuracy/EnduranceDiscount/RechargeTime are gated (skip when the target
# ignores that enhancement); InterruptTime/Range always apply. Every other ETModifies is
# effect-borne (HandleDefaultIncarnateEnh).
_SCALAR_ROUTES: Mapping[str, tuple[str, bool]] = {
    "Accuracy": ("Accuracy", True),
    "EnduranceDiscount": ("EnduranceDiscount", True),
    "InterruptTime": ("Interrupt", False),
    "Range": ("Range", False),
    "RechargeTime": ("RechargeTime", True),
}

# Effect-borne ETModifies that additionally match on DamageType (HandleDefaultIncarnateEnh
# Damage/Defense cases, clsToonX.cs:1309-1318); all other effect-borne aspects match on
# EffectType alone (the default case, clsToonX.cs:1355).
_DAMAGE_TYPED_ASPECTS = frozenset({"Damage", "Defense"})


@dataclass(frozen=True, slots=True)
class IncarnateSubPower:
    """One granted sub-power carrying an incarnate aspect and its accept-gate class list."""

    full_name: str
    enhancements: frozenset[int]
    effects: tuple[Effect, ...]


@dataclass(frozen=True, slots=True)
class Incarnate:
    """One StatInclude ``Incarnate.*`` build power and its granted sub-powers."""

    build_index: int
    full_name: str
    sub_powers: tuple[IncarnateSubPower, ...]


@dataclass(frozen=True, slots=True)
class IncarnateAddends:
    """The pre/post-ED incarnate contributions the numeric core folds in.

    ``scalar`` is keyed by ``(build_index, eEnhance aspect name)`` and carries the
    ``(pre_ed, post_ed)`` scalar addends. ``effect`` is keyed by ``(build_index,
    effect_index)`` and carries the ready-to-add effect-mag addend ``ED(pre_ed) +
    post_ed`` (added onto ``1 + ED(Σ slotted)`` for that effect).
    """

    scalar: Mapping[tuple[int, str], tuple[float, float]]
    effect: Mapping[tuple[int, int], float]


def load_incarnates(path: Path | str) -> tuple[Incarnate, ...]:
    """Parse an ``incarnates.json`` Mids reference dump.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        records = json.load(stream)
    return tuple(
        Incarnate(
            build_index=r["BuildIndex"],
            full_name=r["FullName"],
            sub_powers=tuple(
                IncarnateSubPower(
                    full_name=s["FullName"],
                    enhancements=frozenset(s["Enhancements"]),
                    effects=tuple(_parse_incarnate_effect(fx) for fx in s["Effects"]),
                )
                for s in r["SubPowers"]
            ),
        )
        for r in records
    )


def _parse_incarnate_effect(raw: dict[str, Any]) -> Effect:
    """One incarnate sub-power effect. Mirrors ``effect._parse_effect`` field-for-field."""
    return Effect(
        index=raw["Index"],
        effect_type=raw["EffectType"],
        damage_type=raw["DamageType"],
        mez_type=raw["MezType"],
        et_modifies=raw["ETModifies"],
        scale=f32(raw["Scale"]),
        n_magnitude=f32(raw["nMagnitude"]),
        n_duration=f32(raw["nDuration"]),
        attrib_type=raw["AttribType"],
        aspect=raw["Aspect"],
        modifier_table=raw["ModifierTable"],
        n_modifier_table=raw["nModifierTable"],
        to_who=raw["ToWho"],
        pv_mode=raw["PvMode"],
        stacking=raw["Stacking"],
        suppression=raw["Suppression"],
        buffable=raw["Buffable"],
        resistible=raw["Resistible"],
        ignore_ed=raw["IgnoreED"],
        ignore_scaling=raw["IgnoreScaling"],
        variable_modified=raw["VariableModified"],
        base_probability=f32(raw["BaseProbability"]),
        probability=f32(raw["Probability"]),
        procs_per_minute=f32(raw["ProcsPerMinute"]),
        ticks=raw["Ticks"],
        delayed_time=f32(raw["DelayedTime"]),
        effect_class=raw["EffectClass"],
        special_case=raw["SpecialCase"],
        n_id_class_name=raw["nIDClassName"],
        absorbed_effect=raw["Absorbed_Effect"],
        absorbed_power_type=raw["Absorbed_PowerType"],
        absorbed_class_n_id=raw["Absorbed_Class_nID"],
        active_conditionals_count=raw["ActiveConditionalsCount"],
        expr_magnitude=raw["ExprMagnitude"],
        expr_duration=raw["ExprDuration"],
        expr_probability=raw["ExprProbability"],
        display_percentage=raw["DisplayPercentage"],
    )


# A synthetic power context for the sub-power magnitude read: incarnate sub-power effects
# carry no ForcedClass and no variable scaling, so effect_mag routes GetModifier to the
# build's archetype at the fixed math level (the Melee_Ones table these effects use is
# all-ones, so BuffedMag == Scale).
def _sub_power_context(full_name: str) -> Power:
    return Power(
        build_index=-1,
        nid_power=-1,
        full_name=full_name,
        static_index=-1,
        power_type="",
        forced_class="",
        click_buff=False,
        level=0,
        end_cost=0.0,
        activate_period=0.0,
        toggle_cost=0.0,
        variable_enabled=False,
        stat_include=False,
        variable_value=0,
        effects=(),
    )


@dataclass(frozen=True, slots=True)
class _ResolveContext:
    """The shared inputs the incarnate magnitude read needs."""

    mods: AttribMods
    classes: ArchetypeDb
    archetype_index: int
    tables: MathTables


def _buffed_mag(effect: Effect, sub_full_name: str, ctx: _ResolveContext) -> float:
    """The sub-power effect's ``BuffedMag`` — its base ``Mag`` (Pass5 has not run)."""
    return effect_mag(effect, _sub_power_context(sub_full_name), ctx.mods, ctx.classes, ctx.archetype_index)


def _scalar_aspect(effect: Effect, power: Power) -> str | None:
    """The scalar handler aspect an incarnate effect folds into, or ``None`` if effect-borne.

    Returns ``None`` both for a genuinely effect-borne ``ETModifies`` and for a gated
    scalar aspect the target ignores (``IgnoreEnhancement`` false) — in the latter case
    Mids' switch falls through to the effect-mag default, which finds no matching scalar
    effect, so dropping it is faithful.
    """
    route = _SCALAR_ROUTES.get(effect.et_modifies)
    if route is None:
        return None
    aspect, gated = route
    if gated and aspect in power.ignore_enh:
        return None
    return aspect


def _matches_effect(target_fx: Effect, inc: Effect) -> bool:
    """Whether an incarnate effect-borne aspect enhances this Buffable target effect.

    ``HandleDefaultIncarnateEnh``: the target effect must be Buffable and its
    ``EffectType`` equal the incarnate ``ETModifies``; Damage/Defense additionally match
    on ``DamageType`` (clsToonX.cs:1300-1318), every other aspect on EffectType alone.
    """
    if not target_fx.buffable or target_fx.effect_type != inc.et_modifies:
        return False
    if inc.et_modifies in _DAMAGE_TYPED_ASPECTS:
        return target_fx.damage_type == inc.damage_type
    return True


def _guard_supported(effect: Effect, sub_full_name: str) -> None:
    """Refuse the incarnate delivery paths this port does not yet apply.

    Raises:
        NotImplementedError: ``E20`` for a DamageBuff / GrantPower / GlobalChanceMod
            sub-effect (damage-Alpha, nested GrantPower, Hybrid GlobalChanceMod) or a Mez
            aspect (the duration/magnitude split is unported) — each needs its own
            validated fixture before it is applied, so fail loud rather than under-report.
    """
    if effect.effect_type != "Enhancement":
        raise NotImplementedError(
            f"E20: incarnate sub-power {sub_full_name!r} carries a {effect.effect_type!r} effect; only "
            "Enhancement-delivered incarnate aspects are ported (DamageBuff/GrantPower/GlobalChanceMod need "
            "a damage-Alpha / nested-GrantPower / Hybrid fixture first)"
        )
    if effect.et_modifies == "Mez":
        raise NotImplementedError(
            f"E20: incarnate sub-power {sub_full_name!r} enhances Mez; the magnitude/duration split of an "
            "incarnate Mez aspect is unported — add a Nerve-style fixture before applying it"
        )


def _route_effect(
    inc: Effect,
    sub_full_name: str,
    power: Power,
    ctx: _ResolveContext,
    scalar: dict[tuple[int, str], tuple[float, float]],
    effect_pre: dict[tuple[int, int], tuple[float, float]],
) -> None:
    """Route one accepted incarnate effect for one target power into the addend buckets."""
    mag = _buffed_mag(inc, sub_full_name, ctx)
    aspect = _scalar_aspect(inc, power)
    if aspect is not None:
        _add_split(scalar, (power.build_index, aspect), mag, inc.ignore_ed)
        return
    _guard_supported(inc, sub_full_name)
    for target_fx in power.effects:
        if _matches_effect(target_fx, inc):
            _add_split(effect_pre, (power.build_index, target_fx.index), mag, inc.ignore_ed)


def _add_split(bucket: dict[Any, tuple[float, float]], key: Any, mag: float, ignore_ed: bool) -> None:
    """Accumulate ``mag`` into the pre-ED (``IgnoreED`` false) or post-ED (true) slot of ``key``."""
    pre, post = bucket.get(key, (0.0, 0.0))
    if ignore_ed:
        bucket[key] = (pre, f32(post + mag))
    else:
        bucket[key] = (f32(pre + mag), post)


def resolve_incarnates(
    incarnates: Iterable[Incarnate],
    powers: Sequence[Power],
    *,
    mods: AttribMods,
    classes: ArchetypeDb,
    archetype_index: int,
    tables: MathTables,
    slots: Mapping[int, Sequence[Any]] | None = None,
) -> IncarnateAddends:
    """Fold every accepted incarnate aspect over every build power into the addend maps.

    ``slots`` (when supplied) is only consulted to refuse the co-slotting case the fixture
    does not cover: a target effect that carries both a slotted enhancement and an
    incarnate effect addend must be co-ED'd, which this separate-ED path does not do.

    Raises:
        NotImplementedError: ``E19`` if an incarnate effect addend lands on a power that
            also has filled slots (the co-ED path is unported); ``E20`` via
            :func:`_guard_supported` for an unported delivery path.
    """
    ctx = _ResolveContext(mods=mods, classes=classes, archetype_index=archetype_index, tables=tables)
    by_index = {power.build_index: power for power in powers}
    scalar: dict[tuple[int, str], tuple[float, float]] = {}
    effect_pre: dict[tuple[int, int], tuple[float, float]] = {}

    for incarnate in incarnates:
        for sub in incarnate.sub_powers:
            for power in powers:
                if not sub.enhancements.intersection(power.enhancements):
                    continue
                for inc in sub.effects:
                    _route_effect(inc, sub.full_name, power, ctx, scalar, effect_pre)

    effect = _ed_effect_addends(effect_pre, by_index, tables, slots)
    return IncarnateAddends(scalar=scalar, effect=effect)


def _ed_effect_addends(
    effect_pre: Mapping[tuple[int, int], tuple[float, float]],
    by_index: Mapping[int, Power],
    tables: MathTables,
    slots: Mapping[int, Sequence[Any]] | None,
) -> dict[tuple[int, int], float]:
    """Turn per-effect ``(pre_ed, post_ed)`` into the ED'd addend, refusing co-slotting.

    The ED schedule is the target effect's aspect schedule (``schedule_for_enhance`` on
    the effect's ``EffectType``), matching Mids' Pass 2, which EDs the effect's Math_Mag
    on the enhancement schedule named by its EffectType.
    """
    out: dict[tuple[int, int], float] = {}
    for (build_index, effect_index), (pre, post) in effect_pre.items():
        if slots is not None and _has_filled_slot(slots.get(build_index, ())):
            raise NotImplementedError(
                f"E19: build power index {build_index} carries both filled slots and an incarnate effect "
                "enhancement; co-ED of slotted + incarnate pre-ED terms on one effect is unported — the "
                "recharge-Alpha fixture is empty-slot. Add a slotted-incarnate fixture and co-ED both terms."
            )
        power = by_index[build_index]
        target_fx = next(fx for fx in power.effects if fx.index == effect_index)
        # Damage/Defense effects share the enhancement schedule of their aspect name; a
        # generic (schedule A) fallback covers Recovery/Endurance/Heal/etc.
        schedule = schedule_for_enhance(target_fx.effect_type)
        out[(build_index, effect_index)] = f32(apply_ed(schedule, pre, tables) + post)
    return out


def _has_filled_slot(power_slots: Sequence[Any]) -> bool:
    """Whether any of the power's slots holds an enhancement (``enh > -1``)."""
    return any(getattr(slot, "enh", -1) > -1 for slot in power_slots)
