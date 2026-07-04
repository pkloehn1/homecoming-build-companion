"""StaticIndex resolution maps the .mxd reader needs.

A ``.mxd`` build references powers and enhancements by ``StaticIndex`` (the stable
on-disk id), not by name. Resolving them requires two maps exported by the oracle
harness:

- ``power_static_index.json`` — ``StaticIndex`` -> power ``FullName``.
- ``enhancements.json`` — ``StaticIndex`` -> ``{UID, TypeID}``. The ``TypeID`` is
  essential: ``ReadSlotData`` branches on it to know how many bytes follow each
  enhancement reference.

Entries with a negative ``StaticIndex`` are dropped: ``-1`` is the .mxd sentinel
for an empty reference, so it must resolve to "not found".
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EnhIndexEntry:
    """An enhancement's identity and type, keyed by ``StaticIndex``."""

    uid: str
    type_id: str


def load_power_index(path: Path | str) -> dict[int, str]:
    """Load the ``StaticIndex`` -> power ``FullName`` map.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        records = json.load(stream)
    return {r["StaticIndex"]: r["FullName"] for r in records if r["StaticIndex"] >= 0}


def load_enhancement_index(path: Path | str) -> dict[int, EnhIndexEntry]:
    """Load the ``StaticIndex`` -> :class:`EnhIndexEntry` map.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        records = json.load(stream)
    return {
        r["StaticIndex"]: EnhIndexEntry(uid=r["UID"], type_id=r["TypeName"]) for r in records if r["StaticIndex"] >= 0
    }
