---
title: "Recharge Guide — Everything you need to know about Recharge…and then some"
url: "https://forums.homecomingservers.com/topic/12685-recharge-guide/"
source: "forums.homecomingservers.com"
authors: ["Bopper"]
date_posted: "2019-11-17"
date_captured: "2026-04-27"
captured_by: "local-capture"
topic_tags: ["recharge", "mechanics", "hasten", "force-feedback", "ageless"]
trust: "community-consensus"
multi_post: true
post_count: 9
contradicts_data: "none"
---

# Recharge Guide — Everything you need to know about Recharge…and then some

## Summary

- Recharge calculations involve two time domains: real-world time (what you experience) and cooldown time (what the power experiences). Total cooldown experienced over an interval = total recharge boost in that interval × real-world duration of that interval. A power finishes recharging when accumulated cooldown reaches its base recharge.
- The total recharge cap is 500% (base 100% + boosts up to +400%); when summed boosts exceed that, the cap clips them. The guide breaks the problem into intervals where the active stack is constant, sums cooldown contributions until the base recharge is met, and solves for the unknown final interval.
- Two equivalent solving methods are presented: Time Interval Analysis (Chapters 1–2) splits the timeline by when each boost is active; Recharge Boost Duration Analysis (Chapter 3, Formula 3.2) subtracts each temporary boost × its duration from base recharge and divides by total permanent boosts. Boost-Duration is faster but inaccurate when total boosts exceed 500% during play.
- Practical mental shortcuts: a Force Feedback Proc's 5 seconds at +100% effectively shaves 5 seconds off a power's base recharge; Hasten's 120 seconds at +70% effectively shaves 84 seconds. To compute total permanent recharge, just read enhanced recharge in-game (post-ED) plus global "+Recharge" / "Haste" from Mids' (with Hasten and similar temp boosts off) and add 100%.
- Ageless Destiny's actual structure (per the in-game description) is four stacked boosts: +40% for 10s, +10% for 30s, +10% for 60s, +10% for 120s — which produces the cascade described elsewhere as +70/+30/+20/+10. When you cast Ageless and Hasten back-to-back and the resulting recharge is shorter than a temporary boost's duration, treat that boost as permanent and recalculate (Formula 3.1a iteration).

## Verbatim excerpt

### Post 1 — Section: Introduction & guide structure

Recharge Guide — Everything you need to know about Recharge…and then some. By Bopper. Written: 17 Nov 2019. Updated: N/A.

The purpose of this guide is to teach you everything you need to know about recharge. I have broken up this guide into chapters in an effort to build up your understanding on how recharge works. My methods for building up your knowledge will be a bit backwards. Normally in a textbook, you will be given a formula, the formula will be derived, then you will see examples on how to use the formula. Instead, Chapter 1 will show you examples with step-by-step solutions in hopes of learning and observing all the details that goes into solving the Recharge Problem. In Chapter 2, I will introduce formulas that could be used for solving the examples from Chapter 1 in hopes that you can apply those formulas for your own needs. In Chapter 3, I introduce a new technique for solving the Recharge Problem that is faster and easier to implement, although it has its limitations. At that point, you will have all the knowledge you need to know. But if you would like to read on, Chapter 4 provides additional formulas that apply to the Recharge Problem that could be useful to you. Finally, Chapter 5 (not complete), will be additional examples that I will solve by request.

