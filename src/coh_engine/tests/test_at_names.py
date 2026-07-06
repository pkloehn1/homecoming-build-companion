"""Archetype-name resolution — any input form to the one canonical key."""

import pytest

from coh_engine.at_names import resolve_at_key

_KEYS = ("Tanker", "Scrapper", "Arachnos_Soldier", "Arachnos_Widow")


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Scrapper", "Scrapper"),
        ("scrapper", "Scrapper"),  # case-insensitive
        ("Arachnos Soldier", "Arachnos_Soldier"),  # display name with a space
        ("Arachnos_Soldier", "Arachnos_Soldier"),  # already canonical
        ("Class_Arachnos_Widow", "Arachnos_Widow"),  # Class_ prefix
        ("  Tanker  ", "Tanker"),  # surrounding whitespace
    ],
)
def test_resolves_any_form_to_the_canonical_key(name: str, expected: str) -> None:
    """Case, spaces, and the Class_ prefix all resolve to the canonical breakpoints key."""
    assert resolve_at_key(name, _KEYS) == expected


def test_unknown_archetype_fails_loud() -> None:
    """A name matching no key is refused (E19), never guessed."""
    with pytest.raises(ValueError, match="E19"):
        resolve_at_key("Blapper", _KEYS)
