"""Loader for the archetype/class records the oracle harness dumps.

Mirrors the fields MidsReborn reads in ``Archetype.cs:89-115`` and the
case-insensitive ``DatabaseAPI.NidFromUidClass`` lookup (``DatabaseAPI.cs:122-133``).
The per-class ``Column`` is a stored indirection into the AttribMod tables
(``Archetype.cs:102,153``); it must be read, never assumed to equal the class
index. Spec: docs/engine/mids-port-spec.md § at-modifier-tables.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Archetype:
    """One class record: identity, the AttribMod ``Column``, and the AT caps."""

    index: int
    class_name: str
    display_name: str
    class_type: str
    column: int
    playable: bool
    hitpoints: int
    hp_cap: float
    res_cap: float
    damage_cap: float
    recharge_cap: float
    recovery_cap: float
    regen_cap: float
    perception_cap: float
    base_recovery: float
    base_regen: float
    base_threat: float


@dataclass(frozen=True, slots=True)
class ArchetypeDb:
    """The class table, indexed as ``Database.Classes`` is in MidsReborn."""

    classes: tuple[Archetype, ...]

    def nid_from_uid_class(self, name: str) -> int:
        """Case-insensitive ``ClassName`` -> index lookup; -1 if not found."""
        target = name.casefold()
        for at in self.classes:
            if at.class_name.casefold() == target:
                return at.index
        return -1


def load_archetypes(path: Path | str) -> ArchetypeDb:
    """Parse an ``archetypes.json`` oracle dump into :class:`ArchetypeDb`.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        records = json.load(stream)
    classes = tuple(
        Archetype(
            index=r["Index"],
            class_name=r["ClassName"],
            display_name=r["DisplayName"],
            class_type=r["ClassType"],
            column=r["Column"],
            playable=r["Playable"],
            hitpoints=r["Hitpoints"],
            hp_cap=r["HPCap"],
            res_cap=r["ResCap"],
            damage_cap=r["DamageCap"],
            recharge_cap=r["RechargeCap"],
            recovery_cap=r["RecoveryCap"],
            regen_cap=r["RegenCap"],
            perception_cap=r["PerceptionCap"],
            base_recovery=r["BaseRecovery"],
            base_regen=r["BaseRegen"],
            base_threat=r["BaseThreat"],
        )
        for r in records
    )
    return ArchetypeDb(classes=classes)
