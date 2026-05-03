# Lane diff summary

Cross-check of patch-history overrides (data/diff/current_overrides.json)
against the canonical zip (data/canonical/).

Generated: 2026-04-27 21:20

## Counts

| Bucket | Count |
|---|---:|
| Override agrees with canonical | 5 |
| **Override drifts from canonical** | **35** |
| Unresolved (no canonical file or field) | 63 |

## Drift by patch

| Patch | Drift count |
|---|---:|
| Issue_26_Page_4 | 35 |

## Drifts (override = current Homecoming truth; canonical = stale)

| Entity | Field | Override | Canonical | Source patch |
|---|---|---:|---:|---|
| Tanker.Battle_Axe.Cleave | max_targets_hit | 16 | 5 | Issue_26_Page_4 |
| Tanker.Battle_Axe.Pendulum | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Battle_Axe.Whirling_Axe | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Broad_Sword.Head_Splitter | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Broad_Sword.Slice | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Broad_Sword.Whirling_Sword | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Claws.Eviscerate | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Claws.Spin | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Dark_Melee.Dark_Consumption | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Electrical_Melee.Lightning_Clap | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Electrical_Melee.Thunder_Strike | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Energy_Melee.Whirling_Hands | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Fiery_Melee.Breath_of_Fire | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Fiery_Melee.Combustion | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Fiery_Melee.Fire_Sword_Circle | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Ice_Melee.Frost | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Ice_Melee.Frozen_Aura | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Martial_Arts.Dragons_Tail | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Psionic_Melee.Mass_Levitate | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Psionic_Melee.Psi_Blade_Sweep | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Radiation_Melee.Atom_Smasher | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Savage_Melee.Rending_Flurry | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Savage_Melee.Shred | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Spines.Ripper | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Spines.Spine_Burst | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Staff_Fighting.Eye_of_the_Storm | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Staff_Fighting.Guarded_Spin | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Staff_Fighting.Innocuous_Strikes | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.Stone_Melee.Fault | max_targets_hit | 16 | 0 | Issue_26_Page_4 |
| Tanker.Stone_Melee.Tremor | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Super_Strength.Foot_Stomp | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Super_Strength.Hand_Clap | max_targets_hit | 16 | 10 | Issue_26_Page_4 |
| Tanker.Titan_Weapons.Arc_of_Destruction | arc | 10 | 120.0003 | Issue_26_Page_4 |
| Tanker.War_Mace.Shatter | max_targets_hit | 10 | 5 | Issue_26_Page_4 |
| Tanker.War_Mace.Whirling_Mace | max_targets_hit | 16 | 10 | Issue_26_Page_4 |

## Unresolved (couldn't map override to a canonical file/field — needs manual review)

