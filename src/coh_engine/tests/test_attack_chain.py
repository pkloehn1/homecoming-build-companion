"""The attack-chain sequencer: rotation, gap detection, and chain endurance/sec.

The cadence inputs (recharge/cast) are parity-validated in test_statistics; here the
rotation and gap logic — the port's own, with no Mids equivalent — is exercised directly.
"""

from coh_engine.attack_chain import build_attack_chain
from coh_engine.maths import f32
from coh_engine.statistics import PowerStats


def _stat(name: str, *, recharge: float, cast: float, end: float, is_attack: bool = True) -> PowerStats:
    return PowerStats(
        full_name=name,
        recharge_time=recharge,
        end_cost=end,
        interrupt_time=0.0,
        end_per_sec=0.0,
        cast_time=cast,
        is_attack=is_attack,
    )


def test_no_attacks_is_an_empty_chain() -> None:
    """A build with no attacks yields an empty, trivially gap-free chain with no drain."""
    chain = build_attack_chain([_stat("Toggle", recharge=0.0, cast=0.0, end=0.0, is_attack=False)])
    assert chain.rotation == ()
    assert chain.gap_free is True
    assert chain.end_per_sec == 0.0
    assert chain.cycle_time == 0.0


def test_gap_free_chain_cycles_on_cast_time() -> None:
    """When the cast total covers every attack's recharge, the chain is gap-free."""
    # 3 attacks, cast 1.0 each (cast_sum 3.0); each recharge 1.0 -> max(cast+rech)=2.0 <= 3.0.
    attacks = [_stat(f"A{i}", recharge=1.0, cast=1.0, end=6.0) for i in range(3)]
    chain = build_attack_chain(attacks)
    assert chain.gap_free is True
    assert chain.cast_sum == f32(3.0)
    assert chain.cycle_time == f32(3.0)
    assert chain.gap == 0.0
    # end/sec = 18 end over the 3.0s cycle.
    assert chain.end_per_sec == f32(18.0 / 3.0)


def test_slow_attack_creates_a_gap() -> None:
    """An attack whose recharge outlasts the rest of the chain stretches the cycle (gap)."""
    # A: cast 1, recharge 5 -> ready at 6; B: cast 1, recharge 1. cast_sum 2, bottleneck 6.
    chain = build_attack_chain(
        [_stat("A", recharge=5.0, cast=1.0, end=5.0), _stat("B", recharge=1.0, cast=1.0, end=5.0)]
    )
    assert chain.gap_free is False
    assert chain.cast_sum == f32(2.0)
    assert chain.cycle_time == f32(6.0)
    assert chain.gap == f32(4.0)
    assert chain.end_per_sec == f32(10.0 / 6.0)


def test_rotation_orders_longest_recharge_first() -> None:
    """The rotation is presented longest-recharge first (order does not affect the math)."""
    chain = build_attack_chain(
        [
            _stat("Fast", recharge=2.0, cast=1.0, end=5.0),
            _stat("Slow", recharge=8.0, cast=1.0, end=5.0),
            _stat("Mid", recharge=4.0, cast=1.0, end=5.0),
        ]
    )
    assert chain.rotation == ("Slow", "Mid", "Fast")


def test_non_attacks_are_excluded() -> None:
    """Only is_attack power stats enter the chain; toggles/buffs are ignored."""
    chain = build_attack_chain(
        [
            _stat("Attack", recharge=1.0, cast=1.0, end=5.0),
            _stat("Heal", recharge=10.0, cast=2.0, end=20.0, is_attack=False),
        ]
    )
    assert chain.rotation == ("Attack",)
    # Only the attack counts; a lone attack still waits its own recharge (cycle = cast+recharge = 2).
    assert chain.cycle_time == f32(2.0)
    assert chain.end_per_sec == f32(5.0 / 2.0)
