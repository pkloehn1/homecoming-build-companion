"""Attack-chain sequencer — a repeatable attack rotation and its endurance cost.

Given a build's attacks and their CP6.1 buffed recharge / cast times
(:class:`~coh_engine.statistics.PowerStats`), this orders them into a rotation and
reports whether the chain is gap-free and what it drains per second. It feeds the full
endurance-sustainability check (:mod:`coh_engine.scoring`): a build must sustain its
toggle drain **plus** its attack-chain drain from recovery.

**Novel to the port — no Mids parity reference.** Mids has no attack-chain sequencer in
its calc core (the UI "Rotation Helper" sequences for damage, not endurance). The
per-attack cadence this consumes *is* parity-validated (``statistics`` reproduces Mids'
buffed recharge/cast), but the rotation and gap logic here is the port's own.

The chain model (standard CoH): each attack fires once per cycle, and its recharge runs
concurrently with the other attacks' activations. So an attack ``i`` is ready in time iff
the rest of the chain's cast time covers its recharge — ``cast_sum - cast_i >= recharge_i``,
i.e. ``cast_sum >= cast_i + recharge_i``. The chain is gap-free iff ``cast_sum`` covers the
worst attack's ``cast_i + recharge_i``; otherwise the cycle stretches to that bottleneck
and the difference is idle (gap) time. Ordering does not change the cycle time, the gap, or
the drain — only the presentation order — so the endurance math is order-independent.

Damage / chain DPS are deferred (CP6.2 / #31): identifying an attack needs only that it
deals damage, not the damage value, so the sequencer runs on recharge/cast alone.

Spec: .claude/rules/exemplar-10.md; docs/engine/build-types-and-goals.md.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from coh_engine.maths import f32
from coh_engine.statistics import PowerStats


@dataclass(frozen=True, slots=True)
class AttackChain:
    """A build's attack rotation and the endurance it costs per second.

    ``rotation`` is the attack full-names ordered longest-recharge first (presentation
    only). ``cast_sum`` is the animation-locked cycle floor (Σ cast times); ``cycle_time``
    is the real cycle including any wait for a slow attack; ``gap`` is the idle time per
    cycle (0 when gap-free). ``end_per_sec`` is the chain's endurance drain, Σ end cost over
    the cycle.
    """

    rotation: tuple[str, ...]
    cast_sum: float
    cycle_time: float
    gap: float
    gap_free: bool
    end_per_sec: float


_EMPTY_CHAIN = AttackChain(rotation=(), cast_sum=0.0, cycle_time=0.0, gap=0.0, gap_free=True, end_per_sec=0.0)


def build_attack_chain(power_stats: Sequence[PowerStats]) -> AttackChain:
    """Sequence a build's attacks into a rotation and derive its endurance drain.

    Attacks are the ``is_attack`` power stats. With none, the chain is empty (no drain,
    trivially gap-free). ``cycle_time`` is ``max(Σ cast, max(cast_i + recharge_i))``; the
    chain is gap-free when the cast total already covers the slowest attack's recharge.
    """
    attacks = [s for s in power_stats if s.is_attack]
    if not attacks:
        return _EMPTY_CHAIN

    cast_sum = _f32_sum(s.cast_time for s in attacks)
    end_sum = _f32_sum(s.end_cost for s in attacks)
    bottleneck = max(f32(s.cast_time + s.recharge_time) for s in attacks)
    cycle_time = max(cast_sum, bottleneck)
    gap = f32(cycle_time - cast_sum)
    rotation = tuple(s.full_name for s in sorted(attacks, key=lambda s: (-s.recharge_time, s.full_name)))
    end_per_sec = f32(end_sum / cycle_time) if cycle_time > 0.0 else 0.0
    return AttackChain(
        rotation=rotation,
        cast_sum=cast_sum,
        cycle_time=cycle_time,
        gap=gap,
        gap_free=gap <= 0.0,
        end_per_sec=end_per_sec,
    )


def _f32_sum(values: Iterable[float]) -> float:
    total = 0.0
    for value in values:
        total = f32(total + value)
    return total
