"""Tests for coh_engine.effect — Effect.Mag and the GetModifier class routing."""

from collections.abc import Callable

import pytest

from coh_engine.archetypes import ArchetypeDb
from coh_engine.attribmod import AttribMods
from coh_engine.effect import Effect, Power, _parse_requirement_groups, effect_mag, get_modifier_for_effect
from coh_engine.maths import f32


def test_parse_requirement_groups_drops_blanks_and_empty_groups() -> None:
    """A ``Requires`` array: blank second slots (single-power reqs) and empty groups are dropped."""
    raw = [["A", "B"], ["C", ""], ["", ""], []]
    assert _parse_requirement_groups(raw) == (("A", "B"), ("C",))


def test_parse_requirement_groups_empty_is_empty() -> None:
    """No requirement data parses to an empty tuple."""
    assert _parse_requirement_groups(()) == ()


MakeEffect = Callable[..., Effect]
MakePower = Callable[..., Power]


def test_magnitude_is_scale_times_nmag_times_modifier(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(scale=0.5, n_magnitude=3.0, modifier_table="Twos", n_modifier_table=1)
    power = make_power(fx)
    # 0.5 * 3.0 * Twos[49][column 0] = 0.5 * 3.0 * 2.0
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == f32(3.0)


def test_damage_effect_reports_negative_mag(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(effect_type="Damage", scale=2.0)
    power = make_power(fx)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == f32(-2.0)


def test_duration_attrib_type_returns_nmagnitude(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(attrib_type="Duration", scale=99.0, n_magnitude=4.0)
    power = make_power(fx)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == f32(4.0)


def test_blank_expression_falls_back_to_scale_times_nmag(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(attrib_type="Expression", scale=2.0, n_magnitude=3.0)
    power = make_power(fx)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == f32(6.0)


def test_expression_with_magnitude_string_is_deferred(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(attrib_type="Expression", expr_magnitude="@StdResult * 2")
    power = make_power(fx)
    with pytest.raises(NotImplementedError, match="E08"):
        effect_mag(fx, power, tiny_mods, tiny_classes, 0)


def test_unknown_attrib_type_yields_zero(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(attrib_type="Unknown")
    power = make_power(fx)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == 0.0


def test_forced_class_overrides_archetype_column(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(modifier_table="Twos", n_modifier_table=1)
    power = make_power(fx, forced_class="Class_Pet")
    # Class_Pet has Column 1 -> Twos[49][1] = 3.0, not the archetype's 2.0.
    assert get_modifier_for_effect(fx, power, tiny_mods, tiny_classes, 0) == f32(3.0)


def test_absorbed_class_beats_archetype_but_not_forced_class(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(modifier_table="Twos", n_modifier_table=1, absorbed_class_n_id=1)
    assert get_modifier_for_effect(fx, make_power(fx), tiny_mods, tiny_classes, 0) == f32(3.0)
    forced = make_power(fx, forced_class="Class_Test")
    assert get_modifier_for_effect(fx, forced, tiny_mods, tiny_classes, 0) == f32(2.0)


def test_variable_scaling_zeroes_variable_modified_effects(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(scale=0.3, variable_modified=True)
    power = make_power(fx, variable_enabled=True, variable_value=0)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == 0.0


def test_variable_scaling_multiplies_by_variable_value(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(scale=0.25, variable_modified=True)
    power = make_power(fx, variable_enabled=True, variable_value=4)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == f32(1.0)


def test_variable_scaling_respects_ignore_scaling(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(scale=0.5, variable_modified=True, ignore_scaling=True)
    power = make_power(fx, variable_enabled=True, variable_value=0)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == f32(0.5)


def test_variable_scaling_needs_variable_enabled_power(
    make_effect: MakeEffect, make_power: MakePower, tiny_mods: AttribMods, tiny_classes: ArchetypeDb
) -> None:
    fx = make_effect(scale=0.5, variable_modified=True)
    power = make_power(fx, variable_enabled=False, variable_value=0)
    assert effect_mag(fx, power, tiny_mods, tiny_classes, 0) == f32(0.5)