If you prefer the PDF version or Word document version (they are much more readable than the forum's formatting), they are attached. Background information was discussed in a prior thread on calculating total recharge time using varying recharge buffs.

Edited 17 November 2019 by Bopper.

### Post 2 — Section: Chapter 1 — Calculating Time to Recharge by examples

The first thing to understand about recharge is that we are working with two time domains: the real-world time domain (which is what you experience), and the cooldown time domain (which is what your power experiences). The recharge in the power is the rate at which the cooldown time domain experiences for every second that passes in the real-world time domain. This leads us to our first formula, which is the amount of cooldown time experienced.

To understand how to apply this formula, let's start with the most common example recharge question: How much recharge do I need to make Hasten permanent?

Example #1.1: Hasten has a base recharge of 450 seconds and a duration of 120 seconds. Thus, to make Hasten permanent, we need our power to experience 450s of cooldown within 120s of real-world time.

Example #1.2 (paraphrased setup): Assume 300% permanent recharge in Hasten from outside sources. We break the problem into two parts. First we analyze when Hasten is active (370% recharge for 120 seconds) and the second part we analyze when Hasten wears off (300% recharge for some additional amount of time). Our power will still need to experience 450s of cooldown. This tells us Hasten will recharge in 120 + 2 = 122 seconds.

Example #1.3: Same setup, but a Force Feedback Proc (+100% recharge for 5 seconds) goes off once while Hasten is active. This adds complexity as we don't know if Hasten will become permanent or not, so we may have to analyze this in up to three parts: Hasten + FF active (5 seconds), Hasten active (120 seconds minus the 5 secs for FF), and nothing active (some additional amount). Starting from highest recharge then working down: it turns out we still do not achieve permanent Hasten as it would take 120 + 0.33 = 120.33 seconds to recharge. If the residual time were equal to or less than zero, we would have achieved perma.

Example #1.4: Now assume two Force Feedback Procs occur (a total of 10 seconds worth of +100% recharge) plus the same 300% boost. Hasten finishes recharging prior to the expiration of Hasten's 120 second duration (perma achieved). We need to tweak the formula by removing the 120 seconds Hasten duration assumption (we never reach it) and substituting our calculated time. Total recharge time = 10 + 108.92 = 118.92 seconds.

Tier 4 Ageless Destiny incarnate power (Core Epiphany or Radial Epiphany): 120 second cooldown duration unaffected by recharge; when cast, it provides a recharge bonus that cascades from strongest boost to weakest boost. It provides a 70% recharge boost for the first 10 seconds, then 30% for the next 20 seconds, then 20% for the next 30 seconds, then 10% for the final 60 seconds (120 seconds total).

Example #1.5: Assume 300% permanent recharge in Hasten from outside sources, and we cast Ageless and Hasten back-to-back. Once again we break by time intervals where the recharge boost in Hasten is different. Hasten will recharge in 10 + 20 + 30 + 55 = 115 seconds, achieving perma-Hasten.

Example #1.6a: Incorporate the Force Feedback Proc into the Ageless example. We care about when the FF Proc fires because if it fires within the first 10 seconds, the total recharge becomes 300% + 70% (Hasten) + 70% (Ageless) + 100% (FF) = 540%, over the 500% recharge cap. For the first 10 seconds we get the recharge-capped result. Hasten recharges in 60 + 54.2105 = 114.2105 seconds.

Example #1.6b: FF Proc fires after 10 seconds (thus, never surpassing the cap). It won't matter where it fires; the math doesn't change the result. Hasten recharges in 60 + 53.6842 = 113.6842 seconds, slightly faster than the recharge-capped scenario as we don't waste any of our boosts.

Edited 17 November 2019 by Bopper.

### Post 3 — Section: Chapter 2 — Formulas using Time Interval Analysis

I know that was a lot of math and a lot of examples I just threw at you. I didn't do that for the purpose of triggering your math class PTSD; I did it because it is my goal to make you an expert in understanding how recharge works and how to calculate a power's recharge for ANY situation. These examples covered everything ranging from static recharge, fluctuating recharge, and cap-saturated recharge. All these formulas were used in the examples, but now I will call them out explicitly.

Formula 2.1 (foundational): cooldown experienced = recharge × real-world time.

Formula 2.2: total cooldown is the summation of products of each (n-th) recharge amount with its respective real-world time duration. We used this formula in almost every example by plugging in the Base Recharge of the power as our target, then adding up the total recharge amount for each known time interval and multiplying them together, then solving for the last unknown time interval.

Formula 2.3: rearranged to solve directly for the unknown time interval.

Formula 2.4: total time it takes for a power to recharge is simply the sum of all time intervals (stated for completeness).

Formula 2.5: total recharge of the power for each time interval is the summation of each source of recharge that is present for the entirety of its time interval. Add up all permanent recharge boosts (the l-th of L permanent boosts) and add up all temporary boosts (the m-th of M temporary boosts) that are active for the entirety of the n-th interval. If total recharge boosts exceed 500%, cap them at 500%.

In layman's terms: total recharge is calculated by adding up all recharge sources for the power. Permanent boosts include your 100% base recharge, the power's recharge enhancements (after Enhancement Diversification), global set IO bonuses (e.g. slotting a Luck of the Gambler: Defense/Increased Recharge Speed, or 5-slotting an Apocalypse set), or auto powers (Quickness, Lightning Reflexes). Temporary boosts include powers with finite duration (Hasten, Ageless Destiny) and temporary buffs (Force Feedback Proc).

Practical: you only need to check two things, in-game or in Mids' Reborn — look up the recharge slotted in the power (the Enhancement Diversification amount), and look up your Global Recharge with no temporary boosts active (turn Hasten off). Mids' Reborn shows this as "+Recharge" in the Totals tab or as "Haste" in the Totals/Misc Buffs panel. Add those two numbers to your base recharge for your total permanent recharge.

Edited 17 November 2019 by Bopper.

### Post 4 — Section: Chapter 3 — Formulas using Recharge Boost Duration Analysis

In Chapter 1, step-by-step examples showed how to calculate full recharge by breaking the analysis into time intervals where total recharge in each interval is constant. Chapter 2 formalized that. Now I want to change course by breaking the analysis up by recharge boost as opposed to time interval.

Figure 3.1 (Time Interval Analysis): same as Example #1.3 (with the diagram showing total permanent boost as 250% rather than 300%) — for the first 5 seconds we calculate cooldown when the FF Proc and Hasten were both active (white), the next 115 seconds for Hasten alone (yellow), and an additional amount for permanent boosts only (green). That additional amount is what we solved for.

Figure 3.2 (Recharge Boost Duration Analysis): instead, we evaluate each individual recharge boost and its duration. Temporary boosts are evaluated for amount × duration; permanent boosts are evaluated until the power becomes fully recharged.

The benefit: this method is time-agnostic. We don't need to worry about calculating time intervals for when each boost is active/inactive, which makes for easier and faster calculations. The downside: by ignoring when boosts are active (and thus how much recharge is stacked at any given moment), we could go over the 500% recharge cap, resulting in inaccurate calculations. So these formulas are only accurate if your boosts never go over the 500% recharge cap. Lucky for most of us, this will typically be the case — and even when temporarily over the cap, it likely won't be sustained long enough to change final results by much (Examples #1.6a and #1.6b show this).

Formula 3.1: cooldown contribution decomposed by boost. Each temporary boost has a duration; permanent boosts are evaluated until the power is recharged. Caveat: each temporary boost duration can't be greater than the recharge time. If it is, treat the temporary boost as permanent and only evaluate it until the power recharges.

Formula 3.1a: since we're solving for the recharge time, we won't know if a temporary boost's duration will exceed it until we run the numbers. So, like Example #1.4, if our solution is in error (the temp boost's duration is greater than the computed recharge), we must iterate by changing the longest temporary boost duration to permanent treatment, recalculate, then check the remaining temp boosts. You can save iterations by identifying ahead of time which temporary boosts will definitely be active for the entire recharge — e.g. powers that are already perma'd (if Hasten or ChronoShift are already perma'd, treat them as permanent), or a power whose base recharge is less than the temp boost's duration.

