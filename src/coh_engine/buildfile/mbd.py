"""Reader for the ``.mbd`` modern build format (plain indented JSON).

Mirrors ``CharacterBuildData.LoadBuild`` (``Core/BuildFile/CharacterBuildData.cs``)
and ``EnhancementDataConverter`` (``Core/BuildFile/EnhancementDataConverter.cs``).

Offsets, reproduced exactly (spec § data-and-build-formats, B.4 + gotchas):
- Power ``Level`` and slot ``Level`` are stored **+1** and get **-1** on load, so
    the model holds MidsReborn's internal 0-based level (character level = level + 1).
- ``LastPower`` is assigned **raw** on ``.mbd`` load — no ``-1`` (CharacterBuildData.cs:284),
    unlike the ``.mxd`` path.
- The top-level character ``Level`` is a raw integer, no offset.

An ``Enhancement`` object carries five keys; ``EnhancementDataConverter`` also
accepts a legacy ``Enhancement`` key as the ``Uid`` and a JSON ``null`` as an
empty slot.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class MetaData:
    """The ``BuiltWith`` block: app + database provenance."""

    app: str
    version: str
    database: str
    database_version: str


@dataclass(frozen=True, slots=True)
class Enhancement:
    """A slotted enhancement (``EnhancementData``)."""

    uid: str
    grade: str = "None"
    io_level: int = 1
    relative_level: str = "Even"
    obtained: bool = False


@dataclass(frozen=True, slots=True)
class Slot:
    """One enhancement slot on a power. ``level`` is 0-based (character level - 1)."""

    level: int
    is_inherent: bool
    enhancement: Enhancement | None
    flipped_enhancement: Enhancement | None


@dataclass(frozen=True, slots=True)
class SubPower:
    """A sub-power entry (e.g. a toggle's granted variant)."""

    power_name: str
    stat_include: bool


@dataclass(frozen=True, slots=True)
class PowerEntry:
    """A picked power. ``level`` is 0-based (character level - 1)."""

    power_name: str
    level: int
    stat_include: bool
    proc_include: bool
    variable_value: int
    inherent_slots_used: int
    sub_power_entries: tuple[SubPower, ...]
    slot_entries: tuple[Slot, ...]


@dataclass(frozen=True, slots=True)
class Build:
    """A parsed ``.mbd`` build."""

    meta: MetaData
    level: int
    class_name: str
    origin: str
    alignment: str
    name: str
    comment: str
    power_sets: tuple[str, ...]
    last_power: int
    power_entries: tuple[PowerEntry, ...] = field(default_factory=tuple)


def _parse_enhancement(obj: Any) -> Enhancement | None:
    """Parse an ``EnhancementData`` object, or ``None`` for a JSON null/empty slot."""
    if obj is None:
        return None
    # Legacy converter fallback: an "Enhancement" key stands in for "Uid".
    uid = obj.get("Uid")
    if uid is None:
        uid = obj.get("Enhancement")
    if uid is None:
        return None
    return Enhancement(
        uid=uid,
        grade=obj.get("Grade", "None"),
        io_level=obj.get("IoLevel", 1),
        relative_level=obj.get("RelativeLevel", "Even"),
        obtained=obj.get("Obtained", False),
    )


def _parse_slot(obj: dict[str, Any]) -> Slot:
    return Slot(
        level=obj["Level"] - 1,  # -1 offset
        is_inherent=obj.get("IsInherent", False),
        enhancement=_parse_enhancement(obj.get("Enhancement")),
        flipped_enhancement=_parse_enhancement(obj.get("FlippedEnhancement")),
    )


def _parse_power_entry(obj: dict[str, Any]) -> PowerEntry:
    power_name = obj["PowerName"]
    # Mids applies the -1 only to a real (resolved) power; an empty placeholder
    # entry keeps its stored level (Mids substitutes Levels_MainPowers, a DB value
    # not available at the parse layer — deferred to CP10).
    level = obj["Level"] - 1 if power_name else obj["Level"]
    return PowerEntry(
        power_name=power_name,
        level=level,
        stat_include=obj.get("StatInclude", False),
        proc_include=obj.get("ProcInclude", False),
        variable_value=obj.get("VariableValue", 0),
        inherent_slots_used=obj.get("InherentSlotsUsed", 0),
        sub_power_entries=tuple(
            SubPower(power_name=s["PowerName"], stat_include=s.get("StatInclude", False))
            for s in obj.get("SubPowerEntries", [])
        ),
        slot_entries=tuple(_parse_slot(s) for s in obj.get("SlotEntries", [])),
    )


def parse_mbd(data: dict[str, Any]) -> Build:
    """Build a :class:`Build` from a decoded ``.mbd`` JSON object.

    Raises:
        ValueError: if the required ``BuiltWith`` block is missing.
    """
    meta_obj = data.get("BuiltWith")
    if meta_obj is None:
        raise ValueError("mbd build is missing the required BuiltWith block")
    meta = MetaData(
        app=meta_obj.get("App", ""),
        version=meta_obj.get("Version", ""),
        database=meta_obj.get("Database", ""),
        database_version=meta_obj.get("DatabaseVersion", ""),
    )
    return Build(
        meta=meta,
        level=int(data["Level"]),
        class_name=data["Class"],
        origin=data.get("Origin", ""),
        alignment=data.get("Alignment", ""),
        name=data.get("Name", ""),
        comment=data.get("Comment", ""),
        power_sets=tuple(data.get("PowerSets", [])),
        last_power=data.get("LastPower", 0),  # raw, no -1 offset
        power_entries=tuple(_parse_power_entry(p) for p in data.get("PowerEntries", [])),
    )


def load_mbd(path: Path | str) -> Build:
    """Read and parse a ``.mbd`` file from disk.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
        ValueError: if the JSON is invalid or the ``BuiltWith`` block is missing.
    """
    with open(path, encoding="utf-8") as stream:
        data = json.load(stream)
    return parse_mbd(data)
