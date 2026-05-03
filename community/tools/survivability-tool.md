---
title: "The Survivability Tool"
url: "https://forums.homecomingservers.com/topic/12212-the-survivability-tool/"
source: "forums.homecomingservers.com"
authors: ["Bopper"]
date_posted: "2019-11-02"
date_captured: "2026-04-27"
captured_by: "local-capture"
topic_tags: ["survivability", "tools", "defense", "regen", "mids"]
trust: community-consensus
multi_post: true
post_count: 3
contradicts_data: "none"
---

# The Survivability Tool

## Summary

- The Survivability Tool is a Google Sheets calculator (you make a local copy via the OP's "/copy" link) that takes user inputs — Archetype, defenses by position and type, resistances by damage type, Max HP boosts, total Regeneration including the 100% base, additional HP/sec, damage debuff, to-hit debuff, plus enemy attack profile (DPS, attack type, damage type, enemy to-hit, rank, and relative level) — and computes layered survivability metrics in real time.
- Key outputs include Probability to Hit (with the cap correctly applied via min/max), Damage Taken after Resistance, HP/sec recovery (5% of Max HP per regen tick, with tick interval shrinking as regen rises), Time until Death, Max DPS for Survival Duration, Survivability Score (a ratio against the unboosted base), and the v2.0+ Immortality Score — the maximum enemy DPS your build can sustain indefinitely.
- v2.0 (June 2020) added a positional/type matrix so all 16 attack-type × damage-type permutations display at once (including a rare "No Position" column for psionic attacks that lack a positional tag); v3.0 (December 2020) added Arachnos's Conditioning inherent (regen tick 1 per 10s vs. 12s), Mastermind Bodyguard Mode (pick 0–6 pets to divide incoming damage), and pre-Purple-Patch DPS / damage-debuff / to-hit-debuff inputs that the tool now scales by enemy relative level.
- Limitations called out by the author: the tool does not natively model the Absorb mechanic, clickable heals (Reconstruction, Aid Self, etc.), proc-based regen on toggles like Power Transfer, or Mastermind binomial cascades — the user must convert those into an estimated "Additional Heal over Time (HPS)" number and feed it into the input field.
- Color coding inside the sheet is enforced: green cells are user inputs, orange cells are calculated (read-only — editing them breaks formulas), and black cells are fixed AT-cap tables (base/max HP, max regen, max resistance per Archetype).

## Verbatim excerpt

### Post 1 — The Survivability Tool (overview & inputs/outputs)

The Survivability Tool by Bopper. Written: 2 November 2019. Last Updated: 17 June 2020. (How long will it take until you're dead?)

Author's Note: This tool is always a work in progress. I am always updating the tool when new information comes in (like how I learned about Blasters having a higher max HP than what's listed on Paragon Wiki). There is also a giant exclusion from this tool that needs to be incorporated: the Absorb mechanic. I don't entirely understand how it works and I don't entirely understand how I can factor it into the survivability measurements. The temporary duration of an absorb shield is an issue, but once I better grasp it I will incorporate it.

Have you ever wondered how strong am I, really? Well, I have a simple test for that. I have written a program that allows the user to enter characteristics of their hero/villain — such as Archetype, Defenses, Resistances, Max Health Bonuses — and computes survivability. Why would I want to know this? Answer, you might not; but if you have ever asked the question, "should I add more defense or resistance (or more HP, or more regeneration)?" then this is the tool for you. In real time, you can tweak any parameter and see how it will impact your survivability.

Without further ado, here is a link to the Survivability Tool (it is a Google Doc that you will make a local copy of).

How do I use the tool?

First off, you can only edit the fields marked with a Green background. Also, there are two types of editable fields: ones you enter a value into (e.g. changing Max HP Boost from 50% to 15%), and ones you select from a drop-down menu (e.g. changing Archetype from Brute to Defender).

The fields marked with an Orange background are calculated fields, which take the user-input information to determine their values. You can't edit these fields, otherwise you would break the formulas.

The fields marked with a Black background are fixed tables.

Inputs — Enter Your Build's Information

Max HP Boost (%): The user enters the amount of Max HP boosts in the build. This could include boosts from Set IO Bonuses, or it could be a power that increases the Max HP. Add up all the bonuses and do not include the 100% from base. Max HP Boosts do 2 things for the character: more Max HP means more damage needs to be done to kill you, and more Max HP means more HP is recovered every time a regeneration tick is triggered (5% of max HP is recovered on each tick).

Regeneration Total (%): The user enters the total amount of Regeneration in the build (100% from base, regeneration from set IO bonuses and powers). Add up all of them (or use Mids' Reborn and look at the totals — do include the 100% base). Regeneration determines how frequently the 5% HP recovery triggers.

Additional Heal over Time (HPS): The user enters the average amount of additional Healing the character receives in units of Hit Points per Second. For example, if every 90 seconds the character heals themselves for some amount, divide that heal amount by 90 and put the result in this field.

Damage Debuff: The user enters the amount of damage debuff their character applies to the enemy. The enemy can resist this debuff, so input the post-resisted debuff value.

To-Hit Debuff: The user enters the amount of to-hit debuff their character applies to the enemy. In the game the enemy can resist this debuff, so the user must enter the post-resisted debuff value into this field. For example, if the character applies a 30% to-hit debuff and the enemy resists 25% of the debuff, the user must input 22.5%.

Inputs — Enter Your Enemy's Attack Info

Attack Damage Per Second: The user enters the DPS coming from an enemy's attack (this is a value prior to looking at defense, resistance, etc. — just the raw damage).

Survival Duration: Duration (in seconds) the user wants to be capable of surviving. Used for "Max DPS for Survival Duration" and "Survivability Score" calculations.

Attack Type / Damage Type: The user selects the type of attack and the damage type for the Survivability Calculation.

Enemy To Hit: The user enters the enemy's to-hit modifier. Enemy Rank determines additional to-hit and accuracy modifiers. Enemy Relative Level can introduce additional to-hit/accuracy modifiers.

Inputs — Enter Your Defense/Resistance Values

Defense: Defense per position and type. Note that there is no such thing as toxic defense (at least according to Mids), so keep that set to 0%.

Resistance: Resistance per damage type. Note that there is no such thing as positional resistances, so keep those set to 0%.

Outputs — Max Values for your AT

HP (base): Base Hit Points for the user-selected Archetype.
HP (max): Maximum Hit Points for the user-selected Archetype.
Regeneration (max): Maximum regeneration for the user-selected Archetype.
Resistance (max): Maximum resistance for the user-selected Archetype.

Outputs — Your Health Calculations

Resistance: The resistance value to the user-selected damage type (capped at AT max).

Regen Tick Interval: As regeneration boosts are increased, the interval between ticks reduces.

HP per Regen Tick: 5% of the Max Health you recover on each regeneration tick.

HP/sec: Average amount of HP recovery each second; the formula simplifies algebraically.

Outputs — Your Damage Taken Calculations

Damage Taken (after Resistance): Damage you take when an attack hits, reduced by your resistance and any damage debuffs.

Total Accuracy Mods (product): Combined accuracy modifier for the enemy — product of general, rank, and relative-level accuracy mods.

Total ToHit Mods (sum): Combined to-hit modifier — sum of general, relative-level, and to-hit debuff.

Probability to Hit: Final probability of an attack hitting you, with min/max applied.

Outputs — Survivability Calculations

In v2.0+, the Survivability Calculations display scores for every permutation of Positional and Type attacks in a matrix instead of forcing manual selection. For one example build, a Smashing-Melee attack might show an Immortality Score of 193.33 (same for Ranged/AoE/No Position when Smashing type defense is higher than positional defenses); Psionic-Range might show 54.39. The "No Position" (positionless) attack is rare, but a few enemies do psionic attacks not tagged with a position, in which case positional defenses are ignored and only the type defense is used.

Time until Death: How long it takes to go from 100% health to death. Uses the inputs above.

Survivability Score: Ratio of "Max DPS for Survival Duration" against a baseline build (no defense, no resistance, no HP boost, no additional regeneration). Not intended to compare across Archetypes since base HP differs.

Immortality Score: Perhaps the definitive metric. Calculates how much DPS the enemy needs to overtake your build's HP/sec. Anything more, and your health bar will trend downward over time — so this is the maximum DPS your character can withstand while still surviving forever.

Edited 17 June 2020 by Bopper: long-overdue update to the Guide. It now properly reflects the features of the Tool.

### Post 2 — Revision History

13 Dec 2020 (v3.0):

- Note: Content of the guide does not reflect recent changes to the Tool. That will come later.
- Added the Conditioning Inherent for Arachnos. Previously it was using the base regeneration of 1 tick every 12s; it should have been 1 tick every 10s.
- Added Bodyguard Mode for Masterminds. You can choose your number of pets (0–6) to divide your damage across. The tool will assume the pets won't die, so temper expectations.
- Incorporated Purple Patch for Enemy Relative Level selections. Previously, the Attack Damage Per Second, Damage Debuff, and To Hit Debuff fields were assumed to have the Purple Patch included. I have now broken that out so that those three fields will be pre–Purple-Patch (e.g. if you enter a Damage Debuff of 40%, but select the Enemy Relative Level to be +3, the Purple Patch modifier of 0.65 will be applied, making the actual damage debuff 26%).

17 Jun 2020 (v2.0):

- Updated computational blocks so you start losing life on average is shown directly.
- Added new computational blocks that allow you to see all of your Survivability Calculations for every positional/type damage pairing — quality-of-life so you no longer have to select between every permutation just to see each score.
- Included "No Position" in the new Survivability Calculations. This is rare, but I believe there are some psychic attacks that are positionless, which would render Psionic defense the only check, with no Melee/AoE/Range defense applied.
- Made a new sheet for notes on the program (notes still need updating).

9 Nov 2019 (v1.03):

- Added a new user input for Health Bonuses, "Additional Heal over Time".

3 Nov 2019 (v1.02):

- Updated the Survivability Tool to correct an error in the "Probability to Hit" formula (forgot a min/max function).
- Added a new user input for Enemy's Attack Info, "Survival Duration".
- Added a new Survivability Calculation, "Max DPS for Survival Duration".
- Changed the "Survivability Score" to be a ratio of the "Max DPS for Survival Duration" result with its Base result.

Edited 13 December 2020 by Bopper.

### Post 3 — Reserved

(Placeholder for future content.)

## Notable replies

- @r0y (May 2020) asked whether Power Transfer procs and other regen procs in toggles/autos could be modeled. Bopper clarified in reply that the math is the same for autos and toggles but autos are 0-radius and only proc off the user, while toggle procs can roll off enemies/league mates within range. He explained that clickable heals (Reconstruction, Aid Self, Siphon Life, Dull Pain on a fixed 120s cycle, etc.) cannot be added natively because the tool can't know your power, recharge, or enhancement state — instead, divide the heal value by your realistic recycle interval and feed the resulting HP/sec into the "Additional Heal over Time (HPS)" input. Globals like Numina, Regenerative Tissue, and Impervious Skin are already captured by total regen as Mids reports it, so no extra calculation is needed for those.

- @Arbegla (December 2020) asked about Mastermind Bodyguard Mode. Bopper initially recommended the simplified workaround — multiply DPS by 4 (best case, all 6 pets up) for the lower bound and bracket against a worst case (e.g. ×2) — but in the next post reversed course and added a "number of pets (0–6)" field that the tool now uses to divide incoming damage automatically when the AT is set to Mastermind, alongside the Purple Patch fix. (This became the v3.0 release.)

- @Caulderone (Feb 2020) noted that the new sheet's `/copy` link could fail without being signed in to Google; removing `/copy` loaded the file and let users save a local copy. Bopper acknowledged and fixed.

- @Arbegla (May 2021) asked about modeling damage from multiple simultaneous sources (which hurts defense more than resistance because of N-choose-K interactions). Bopper said expansion to handle various attack types and ranked enemies is possible, but the binomial/distribution math won't be incorporated because it doesn't change average performance and would force a distribution view that's too complex for a spreadsheet — the same reason cascading defense failure isn't modeled.

## Build attachments

- Survivability Tool (Google Sheets, copy-on-open): `https://docs.google.com/spreadsheets/d/1Yxcprm9njP6VcOklYrcFZhQgLU1-2Z0IZ-FLVipy2t8/copy`

(No .mxd files or DataLink build links are posted by Bopper in this thread; the only attachment is the Google Sheets calculator above.)
