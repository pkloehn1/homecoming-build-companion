"""Archetype-name resolution — one canonical key from any input form.

Archetypes are named several ways across the project: the canonical breakpoints /
strategy keys (``Scrapper``, ``Arachnos_Soldier``), the archetype record's
``DisplayName`` (``Arachnos Soldier``, with a space), and its ``ClassName``
(``Class_Arachnos_Soldier``). :func:`resolve_at_key` maps any of them — case-, space-,
and ``Class_``-prefix-insensitive — back to the one canonical key, so a caller never has
to know which form a given layer expects. Reused by ``profiles`` (the ``{at}`` ref
substitution), scoring, and any CLI/DTO ingest that names an AT.
"""

from collections.abc import Iterable


def _normalize(name: str) -> str:
    return name.strip().removeprefix("Class_").replace(" ", "_").casefold()


def resolve_at_key(name: str, valid_keys: Iterable[str]) -> str:
    """Resolve an archetype named in any form to its canonical key among ``valid_keys``.

    Accepts ``"Scrapper"``, ``"scrapper"``, ``"Arachnos Soldier"``, ``"Arachnos_Soldier"``,
    and ``"Class_Arachnos_Soldier"`` — all resolve to the matching key.

    Raises:
        ValueError: ``E19`` if ``name`` matches no key (or, defensively, more than one) —
            never silently guessed.
    """
    keys = list(valid_keys)
    normalized = _normalize(name)
    matches = [key for key in keys if _normalize(key) == normalized]
    if len(matches) == 1:
        return matches[0]
    raise ValueError(
        f"E19: archetype {name!r} matches {len(matches)} of the {len(keys)} known keys {sorted(keys)}; "
        "pass a recognizable archetype name (canonical key, display name, or Class_ name)"
    )