Formula 3.1b: since each permanent boost is multiplied by the same time duration (the recharge time), we can add all permanent boosts together first, then multiply.

Formula 3.2: take the base recharge of the power, subtract the product of each temporary recharge boost and its duration, then divide by the total permanent recharge boost. As simple as it gets for solving a power's recharge time.

Example #3.1 (revisits #1.3 using Formula 3.2): same answer as before.

Note on Ageless: my original description (70/30/20/10 for 10/20/30/60s) simply added the stacks of recharge together. The actual in-game description is four separate boosts: +40% for 10s, +10% for 30s, +10% for 60s, +10% for 120s. Use the four-boost form in the formula.

Example #3.2 (revisits #1.5 with Ageless + Hasten back-to-back, 300% permanent): we have a recharge time less than the duration of two of our temporary boosts (see Formula 3.1a). Since both boosts have a 120 second duration and we now know the recharge is less than 120 seconds, we must re-do our calculation with these temporary boosts treated as permanent boosts. Same answer as before.

From these examples we can see that using Recharge Boost Duration analysis is viable, if not ultimately more convenient. The nice thing with this method is that you can see a temporary boost and instantly know what its impact on a power will be. For example, the Force Feedback Proc's 5 seconds of 100% recharge effectively takes off 5 seconds of a power's base recharge. Hasten's 120 seconds of 70% recharge effectively takes off 84 seconds. Those are numbers you can quickly calculate and apply whenever you need.

Edited 17 November 2019 by Bopper.

### Post 5 — Section: Chapter 4 — Additional Useful Formulas (FAQ)

So far, I've taken you through an exhaustive journey in understanding how to do one calculation: Time to Recharge. Now I want to go through some of the formulas you can use to answer some of the more common questions that come up relating to recharge. For this chapter, I will format it more like a FAQ section.

