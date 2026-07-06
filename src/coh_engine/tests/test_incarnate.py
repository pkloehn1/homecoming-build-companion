"""Unit tests for the incarnate subsystem: routing, gating, and the fail-loud guards.

The end-to-end magnitude parity lives in ``test_incarnate_parity.py`` (against the Agility
Alpha reference dump); here the routing decisions and the unported-path refusals are
exercised directly with synthetic incarnates over the ``tiny_mods`` / ``tiny_classes``
harness, whose ``Ones`` modifier table makes an effect's ``BuffedMag`` equal its ``Scale``.
"""

from typing import Any

import pytest

from coh_engine import base_totals, incarnate
from coh_engine.archetypes import ArchetypeDb
from coh_engine.attribmod import AttribMods
from coh_engine.enhancement import SlotRef
from coh_engine.incarnate import (
    Incarnate,
    IncarnateSubPower,
    resolve_incarnates,
)
from coh_engine.maths import MathTables, f32


def _sub(*effects: Any, enhancements: frozenset[int] = frozenset({5})) -> IncarnateSubPower:
    return IncarnateSubPower(full_name="Incarnate.Alpha_Silent.Test", enhancements=enhancements, effects=tuple(effects))


def _filled_slot() -> SlotRef:
    return SlotRef(level=0, is_inherent=False, enh=42, grade=0, io_level=49, relative_level=1)


class TestScalarAspect:
    """``_scalar_aspect`` maps an incarnate ETModifies to a scalar handler or ``None``."""

    def test_recharge_routes_when_enhanceable(self, make_effect: Any, make_power: Any) -> None:
        fx = make_effect(effect_type="Enhancement", et_modifies="RechargeTime")
        assert incarnate._scalar_aspect(fx, make_power()) == "RechargeTime"

    def test_gated_aspect_ignored_by_target_is_dropped(self, make_effect: Any, make_power: Any) -> None:
        fx = make_effect(effect_type="Enhancement", et_modifies="RechargeTime")
        assert incarnate._scalar_aspect(fx, make_power(ignore_enh=("RechargeTime",))) is None

    def test_interrupt_is_ungated(self, make_effect: Any, make_power: Any) -> None:
        fx = make_effect(effect_type="Enhancement", et_modifies="InterruptTime")
        assert incarnate._scalar_aspect(fx, make_power(ignore_enh=("Interrupt",))) == "Interrupt"

    def test_range_routes(self, make_effect: Any, make_power: Any) -> None:
        fx = make_effect(effect_type="Enhancement", et_modifies="Range")
        assert incarnate._scalar_aspect(fx, make_power()) == "Range"

    def test_effect_borne_aspect_is_none(self, make_effect: Any, make_power: Any) -> None:
        fx = make_effect(effect_type="Enhancement", et_modifies="Defense")
        assert incarnate._scalar_aspect(fx, make_power()) is None


class TestMatchesEffect:
    """``_matches_effect`` reproduces HandleDefaultIncarnateEnh's per-effect match."""

    def test_defense_matches_on_damage_type(self, make_effect: Any) -> None:
        inc = make_effect(et_modifies="Defense", damage_type="Smashing")
        target = make_effect(effect_type="Defense", damage_type="Smashing", buffable=True)
        assert incarnate._matches_effect(target, inc)

    def test_defense_wrong_damage_type_no_match(self, make_effect: Any) -> None:
        inc = make_effect(et_modifies="Defense", damage_type="Smashing")
        target = make_effect(effect_type="Defense", damage_type="Fire", buffable=True)
        assert not incarnate._matches_effect(target, inc)

    def test_recovery_matches_on_effect_type_only(self, make_effect: Any) -> None:
        inc = make_effect(et_modifies="Recovery", damage_type="None")
        target = make_effect(effect_type="Recovery", damage_type="Smashing", buffable=True)
        assert incarnate._matches_effect(target, inc)

    def test_non_buffable_target_no_match(self, make_effect: Any) -> None:
        inc = make_effect(et_modifies="Recovery")
        target = make_effect(effect_type="Recovery", buffable=False)
        assert not incarnate._matches_effect(target, inc)

    def test_wrong_effect_type_no_match(self, make_effect: Any) -> None:
        inc = make_effect(et_modifies="Recovery")
        target = make_effect(effect_type="Defense", buffable=True)
        assert not incarnate._matches_effect(target, inc)


class TestGuardSupported:
    """``_guard_supported`` refuses the incarnate delivery paths that are not ported."""

    def test_damage_buff_is_refused(self, make_effect: Any) -> None:
        with pytest.raises(NotImplementedError, match="E20"):
            incarnate._guard_supported(make_effect(effect_type="DamageBuff", et_modifies="Damage"), "Sub")

    def test_grant_power_is_refused(self, make_effect: Any) -> None:
        with pytest.raises(NotImplementedError, match="E20"):
            incarnate._guard_supported(make_effect(effect_type="GrantPower"), "Sub")

    def test_mez_aspect_is_refused(self, make_effect: Any) -> None:
        with pytest.raises(NotImplementedError, match="E20"):
            incarnate._guard_supported(make_effect(effect_type="Enhancement", et_modifies="Mez"), "Sub")

    def test_supported_enhancement_passes(self, make_effect: Any) -> None:
        incarnate._guard_supported(make_effect(effect_type="Enhancement", et_modifies="Defense"), "Sub")


