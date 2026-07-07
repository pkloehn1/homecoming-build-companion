"""The character-level schedule loader (``levels.json`` → :class:`LevelSchedule`)."""

from pathlib import Path

from coh_engine.levels import load_level_schedule

FIXTURES = Path(__file__).parent / "fixtures"
MIDS = FIXTURES / "mids"


def test_schedule_grants_67_total_slots() -> None:
    """The Homecoming slot schedule grants exactly 67 slots (the MaxSlots budget)."""
    schedule = load_level_schedule(MIDS / "levels.json")
    assert schedule.total_slots_granted == 67


def test_schedule_has_24_power_pick_levels_by_index() -> None:
    """Level index 0 collapses in the set, so 24 picks map to 23 distinct pick indices."""
    schedule = load_level_schedule(MIDS / "levels.json")
    # The 24-pick schedule is [1,1,2,4,...]; level index 0 (game level 1) appears twice.
    assert 0 in schedule.power_pick_levels
    assert len(schedule.power_pick_levels) == 23


def test_early_grant_levels_give_two_slots() -> None:
    """Level index 2 (game level 3) grants 2 slots; a late level grants 3."""
    schedule = load_level_schedule(MIDS / "levels.json")
    assert schedule.slots_per_level[2] == 2
    assert schedule.slots_per_level[49] == 3  # game level 50


def test_slot_grant_levels_is_the_key_set() -> None:
    """``slot_grant_levels`` is the set of levels that grant a slot."""
    schedule = load_level_schedule(MIDS / "levels.json")
    assert schedule.slot_grant_levels == frozenset(schedule.slots_per_level)
    assert 0 not in schedule.slot_grant_levels  # level 1 grants no added slot
