---
title: "Procs Per Minute (PPM) Information Guide"
url: "https://forums.homecomingservers.com/topic/5290-procs-per-minute-ppm-information-guide/"
source: "forums.homecomingservers.com"
authors: ["Bopper"]
date_posted: "2019-06-27"
date_captured: "2026-04-27"
captured_by: "local-capture"
topic_tags: ["procs", "ppm", "mechanics", "enhancements", "guide"]
trust: community-consensus
contradicts_data: "none"
---

# Procs Per Minute (PPM) Information Guide

## Summary

- For click powers, proc probability = PPM _ (MRT + CastTime) / (60 _ AreaMod), where MRT uses only enhancement/Alpha recharge — global recharge buffs (Hasten, set bonuses, team buffs) do NOT reduce MRT for proc calculations.
- For toggles, autos, and pseudopets, proc probability = PPM _ ActivatePeriod / (60 _ AreaMod), where ActivatePeriod is the enhancement's 10-second pulse, not the power's tick rate.
- Proc probability is clamped to a maximum of 90% and a minimum of 5% + PPM \* 1.5%, preserving randomness while protecting AoE procs from being over-penalized.
- AreaMod = 0.25 + 0.75 \* AF dampens the original Area Factor punishment introduced in i24; cone radius equals the power's base range and is not affected by range enhancement.
- Adding a small amount of enhanced recharge to a proc power causes a steep early drop in proc probability (hitting ~80% probability around 30% enhancement), so builders should generally either skip recharge slotting in proc powers or commit fully and accept diminishing returns.

## Verbatim excerpt

Procs Per Minute (PPM) Information Guide by Bopper. Written: 9 August 2019. Last updated: 16 August 2019. (Information that might help new players in understanding the PPM game mechanics)

Update (9 August 2019): This thread has adapted quite a bit since I first put the call out for Testers to determine how the PPM mechanics actually work and to clear up the confusion from outdated resources (love you Paragon Wiki, but you're i23, and we've moved on). Since then a lot of good information was discovered and plenty of mechanics have been confirmed.

PPM Formulas — Breakdown of Formulas:

For Click Type Powers: Probability to Proc = PPM _ (MRT + CastTime) / (60 _ AreaMod)

For all other Powers (Toggles, Auto, Pseudopets?): Probability to Proc = PPM _ ActivatePeriod / (60 _ AreaMod). _Note_ This is not the ActivatePeriod of the power, it is the ActivatePeriod of the Proc Enhancement which seems to always be 10 seconds.

Modified Recharge Time: MRT = BaseRecharge / (1 + RechargeBoost_from_Enhancements_and_Alpha / 100). _Note_ The MRT is not affected by outside global recharge boosts, such as Hasten, Set IO bonuses, team buffs, etc.

Area Modifier: AreaMod = 0.25 + 0.75 * AF. *Note\* This is a dampening effect Phil "Synapse" incorporated for i24. He felt the game's Area Factor punished procs too much.

Area Factor:

- Single Target: AF = 1
- Sphere (PBAoE or Target AoE): AF = 1 + 0.15 \* Radius
- Cone: AF = 1 + 0.15 _ Radius - 0.011 _ Radius x (360 - Arc) / 30. _Note_ The original Range of a Cone Attack is considered the Radius. Enhancing the Range will not change the Radius, thus will not affect the proc probability.
- Chain: AF = 1 + 0.75 * MaxTargetsHit. *Note\* I have yet to find a power in the game that is tagged as a kEffectArea_Chain that would use this Area Factor.

One Formula to Rule them All (Except Chain): AF = 1 + Radius x (11 \* Arc + 540) / 30,000. For Single Target use Radius = 0. For Sphere use Arc = 360.

Maximum Probability to Proc: MaxProb = 0.90 (90%). Minimum Probability to Proc: MinProb = 0.05 + 0.015 \* PPM (5% + PPM x 1.5%).

Scope: The purpose of this guide is to clear up the PPM mechanics that are used in i25+, which incorporated changes made in i24 Beta but never made it to Live. Most of the information in this guide comes from reviewing the original forum posts discussing this topic (Phil "Synapse," circa April of 2012), extensive testing used to confirm the proposals made in the forum discussion, and reviewing source code by the SCoRE team which further confirmed these formulas.

Background: A "Proc" is a procedure that has a chance of happening. Every time you hit a target (self, ally or enemy) with a power slotted with a Proc enhancement, the effect of the Proc has a chance to trigger.

History: Basically, prior to i21 almost all Proc enhancements worked as a fixed percentage. This allowed for many exploits such as slotting AoE powers with a high tick rate to "buzzsaw" enemies. Then sometime in the i21 timeframe, the game introduced Archetype Origin enhancements (ATOs) which introduced the new Procs Per Minute (PPM) mechanic, which used base recharge, area factor, and cast time to calculate the probability of a proc triggering its effect. Finally, in i23, the original Proc enhancements had their fixed percentage mechanics replaced with PPM. Due to exploits that could be achieved with the PPM mechanics (100% Proc probabilities, increased Proc rates using extremely high recharge builds, etc.), the devs decided to retune the PPM mechanic such that it used global recharge instead of base recharge and cap the probability to Proc at 90%. There was an obvious outcry as this unfairly punished players who built high-recharge characters. After much discussion with players, the devs came to a compromise and decided to only use the enhanced recharge (recharge buffs from enhancements or the Agility/Spiritual Alpha incarnates). The devs also compromised by incorporating a minimum Proc probability of at least 5% and dampened the negative effects of Area Factor so that AoE powers are not too severely punished. This was all incorporated into the i24 Beta when the game abruptly shut down.

