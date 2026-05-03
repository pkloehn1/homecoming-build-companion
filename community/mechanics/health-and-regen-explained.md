---
title: "A Guide To Health & Regeneration and how they work"
url: https://forums.homecomingservers.com/topic/2065-a-guide-to-health-amp-regeneration-and-how-they-work/
source: forums.homecomingservers.com
authors: [Harlequin565]
date_posted: 2019-05-22
date_captured: 2026-04-27
captured_by: local-capture
topic_tags: [regeneration, health, mechanics, slotting, spreadsheet]
trust: community-consensus
multi_post: false
post_count: 1
contradicts_data: none
---

## Summary

- Regeneration in CoH is tick-based, not continuous: at base you get one tick of 5% HP every 12 seconds (25% HP/min). The "HP/sec" figures in tools like Mids are a smoothed estimate of an underlying tick interval.
- Two levers do different jobs: increasing **Regeneration** shortens the interval between ticks; increasing **Max HP** raises the size of each tick. Slot accordingly depending on which one your build is short on.
- Worked examples: a level-50 Scrapper with only a single 50 Healing IO in Health regens ~8.6 HP/sec (a 67-HP tick every 7.8s). The same Scrapper with +165% regen and +13% HP regens ~16.7 HP/sec (a 75.6-HP tick every 4.5s) — the regen bonus mostly compresses the interval.
- The OP includes a downloadable Excel spreadsheet (`regencalc.xlsx`) that plugs alongside Mids/Pines: change AT in cell B4, paste in your set bonuses / HP bonuses, set "Number of" to 0 to A/B test a slot, and the sheet shows the resulting tick size and tick interval. Helpful for setting concrete goals like "1 tick every second."
- Caveat from the OP: this is a 2019 repost of a pre-Homecoming guide and was not re-verified against I25 mechanics; treat the formulas/conclusions as a strong starting point but spot-check against current tool output. The Dropbox link to the spreadsheet may also be stale.

## Verbatim excerpt

### Post 1 — Section: Guide (2019-05-22)

[Repost of my old guide - not checked its relevance vs I25 but assuming it's still solid]

This is not so much a guide as a help feature for those who don't understand regeneration.

I understand Recharge. I understand Endurance recovery. But I could never get my head around Regeneration. Stamina, for example, is a good benchmark for Recovery. For thos of you that remember pre-innate Fitness, you knew how much of a difference Stamina made when you took it at 20. But I never really "felt" the difference Health made.

Mainly I think that's because "tough" toons are tough. You expect them to be able to withstand damage and they can have a lot of mitigation as well (even Regen toons). Squishy toons are generally squishy. When they pull a group of mobs, that health bar can go down (mitigation aside) quite fast. Apart from on a /Regen toon, the speed your health comes back is only noticeable when you self-heal, or when you rest.

[Author's note that intuition wasn't enough — they had to work through the mechanics at their own pace.]

For the tl;dr crowd, download my spreadsheet and play. For the rest of you...

Regeneration works by healing a portion of your health every x seconds. At its base level (numbers from City of Data) it's 25% of your health every minute. In-game this results in 5% of your Health every 12 seconds.

And this is where it gets confusing. The "real numbers" quote hp/sec regeneration rates, but all this does is give you an idea of your regen rate, because what actually happens, is that (at base) you get NO health back for eleven seconds, then a huge tick of health on the 12th second.

> **Example**
>
> - With no regen bonuses, and a single 50 Healing IO in Health (assuming a level 50 scrapper) your HP/sec rate is about 8.6. What actually happens is you get a tick every 7.8 seconds which heals 67 HP.
> - That same character with 165% regen bonus and a 13% HP bonus from sets/slotted health has a hp/sec rate of 16.7. In reality they get a tick every 4.5 seconds for 75.6 HP.

Also...

> Increasing your Regeneration will reduce the time between ticks.
> Increasing your HP will increase the amount of health you get back with each tick.

So what does it mean to enhance Health? Is it worth plopping a Regen Tissue in Health, or a single Health IO? Those powers that increase your HP. Are they worth slotting with Healing IOs to increase the max HP of your toon?

I built a spreadsheet. **Dropbox Excel Download Link** (`regencalc.xlsx`).

It works in conjunction with Mids/Pines and you can play with it in several ways.

To Use it...

Change the AT in cell B4 to whatever your AT is. This will populate your base HP, capped HP and regen caps into the sheet. No data for Sentinels at the moment. It's easy to add though.

You can then fill out columns f & k with your various bonuses — be they set bonuses from IO sets, or powers that increase HP. If you want to do it quickly, just take the summaries from Mids and plop them in.

- You can change the "Number of" to 0 to remove them from the calculations. This quickly allows you to see the real effect of removing/adding something.
- The "Before" numbers assume a single 50 Healing IO in Health and nothing more, so don't forget to add Health back in.
- You can also just add percentages to the column to watch the regen rates change if you had a goal (for example) of 1 tick every second. You then know how much regen you need to build for in order to get that rate.

B16/17 affects the time between ticks rather than the the amount you heal (which will differ depending on AT)

[Screenshots of the sheet at full and zoomed views.]

Hopefully this will help understanding of Regeneration!

Lastly, I apologise for the .xls format of the spreadsheet to those without Excel. I did try converting it to Google Docs but it broke my cell validation list. If someone else wants to convert it — feel free! The calculations aren't that hard. I'd be happy to repost a link in this guide (and give you credit!)

## Notable replies

- Bopper (2019-09-18): Thanked the OP and noted "I was hoping to see the formulas exactly, but I imagine when I open your spreadsheet, I'll get them from there." Codifies that the formulas live inside the workbook rather than being spelled out in the post body — useful pointer for anyone who only reads the thread and doesn't open the .xlsx.
- Harlequin565 (OP, 2019-09-26): Confirmed they no longer remember the math from memory and "just rely on the sheet, but it's very simple excel work." Reinforces that the spreadsheet is the canonical reference for this guide.

## Build attachments

- `regencalc.xlsx` — Dropbox: https://www.dropbox.com/s/k427gg0voey0sqe/regencalc.xlsx?dl=0 — Author's Excel regeneration calculator. Drives off AT in cell B4, then takes set-bonus / HP-bonus rows in columns F & K. Note: when this thread was captured, opening the Dropbox URL returned an error page suggesting the link may be dead; verify before relying on it.