| Entity | Field | Override value | Source patch | Reason |
|---|---|---:|---|---|
| Blast_Power_Set_Updates.Full_Auto | arc | 90 | Issue_27_Page_6 | ambiguous: 13 canonical files match — needs manual disambiguation. Files: powers\blaster_ranged\assault_rifle\full_auto.json; powers\corruptor_ranged\assault_rifle\full_auto.json; powers\defender_ranged\assault_rifle\full_auto.json; powers\family\family_tommy_gun_lt\full_auto.json; powers\mastermind_pets\commando_2\full_auto.json; powers\mission_maker_attacks\assault_rifle\full_auto.json; powers\mission_maker_pets\commando\full_auto.json; powers\mission_maker_secondary\assault_rifle\full_auto.json; powers\sentinel_ranged\assault_rifle\full_auto.json; powers\v_arachnos\arachnobot_minion\full_auto.json; powers\v_freedomcorps\officer\full_auto.json; powers\v_genericvillains\assault_rifle_corruptor_high\full_auto.json; powers\v_mooks\boss_capo_low\full_auto.json |
| Blaster_Secondary_Revamp.Aging_Touch | damage_scale | 1.02 | Issue_27_Page_1 | canonical file powers\blaster_support\time_manipulation\aging_touch.json has no field 'damage_scale' |
| Blaster_Secondary_Revamp.Blinding_Powder | magnitude | 3 | Issue_27_Page_1 | canonical file powers\blaster_support\ninja_training\blinding_powder.json has no field 'magnitude' |
| Blaster_Secondary_Revamp.Cauterizing_Aura | max_targets_hit | 10 | Issue_27_Page_1 | no canonical file matched |
| Blaster_Secondary_Revamp.Frigid_Protection | max_targets_hit | 10 | Issue_27_Page_1 | no canonical file matched |
| Blaster_Secondary_Revamp.Telekinetic_Thrust | damage_scale | 2.92 | Issue_27_Page_1 | canonical file powers\blaster_support\mental_manipulation\telekinetic_thrust.json has no field 'damage_scale' |
| Disruption_Arrow | max_targets_hit | 16 | Issue_27_Page_1 | no canonical file matched |
| Earth_Assault | activation_time | 120.5 | Issue_26_Page_2 | no canonical file matched |
| Earth_Assault | recharge_time | 14 | Issue_26_Page_2 | no canonical file matched |
| Earth_Manipulation.Seismic_Smash | magnitude | 3 | Issue_27_Page_3 | ambiguous: 3 canonical files match — needs manual disambiguation. Files: powers\blaster_support\earth_manipulation\seismic_smash.json; powers\mission_maker_secondary\earth_manipulation\seismic_smash.json; powers\v_arachnos_proxy\earth_manipulation\seismic_smash.json |
| Enemies.Crey_Industries.Crey_Agents | max_targets_hit | 1 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Crey_Industries.Cryogenicist | duration | 1 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Crey_Industries.Cryogenicist | heal_scale | 4 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Gold_Brickers.Breaker | defense_scale | 1 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Skulls.Death_Heads | accuracy | 2.5 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Skulls.Death_Heads | arc | 0.91 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Skulls.Death_Walkers_Death_Dolls | duration | 1 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Skulls.Gravediggers | accuracy | 0.95 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Skulls.Gravediggers | defense_scale | 1.67 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Warriors | damage_scale | 1.32 | Issue_28_Page_2 | no canonical file matched |
| Enemies.Warriors | defense_scale | 3.46 | Issue_28_Page_2 | no canonical file matched |
| Enemy_Group_Revamp_The_Warriors | damage_scale | 0.966 | Issue_28_Page_1 | no canonical file matched |
| Energy_Assault | activation_time | 1.67 | Issue_26_Page_2 | no canonical file matched |
| Icy_Assault | recharge_time | 17 | Issue_26_Page_2 | no canonical file matched |
| Martial_Assault | damage_scale | 0.8985 | Issue_26_Page_2 | no canonical file matched |
| Martial_Assault | recharge_time | 86.4 | Issue_26_Page_2 | no canonical file matched |
| Other_Powers_Changes.Shadow_Maul | max_targets_hit | 5 | Issue_27_Page_1 | ambiguous: 20 canonical files match — needs manual disambiguation. Files: powers\5thcolumn\fifth_column_requiem_hm\shadow_maul.json; powers\5thcolumn\fifth_column_requiem_melee\shadow_maul.json; powers\blaster_support\darkness_manipulation\shadow_maul.json; powers\brute_melee\dark_melee\shadow_maul.json; powers\freaklok\eidolon_male\shadow_maul.json; powers\incarnate_i20\exorcist\shadow_maul.json; powers\mission_maker_attacks\dark_melee\shadow_maul.json; powers\mission_maker_secondary\darkness_manipulation\shadow_maul.json; powers\mission_maker_secondary\dark_melee\shadow_maul.json; powers\praetorians\black_swan\shadow_maul.json; powers\praetorians\black_swan_minion\shadow_maul.json; powers\scrapper_melee\dark_melee\shadow_maul.json; powers\skulls\morana\shadow_maul.json; powers\skulls\morana_high\shadow_maul.json; powers\stalker_melee\dark_melee\shadow_maul.json; powers\tanker_melee\dark_melee\shadow_maul.json; powers\tsoo\deathshead\shadow_maul.json; powers\v_arachnos\olivia_darque\shadow_maul.json; powers\v_arachnos_proxy\darkness_manipulation\shadow_maul.json; powers\v_genericvillains\dark_brute\shadow_maul.json |
| Other_VEAT_Changes | max_targets_hit | 15.6 | Issue_27_Page_7 | no canonical file matched |
| Placate | max_targets_hit | 5 | Issue_27_Page_3 | no canonical file matched |
| Pool_Powerset_Revamp_Teleportation.Team_Teleport | endurance_cost | 16 | Issue_27_Page_1 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\event\event_teleportation\team_teleport.json; powers\pool\teleportation\team_teleport.json |
| Pool_Powerset_Update_Sorcery.Mystic_Flight.Mystic_Flight_Translocation | endurance_cost | 9.75 | Issue_27_Page_2 | no canonical file matched |
| Power_Bug_Fixes | damage_scale | 1.1818 | Issue_27_Page_4 | no canonical file matched |
| Psionic_Assault | activation_time | 1 | Issue_26_Page_2 | no canonical file matched |
| PvP-Specific_Changes.Other_PvP_Power_Changes.Stalker_Staff_Melee_Sky_Splitter | damage_scale | 2.981 | Issue_27_Page_2 | no canonical file matched |
| Radioactive_Assault | recharge_time | 207.9 | Issue_26_Page_2 | no canonical file matched |
| Savage_Assault | recharge_time | 123.8 | Issue_26_Page_2 | no canonical file matched |
| Savage_Melee_Bug_Sweep.Hemorrhage | damage_scale | 1.17 | Issue_27_Page_3 | ambiguous: 7 canonical files match — needs manual disambiguation. Files: powers\brute_melee\savage_melee\hemorrhage.json; powers\event\labyrinth_corrupted\hemorrhage.json; powers\mission_maker_attacks\savage_melee\hemorrhage.json; powers\mission_maker_secondary\savage_melee\hemorrhage.json; powers\scrapper_melee\savage_melee\hemorrhage.json; powers\stalker_melee\savage_melee\hemorrhage.json; powers\tanker_melee\savage_melee\hemorrhage.json |
| Savage_Melee_Bug_Sweep.Maiming_Slash_Scrapper_only | damage_scale | 1.4188 | Issue_27_Page_3 | no canonical file matched |
| Savage_Melee_Bug_Sweep.Rending_Flurry | endurance_cost | 13.52 | Issue_27_Page_3 | ambiguous: 12 canonical files match — needs manual disambiguation. Files: powers\brute_melee\savage_melee\rending_flurry.json; powers\crey_altruist\altruist_moon_fang_offense\rending_flurry.json; powers\dominator_assault\savage_assault\rending_flurry.json; powers\event\labyrinth_corrupted\rending_flurry.json; powers\hero_corps_sig\feralina\rending_flurry.json; powers\mission_maker_attacks\savage_assault\rending_flurry.json; powers\mission_maker_attacks\savage_melee\rending_flurry.json; powers\mission_maker_secondary\savage_assault\rending_flurry.json; powers\mission_maker_secondary\savage_melee\rending_flurry.json; powers\scrapper_melee\savage_melee\rending_flurry.json; powers\stalker_melee\savage_melee\rending_flurry.json; powers\tanker_melee\savage_melee\rending_flurry.json |
| Savage_Melee_Bug_Sweep.Shred | damage_scale | 0.2991 | Issue_27_Page_3 | ambiguous: 9 canonical files match — needs manual disambiguation. Files: powers\brute_melee\savage_melee\shred.json; powers\crey_altruist\altruist_moon_fang_offense\shred.json; powers\event\labyrinth_corrupted\shred.json; powers\mission_maker_attacks\savage_melee\shred.json; powers\mission_maker_secondary\savage_melee\shred.json; powers\scrapper_melee\savage_melee\shred.json; powers\stalker_melee\savage_melee\shred.json; powers\tanker_melee\savage_melee\shred.json; powers\vahzilok\salamander\shred.json |
| Sentinel_Archetype_Revamp | damage_scale | 1.1 | Issue_27_Page_5 | no canonical file matched |
| Shadow_Maul | activation_time | 2.35 | Issue_26_Page_5 | no canonical file matched |
| Shadow_Maul | arc | 120 | Issue_26_Page_5 | no canonical file matched |
| Shadow_Maul | max_targets_hit | 10 | Issue_26_Page_5 | no canonical file matched |
| Shadow_Maul | recharge_time | 11 | Issue_26_Page_5 | no canonical file matched |
| Stalker_Crit_Consistency_Pass.Staff_Fighting.Guarded_Spin | damage_scale | 1.2085 | Issue_27_Page_2 | canonical file powers\stalker_melee\staff_fighting\guarded_spin.json has no field 'damage_scale' |
| Story_Arcs | duration | 18 | Issue_27_Page_1 | no canonical file matched |
| Tanker.Dark_Melee.Shadwo_Maul | max_targets_hit | 10 | Issue_26_Page_4 | no canonical file matched |
| Tanker.Dual_Blades.One_Thousand_Cuts | max_targets_hit | 16 | Issue_26_Page_4 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\mission_maker_attacks\dual_blades\one_thousand_cuts.json; powers\mission_maker_secondary\dual_blades\one_thousand_cuts.json |
| Tanker.Dual_Blades.Sweeping_Strike | max_targets_hit | 10 | Issue_26_Page_4 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\mission_maker_attacks\dual_blades\sweeping_strike.json; powers\mission_maker_secondary\dual_blades\sweeping_strike.json |
| Tanker.Dual_Blades.Typhoons_Edge | max_targets_hit | 16 | Issue_26_Page_4 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\mission_maker_attacks\dual_blades\typhoons_edge.json; powers\mission_maker_secondary\dual_blades\typhoons_edge.json |
| Tanker.Katana.Flashing_Steel | max_targets_hit | 10 | Issue_26_Page_4 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\mission_maker_attacks\katana\flashing_steel.json; powers\mission_maker_secondary\katana\flashing_steel.json |
| Tanker.Katana.Golden_Dragonfly | max_targets_hit | 10 | Issue_26_Page_4 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\mission_maker_attacks\katana\golden_dragonfly.json; powers\mission_maker_secondary\katana\golden_dragonfly.json |
| Tanker.Katana.The_Lotus_Drops | max_targets_hit | 16 | Issue_26_Page_4 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\mission_maker_attacks\katana\the_lotus_drops.json; powers\mission_maker_secondary\katana\the_lotus_drops.json |
| Tanker.Kinetic_Melee.Burst | max_targets_hit | 16 | Issue_26_Page_4 | ambiguous: 57 canonical files match — needs manual disambiguation. Files: powers\arachnos_soldiers\arachnos_soldier\burst.json; powers\blackwingindustries\neutralizer\burst.json; powers\blaster_ranged\assault_rifle\burst.json; powers\brute_melee\kinetic_attack\burst.json; powers\corruptor_ranged\assault_rifle\burst.json; powers\crey_altruist\altruist_siberian_punk_offense\burst.json; powers\defender_ranged\assault_rifle\burst.json; powers\dominator_assault\arsenal_assault\burst.json; powers\family\assaultrifle_mn\burst.json; powers\family\family_tommy_gun\burst.json; powers\family\family_tommy_gun_lt\burst.json; powers\freaklok\idx\burst.json; powers\freaklok\virus\burst.json; powers\incarnate\lore_pet_longbow_lt\burst.json; powers\incarnate\lore_pet_vanguard_lt\burst.json; powers\mastermind_pets\commando\burst.json; powers\mastermind_pets\thug_lt\burst.json; powers\mastermind_summon\mercenaries\burst.json; powers\mission_maker_attacks\arsenal_assault\burst.json; powers\mission_maker_attacks\assault_rifle\burst.json; powers\mission_maker_attacks\kinetic_attack\burst.json; powers\mission_maker_attacks\mercenaries\burst.json; powers\mission_maker_pets\commando\burst.json; powers\mission_maker_secondary\arsenal_assault\burst.json; powers\mission_maker_secondary\assault_rifle\burst.json; powers\mission_maker_secondary\kinetic_attack\burst.json; powers\praetorianidf\trooper_elite_boss_missile\burst.json; powers\praetorianresistance\minion\burst.json; powers\praetorianresistance\minion_low\burst.json; powers\praetorianresistance\minion_low_tutorial\burst.json; powers\scrapper_melee\kinetic_attack\burst.json; powers\sentinel_ranged\assault_rifle\burst.json; powers\skulls\skulls_lt_assaultrifle\burst.json; powers\stalker_melee\kinetic_attack\burst.json; powers\syndicate\minion_burst\burst.json; powers\tanker_melee\kinetic_attack\burst.json; powers\tsoo\chi_master\burst.json; powers\tsoo\endgame_bs_kinetic\burst.json; powers\tsoo\riverdragon\burst.json; powers\tsoo\tsoo_brown_ink_melee\burst.json; powers\vanguard\gaussian\burst.json; powers\vanguard\sr71_rifle\burst.json; powers\v_arachnos\wolf_spider_submachinegun\burst.json; powers\v_arachnos_proxy\arachnos_soldier_proxy\burst.json; powers\v_arachnos_proxy\arsenal_assault\burst.json; powers\v_freedomcorps\nullifier\burst.json; powers\v_freedomcorps\sargeant\burst.json; powers\v_genericvillains\assault_rifle_corruptor\burst.json; powers\v_miscellaneous\keith_nance\burst.json; powers\v_mooks\boss_capo_low\burst.json; powers\v_mooks\minion_gunner\burst.json; powers\v_paragonpolice\police_assault_rifle_2\burst.json; powers\v_paragonpolice\police_submachinegun\burst.json; powers\v_security_guards\security_guard_advanced_assaultrifle_boss\burst.json; powers\v_security_guards\security_guard_advanced_submachinegun\burst.json; powers\v_security_guards\security_guard_assaultrifle_boss\burst.json; powers\v_security_guards\security_guard_submachinegun\burst.json |
| Tanker.Kinetic_Melee.Repulsing_Torrent | max_targets_hit | 16 | Issue_26_Page_4 | ambiguous: 15 canonical files match — needs manual disambiguation. Files: powers\brute_melee\kinetic_attack\repulsing_torrent.json; powers\crey\revenant_bioranger_backupb\repulsing_torrent.json; powers\crey_altruist\altruist_siberian_punk_offense\repulsing_torrent.json; powers\freaklok\bigfreak\repulsing_torrent.json; powers\mission_maker_attacks\kinetic_attack\repulsing_torrent.json; powers\mission_maker_secondary\kinetic_attack\repulsing_torrent.json; powers\mission_pets\drtodd_high\repulsing_torrent.json; powers\praetorianpolice\zane\repulsing_torrent.json; powers\scrapper_melee\kinetic_attack\repulsing_torrent.json; powers\summerevent\mrdubois\repulsing_torrent.json; powers\tanker_melee\kinetic_attack\repulsing_torrent.json; powers\tsoo\chi_master\repulsing_torrent.json; powers\tsoo\endgame_bs_kinetic\repulsing_torrent.json; powers\tsoo\endgame_bs_sorcerer\repulsing_torrent.json; powers\tsoo\riverdragon\repulsing_torrent.json |
| Tanker.Street_Justice.Spinning_Strike | max_targets_hit | 16 | Issue_26_Page_4 | ambiguous: 10 canonical files match — needs manual disambiguation. Files: powers\blackwingindustries\commander\spinning_strike.json; powers\brute_melee\brawling\spinning_strike.json; powers\crey\hopkins_melee_missions\spinning_strike.json; powers\mission_maker_attacks\brawling\spinning_strike.json; powers\mission_maker_secondary\brawling\spinning_strike.json; powers\scrapper_melee\brawling\spinning_strike.json; powers\stalker_melee\brawling\spinning_strike.json; powers\tanker_melee\brawling\spinning_strike.json; powers\v_arachnos_proxy\brawling\spinning_strike.json; powers\warriors_new\warrior_brawl_lt\spinning_strike.json |
| Tanker.Street_Justice.Sweeping_Cross | max_targets_hit | 10 | Issue_26_Page_4 | ambiguous: 9 canonical files match — needs manual disambiguation. Files: powers\brute_melee\brawling\sweeping_cross.json; powers\crey_altruist\altruist_shining_diamond_offense\sweeping_cross.json; powers\mission_maker_attacks\brawling\sweeping_cross.json; powers\mission_maker_secondary\brawling\sweeping_cross.json; powers\scrapper_melee\brawling\sweeping_cross.json; powers\stalker_melee\brawling\sweeping_cross.json; powers\tanker_melee\brawling\sweeping_cross.json; powers\v_arachnos_proxy\brawling\sweeping_cross.json; powers\warriors_new\warrior_brawl_minion\sweeping_cross.json |
| Tanker.Titan_Weapons.Whirling_Smash | max_targets_hit | 16 | Issue_26_Page_4 | ambiguous: 2 canonical files match — needs manual disambiguation. Files: powers\mission_maker_attacks\titan_weapons\whirling_smash.json; powers\mission_maker_secondary\titan_weapons\whirling_smash.json |
| Thorny_Assault | activation_time | 10 | Issue_26_Page_2 | no canonical file matched |
| Thorny_Assault | recharge_time | 18 | Issue_26_Page_2 | no canonical file matched |
| Thunder_Strike_consistency_pass | endurance_cost | 18.512 | Issue_27_Page_7 | no canonical file matched |
| Travel_Power_Updates.Sorcery_Pool.Mystic_Flight.Mystic_Flight_Translocation | endurance_cost | 9.75 | Issue_27_Page_2 | no canonical file matched |

## Resolution rule (escalation)

- When override and canonical agree → no action.
- When they disagree → the **override wins**; the canonical zip is older than
  the patch. Per-power detail in data/diff/powers/<entity>.<field>.md.
- When unresolved → the override entity name didn't map to a canonical file.
  Likely causes: (a) patch refers to an inherent or non-power feature
  (e.g. "Tanker_AT_inherent_changes"), (b) parsed entity prefix is a date or
  section heading that wasn't filtered out, (c) typo in the patch notes
  (e.g. "Shadwo Maul" misspelled). Walk the unresolved list and fix tools/
  parse-patches.ps1's Build-EntityPath skip list, or add manual aliases.
