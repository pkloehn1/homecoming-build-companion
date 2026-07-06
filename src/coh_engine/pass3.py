"""The Pass-3/4 per-power scalar fold — one filter-aware helper for both consumers.

``GBPA_Pass3_EnhancePostED`` (clsToonX.cs:1924) turns a per-power aspect's slotted
enhancement aggregate plus the global ``_selfEnhance`` term into the multiplier a
buffed scalar is divided by: ``(( ED(sum slotted) + global ) + 1)``, then
``GBPA_Pass4_Add``'s ``+1`` and ``GBPA_ApplyArchetypeCaps``'s optional clamp.

This was implemented twice — the CP5 toggle-EndUse arm in
``base_totals._gbd_toggle_end_and_fly`` and the CP6.1 per-power arm in
``statistics`` — and the two diverged (only the latter honored ``Power.IgnoreEnh``).
Both now route through :func:`fold_divisor`, so the character ``Totals.EndUse`` and the
per-power ``end_per_sec`` can never disagree on the fold order, the ignore gate, or the
cap.

**Filters.** ``ignored_aspects`` is the extensible filter set: an aspect present in it
(``Power.IgnoreEnh`` / ``IgnoreEnhancement``) has a zero modifiable base, so the fold is
skipped and the scalar stays at base. Additional per-aspect filters compose into that
set by the caller.

Spec: docs/engine/mids-port-spec.md § gbpa-pass-pipeline (Pass 3).
"""

from collections.abc import Collection

from coh_engine.maths import f32


def fold_divisor(
    aggregate: float,
    global_term: float,
    *,
    aspect: str,
    ignored_aspects: Collection[str] = (),
    cap: float | None = None,
) -> float:
    """The per-power fold multiplier for one scalar aspect.

    Returns ``(( aggregate + global_term ) + 1)`` in the C# float order, clamped to
    ``cap`` when given (the AT recharge cap, ``GBPA_ApplyArchetypeCaps``). Returns
    ``1.0`` — no fold — when ``aspect`` is in ``ignored_aspects`` (the power ignores
    that enhancement, so its modifiable base is zero).

    ``aggregate`` is the ED-reduced sum of the power's slotted enhancement for
    ``aspect`` (from :func:`~coh_engine.enh_pipeline.aggregate_and_ed`); ``global_term``
    is the matching global ``_selfEnhance`` scalar
    (:class:`~coh_engine.base_totals.GlobalEnhance`).
    """
    if aspect in ignored_aspects:
        return 1.0
    divisor = f32(f32(aggregate + global_term) + 1.0)
    if cap is not None:
        divisor = min(divisor, cap)
    return divisor
