---
title: "+HP/+Regen Proc Cheat Sheet"
url: https://forums.homecomingservers.com/topic/19022-hpregen-proc-cheat-sheet/
source: forums.homecomingservers.com
authors: [Bopper]
date_posted: 2020-05-11
date_captured: 2026-04-27
captured_by: local-capture
topic_tags: [procs, regeneration, slotting, mechanics, ios]
trust: community-consensus
multi_post: true
post_count: 17
contradicts_data: none
---

## Summary

- The two staple +HP procs work on different scales: **Power Transfer (PT) Chance to Heal** = 5% of your AT's _base_ HP (so it favors high-base-HP ATs like Tanker/Brute), while **Panacea Chance for +Hit Points/Endurance** = 6.7% heal driven by the Heal_Other_Melee modifier table off general base AT HP (1070.9 HP), which makes it strongest on high-heal-mod ATs like Defenders. Both are 3 PPM, so in an auto power they average ~1 proc per 20s.
- The cheat-sheet charts compare every +HP and +Regen proc (PT, Panacea, Regenerative Tissue +25%, Impervious Skin +25%, Numina's Convalescence +20%) on a 20-second-window basis. Each AT has both a "base HP" and "max HP" column, since +Regen procs scale with your _current_ max HP and +HP procs do not. Green = best return; red = the rare cases where a +25% Regen IO beats a +HP proc.
- Power Transfer's "once per cast" mechanic was originally synchronized across auto powers, so multiple PT procs slotted in different autos cancelled each other down to one proc per tick. **Update from page 2 of the thread (2023-12-03):** this has since been fixed — different auto powers now stack PT procs independently. Comments earlier in the thread describing PT collisions are outdated.
- Panacea, Numina, etc. _never_ interfered with each other or with PT; only PT vs PT had the synchronization issue. Panacea is also bugged in AoEs (only fires on the caster as if a single-target heal), which makes Health the canonical slot for Panacea on most builds.
- VEATs have base Regen 0.30 and base Recovery 1.05 (vs. 0.25 / 1.00 for everyone else), which manifests as **5% HP every 10s** (not 12s) and an Endurance tick every **3.81s** (not 4s). Bopper updated the charts on 2020-09-02 to reflect this Conditioning inherent for VEATs.

## Verbatim excerpt

### Post 1 — Section: OP / Cheat Sheet (2020-05-11, last edited 2023-10-02)

Since Power Transfer was introduced with its 3 PPM chance at +5% HP, there has been discussion on which is better Panacea or PT? The answer is, it depends. They work very differently from one another, as PT's heal is 5% of your AT's base hit points (so it will benefit Tankers/Brutes more) whereas Panacea does a 6.7% heal of the general base AT hit points (1070.9 HP) using the Heal Other - Melee modifier (so it benefits Defenders the most).

Some things to note:

- Power Transfer is mechanized to proc only once per cast. However, this functionality appears to actually only proc once at an instance of time. So with an AoE attack, this works as intended: multiple procs from multiple hit targets get reduced to 1 proc as all those multiple procs try to resolve at the same time. However, there are consequences with this mechanic, as you could slot Power Transfer into multiple Auto powers (Stamina, Physical Perfection, Superior Conditioning, …) and because all auto powers proc-tick at the same time, only one Power Transfer proc will fire even though all of them tried at the same time. [Subsequently corrected in 2023 — see Post 17.]
- Auto-power sync also previously meant teleport jumps were treated as separate casts. (This was fixed awhile ago.)
- The +Regeneration procs in the chart are the Regenerative Tissue +25%, Impervious Skin +25%, and Numina's Convalescence +20%.
- This chart will show the amount of HP received from a +HP proc, however +Regeneration works very differently (you get back 5% of your total HP faster, as opposed to getting back a fixed HP at a fixed time-interval/cast). So I scaled the +Regen procs to show the amount of additional HP received in a 20 second interval. I chose this duration because if you slot a +HP proc into an auto power, it will average 1 proc per 20 seconds (both Panacea and P.T. are 3 PPM).
- Also for +Regen procs, I show the amount of HP per 20 seconds for both the base HP and the max HP for each AT. Since regeneration works off your total hit points, whereas the +HP procs do not, I chose to show the range of values for the +Regen procs.
- I highlighted in green which proc is the most effective.

[Original chart image embedded.]

I showed the equivalent HP per 20 seconds from adding a +Regeneration IO as a means of directly comparing it to the Power Transfer and Panacea procs (the procs fire on average once every 20 seconds in auto powers). I have updated the table to now also show the reverse of that, making the Power Transfer and Panacea procs equivalent to added regeneration. I hope this puts into context how strong these procs can be under various levels of total Hit Points. I highlighted in green whichever IO provided the best return (most HP over time). I highlighted in red the lone exceptions/scenarios where a +HP proc is not superior to a 25% regeneration IO.

[Equivalent-regen chart image embedded.]

**Update 02 September 2020:** Corrected the charts to properly calculate the equivalent values for VEATs. Previous charts did not reflect their Conditioning Inherent.

_(Edited October 2, 2023 by Bopper — "Corrections to Arachnos")_

### Post 2 — Section: Panacea is bugged in AoEs (2020-05-11)

Agreed, but until recently I might have argued the "best to slot for health" claim. For 95% of the time, that is a very true statement, however slotting it in a power like Dark Regeneration or DNA Siphon was awesome. But recently (likely around the time of introducing the PT proc and tweaking how Call of the Sandman only proc'd once per cast), the Panacea stopped procing in those AoE powers. Very frustrating. So now that Panacea is bugged in AoEs, I have to say you are 100% right that its best in Health (well…99% perhaps, there might be other cases I'm not thinking of).

### Post 3 — Section: PT is the only proc with auto-power interference (2020-05-11)

[Re: does Performance Shifter slotted alongside Power Transfer in the same auto reduce PT proc rate?] Only Power Transfer.

Edit: by only power transfer, I meant only power transfer has this effect and its against itself. Other procs (not called power transfer) have no effect.

### Post 4 — Section: Why PT collides with itself, and only itself (2020-05-11)

The only proc that has diminished returns in auto powers is Power Transfer when there are other Power Transfers slotted. All other procs/IOs have no impact on Power Transfer's proc.

The only other known procs that only can proc once per cast are Force Feedback (which doesn't get slotted into an auto) and Call of the Sandman (which doesn't get slotted into an auto). So the behavior I described is strictly a Power Transfer concern, as it also only can proc once per cast, but because auto powers are synchronized with proc ticks, the other autos are effectively being treated as the same cast (thus up to only one proc can trigger).

Slot as many Performance Shifters as you want, they can't hurt you.

### Post 5 — Section: PT in click powers vs. autos (2020-05-12)

[Re: PT in Conserve Power / Consume / Victory Rush] Conserve Power, Energize and other endurance discount powers don't take endurance modification IOs, so Power Transfer can't be slotted. Consume will only proc Power Transfer up to one time on one cast. But the chance to proc is still checked on each target hit, so you greatly increase your chance of getting that one PT proc. I don't know Victory Rush's mechanics intimately, but I suspect it would trigger only once with PT proc.

If anyone is familiar with how Force Feedback works, Power Transfer works the same way (procs only once per cast). It truly is the silliness/bug of autopowers being synchronized causing only one PT proc to fire between all the auto powers at a single instance of time. If the proc was working as intended, the chance to proc between all auto powers would be independent and you could get multiple PT procs during each auto proc tick chance. Until that's fixed, just know autopowers are being treated as one cast of PT, thus only one PT can proc (but with better reliability because you have more autopowers with a chance to proc — it requires all to miss for the proc to not fire).

### Post 6 — Section: How many PT procs in autos is worth it (2020-05-12)

I think it was an effect of the coding process. Maybe this is how other "one proc only" procs work and this is the first time we've seen the effects of that type of proc in an auto. Perhaps there are toggles that do knockback that could stack, and maybe we'd see dampened effects with multiple force feedback, but that would be a very niche situation.

Overall, I'd probably only slot one in an auto…2 at most if there's room. There are cases where even having half the expected value of PT still compares well to slotting up Health for regen. In the end, though, I think an electric armor tank would leverage the proc the best since its Lightning Field could easily become asynchronized with an auto by re-toggling it whenever you zone in.

Or — if you want to be a psychopath — you could unslot and reslot the PT proc in an auto every time you load into a new map. You'll make the asynchronized and get the full 3 PPM benefits once again — until your next map load. I don't advise this for anyone, I'm only providing silly game mechanics people could consider.

### Post 7 — Section: Equivalent-regeneration chart added (2020-05-27)

Added new chart to reflect what the +HP proc's equivalent regeneration is as an easy comparison to +Regeneration IOs. This isn't new findings, just a new way of comparing.

### Post 8 — Section: VEAT base regen question (2020-08-22)

[Re: macskull's note that Corruptors / HEATs / VEATs share base HP but VEATs have higher base regen] I'm unfamiliar with VEATS so can you explain the impact of higher base regeneration? For example, if VEATs have a base of 150% regeneration, and you get a set bonus of 10% regeneration, does that set bonus have a different Healing per Second impact than another AT that also has a 10% regeneration set bonus?

### Post 9 — Section: VEAT Conditioning confirmed (2020-08-22)

Thank you, and thank you @macskull for bringing this to my attention. I did see that typical ATs have a Base Regen of 0.25 and Base Recovery of 1.00, while VEATs have a Base Regen of 0.30 and Base Recovery of 1.05. I wasn't sure if this meant VEATs at base would be 5% of their HP every 10 seconds or if it meant they get 6% of their HP every 12 seconds. Thanks for clarifying that for me. I'll update this chart (and my Survivor Tool) with this information soon.

### Post 10 — Section: 4-PT-in-autos question (2020-08-28)

[Re: does the cheat sheet account for stacking 4 PT procs across autos giving ~97% chance of a proc every 10s?] It does not.

### Post 11 — Section: VEAT chart corrections shipped (2020-09-02)

Finally got around to correcting the charts. I did test it out and it showed Arachnos still have their regeneration ticks do 5% HP and their recovery ticks do 1/15th Endurance. So Conditioning does in fact increase the base frequency of regeneration/recovery ticks. In this case, the base regeneration for VEATS is 10s (instead of 12s), and the base recovery is 3.81s (instead of 4s).

### Post 12 — Section: Multi-proc / multi-set behavior FAQ (2020-10-06)

1. You will be fine. The only proc that has the weird mechanics due to auto/toggle powers synching up is Power Transfer because that proc is specifically mechanized to only proc once when cast. For whatever reason, that mechanization is causing it to not proc more than once despite the fact you have the proc slotted in different powers. So do not worry about your Panacea or other procs, this is a Power Transfer proc problem only.

2. Nothing happens. It works as you would expect. All procs working independently of each other with no negative effects.

3. Only interferes with each other. The only other proc I know of that would act this way would be Call of the Sandman, but I am unfamiliar with any character being able to slot two auto/toggle sleep powers.

### Post 13 — Section: +Regen proc independence from +Regen power buffs (2021-04-13)

Added Regeneration is independent. So using a +regen power will not change the contribution that you get from the Regeneration proc. The only thing that changes your performance is a change in your max HP. If your max HP goes up or down, the HP/sec that you get from the Regeneration proc will go up or down with it.

### Post 14 — Section: Panacea in Triage Beacon / pseudopet auras (2021-04-14)

Panacea will have a chance to proc on any ally the power affects, so you seeing teammates and pets being beneficiaries makes complete sense.

First, a breakdown of the power. It has a 200s base cooldown and when cast it summons a pseudopet. That pseudopet lasts for 90s and has a 40 foot radius.

For the pseudopet, the large radius floors your proc probability to 9.5%. However, you can hit up to 255 targets in that 40 ft radius, so you certainly have enough chances to see it fire on somebody. Plus, it lasts 90s, so you get 9 proc chances with one summon (0s, 10s, 20s, …80s. You don't get one at 90s because it will die off just before another proc chance).

On top of the pet proc'ing, I suspect summoning the pet will also have a chance to proc on you. This is the part that I would need to test to confirm, but I wouldn't be surprised if there is a 90% chance to proc on yourself everytime you summon the pet.

_(See @UberGuy's correction in Notable replies — pet-aura procs use the proc's own activation period and the area factor, not Triage Beacon's recharge/cast time.)_

### Post 15 — Section: PT FAQ + how to compute equivalent regen for your max HP (2021-11-13)

1. Does PT:CHS use Base HP or Max HP? **Base HP.**

2. Can the effect be stacked with itself using different powers that aren't auto powers? Yes. They now can also stack from different powers that are auto powers. **That was a bug fix introduced sometime this year.**

3. Can the effect be stacked with other Chance to Heal Self procs (e.g. Entropic Chaos: Chance to Heal Self in the same power)? **Yes.**

[Re: when would you slot this kind of proc?] For Auto Powers: If the equivalent regeneration of the PT:CHS is more than what slotting a Heal IO into another auto-power would offer. In the cheat sheet I show the "equivalent regeneration" for all ATs at both Base HP and Max HP. For your character's current max HP, you'll need to calculate it. Luckily, the relationship is linear, so let's do an example on how to do that.

If you are a Blaster with 1500 HP, your equivalent regeneration of the PT:CHS is 60% at 1204.8 HP and 39.13% at 1847.3 HP. The equivalent regeneration at 1500 HP is:

`ER = 60% + (1500 − 1204.8) × (39.13% − 60%) / (1847.3 − 1204.8)`
`ER = 50.41%`

For Click Powers: This is a huge "it depends." You would have to factor in your probability to hit, probability to proc, and the rate of using your attack. From that you can calculate an average HP/sec which you can translate into an equivalent regeneration.

### Post 16 — Section: Why Panacea is stronger on Defenders than Controllers/Doms despite same base HP (2023-07-09)

Panacea uses the Melee_Heal modifier table, not the Melee_HealSelf modifier table (that uses base HP). Since Defenders have the highest healing modifier, their procs will be stronger than those other ATs.

### Post 17 — Section: Converting clickies (e.g. Siphon Life) into regen-equivalents + PT collision is fixed (2023-12-02 / 2023-12-03)

The best way to come up with a formula is start somewhere that has all the variables you'd need. Let's start with Siphon Life unenhanced.

Siphon Life heals 10% of base HP at the time of the power's use. Siphon Life has a 10s cooldown and 1.93s cast time. For argument's sake, let's assume you slotted the power with a healing SO and two recharge SOs, that puts us at 33.3% heal strength and 66.6% cooldown reduction. That gives us a heal amount that is 13.33% of base HP and a cooldown of 6s. Combined with the cast time, that gives us a cycle time of 6s + 1.93s = 7.93s.

So in this example, we're looking at Siphon Life doing 13.33% base HP every 7.93s.

What is that in terms of regeneration? Well this now depends on what your Max HP is, because regen works off max HP (self heals work off of base HP, as shown previously). Let's assume you have raised your max HP by 50%, so your max HP = 1.5 × base HP. Knowing that 100% regeneration (base regen rate) gives you 5% of your max HP every 12s, we can state 100% regen = 5% × 1.5 × base HP every 12s.

So what is Siphon Life in terms of Regeneration in this specific example?

`Siphon Life = 13.33% base HP every 7.93s = X% regen = X% × (5% × 1.5 × base HP every 12s)`
`(13.33% × base HP / 7.93s) / (5% × 1.5 × base HP / 12s) = X%`
`(13.33 × 12) / (7.93 × 5 × 1.5) = 159.96 / 59.475 = 2.69 = 269%`

So there is a way to convert Siphon Life into terms of regeneration equivalency, but it depends on what your max HP is, how much heal your Siphon Life is doing (relative to base HP), and how often you're casting Siphon Life.

There is one thing I did not include in the calculation that is worth noting. I assumed Siphon Life hit. If you factor in your chance to hit, you can simply scale from there. Let's say you had a 90% chance to hit, then your regeneration equivalency would be 0.90 × 269% = 242%.

[Follow-up, 2023-12-03] **There is no longer a conflict.** I think I updated the original post with that detail, but comments in the thread may be outdated.

## Notable replies

- **@macskull (page 1, 2020-08-22):** Flagged that Corruptors / HEATs / VEATs share base HP but VEATs' Conditioning gives them a higher base regen rate, which means the +Regen-proc rows in the original chart were slightly understated for VEATs. This is what triggered Bopper's Posts 9 and 11 (chart corrections shipped 2020-09-02).
- **@Gulbasaur (page 1, 2020-08-22):** Confirmed VEAT Conditioning is a base-rate multiplier and pointed at @Vanden's earlier endurance breakdown. Their clarification — "5% every 12s base, but VEATs regen 6% every 12s without factoring in Health" — let Bopper resolve the ambiguity into the canonical "VEATs tick every 10s" finding.
- **@Sir Myshkin (page 1, 2020-05-12):** Reported limited testing showing multiple PT-slotted autos still produced more procs than a single one (just not 3×), and floated the design idea that "limited-style trigger locks" could be a deliberate dev tool for proc balancing. Codifies the practical takeaway that Bopper formalizes in Post 6: 1 PT in an auto is the safe choice, 2 only if slots are free.
- **@Arbegla (page 2, 2021-04-14):** Asked about Panacea in Triage Beacon, reporting independent proc chances per affected target every ~10s plus heals on pets and teammates. This prompted Bopper's Post 14 on pseudopet aura mechanics.
- **@UberGuy (page 2, 2021-04-15) — materially correcting the pet-aura PPM math:** "That's not how PPM procs work in effects like this. This is the Triage Beacon pet's regen aura power. PPM code looks at the activation period of the power. A value > 0 on the power is something that only passive/auto and toggle powers have. In powers with a non-zero activation period, the proc activation chance calculation fully ignores recharge and cast times. It's based instead on the proc (enhancement's own) activation period alone, which is usually 10s. (And the power's area factor, of course.) I'm pretty sure procs like this can activate on you directly when you summon the pet, and that will use the cast and activation time math for PPM chance of happening." Important correction to Bopper's Post 14 — for the _aura_ portion of Triage Beacon (and other pseudopet healing auras), proc chance is driven by the proc's own activation period (typically 10s) and the power's area factor, _not_ by the parent power's recharge/cast time. The summon-tick on the caster is a separate event that does follow the standard PPM cast/activation math.
- **@Glacier Peak (page 2, 2021-11-13):** Asked the four canonical PT:CHS questions — Base vs Max HP, stacks across non-auto powers, stacks with other Chance-to-Heal-Self procs (e.g. Entropic Chaos in the same Zapping Bolt slot), and what scenarios make PT:CHS worth a slot at all. Bopper's reply (Post 15) is the canonical answer set: Base HP; Yes; Yes; and use the linear interpolation formula on the cheat-sheet's Base-HP / Max-HP columns to decide whether PT:CHS beats a flat Heal IO at _your_ current max HP.
- **@Story Archer (page 2, 2023-11-30 → 2023-12-03):** Asked for a way to convert clicky self-heals like Siphon Life into a regen-equivalency for direct comparison, and separately whether stacking a Power Transfer + Performance Shifter in Quick Recovery and again in Stamina (alongside Panacea in Health and Preventive Medicine in an always-on RtoC) introduced any conflict. Bopper's replies (Post 17) (a) gave the worked Siphon Life example that lets the cheat sheet incorporate self-heal click powers, and (b) confirmed that the PT auto-power collision bug has since been fixed — making earlier Posts 1, 4, 5, 6, and 12 outdated on that point.

## Build attachments

No `.mxd` / DataLink build files were posted. The OP is built around two embedded chart images:

- `image.png.27f504d0852326d13e5f98a75f9e84df.png` — first cheat-sheet chart: HP-per-20-second comparison of Power Transfer, Panacea, Regenerative Tissue +25%, Impervious Skin +25%, and Numina's Convalescence +20% across all ATs (with separate Base-HP and Max-HP columns for the +Regen procs). Green = best return; yellow = next-best.
- `image.png.3d16b2508fc340718fb882543f1184c7.png` — second chart added 2020-05-27, expressing each +HP proc's equivalent +Regeneration % relative to a +25% Regen IO. Green = best return; red = the rare cases where a +25% Regen IO beats the +HP proc.
- VEAT corrections (2020-09-02) and Arachnos corrections (2023-10-02) are baked into the current versions of those two images.
- Companion thread referenced from the OP signature: Bopper's _Survivability Tool_ — `https://forums.homecomingservers.com/topic/12212-the-survivability-tool/` (already captured separately).
