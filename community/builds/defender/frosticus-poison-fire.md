---
title: Frosticus — Poison / Fire Blast Defender (Psychic Mastery, resist + -damage layered build)
parent_guide: ../../powersets/poison.md
parent_url: https://forums.homecomingservers.com/topic/17683-poison-guide-a-guide-to-the-most-deadly-poisons/
post_url: unknown
build_author: Frosticus
date_posted: 2020-04-08
date_captured: 2026-04-29
captured_by: local-capture
archetype: Defender
primary: Poison
secondary: Fire Blast
ancillary: Psychic Mastery
build_goal: resistance + -damage debuff layered survivability with cycling Rune of Protection / Melee Hybrid mez coverage
build_format: forum-export
verified: false
contradicts_data: none
suggested_filename: builds/defender/frosticus-poison-fire.md
---

## Context

Frosticus's own Poison/Fire Defender, posted as Section 5 of the 2020 Poison
guide (see [parent](../../powersets/poison.md)). Picked Fire because Fire is
"still the damage king" and doesn't require heavy proc slotting to perform,
freeing up recharge enhancement slots. Across many respecs the author settled
on a resistance-focused build over soft-capped defense, on the philosophy
that resistances and -damage debuffing combine well with Melee Hybrid's
regen and Defender ATO absorbs/heals — the author prefers "predictable and
avoidable" failures over the "hero to zero" pattern of squishy defense
builds. Mez is covered by cycling Rune of Protection with Melee Hybrid.
Hybrid is T4 in both Assault Radial and Melee. Reported pylon times: ~1:50
with Assault Radial (~475 DPS), ~2:15 with Melee Core (~410 DPS).

## Verbatim build

