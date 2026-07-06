"""Enhancement placement legality (``Power.IsEnhancementValid`` + ``Build.EnhancementTest``).

Two layers, both ported from the fork:

- **Placement** (``Power.IsEnhancementValid`` -> ``GetValidEnhancements``,
    Power.cs:2104-2127): a *set* IO is legal iff its set type is in the power's
    ``SetTypes`` (reusing CP5's :func:`~coh_engine.set_bonuses.power_accepts_set`);
    a *standard* IO is legal iff one of its enhancement class IDs is in the power's
    ``Enhancements`` list. Routing everything through ``EnhancementTest`` is the
    resolved trap — it never class-checks standard IOs, so it wrongly accepts a
    Recharge IO in One with the Shield (mids-port-spec § legality-predicates).
- **Build-wide** (``Build.EnhancementTest``, Build.cs:1026-1149): a global
    ``Unique`` IO may appear once; superior/attuned versions of the same set piece
    are mutually exclusive (the ``(Attuned_|Superior_)`` base-version regex, which
    also pairs Superior ATO/Winter variants); stealth procs are mutually exclusive;
    and one set piece may appear once per power.

The ``Superior`` flag alone does NOT imply a mutex — purples carry ``Superior=True``
(the x1.25 value flag) with ``MutExID=None``, so the version mutex gates on the mutex
id, never on ``Superior``. Attuned set IOs are plain ``SetO`` and validate by set type
exactly like their crafted counterparts.

Mids strips class-illegal slots on load and enforces unique/mutex only interactively,
so a Mids-round-tripped build never trips these; the checks guard direct build
*generation* (optimizer/DTO/hand-authored), reporting all findings as
:class:`~coh_engine.diagnostics.Diagnostic` rather than raising on the first.
"""

import json
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from types import MappingProxyType
from typing import Any

from coh_engine.diagnostics import Diagnostic
from coh_engine.effect import Power
from coh_engine.enhancement import SlotRef
from coh_engine.set_bonuses import SetBonusDb, power_accepts_set

# Build.cs:1078: the superior/attuned base-version key strips both prefixes so a
# Superior_Attuned_Superior_X and its Attuned_X (or the ATO/Winter regular version)
# collapse to the same base string and read as mutually exclusive.
_VERSION_PREFIX = re.compile(r"(Attuned_|Superior_)")

# eEnhMutex.None / .Stealth names (the two the build-wide mutex special-cases).
_MUTEX_NONE = "None"
_MUTEX_STEALTH = "Stealth"


@dataclass(frozen=True, slots=True)
class EnhancementLegality:
    """The legality-relevant fields of one enhancement (from ``enhancements.json``)."""

    nid: int
    uid: str
    long_name: str
    type_name: str  # eType name: None / Normal / InventO / SpecialO / SetO.
    class_ids: tuple[int, ...]  # EnhancementClasses[..].ID list; tested against Power.Enhancements.
    nid_set: int  # owning set (-1 for non-set IOs).
    unique: bool
    mutex_name: str  # eEnhMutex name: None / Stealth / ArchetypeA..F.
    superior: bool