PPM Mechanics — Procs Per Minute (PPM): PPM is roughly the average number of times per minute an effect from a Proc should fire. Each Proc enhancement will list this number in its description info and is used directly in calculating the Proc's probability to trigger.

Modified Recharge Time (MRT): MRT is the power's actual recharge time when no global recharge boosts are present. If you're not sure what your MRT is, you can check this in the game. Just right-click on the power, select "info," and see what is listed as the recharge time. This recharge time will incorporate the recharge enhancements and alpha enhancements installed in the power, after enhancement diversification is factored in (again, global recharge boosts will not affect this).

Example table — Base 10s recharge: with 0% enh/0% global → Actual 10s, MRT 10s; with 0% enh/100% global → Actual 5s, MRT 10s; with 114% enh/0% global → Actual 4.67s, MRT 4.67s; with 114% enh/100% global → Actual 3.18s, MRT 4.67s. As we can see, the global recharge bonus has no effect on the modified recharge time. If your build already has managed high global recharge, you might be better off not slotting any recharge enhancements into your Proc powers as your actual recharge time will not decrease by much but your Proc performance can greatly decrease due to the significant decrease in MRT.

Activation Period (ActivatePeriod): Activation Period is the time between when the effects of an ENHANCEMENT trigger. The Activation Period has nothing to do with the power itself, but rather how the enhancement functions. When an enhancement is slotted, its effects trigger every 10 seconds (this is the ActivatePeriod) and those effects will last a duration of 10.25 seconds. A change was made that resulted in powers such as toggles, autos, etc would only have the Procs pulse once every 10 seconds, by using the enhancement's activation period.

The Proc can only trigger when the power ticks, but will still be able to trigger once in every 10 second interval. World of Confusion has an Activate Period of 4 seconds, so when you cast it, it will tick at 0, 4, 8, 12, 16, 20 sec, etc. Even though the time between the 2nd and 3rd proc is only 8 seconds, they fall into different 10 second intervals (0-9.9, 10-19.9, 20-29.9). When you attempt to calculate your Proc rates with toggles you can expect on average one Proc opportunity per 10 seconds.

Area Modifier (AreaMod): AreaMod is an unofficial term used to help distinguish itself from Area Factor, which is used in the game for things outside of PPM mechanics. AreaMod is the new Area Factor for PPM calculations, which uses the 0.75 weight to dampen the effects on Proc probabilities (per Synapse's design). It's worth noting the AreaMod (and the Area Factor that feeds into it) is entirely dependent on the area of effect of the power, and has no dependence on the maximum number of targets the power can hit.

Area Factor (AF) — Single Target: always 1. Sphere: applies to any non-cone AoE centered on a location (self, target, or patch). Cone: always less than its Sphere counterpart for the same radius, since a cone has less than 360 degree coverage. For ranged cone powers, the radius is always equal to the base range of the power (enhancing the range will not change the radius, so no impact on PPM calculations). Chain: depends entirely on the maximum number of targets it can hit. As of 14 Aug 2019, only Refractor Beam (Sentinel, Beam Rifle) and Rehabilitating Circuit (Sentinel, Electric Mastery) might be tagged with kEffectArea_Chain. If Trick Shot becomes a Chain Attack with a maximum of 10 targets, its AreaMod would be 6.625 — equivalent to a Sphere attack with a 50 foot radius. The dev team will seriously need to tweak the Chain - AF formula for it to become viable for Proc usage.

FAQ 1 — How much enhanced recharge can I put into a click-power and still achieve the maximum 90% Proc probability? If the Proc has a greater than 90% probability to Proc without enhancement, you can calculate the maximum allowed enhanced recharge using the derived formula.

FAQ 2 — What is the impact of adding just a little bit of recharge enhancement into my click-power? A lot, actually. MRT will decay rapidly with just a little added recharge enhancement, then will slow its decay rate as it approaches its CastTime limit. In each example you hit the 80% mark very quickly (~30% enhancement), but the 60% mark is not hit until much later (approximately triple the 80% mark's enhancement value). The lesson here is to either go all in on not adding enhanced recharge, or put as much recharge as you want knowing that the drop off in Proc probability will have diminishing returns. If you are over the maximum probability (90%) you should go ahead and add enhanced recharge up to that limit (in one example, 48% enhanced recharge still kept the 90% Proc probability). The goal is to maximize Proc rate (Procs per minute), which is a function of Proc probability (requires recharge to be minimized) and Proc opportunity rate (requires recharge to be maximized). There is a balance between Proc probability and opportunity rate that can be calculated using simple calculus.

Update History (selected):

- Update 1: Improving Range for Cones (via Enhancement or Boost) has NO IMPACT on proc performance.
- Update 3: Max probability is confirmed at 90%. Minimum probability is confirmed at 5% + PPM x 1.5%.
- Update 7: Corrected misinformation in the ActivatePeriod section. Testing showed Procs in toggles can trigger once per 10 second intervals, but are not required to wait 10 seconds between Procs (16 Aug 2019).

Edited August 3, 2020 by Bopper.