```text
Hero Plan by Mids' Reborn: Hero Designer 2.6.0.7 — https://github.com/ImaginaryDevelopment/imaginary-hero-designer

Level 50 Magic Defender
Primary Power Set: Poison
Secondary Power Set: Fire Blast
Power Pool: Speed
Power Pool: Leaping
Power Pool: Sorcery
Power Pool: Leadership
Ancillary Pool: Psychic Mastery

Hero Profile:

- Level 1: Envenom — AchHee-ResDeb%(A), EndRdx-I(33)
- Level 1: Flares — SprWntBit-Rchg/SlowProc(A)
- Level 2: Weaken — CldSns-ToHitDeb(A), CldSns-%Dam(15), CldSns-Acc/Rchg(15), CldSns-ToHitDeb/EndRdx/Rchg(21), CldSns-Acc/ToHitDeb(25), CldSns-Acc/EndRdx/Rchg(43)
- Level 4: Fire Blast — SprVglAss-Dmg/Rchg(A), SprVglAss-Acc/Dmg/EndRdx(5), SprVglAss-Acc/Dmg(5), GldJvl-Dam%(13)
- Level 6: Fire Ball — Rgn-Dmg/Rchg(A), Rgn-Acc/Dmg/Rchg(7), Rgn-Acc/Rchg(7), Rgn-Dmg/EndRdx(9), Rgn-Knock%(13)
- Level 8: Hasten — RechRdx-I(A), RechRdx-I(9)
- Level 10: Combat Jumping — LucoftheG-Def/Rchg+(A), Ksm-ToHit+(11), ShlWal-ResDam/Re TP(11), Rct-ResDam%(43)
- Level 12: Spirit Ward — Prv-Absorb%(A)
- Level 14: Mystic Flight — BlsoftheZ-ResKB(A)
- Level 16: Maneuvers — LucoftheG-Def/Rchg+(A), LucoftheG-Def(17), LucoftheG-Def/EndRdx(17), LucoftheG-Def/EndRdx/Rchg(19)
- Level 18: Tactics — AdjTrg-ToHit/EndRdx(A), AdjTrg-ToHit(21), AdjTrg-ToHit/Rchg(40), AdjTrg-ToHit/EndRdx/Rchg(43), AdjTrg-EndRdx/Rchg(46)
- Level 20: Aim — RechRdx-I(A), GssSynFr--Build%(50)
- Level 22: Rune of Protection — StdPrt-ResKB(A), GldArm-Res/Rech/End(23), GldArm-3defTpProc(23), StdPrt-ResDam/Def+(25), GldArm-RechRes(42), UnbGrd-Max HP%(45)
- Level 24: Vengeance — LucoftheG-Def/Rchg+(A)
- Level 26: Poison Trap — FuroftheG-ResDeb%(A), Arm-Dam%(27), Obl-%Dam(27), Erd-%Dam(34), ScrDrv-Dam%(34), UnbCns-Acc/Rchg(37)
- Level 28: Blaze — SprVglAss-Dmg/EndRdx/Rchg(A), SprVglAss-Acc/Dmg/EndRdx/Rchg(29), SprVglAss-Rchg/+Absorb(29), Apc-Dam%(33), GldJvl-Dam%(33), Apc-Dmg/EndRdx(34)
- Level 30: Paralytic Poison — BslGaz-Acc/Rchg(A), BslGaz-Acc/Hold(31), BslGaz-Rchg/Hold(31), BslGaz-EndRdx/Rchg/Hold(31)
- Level 32: Venomous Gas — AchHee-ResDeb%(A), DmpSpr-ToHitDeb/EndRdx(42), DmpSpr-ToHitDeb(46)
- Level 35: Blazing Bolt — StnoftheM-Dam%(A), StnoftheM-Acc/Dmg(36), StnoftheM-Dmg/EndRdx(36), GldJvl-Dam%(36), SprDfnBst-Rchg/Heal%(37), Thn-Dmg/EndRdx(37)
- Level 38: Dominate — UnbCns-Dam%(A), GhsWdwEmb-Dam%(39), NrnSht-Dam%(39), GldNet-Dam%(39), GldJvl-Dam%(40), SprEnt-Rchg/AbsorbProc(40)
- Level 41: Inferno — Arm-Acc/Dmg/Rchg(A), Arm-Dmg/Rchg(42)
- Level 44: Mind Over Body — GldArm-End/Res(A), GldArm-ResDam(45), GldArm-Res/Rech/End(45)
- Level 47: World of Confusion — CrcPrs-Conf/EndRdx(A), CrcPrs-Conf(48), CrcPrs-Conf/Rchg(48), CrcPrs-Acc/Conf/Rchg(48), CrcPrs-Acc/Rchg(50), CrcPrs-Conf%(50)
- Level 49: Assault — EndRdx-I(A)

Inherent / auto:

- Level 1: Brawl — Empty
- Level 1: Quick Form
- Level 1: Prestige Power Dash / Slide / Quick / Rush / Surge — Empty
- Level 1: Sprint — Empty
- Level 1: Vigilance
- Level 2: Rest — Empty
- Level 4: Ninja Run
- Level 2: Swift — Run-I
- Level 2: Health — Pnc-Heal/+End(A), Mrc-Rcvry+(3), NmnCnv-Regen/Rcvry+(46)
- Level 2: Hurdle — Jump-I
- Level 2: Stamina — PrfShf-End%(A), PrfShf-EndMod(3), Empty(19)

Accolades & Incarnates:

- Freedom Phalanx Reserve
- Portal Jockey
- Task Force Commander
- The Atlas Medallion
- Level 50: Musculature Radial Paragon
- Level 50: Melee Core Embodiment
```

## DataLink

Embedded as an inline DataLink in the OP's Section 5.2 (not captured here as
a decoded blob). Planner project: <https://github.com/ImaginaryDevelopment/imaginary-hero-designer>.

## Notes from the author (if any)

The author notes the build would likely be stronger with Cardiac and Barrier
instead of Musculature and Ageless, but the latter pair was a conscious DPS
choice; they intend to finish out alternate Incarnates for difficult
encounters such as the final warwalker standoff in the Tin Mage TF, which
they had not yet beaten solo no-insp/temp/Lore at the time of posting.

A 12 November 2024 follow-up from Frosticus notes two game changes since the
original guide: secondary T1s can now be skipped, and Rune of Protection has
been nerfed.