def load_enhancement_legality(path: Path | str) -> Mapping[int, EnhancementLegality]:
    """Parse an ``enhancements.json`` dump into legality records, keyed by nID.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        records = json.load(stream)
    out = {
        r["Nid"]: EnhancementLegality(
            nid=r["Nid"],
            uid=r["UID"],
            long_name=r["LongName"],
            type_name=r["TypeName"],
            class_ids=tuple(r["ClassIds"]),
            nid_set=r["nIDSet"],
            unique=r["Unique"],
            mutex_name=r["MutExName"],
            superior=r["Superior"],
        )
        for r in records
    }
    return MappingProxyType(out)


class PlacementVerdict(Enum):
    """The one placement decision, consumed by both the predicate and the diagnostic."""

    VALID = auto()
    UNKNOWN_SET = auto()
    SET_NOT_ACCEPTED = auto()
    CLASS_NOT_ACCEPTED = auto()


def classify_placement(power: Power, enh: EnhancementLegality, set_db: SetBonusDb) -> PlacementVerdict:
    """``Power.IsEnhancementValid`` (Power.cs:2119) as a typed verdict — the single source.

    A set IO's set type must be accepted by the power (``power_accepts_set``, the shared
    primitive); a standard IO's class ID must be in the power's accepted classes. The
    verdict backs both :func:`is_enhancement_valid` (the Mids-validated predicate) and the
    placement rule's diagnostics, so the tested decision and the production decision are
    one function, not two that can drift.
    """
    if enh.type_name == "SetO":
        set_def = set_db.sets.get(enh.nid_set)
        if set_def is None:
            return PlacementVerdict.UNKNOWN_SET
        return PlacementVerdict.VALID if power_accepts_set(power, set_def) else PlacementVerdict.SET_NOT_ACCEPTED
    return (
        PlacementVerdict.VALID
        if any(cid in power.enhancements for cid in enh.class_ids)
        else PlacementVerdict.CLASS_NOT_ACCEPTED
    )


def is_enhancement_valid(power: Power, enh: EnhancementLegality, set_db: SetBonusDb) -> bool:
    """Whether ``enh`` may slot in ``power`` — ``classify_placement`` reduced to a bool."""
    return classify_placement(power, enh, set_db) is PlacementVerdict.VALID


_FilledSlot = tuple[Power, SlotRef, EnhancementLegality | None]


@dataclass(frozen=True, slots=True)
class LegalityContext:
    """The pre-built inputs every legality rule reads — the build's slots walked once.

    ``filled`` is every ``(power, filled slot, resolved enhancement)`` in build order,
    with the enhancement ``None`` when its nID is absent from the database. Building it
    once means no rule re-walks the slots and none re-resolves an enhancement.
    """

    set_db: SetBonusDb
    filled: tuple[_FilledSlot, ...]


def _build_filled(
    powers: Sequence[Power], slots: Mapping[int, Sequence[SlotRef]], enh_db: Mapping[int, EnhancementLegality]
) -> tuple[_FilledSlot, ...]:
    return tuple(
        (power, slot, enh_db.get(slot.enh))
        for power in powers
        for slot in slots.get(power.build_index, ())
        if slot.enh >= 0
    )


LegalityRule = Callable[[LegalityContext], Iterable[Diagnostic]]
_RULES: list[LegalityRule] = []


def legality_rule(fn: LegalityRule) -> LegalityRule:
    """Register a legality rule — a new dimension is a new ``@legality_rule``, no runner edit."""
    _RULES.append(fn)
    return fn


def registered_rules() -> list[str]:
    """The names of the registered legality rules — the introspectable registry."""
    return [rule.__name__ for rule in _RULES]


def _error(rule_id: str, message: str, **ctx: Any) -> Diagnostic:
    return Diagnostic(rule_id=rule_id, severity="error", message=message, **ctx)


def _placement_diagnostic(
    verdict: PlacementVerdict, power: Power, enh: EnhancementLegality, set_db: SetBonusDb
) -> Diagnostic:
    """Map a non-VALID placement verdict to its diagnostic (H-ENH-001/002/003)."""
    if verdict is PlacementVerdict.UNKNOWN_SET:
        return _error(
            "H-ENH-002",
            f"{enh.uid} in {power.full_name!r} is a set IO whose set (nIDSet {enh.nid_set}) is not in the set database",
            fix="re-dump the set database so it includes this set, or remove the piece",
        )
    if verdict is PlacementVerdict.SET_NOT_ACCEPTED:
        set_def = set_db.sets[enh.nid_set]
        return _error(
            "H-ENH-001",
            f"set {set_def.uid!r} (set type {set_def.set_type}) is not slottable in {power.full_name!r} "
            f"(accepts set types {sorted(power.set_types)})",
            fix="move the piece to a power that accepts this set",
            expected=sorted(power.set_types),
            actual=set_def.set_type,
        )
    return _error(
        "H-ENH-003",
        f"{enh.long_name!r} ({enh.uid}) is not slottable in {power.full_name!r}: its enhancement "
        f"class {list(enh.class_ids)} is not in the power's accepted classes",
        fix="move the piece to a power that accepts this enhancement class",
        expected=sorted(power.enhancements),
        actual=list(enh.class_ids),
    )


@legality_rule
def _rule_placement(ctx: LegalityContext) -> Iterable[Diagnostic]:
    """Per-slot placement (``classify_placement``): unknown-enh H-ENH-007, else the verdict."""
    for power, slot, enh in ctx.filled:
        if enh is None:
            yield _error(
                "H-ENH-007",
                f"enhancement nID {slot.enh} slotted in {power.full_name!r} is not in the enhancement database",
                fix="remove the slot or re-dump the enhancement database",
            )
            continue
        verdict = classify_placement(power, enh, ctx.set_db)
        if verdict is not PlacementVerdict.VALID:
            yield _placement_diagnostic(verdict, power, enh, ctx.set_db)


@legality_rule
def _rule_global_unique(ctx: LegalityContext) -> Iterable[Diagnostic]:
    """H-ENH-004: a ``Unique`` IO slotted more than once build-wide."""
    seen: dict[int, str] = {}
    for power, _, enh in ctx.filled:
        if enh is None or not enh.unique:
            continue
        if enh.nid in seen:
            yield _error(
                "H-ENH-004",
                f"unique enhancement {enh.long_name!r} ({enh.uid}) is slotted more than once "
                f"(also in {seen[enh.nid]!r}, now {power.full_name!r}); a unique IO may be slotted once per build",
                fix="remove the extra copy",
            )
        else:
            seen[enh.nid] = power.full_name


@legality_rule
def _rule_mutex(ctx: LegalityContext) -> Iterable[Diagnostic]:
    """H-ENH-005: stealth procs, and superior/attuned versions of one set piece, are mutex.

    Gated on ``mutex_name != None`` (Build.cs:1074) — the ``Superior`` value flag alone
    never triggers this, so purples (Superior=True, MutExID=None) do not conflict.
    """
    stealth: str | None = None
    versions: dict[str, str] = {}
    for power, _, enh in ctx.filled:
        if enh is None or enh.mutex_name == _MUTEX_NONE:
            continue
        if enh.mutex_name == _MUTEX_STEALTH:
            if stealth is not None:
                yield _mutex_error(enh, power, f"the stealth proc in {stealth!r}", "one stealth proc")
            else:
                stealth = power.full_name
            continue
        base = _VERSION_PREFIX.sub("", enh.uid)
        if base in versions:
            yield _mutex_error(enh, power, f"a version of the same piece in {versions[base]!r}", "one version")
        else:
            versions[base] = power.full_name


@legality_rule
def _rule_per_power_set_dup(ctx: LegalityContext) -> Iterable[Diagnostic]:
    """H-ENH-006: the same set piece slotted twice in one power."""
    seen_by_power: dict[int, set[int]] = {}
    for power, _, enh in ctx.filled:
        if enh is None or enh.nid_set < 0:
            continue
        seen = seen_by_power.setdefault(power.build_index, set())
        if enh.nid in seen:
            yield _error(
                "H-ENH-006",
                f"set piece {enh.uid} is slotted more than once in {power.full_name!r}; only one of "
                "each set piece is allowed per power",
                fix="replace the duplicate with a different piece from the set",
            )
        else:
            seen.add(enh.nid)


def _mutex_error(enh: EnhancementLegality, power: Power, conflict: str, limit: str) -> Diagnostic:
    return _error(
        "H-ENH-005",
        f"{enh.long_name!r} ({enh.uid}) in {power.full_name!r} is mutually exclusive with {conflict}; "
        f"only {limit} may be slotted across the build",
        fix="remove one of the mutually exclusive pieces",
    )


def check_build_legality(
    powers: Sequence[Power],
    slots: Mapping[int, Sequence[SlotRef]],
    enh_db: Mapping[int, EnhancementLegality],
    set_db: SetBonusDb,
) -> list[Diagnostic]:
    """Every legality violation, by running the registered rules over a pre-built context.

    The runner holds no per-dimension logic: it builds the :class:`LegalityContext` once
    and folds every ``@legality_rule`` over it. A new legality dimension is a new
    ``@legality_rule`` — never an edit here. An empty list means legal.
    """
    ctx = LegalityContext(set_db=set_db, filled=_build_filled(powers, slots, enh_db))
    return [diagnostic for rule in _RULES for diagnostic in rule(ctx)]