class TestAddSplit:
    """``_add_split`` accumulates into the pre-ED or post-ED slot by ``IgnoreED``."""

    def test_pre_and_post_accumulate_independently(self) -> None:
        bucket: dict[Any, tuple[float, float]] = {}
        incarnate._add_split(bucket, ("k",), 0.11, ignore_ed=False)
        incarnate._add_split(bucket, ("k",), 0.22, ignore_ed=True)
        incarnate._add_split(bucket, ("k",), 0.05, ignore_ed=False)
        assert bucket[("k",)] == (f32(0.16), f32(0.22))


class TestHasFilledSlot:
    """``_has_filled_slot`` reports whether any slot holds an enhancement."""

    def test_true_for_filled(self) -> None:
        assert incarnate._has_filled_slot([_filled_slot()])

    def test_false_for_empty(self) -> None:
        empty = SlotRef(level=0, is_inherent=False, enh=-1, grade=0, io_level=49, relative_level=1)
        assert not incarnate._has_filled_slot([empty])


class TestIncarnateExcluded:
    """``base_totals._incarnate_excluded`` drops delivery-only incarnates, refuses direct ones."""

    def test_delivery_only_incarnate_is_excluded(self, make_effect: Any, make_power: Any) -> None:
        power = make_power(
            make_effect(effect_type="GrantPower"),
            make_effect(effect_type="LevelShift"),
            full_name="Incarnate.Alpha.Agility_Core_Paragon",
        )
        assert base_totals._incarnate_excluded(power)

    def test_non_incarnate_is_kept(self, make_power: Any) -> None:
        assert not base_totals._incarnate_excluded(make_power(full_name="Pool.Speed.Hasten"))

    def test_direct_effect_incarnate_is_refused(self, make_effect: Any, make_power: Any) -> None:
        power = make_power(
            make_effect(effect_type="GrantPower"),
            make_effect(effect_type="Recovery"),
            full_name="Incarnate.Destiny.Ageless_Core_Epiphany",
        )
        with pytest.raises(NotImplementedError, match="E22"):
            base_totals._incarnate_excluded(power)


def _resolve(
    sub: IncarnateSubPower,
    power: Any,
    *,
    tiny_mods: AttribMods,
    tiny_classes: ArchetypeDb,
    tables: MathTables,
    slots: Any = None,
) -> incarnate.IncarnateAddends:
    inc = Incarnate(build_index=99, full_name="Incarnate.Alpha.Test", sub_powers=(sub,))
    return resolve_incarnates(
        [inc], [power], mods=tiny_mods, classes=tiny_classes, archetype_index=0, tables=tables, slots=slots
    )


class TestResolveIncarnates:
    """End-to-end resolution over a synthetic incarnate and one target power."""

    def test_scalar_addend_split(
        self, make_effect: Any, make_power: Any, tiny_mods: AttribMods, tiny_classes: ArchetypeDb, tables: MathTables
    ) -> None:
        pre = make_effect(effect_type="Enhancement", et_modifies="RechargeTime", scale=0.11, ignore_ed=False)
        post = make_effect(effect_type="Enhancement", et_modifies="RechargeTime", scale=0.22, ignore_ed=True)
        power = make_power(build_index=0, enhancements=(5,))
        addends = _resolve(_sub(pre, post), power, tiny_mods=tiny_mods, tiny_classes=tiny_classes, tables=tables)
        assert addends.scalar[(0, "RechargeTime")] == (f32(0.11), f32(0.22))
        assert addends.effect == {}

    def test_effect_addend_ed_applied(
        self, make_effect: Any, make_power: Any, tiny_mods: AttribMods, tiny_classes: ArchetypeDb, tables: MathTables
    ) -> None:
        pre = make_effect(effect_type="Enhancement", et_modifies="Defense", damage_type="Smashing", scale=0.0667)
        post = make_effect(
            effect_type="Enhancement", et_modifies="Defense", damage_type="Smashing", scale=0.1333, ignore_ed=True
        )
        target = make_effect(index=0, effect_type="Defense", damage_type="Smashing", buffable=True)
        power = make_power(target, build_index=0, enhancements=(5,))
        addends = _resolve(_sub(pre, post), power, tiny_mods=tiny_mods, tiny_classes=tiny_classes, tables=tables)
        # ED(0.0667) is below the schedule-B first knee, so unreduced: addend == 0.0667 + 0.1333.
        assert addends.effect[(0, 0)] == f32(f32(0.0667) + f32(0.1333))
        assert addends.scalar == {}

    def test_gate_miss_contributes_nothing(
        self, make_effect: Any, make_power: Any, tiny_mods: AttribMods, tiny_classes: ArchetypeDb, tables: MathTables
    ) -> None:
        fx = make_effect(effect_type="Enhancement", et_modifies="RechargeTime", scale=0.11)
        power = make_power(build_index=0, enhancements=(18,))  # accepts class 18, sub gates on {5}
        addends = _resolve(_sub(fx), power, tiny_mods=tiny_mods, tiny_classes=tiny_classes, tables=tables)
        assert addends.scalar == {}
        assert addends.effect == {}

    def test_co_slotting_effect_is_refused(
        self, make_effect: Any, make_power: Any, tiny_mods: AttribMods, tiny_classes: ArchetypeDb, tables: MathTables
    ) -> None:
        inc = make_effect(effect_type="Enhancement", et_modifies="Defense", damage_type="Smashing", scale=0.0667)
        target = make_effect(index=0, effect_type="Defense", damage_type="Smashing", buffable=True)
        power = make_power(target, build_index=0, enhancements=(5,))
        with pytest.raises(NotImplementedError, match="E19"):
            _resolve(
                _sub(inc),
                power,
                tiny_mods=tiny_mods,
                tiny_classes=tiny_classes,
                tables=tables,
                slots={0: [_filled_slot()]},
            )
