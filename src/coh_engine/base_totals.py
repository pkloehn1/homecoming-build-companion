"""Base per-attribute totals for a build with no enhancements (CP3).

Ports the no-enhancement slice of MidsReborn's totals pipeline: the buff pass
of ``CalculateAndApplyEffects`` (``clsToonX.cs:507-832``) feeding ``_selfBuffs``
and ``GBD_Totals`` (``clsToonX.cs:839-1002``) folding it into ``Totals`` and
``TotalsCapped``. With zero enhancements every GBPA multiplier is 1, so each
effect's ``BuffedMag`` equals its raw ``Mag`` and the enhancement pass
(``_selfEnhance``) contributes nothing — its read sites are kept at zero here
and wired up in CP4.

Semantics ported verbatim from the C# control flow, including the quirks:

- ``BuffsX.Effect[]`` is written by ``eEffectType`` ordinal and read back by
    ``eStatType`` ordinal (the shared entries coincide; ``enums.json`` is the
    source of both orderings).
- Generic (``DamageType == None``) Defense/Resistance effects fall through to
    ``Effect[eEffectType.*]``, which ``GBD_Totals`` never reads — only typed
    effects reach ``Totals.Def``/``Res``.
- ``MezRes``/``DebuffRes`` are scaled ``* 100`` at copy; ``Def``/``Res`` stay
    fractional.
- The Absorb %-of-HP normalization reads the *previous* recompute's
    ``Totals.HPMax`` (zero on a fresh headless compute).

CP3 conditional stance: effects carrying ``ActiveConditionals`` or a
``SpecialCase`` are excluded (``ValidateConditional`` and the ``CanInclude``
character-state switch are unported leaves). The fixture hazard gate verifies
no such effect feeds any bucket ``GBD_Totals`` reads.

Spec: docs/engine/mids-port-spec.md § effect-model, § gbpa-pass-pipeline,
§ gbd-totals-and-caps.
"""

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

from coh_engine.archetypes import Archetype, ArchetypeDb
from coh_engine.attribmod import AttribMods
from coh_engine.effect import Effect, Power, effect_mag
from coh_engine.maths import f32

_SPEED_EFFECT_TYPES = ("SpeedFlying", "SpeedRunning", "SpeedJumping")


@dataclass(frozen=True, slots=True)
class EnumMaps:
    """Name -> ordinal maps for the enums Mids indexes arrays by."""

    maps: Mapping[str, Mapping[str, int]]

    def size(self, enum_name: str) -> int:
        """Array length for ``enum_name`` — C# ``Enum.GetValues<T>().Length``."""
        return len(self.maps[enum_name])


def load_enum_maps(path: Path | str) -> EnumMaps:
    """Parse an ``enums.json`` Mids reference dump.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        raw = json.load(stream)
    return EnumMaps(maps=MappingProxyType({name: MappingProxyType(dict(members)) for name, members in raw.items()}))


@dataclass(frozen=True, slots=True)
class EngineConfig:
    """The MidsContext.Config state the reference totals were computed under."""

    suppression: int
    disable_pve: bool
    force_level: int
    scaling_to_hit: float


def load_engine_config(path: Path | str) -> EngineConfig:
    """Parse a ``config.json`` Mids reference dump.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        raw = json.load(stream)
    return EngineConfig(
        suppression=raw["Suppression"],
        disable_pve=raw["DisablePvE"],
        force_level=raw["ForceLevel"],
        scaling_to_hit=f32(raw["ScalingToHit"]),
    )


@dataclass(frozen=True, slots=True)
class ServerData:
    """Server-wide constants (``Core/ServerData.cs``), from the reference dump."""

    base_to_hit: float
    max_slots: int
    enable_inherent_slotting: bool
    base_fly_speed: float
    base_jump_speed: float
    base_jump_height: float
    base_perception: float
    base_run_speed: float
    max_fly_speed: float
    max_jump_speed: float
    max_jump_height: float
    max_run_speed: float
    max_max_fly_speed: float
    max_max_jump_speed: float
    max_max_run_speed: float


