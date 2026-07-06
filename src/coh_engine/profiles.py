"""Build-type profile layer: the nine canonical types and their target resolution.

This is the strategy layer ABOVE the calc engine (memory: build-type branching): it
selects a target profile that parameterizes CP7 goal scoring; it does NOT change engine
math. Profiles live in ``strategy/build_profiles.json`` with targets that reference
``strategy/breakpoints.json`` by dotted path — a ref containing ``{at}`` is resolved
against the build's archetype (so resist-cap targets the AT's own cap). The canonical
taxonomy is ``docs/build-types-and-goals.md``; hard-mode / 4-star is a documented GAP
and is deliberately absent.

Spec: docs/build-types-and-goals.md; strategy/breakpoints.json.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from coh_engine.at_names import resolve_at_key

# The nine canonical build types (docs/build-types-and-goals.md § The major build types).
CANONICAL_PROFILES = (
    "soft-cap-defense",
    "resist-cap",
    "perma-hasten",
    "procmonster",
    "farmer",
    "pvp",
    "theme-rp",
    "solo-99-difficulty",
    "speed-runner-tf",
)


@dataclass(frozen=True, slots=True)
class Target:
    """One resolved goal target: a metric, a comparison op, and a concrete value."""

    metric: str
    op: str
    value: float | bool


@dataclass(frozen=True, slots=True)
class BuildProfile:
    """A resolved build-type profile: its targets and survival/damage/recharge priority."""

    name: str
    display_name: str
    priority: tuple[str, ...]
    targets: tuple[Target, ...]


def load_breakpoints(path: Path | str) -> Mapping[str, Any]:
    """Parse ``breakpoints.json`` (the numeric SSOT the profile targets reference).

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        return MappingProxyType(json.load(stream))


def load_build_profiles(path: Path | str) -> Mapping[str, Any]:
    """Parse ``build_profiles.json`` and return its raw (unresolved) ``profiles`` map.

    Raises:
        FileNotFoundError: if ``path`` does not exist.
    """
    with open(path, encoding="utf-8") as stream:
        return MappingProxyType(json.load(stream)["profiles"])


def profile_names(raw_profiles: Mapping[str, Any]) -> list[str]:
    """The profile keys defined in the file."""
    return list(raw_profiles)


def _resolve_ref(ref: str, breakpoints: Mapping[str, Any], at_key: str) -> float:
    """Walk a dotted breakpoints path (``{at}`` -> ``at_key``) to its numeric value.

    When the ref uses ``{at}``, ``at_key`` is resolved to its canonical archetype key
    (:func:`~coh_engine.at_names.resolve_at_key`), so a caller may pass a display name
    (``"Arachnos Soldier"``) or ``Class_`` name and still hit the underscore key.
    """
    node: Any = breakpoints
    if "{at}" in ref:
        at_key = resolve_at_key(at_key, breakpoints.get("archetypes", {}))
    parts = ref.replace("{at}", at_key).split(".")
    for part in parts:
        if not isinstance(node, Mapping) or part not in node:
            raise ValueError(
                f"E16: profile target references breakpoint path {ref!r}, but segment {part!r} is not in "
                "breakpoints.json; fix the ref or add the breakpoint"
            )
        node = node[part]
    # bool is an int subclass; a boolean breakpoint must not resolve to 1.0/0.0.
    if isinstance(node, bool) or not isinstance(node, int | float):
        raise ValueError(
            f"E16: breakpoint path {ref!r} resolved to a non-numeric value {node!r}; point the ref at a "
            "numeric leaf in breakpoints.json (not a sub-object)"
        )
    return float(node)


def _resolve_target(raw: Mapping[str, Any], breakpoints: Mapping[str, Any], at_key: str) -> Target:
    """One raw target -> a :class:`Target` (literal ``value`` or resolved ``ref``)."""
    if "value" in raw:
        return Target(metric=raw["metric"], op=raw["op"], value=raw["value"])
    return Target(metric=raw["metric"], op=raw["op"], value=_resolve_ref(raw["ref"], breakpoints, at_key))


def resolve_profile(
    name: str, raw_profiles: Mapping[str, Any], breakpoints: Mapping[str, Any], *, at_key: str
) -> BuildProfile:
    """Resolve a named profile's targets against ``breakpoints`` for archetype ``at_key``.

    Raises:
        ValueError: ``P-GOAL-001`` if ``name`` is not a defined profile; ``E16`` if a
            target references a breakpoint path that does not exist.
    """
    if name not in raw_profiles:
        raise ValueError(
            f"P-GOAL-001: unknown build profile {name!r}; expected one of {list(raw_profiles)} "
            "(hard-mode / 4-star is a documented gap, not a profile)"
        )
    raw = raw_profiles[name]
    return BuildProfile(
        name=name,
        display_name=raw["display_name"],
        priority=tuple(raw["priority"]),
        targets=tuple(_resolve_target(t, breakpoints, at_key) for t in raw["targets"]),
    )


def select_profile(
    goal: str, raw_profiles: Mapping[str, Any], breakpoints: Mapping[str, Any], *, at_key: str
) -> BuildProfile:
    """Select and resolve the profile for a goal string (the if/else decision layer)."""
    return resolve_profile(goal, raw_profiles, breakpoints, at_key=at_key)