How much will an extra X% recharge give me?
Formula 4.1: you don't need to know your base recharge or temporary boosts. As long as you know your current ("old") recharge and your total permanent boosts (including any temp boosts that are active the entire duration per Formula 3.1a), you can directly calculate the effect of adding more recharge. Gotcha: if the added recharge would turn a previously temporary boost into an effective permanent boost, you must recalculate from scratch using the underlying formulas.

Example #4.1: Hasten with one Force Feedback Proc and a base permanent boost. Compute the current recharge, then apply Formula 4.1 for the effect of adding 10% global recharge from 5-slotting a purple set.

How much will a Force Feedback Proc give me?
Formula 4.2: applies to any temporary boost of any duration (amount and duration are the inputs, e.g. 100%/5s for FF). You only need the current recharge and total permanent boosts. Same gotcha: if the new boost effectively becomes permanent, recalculate from scratch.

Example #4.2: Building on #4.1, add one additional Force Feedback Proc and compute the new Hasten recharge.

How much equivalent recharge does a Force Feedback Proc provide me?
Formula 4.3 (and 4.3a as a cleaner direct form): the FF-equivalent in global recharge is build- and power-specific. The often-cited "an FF Proc is equivalent to about 6% global recharge" is not universal — it depends on the specific power and build.

Example #4.3: building on #4.2, the additional FF Proc shifted Hasten from 138.85s to 136.92s. Using Formula 4.3 / 4.3a, the equivalent global recharge increase is 3.65%. Verifying: replacing the additional FF Proc with +3.65% global recharge yields the same new recharge time. With different starting parameters you'd get different equivalence numbers.

Edited 17 November 2019 by Bopper.

### Post 6 — Section: Chapter 5 — Additional Examples (placeholder)

I've got nothing… so far. Actually there are a few interesting problems that I will write up in the near future. Stay tuned.

Edited 17 November 2019 by Bopper.

### Post 7 — Section: Reserved

(Placeholder reserved by Bopper for future content.)

### Post 8 — Section: Reserved

(Placeholder reserved by Bopper for future content.)

### Post 9 — Section: Reserved

(Placeholder reserved by Bopper for future content.)

## Notable replies

- As @Redlynne noted in reply (19 Nov 2019), an additive shortcut works well for most readers: treat recharge as accumulating "points" per second (base 100 + enhanced + global), with the threshold being BaseRecharge × 100; the power recharges when the accumulated points cross the threshold. Each Force Feedback Proc contributes +500 recharge points over 5 seconds (with a theoretical max of 12 procs/minute since FF doesn't stack). Redlynne used this to derive the same conclusion as Example #1.4 (perma-Hasten with two slotted FF procs and supporting global recharge) and to estimate that at 2 PPM in a regularly used host power, an FF Proc averages about +16.67% effective global recharge for a single slot.
- Bopper's reply (19 Nov 2019, in-thread) confirms the additive approach maps directly onto Formulas 2.2–2.4 (Time Interval Analysis) and is further simplified by Formulas 3.1–3.2 (Recharge Boost Duration Analysis); he flagged the additive method may need a clearer explanation in the guide.
- Bopper's reply (18 Nov 2019, responding to @Call Me Awesome) codified an important Mids' caveat: Mids' Reborn does not accurately compute recharge when recharge changes over the course of time — e.g. if you click Hasten while not perma, Mids' will display numbers as if Hasten were already perma. So for non-perma scenarios Mids' final recharge values are wrong and the manual formulas (or the boost-duration method) are needed.
- Bopper (18 Nov 2019) reinforced FF reliability heuristics that didn't make it into the guide chapters: Knockout Blow can proc FF ~90% of the time, Foot Stomp comparably (assuming enough targets), and Hail of Bullets is practically 100% — so FF as a build-around input is more reliable than skeptics suggest. He also gave a tangible threshold rule of thumb: if you are within ~5% of perma-Hasten, one FF proc won't quite get you there but two will.

## Build attachments

- RechargeGuide.pdf (285.63 kB) — `https://forums.homecomingservers.com/applications/core/interface/file/attachment.php?id=5149`
- RechargeGuide.docx (53.38 kB) — `https://forums.homecomingservers.com/applications/core/interface/file/attachment.php?id=5150`

(No .mxd files or Mids' DataLink build URLs are posted in the OP/co-author posts. The two attachments above are Bopper's offline-readable versions of the same chapter content with the equation/figure renderings intact, since the forum's inline equation images are not preserved in extracted text.)