def load_server_data(path: Path | str) -> ServerData:
    """Parse a ``server_data.json`` Mids reference dump.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        raw = json.load(stream)
    return ServerData(
        base_to_hit=f32(raw["BaseToHit"]),
        max_slots=raw["MaxSlots"],
        enable_inherent_slotting=raw["EnableInherentSlotting"],
        base_fly_speed=f32(raw["BaseFlySpeed"]),
        base_jump_speed=f32(raw["BaseJumpSpeed"]),
        base_jump_height=f32(raw["BaseJumpHeight"]),
        base_perception=f32(raw["BasePerception"]),
        base_run_speed=f32(raw["BaseRunSpeed"]),
        max_fly_speed=f32(raw["MaxFlySpeed"]),
        max_jump_speed=f32(raw["MaxJumpSpeed"]),
        max_jump_height=f32(raw["MaxJumpHeight"]),
        max_run_speed=f32(raw["MaxRunSpeed"]),
        max_max_fly_speed=f32(raw["MaxMaxFlySpeed"]),
        max_max_jump_speed=f32(raw["MaxMaxJumpSpeed"]),
        max_max_run_speed=f32(raw["MaxMaxRunSpeed"]),
    )


@dataclass(slots=True)
class TotalStatistics:
    """Mirror of ``Character.TotalStatistics`` (``Character.cs:1857``)."""

    def_: list[float] = field(default_factory=list)
    res: list[float] = field(default_factory=list)
    mez: list[float] = field(default_factory=list)
    mez_res: list[float] = field(default_factory=list)
    debuff_res: list[float] = field(default_factory=list)
    elusivity: list[float] = field(default_factory=list)
    hp_regen: float = 0.0
    hp_max: float = 0.0
    absorb: float = 0.0
    end_rec: float = 0.0
    end_use: float = 0.0
    end_max: float = 0.0
    run_spd: float = 0.0
    max_run_spd: float = 0.0
    jump_spd: float = 0.0
    max_jump_spd: float = 0.0
    fly_spd: float = 0.0
    max_fly_spd: float = 0.0
    jump_height: float = 0.0
    stealth_pve: float = 0.0
    stealth_pvp: float = 0.0
    threat_level: float = 0.0
    perception: float = 0.0
    buff_haste: float = 0.0
    buff_acc: float = 0.0
    buff_to_hit: float = 0.0
    buff_dam: float = 0.0
    buff_end_rdx: float = 0.0
    buff_range: float = 0.0
    buff_heal: float = 0.0


@dataclass(frozen=True, slots=True)
class BaseTotals:
    """Result pair: uncapped ``Totals`` and AT/server-capped ``TotalsCapped``."""

    totals: TotalStatistics
    totals_capped: TotalStatistics


@dataclass(slots=True)
class _BuffsX:
    """Working accumulator — ``Enums.BuffsX`` (``Enums.cs:1906``), CP3 subset."""

    effect: list[float]
    effect_aux: list[float]
    mez: list[float]
    mez_res: list[float]
    damage: list[float]
    defense: list[float]
    resistance: list[float]
    elusivity: list[float]
    status_protection: list[float]
    status_resistance: list[float]
    debuff_resistance: list[float]
    boosts: list[float]
    boosts_mez: list[float]
    max_end: float


def _new_buffs(enums: EnumMaps) -> _BuffsX:
    n_effect = enums.size("eEffectType")
    n_mez = enums.size("eMez")
    n_damage = enums.size("eDamage")
    return _BuffsX(
        effect=[0.0] * n_effect,
        effect_aux=[0.0] * (n_effect - 1),
        mez=[0.0] * n_mez,
        mez_res=[0.0] * n_mez,
        damage=[0.0] * n_damage,
        defense=[0.0] * n_damage,
        resistance=[0.0] * n_damage,
        elusivity=[0.0] * n_damage,
        status_protection=[0.0] * n_mez,
        status_resistance=[0.0] * n_mez,
        debuff_resistance=[0.0] * n_effect,
        boosts=[0.0] * n_effect,
        boosts_mez=[0.0] * n_mez,
        max_end=0.0,
    )


@dataclass(frozen=True, slots=True)
class _MagContext:
    """The shared lookup context every magnitude computation needs."""

    mods: AttribMods
    classes: ArchetypeDb
    archetype_index: int
    config: EngineConfig


def _can_include(fx: Effect) -> bool:
    """CP3 slice of ``Effect.CanInclude`` (``Effect.cs:1856+``).

    True only for unconditional effects. Effects with ``ActiveConditionals``
    or a ``SpecialCase`` need the character-state evaluation leaves that are
    not ported yet; excluding them is validated by the fixture hazard gate
    (no such effect feeds a bucket ``GBD_Totals`` reads).
    """
    return fx.active_conditionals_count == 0 and fx.special_case == "None"


def _pvx_include(fx: Effect, archetype_index: int, config: EngineConfig) -> bool:
    """``Effect.PvXInclude`` (``Effect.cs:2610-2616``) with a non-null archetype."""
    pv_ok = (fx.pv_mode != "PvP" and not config.disable_pve) or (fx.pv_mode != "PvE" and config.disable_pve)
    class_ok = fx.n_id_class_name == -1 or fx.n_id_class_name == archetype_index
    return pv_ok and class_ok


def _get_effect_mag_sum(
    power: Power,
    i_effect: str,
    ctx: _MagContext,
    *,
    include_delayed: bool = False,
    only_self: bool = False,
    only_target: bool = False,
    max_mode: bool = False,
) -> list[tuple[Effect, float]]:
    """``Power.GetEffectMagSum`` (``Power.cs:1464-1522``) as (effect, mag) pairs.

    With no enhancements ``BuffedMag`` falls back to raw ``Mag``, so each pair
    carries ``Effect.Mag`` (ticks-multiplied for stacking DoTs).
    """
    out: list[tuple[Effect, float]] = []
    for fx in power.effects:
        flag = (
            (fx.to_who == "Target" and not only_self) or (fx.to_who == "Self" and not only_target) or fx.to_who == "All"
        )
        if i_effect in _SPEED_EFFECT_TYPES and not max_mode and fx.aspect == "Max":
            flag = False
        if ctx.config.suppression & fx.suppression:
            flag = False
        if (
            not flag
            or fx.probability <= 0
            or (max_mode and fx.aspect != "Max")
            or fx.effect_type != i_effect
            or fx.effect_class in ("Ignored", "Special")
            or (fx.delayed_time > 5 and not include_delayed)
            or not _can_include(fx)
            or not _pvx_include(fx, ctx.archetype_index, ctx.config)
        ):
            continue
        mag = _mag(fx, power, ctx)
        if fx.ticks > 1 and fx.stacking == "Yes":
            mag = f32(mag * fx.ticks)
        out.append((fx, mag))
    return out


def _mag(fx: Effect, power: Power, ctx: _MagContext) -> float:
    return effect_mag(fx, power, ctx.mods, ctx.classes, ctx.archetype_index)


def _apply_buff_effects(
    power: Power,
    buffs: _BuffsX,
    ctx: _MagContext,
    *,
    enums: EnumMaps,
    prev_hp_max: float,
) -> None:
    """Buff (non-enhancement) pass of ``CalculateAndApplyEffects`` for one power.

    ``clsToonX.cs:507-832`` with ``enhancementPass == false``. GlobalBoost
    powers are skipped by the caller's contract in C#; none exist in a dumped
    build's power list, so the guard is kept here for fidelity.
    """
    if power.power_type == "GlobalBoost":
        return

    effect_type_names = {v: k for k, v in enums.maps["eEffectType"].items()}
    stat = enums.maps["eStatType"]
    e_type = enums.maps["eEffectType"]
    e_mez = enums.maps["eMez"]
    e_damage = enums.maps["eDamage"]
    max_speed_sources = {
        "MaxRunSpeed": "SpeedRunning",
        "MaxJumpSpeed": "SpeedJumping",
        "MaxFlySpeed": "SpeedFlying",
    }

    for eff_index in range(len(buffs.effect)):
        i_effect = effect_type_names[eff_index]
        if i_effect == "Damage":
            continue

        if i_effect in max_speed_sources:
            pairs = _get_effect_mag_sum(power, max_speed_sources[i_effect], ctx, max_mode=True)
            self_sum = _sum_mags(_get_effect_mag_sum(power, i_effect, ctx, only_self=True))
            buffs.effect[stat[i_effect]] = f32(buffs.effect[stat[i_effect]] + self_sum)
        else:
            pairs = _get_effect_mag_sum(power, i_effect, ctx)

        for fx, value in pairs:
            if fx.to_who not in ("Self", "All"):
                continue

            if fx.effect_type == "Enhancement":
                if fx.et_modifies == "Mez" and fx.mez_type != "None":
                    _add(buffs.boosts_mez, e_mez[fx.mez_type], value)
                elif fx.et_modifies not in ("None", "Null", "NullBool", "Mez"):
                    _add(buffs.boosts, e_type[fx.et_modifies], value)
                if fx.et_modifies == "Range":
                    _add(buffs.effect, e_type["Range"], value)
                if fx.et_modifies == "Heal":
                    _add(buffs.effect, e_type["Heal"], value)

            if fx.absorbed_power_type == "GlobalBoost":
                continue

            if fx.effect_type == "Mez":
                _add(buffs.status_protection, e_mez[fx.mez_type], value)
            elif fx.effect_type == "MezResist":
                _add(buffs.status_resistance, e_mez[fx.mez_type], value)
            elif fx.effect_type == "ResEffect":
                _add(buffs.debuff_resistance, e_type[fx.et_modifies], value)

            if fx.effect_type == "Heal" or (fx.effect_type == "Enhancement" and fx.et_modifies == "Heal"):
                continue
            if fx.effect_type == "Endurance" and fx.aspect == "Max":
                buffs.max_end = f32(buffs.max_end + value)
                continue
            if fx.effect_type != "ResEffect" and fx.et_modifies == "Mez":
                _add(buffs.mez, e_mez[fx.mez_type], value)
                continue
            if fx.effect_type != "ResEffect" and fx.et_modifies == "MezResist":
                _add(buffs.mez_res, e_mez[fx.mez_type], value)
                continue
            if i_effect == "Defense" and fx.damage_type != "None":
                _add(buffs.defense, e_damage[fx.damage_type], value)
                continue
            if i_effect == "Resistance" and fx.damage_type != "None":
                _add(buffs.resistance, e_damage[fx.damage_type], value)
                continue
            if i_effect == "Elusivity" and fx.damage_type != "None":
                _add(buffs.elusivity, e_damage[fx.damage_type], value)
                continue
            if fx.effect_type != "ResEffect" and fx.et_modifies == "Accuracy":
                # IsGlobalAccuracySource routes set-bonus / GlobalBoost sources
                # to BuffAcc instead — both arrive with the CP5 set-bonus
                # virtual power; every power in a dumped build list is an
                # ordinary source, and ordinary accuracy buffs act as ToHit.
                _add(buffs.effect, stat["ToHit"], value)
                continue
            if _is_max_speed_cap(fx, "SpeedRunning"):
                _add(buffs.effect, stat["MaxRunSpeed"], value)
                continue
            if _is_max_speed_cap(fx, "SpeedFlying"):
                _add(buffs.effect, stat["MaxFlySpeed"], value)
                continue
            if _is_max_speed_cap(fx, "SpeedJumping"):
                _add(buffs.effect, stat["MaxJumpSpeed"], value)
                continue
            if i_effect == "ToHit":
                if not (fx.is_enhancement_effect and fx.effect_class == "Tertiary"):
                    _add(buffs.effect, eff_index, value)
                continue

            if eff_index == stat["Absorb"] and fx.display_percentage:
                value = f32(value * prev_hp_max)
            _add(buffs.effect, eff_index, value)
            if power.power_type == "Click" and not power.click_buff:
                buffs.effect[eff_index] = f32(buffs.effect[eff_index] - _mag(fx, power, ctx))


def _is_max_speed_cap(fx: Effect, mod: str) -> bool:
    return fx.effect_type != "ResEffect" and fx.et_modifies == mod and fx.aspect == "Max"


def _add(bucket: list[float], index: int, value: float) -> None:
    bucket[index] = f32(bucket[index] + value)


def _sum_mags(pairs: list[tuple[Effect, float]]) -> float:
    total = 0.0
    for _, mag in pairs:
        total = f32(total + mag)
    return total


def compute_base_totals(
    powers: Sequence[Power],
    *,
    class_name: str,
    mods: AttribMods,
    classes: ArchetypeDb,
    enums: EnumMaps,
    config: EngineConfig,
    server: ServerData,
    prev_hp_max: float = 0.0,
) -> BaseTotals:
    """Compute base ``Totals``/``TotalsCapped`` for an empty-slot build.

    ``powers`` are the dumped build powers; only ``stat_include`` entries
    contribute (``GBD_Totals`` preamble). ``prev_hp_max`` is the previous
    recompute's ``Totals.HPMax`` that the Absorb normalization reads — zero on
    a fresh headless compute.

    Raises:
        ValueError: if ``class_name`` is not a known archetype.
    """
    archetype_index = classes.nid_from_uid_class(class_name)
    if archetype_index < 0:
        raise ValueError(f"E09: unknown archetype class name: {class_name!r}")
    archetype = classes.classes[archetype_index]
    ctx = _MagContext(mods=mods, classes=classes, archetype_index=archetype_index, config=config)

    self_buffs = _new_buffs(enums)
    self_enhance = _new_buffs(enums)  # CP4 wires the enhancement pass; zero here.
    included = [p for p in powers if p.stat_include]

    for power in included:
        _apply_buff_effects(power, self_buffs, ctx, enums=enums, prev_hp_max=prev_hp_max)

    return _gbd_totals(
        included,
        self_buffs,
        self_enhance,
        archetype=archetype,
        ctx=ctx,
        enums=enums,
        server=server,
    )


def _gbd_totals(
    included: Sequence[Power],
    self_buffs: _BuffsX,
    self_enhance: _BuffsX,
    *,
    archetype: Archetype,
    ctx: _MagContext,
    enums: EnumMaps,
    server: ServerData,
) -> BaseTotals:
    """``GBD_Totals`` (``clsToonX.cs:839-1002``)."""
    stat = enums.maps["eStatType"]
    totals = TotalStatistics(
        def_=[0.0] * enums.size("eDamage"),
        res=[0.0] * enums.size("eDamage"),
        mez=[0.0] * enums.size("eMez"),
        mez_res=[0.0] * enums.size("eMez"),
        debuff_res=[0.0] * enums.size("eEffectType"),
        elusivity=[0.0] * enums.size("eDamage"),
    )

    can_fly = False
    for power in included:
        if power.power_type == "Toggle":
            totals.end_use = f32(totals.end_use + power.toggle_cost)
        for fx in power.effects:
            if fx.effect_type == "Fly" and _mag(fx, power, ctx) > 0:
                can_fly = True

    if abs(self_buffs.defense[0]) > _FLOAT_EPSILON:
        for index in range(1, len(self_buffs.defense)):
            self_buffs.defense[index] = f32(self_buffs.defense[index] + self_buffs.defense[0])

    for index in range(len(self_buffs.defense)):
        totals.def_[index] = self_buffs.defense[index]
        totals.res[index] = self_buffs.resistance[index]
        totals.elusivity[index] = self_buffs.elusivity[index]

    for index in range(len(self_buffs.status_protection)):
        totals.mez[index] = self_buffs.status_protection[index]
        totals.mez_res[index] = f32(self_buffs.status_resistance[index] * 100)

    for index in range(len(self_buffs.debuff_resistance)):
        totals.debuff_res[index] = f32(self_buffs.debuff_resistance[index] * 100)

    totals.end_max = self_buffs.max_end
    totals.buff_acc = f32(self_enhance.effect[stat["BuffAcc"]] + self_buffs.effect[stat["BuffAcc"]])
    totals.buff_end_rdx = self_enhance.effect[stat["BuffEndRdx"]]
    totals.buff_haste = f32(self_enhance.effect[stat["Haste"]] + self_buffs.effect[stat["Haste"]])
    totals.buff_to_hit = self_buffs.effect[stat["ToHit"]]
    totals.perception = f32(server.base_perception * f32(1 + self_buffs.effect[stat["Perception"]]))
    totals.stealth_pve = self_buffs.effect[stat["StealthPvE"]]
    totals.stealth_pvp = self_buffs.effect[stat["StealthPvP"]]
    totals.threat_level = self_buffs.effect[stat["ThreatLevel"]]
    totals.hp_regen = self_buffs.effect[stat["HPRegen"]]
    totals.end_rec = self_buffs.effect[stat["EndRec"]]
    totals.absorb = self_buffs.effect[stat["Absorb"]]
    totals.buff_range = self_buffs.effect[stat["Range"]]

    totals.fly_spd = _speed(self_buffs.effect[stat["FlySpeed"]], server.base_fly_speed)
    totals.run_spd = _speed(self_buffs.effect[stat["RunSpeed"]], server.base_run_speed)
    totals.jump_spd = _speed(self_buffs.effect[stat["JumpSpeed"]], server.base_jump_speed)
    totals.jump_height = _speed(self_buffs.effect[stat["JumpHeight"]], server.base_jump_height)

    totals.max_fly_spd = f32(server.max_fly_speed + f32(self_buffs.effect[stat["MaxFlySpeed"]] * server.base_fly_speed))
    totals.max_run_spd = f32(server.max_run_speed + f32(self_buffs.effect[stat["MaxRunSpeed"]] * server.base_run_speed))
    totals.max_jump_spd = f32(
        server.max_jump_speed + f32(self_buffs.effect[stat["MaxJumpSpeed"]] * server.base_jump_speed)
    )

    totals.fly_spd = min(totals.fly_spd, server.max_max_fly_speed)
    totals.run_spd = min(totals.run_spd, server.max_max_run_speed)
    totals.jump_spd = min(totals.jump_spd, server.max_max_jump_speed)

    totals.hp_max = f32(self_buffs.effect[stat["HPMax"]] + archetype.hitpoints)
    if not can_fly:
        totals.fly_spd = 0.0

    if all(abs(e) < _FLOAT_EPSILON for e in self_buffs.damage):
        for i in range(len(self_buffs.damage)):
            self_buffs.damage[i] = f32(self_buffs.damage[i] + self_enhance.damage[i])

    dmg_slice = self_buffs.damage[1:8]
    min_dmg = min(dmg_slice)
    max_dmg = max(dmg_slice)
    avg_dmg = f32(_float_average(dmg_slice))
    if max_dmg - avg_dmg < avg_dmg - min_dmg:
        totals.buff_dam = max_dmg
    elif (max_dmg - avg_dmg > avg_dmg - min_dmg) and min_dmg > 0:
        totals.buff_dam = min_dmg
    else:
        totals.buff_dam = max_dmg

    totals.buff_heal = self_buffs.effect[stat["Heal"]]

    if ctx.config.disable_pve:
        for index in range(len(totals.def_)):
            totals.def_[index] = calculate_pvp_dr(totals.def_[index])

    capped = _assign(totals)
    capped.buff_dam = min(capped.buff_dam, f32(archetype.damage_cap - 1))
    capped.buff_haste = min(capped.buff_haste, f32(archetype.recharge_cap - 1))
    capped.hp_regen = min(capped.hp_regen, f32(archetype.regen_cap - 1))
    capped.end_rec = min(capped.end_rec, f32(archetype.recovery_cap - 1))
    for index in range(len(capped.res)):
        capped.res[index] = min(capped.res[index], f32(archetype.res_cap))
    if archetype.hp_cap > 0:
        capped.hp_max = min(capped.hp_max, f32(archetype.hp_cap))
        capped.absorb = min(capped.absorb, capped.hp_max)
    capped.run_spd = min(capped.run_spd, totals.max_run_spd)
    capped.jump_spd = min(capped.jump_spd, totals.max_jump_spd)
    capped.fly_spd = min(capped.fly_spd, totals.max_fly_spd)
    capped.jump_height = min(capped.jump_height, server.max_jump_height)
    capped.perception = min(capped.perception, f32(archetype.perception_cap))

    return BaseTotals(totals=totals, totals_capped=capped)


def calculate_pvp_dr(value: float, a: float = 1.2, b: float = 1.0) -> float:
    """``CalculatePvpDr`` (``clsToonX.cs:335-338``): PvP defense diminishing returns."""
    return f32(value * (1.0 - abs(math.atan(a * value)) * (2.0 / math.pi) * b))


def _speed(effect_value: float, base: float) -> float:
    return f32(f32(1 + max(effect_value, f32(-0.9))) * base)


def _float_average(values: Sequence[float]) -> float:
    # .NET LINQ Average over float[] sums in double, divides, then narrows.
    return sum(values) / len(values)


def _assign(totals: TotalStatistics) -> TotalStatistics:
    """``TotalStatistics.Assign`` — a value copy of every field."""
    return TotalStatistics(
        def_=list(totals.def_),
        res=list(totals.res),
        mez=list(totals.mez),
        mez_res=list(totals.mez_res),
        debuff_res=list(totals.debuff_res),
        elusivity=list(totals.elusivity),
        hp_regen=totals.hp_regen,
        hp_max=totals.hp_max,
        absorb=totals.absorb,
        end_rec=totals.end_rec,
        end_use=totals.end_use,
        end_max=totals.end_max,
        # Verbatim C# quirk: Assign (Character.cs:1940-1970) does NOT copy
        # MaxRunSpd/MaxJumpSpd/MaxFlySpd — TotalsCapped keeps them at 0 and
        # the speed caps below read them from the uncapped Totals instead.
        run_spd=totals.run_spd,
        jump_spd=totals.jump_spd,
        fly_spd=totals.fly_spd,
        jump_height=totals.jump_height,
        stealth_pve=totals.stealth_pve,
        stealth_pvp=totals.stealth_pvp,
        threat_level=totals.threat_level,
        perception=totals.perception,
        buff_haste=totals.buff_haste,
        buff_acc=totals.buff_acc,
        buff_to_hit=totals.buff_to_hit,
        buff_dam=totals.buff_dam,
        buff_end_rdx=totals.buff_end_rdx,
        buff_range=totals.buff_range,
        buff_heal=totals.buff_heal,
    )


# C# float.Epsilon: the smallest positive subnormal single (~1.401e-45).
_FLOAT_EPSILON = 1.401298464324817e-45
