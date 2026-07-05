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
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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


def is_enhancement_valid(power: Power, enh: EnhancementLegality, set_db: SetBonusDb) -> bool:
    """``Power.IsEnhancementValid`` (Power.cs:2119): can ``enh`` slot in ``power``.

    Set IOs check the set type against the power's accepted set types; standard IOs
    check the enhancement's class IDs against the power's accepted classes. An
    unknown set (or a class-less enhancement) is not valid.
    """
    if enh.type_name == "SetO":
        set_def = set_db.sets.get(enh.nid_set)
        return set_def is not None and power_accepts_set(power, set_def)
    return any(cid in power.enhancements for cid in enh.class_ids)


def _error(rule_id: str, message: str, **ctx: Any) -> Diagnostic:
    return Diagnostic(rule_id=rule_id, severity="error", message=message, **ctx)


def _check_set_placement(power: Power, enh: EnhancementLegality, set_db: SetBonusDb) -> list[Diagnostic]:
    """Set-IO placement: unknown set -> H-ENH-002, set type not accepted -> H-ENH-001."""
    set_def = set_db.sets.get(enh.nid_set)
    if set_def is None:
        return [
            _error(
                "H-ENH-002",
                f"{enh.uid} in {power.full_name!r} is a set IO whose set (nIDSet {enh.nid_set}) is not in the "
                "set database",
                fix="re-dump the set database so it includes this set, or remove the piece",
            )
        ]
    if power_accepts_set(power, set_def):
        return []
    return [
        _error(
            "H-ENH-001",
            f"set {set_def.uid!r} (set type {set_def.set_type}) is not slottable in {power.full_name!r} "
            f"(accepts set types {sorted(power.set_types)})",
            fix="move the piece to a power that accepts this set",
            expected=sorted(power.set_types),
            actual=set_def.set_type,
        )
    ]


def _check_placement(
    power: Power, slot: SlotRef, enh_db: Mapping[int, EnhancementLegality], set_db: SetBonusDb
) -> list[Diagnostic]:
    """One slot's placement verdict (``IsEnhancementValid`` as diagnostics)."""
    enh = enh_db.get(slot.enh)
    if enh is None:
        return [
            _error(
                "H-ENH-007",
                f"enhancement nID {slot.enh} slotted in {power.full_name!r} is not in the enhancement database",
                fix="remove the slot or re-dump the enhancement database",
            )
        ]
    if enh.type_name == "SetO":
        return _check_set_placement(power, enh, set_db)
    if any(cid in power.enhancements for cid in enh.class_ids):
        return []
    return [
        _error(
            "H-ENH-003",
            f"{enh.long_name!r} ({enh.uid}) is not slottable in {power.full_name!r}: its enhancement "
            f"class {list(enh.class_ids)} is not in the power's accepted classes",
            fix="move the piece to a power that accepts this enhancement class",
            expected=sorted(power.enhancements),
            actual=list(enh.class_ids),
        )
    ]


def _iter_filled(
    powers: Sequence[Power], slots: Mapping[int, Sequence[SlotRef]], enh_db: Mapping[int, EnhancementLegality]
) -> list[tuple[Power, SlotRef, EnhancementLegality]]:
    """Every (power, filled slot, resolved enhancement) triple, in build order."""
    out: list[tuple[Power, SlotRef, EnhancementLegality]] = []
    for power in powers:
        for slot in slots.get(power.build_index, ()):
            if slot.enh < 0:
                continue
            enh = enh_db.get(slot.enh)
            if enh is not None:
                out.append((power, slot, enh))
    return out


def _check_uniques(triples: Sequence[tuple[Power, SlotRef, EnhancementLegality]]) -> list[Diagnostic]:
    """H-ENH-004: a ``Unique`` IO slotted more than once build-wide."""
    diags: list[Diagnostic] = []
    seen: dict[int, str] = {}
    for power, _, enh in triples:
        if not enh.unique:
            continue
        if enh.nid in seen:
            diags.append(
                _error(
                    "H-ENH-004",
                    f"unique enhancement {enh.long_name!r} ({enh.uid}) is slotted more than once "
                    f"(also in {seen[enh.nid]!r}, now {power.full_name!r}); a unique IO may be slotted once per build",
                    fix="remove the extra copy",
                )
            )
        else:
            seen[enh.nid] = power.full_name
    return diags


def _check_per_power_set_dupes(
    powers: Sequence[Power], slots: Mapping[int, Sequence[SlotRef]], enh_db: Mapping[int, EnhancementLegality]
) -> list[Diagnostic]:
    """H-ENH-006: the same set piece slotted twice in one power."""
    diags: list[Diagnostic] = []
    for power in powers:
        seen: set[int] = set()
        for slot in slots.get(power.build_index, ()):
            enh = enh_db.get(slot.enh) if slot.enh >= 0 else None
            if enh is None or enh.nid_set < 0:
                continue
            if enh.nid in seen:
                diags.append(
                    _error(
                        "H-ENH-006",
                        f"set piece {enh.uid} is slotted more than once in {power.full_name!r}; only one of "
                        "each set piece is allowed per power",
                        fix="replace the duplicate with a different piece from the set",
                    )
                )
            else:
                seen.add(enh.nid)
    return diags


def _check_mutex(triples: Sequence[tuple[Power, SlotRef, EnhancementLegality]]) -> list[Diagnostic]:
    """H-ENH-005: stealth procs, and superior/attuned versions of one set piece, are mutex.

    Gated on ``mutex_name != None`` (Build.cs:1074) — the ``Superior`` value flag alone
    never triggers this, so purples (Superior=True, MutExID=None) do not conflict.
    """
    diags: list[Diagnostic] = []
    stealth: str | None = None
    versions: dict[str, str] = {}
    for power, _, enh in triples:
        if enh.mutex_name == _MUTEX_NONE:
            continue
        if enh.mutex_name == _MUTEX_STEALTH:
            if stealth is not None:
                diags.append(_mutex_error(enh, power, f"the stealth proc in {stealth!r}", "one stealth proc"))
            else:
                stealth = power.full_name
            continue
        base = _VERSION_PREFIX.sub("", enh.uid)
        if base in versions:
            diags.append(_mutex_error(enh, power, f"a version of the same piece in {versions[base]!r}", "one version"))
        else:
            versions[base] = power.full_name
    return diags


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
    """All enhancement-placement and build-wide legality violations, in build order.

    Placement is checked per filled slot (``IsEnhancementValid``); the build-wide
    unique / mutex / per-power-duplicate rules scan the whole build. Every finding is
    an error :class:`~coh_engine.diagnostics.Diagnostic`; an empty list means legal.
    """
    diags: list[Diagnostic] = []
    for power in powers:
        for slot in slots.get(power.build_index, ()):
            if slot.enh < 0:
                continue
            diags.extend(_check_placement(power, slot, enh_db, set_db))
    triples = _iter_filled(powers, slots, enh_db)
    diags.extend(_check_uniques(triples))
    diags.extend(_check_mutex(triples))
    diags.extend(_check_per_power_set_dupes(powers, slots, enh_db))
    return diags
