# Unresolved patch lines — needs manual review

Lines that matched a numeric-change pattern but couldn't be classified by entity path. Walk these manually and either: add to current_overrides.json by hand, or extend scripts/parse-patches.ps1 to
handle the pattern.

Generated: 2026-04-27 21:16
Total: 42

```text
[Issue_26_Page_1] no-entity-context: Rain of Arrows animation has been reduced from 4 to 2 seconds. Base recharge time has been increased 5 seconds to compensate.
[Issue_26_Page_2] no-entity-context: Taser: Recharge reduced from 20 to 10 seconds, duration reduced from scale 10 to scale 5, damage increased from 0.25 to 1.96 (same damage as Energy Punch)
[Issue_26_Page_2] no-entity-context: Pools > Concealment > Invisibility: Endurance cost lowered from 0.65 to 0.2275. You are now be able to attack while this power is active, but should you attack, all it's defense will suppress.
[Issue_26_Page_2] no-entity-context: Illusion Control > Superior Invisibility: Endurance cost lowered from 0.52 to 0.182.
[Issue_26_Page_4] no-entity-context: Brute > Katana > Golden Dragonfly: Max targets reduced from 10 to 5
[Issue_26_Page_4] no-entity-context: Scrapper > Katana > Golden Dragonfly: Max targets reduced from 10 to 5
[Issue_26_Page_4] no-entity-context: Stalker > Ninja Blade > Golden Dragonfly: Max targets reduced from 10 to 5
[Issue_26_Page_4] no-entity-context: Brute Melee > Battle Axe > Cleave: Max targets reduced from 10 to 5
[Issue_26_Page_4] no-entity-context: Scrapper Melee > Battle Axe > Cleave: Max targets reduced from 10 to 5
[Issue_26_Page_4] no-entity-context: Tanker Melee > Battle Axe > Cleave: Max targets reduced from 16 to 10
[Issue_26_Page_5] no-entity-context: Weapon Mastery > Shuriken: This power was erroneously set at half the intended recharge for it's damage. Recharge has now been increased from 3 to 6 seconds.
[Issue_27_Page_7] no-entity-context: Epic > Psionic Mastery > Telekinesis: This power should now behave similarly to the new controller/dominator version of the power, albeit with a 5 foe target cap and smaller radius. Recharges in 240s, max toggle duration 20s. Endurance cost per second reduced from 3.9 to 0.65. Now accepts Immobilize and Accuracy enhancements.
[Issue_27_Page_7] no-entity-context: Epic > Dark Mastery > Netherworld Tentacles (Sentinel) - Recharge increased from 16s to 20s, endurance cost reduced from 16.25 to 12.74
[Issue_27_Page_7] no-entity-context: Epic > Dark Mastery > Petrifying Gaze (Mastermind) - This power now inflicts damage over time. Range increased from 50ft to 60ft, endurance cost increased from 9.75 to 10.66, recharge lowered from 32s to 24s
[Issue_27_Page_7] no-entity-context: Epic > Dark Mastery > Petrifying Gaze (Scraper/Stalker) - Range increased from 50ft to 60ft, Endurance cost increased from 9.75 to 10.66, recharge lowered from 32s to 24s
[Issue_27_Page_7] no-entity-context: Epic > Earth Mastery > Hurl Boulder (Controller) - Range increased from 40ft to 80ft, Recharge increased from 10s to 16s, Cast Time reduced from 2.5s to 2.0s, endurance cost decreased from 11.7 to 10.66
[Issue_27_Page_7] no-entity-context: Epic > Earth Mastery > Quicksand (Brute/Tanker) : Recharge increased from 30s to 50s, end cost increased from 7.8 to 9.75, radius decreased from 25' to 15', target cap reduced from 16 to 10
[Issue_27_Page_7] no-entity-context: Epic > Earth Mastery > Stalagmites (Brute/Tanker) - Recharge reduced from 64s to 32s, Accuracy increased from 0.8 to 1, Endurance Cost increased from 19.5 to 18.98, range increased from 70ft to 80ft
[Issue_27_Page_7] no-entity-context: Epic > Electricity Mastery > Chain Fences (Sentinel) - Recharge increased from 8s to 16s, Endurance cost lowered from 19.5 to 10.751
[Issue_27_Page_7] no-entity-context: Epic > Electricity Mastery > ESD (Mastermind) - Removed self -recovery penalty, reduced recharge from 800s to 180s, reduced radius from 40ft to 25ft, reduced target cap from 16 to 10, reduced Stun from scale 15 to scale 8, reduced -regen debuff duration from 15s to 5s
[Issue_27_Page_7] no-entity-context: Epic > Electricity Mastery > Electric Shackles (Mastermind) - Endurance cost increased from 8.58 to 10.66
[Issue_27_Page_7] no-entity-context: Epic > Electricity MAstery > Paralizing Jolt - Accuracy lowered from 1.2 to 1.0
[Issue_27_Page_7] no-entity-context: Epic > Electricity Mastery > Static Discharge (Blaster/Mastermind) - Recharge increased from 12s to 24s, end cost increased from 14.82 to 27.3, damage increased from scale 0.91 to scale 0.958
[Issue_27_Page_7] no-entity-context: Epic > Energy Mastery > Focused Accuracy (Brute/Scrapper/Stalker/Tanker) - End Cost reduced from 0.39 to 0.195
[Issue_27_Page_7] no-entity-context: Epic > Fire Mastery > Fire Cages (Sentinel) - Recharge increased from 16s to 20s, Endurance cost lowered from 19.5 to 12.74
[Issue_27_Page_7] no-entity-context: Epic > Force Mastery > Repulsion Field (Blaster) - Power no longer drains endurance per target hit in PvE. Target cap reduced from 16 to 10
[Issue_27_Page_7] no-entity-context: Epic > Ice Mastery > Frostbite (Sentinel) - Recharge increased from 16s to 20s, Endurance cost lowered from 19.5 to 12.74
[Issue_27_Page_7] no-entity-context: Epic > Laser Beam Eyes (Scrapper/Stalker) - Endurance Cost reduced from 8.07575 to 6.5
[Issue_27_Page_7] no-entity-context: Epic > Mace Mastery > Focused Accuracy (Brute/Controler/Corruptor/Defender/Tanker) - End Cost reduced from 0.39 to 0.195
[Issue_27_Page_7] no-entity-context: Epic > Psionic Mastery > Psychic Shockwave (Sentinel) - Recharge increased from 20s to 40s, damage scale increased from scale 0.6031 to scale 1.0954, target cap lowered from 16 to 10
[Issue_27_Page_7] no-entity-context: Patron > Leviathan Mastery > Bile Spray (Blaster/Brute/Controller/Dominator/Mastermind/Tanker/VEAT) - Cast time lowered from 2.6 to 1.6s
[Issue_27_Page_7] no-entity-context: Patron > Leviathan Mastery > Spirit Shark (Brute/Tanker/Scrapper/Stalker/VEAT) - Recharge increased from 9s to 13s, End cost increased from 8.58 to 15.86, Cast Time reduced from 3s to 2s, base damage scale increased from scale 1.4 to 1.56
[Issue_27_Page_7] no-entity-context: Patron > Mu Mastery > Conserve Power (Corruptor/Defender) - Changed to Energize. Recharge lowered from 600 to 240s, end cost increased from 9.75 to 13. Now accept Healing enhancements and sets
[Issue_27_Page_7] no-entity-context: Patron > Mu Mastery > Electric Shackles (Blaster/Corruptor/Defender/Mastermind/Scrapper/Stalker) - Endurance cost increased from 8.58 to 10.66
[Issue_27_Page_7] no-entity-context: Patron > Soul Mastery > Darkest Night (Sentinel) - Recharge increased to 20s, Radius decreased from 25 to 15 feet, Target cap lowered from 16 to 10
[Issue_27_Page_7] no-entity-context: Patron > Soul Mastery > Darkest Night (VEAT) - Recharge increased to 20s, Radius decreased from 25 to 15 feet, Target cap lowered from 16 to 10
[Issue_27_Page_7] no-entity-context: Patron > Soul Mastery > Soul Drain (Defender/Corruptor) - Moved to T4, target cap increased from 7 to 10
[Issue_27_Page_7] no-entity-context: Patron > Soul Mastery > Soul Storm (Blaster/Mastermind) - Range reduced from 80 to 60ft
[Issue_27_Page_7] no-entity-context: Patron > Soul Mastery > Soul Storm (Defender/Corruptor) - Moved to T1, range reduced from 80 to 60ft
[Issue_27_Page_7] no-entity-context: Patron > Soul Mastery > Soul Storm (Sentinel) - Range reduced from 80 to 60ft
[Issue_27_Page_7] no-entity-context: Patron > Soul Mastery > Soul Storm (Stalker) - Range reduced from 80 to 60ft
[Issue_28_Page_2] no-entity-context: Accuracy increased from 0.67 to 0.8.
```
