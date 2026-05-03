---
title: "Galaxy Brain's Common Resist Breakdown"
url: "https://forums.homecomingservers.com/topic/11157-galaxy-brains-common-resist-breakdown/"
source: "forums.homecomingservers.com"
authors: ["Galaxy Brain"]
date_posted: "2019-10-04"
date_captured: "2026-04-27"
captured_by: "local-capture"
topic_tags: ["enemy-resists", "damage-types", "data", "research", "spreadsheet"]
trust: community-consensus
multi_post: false
post_count: 1
contradicts_data: "none"
---

# Galaxy Brain's Common Resist Breakdown

## Summary

- The guide is a single Google Sheet that aggregates resistance data for 61 enemy groups (sourced from a Discord user, with coverage roughly through Cimerora and not including Going Rogue+ factions) and weights each damage type's average resistance by how often you actually encounter resistant enemies, producing an "Adjusted Average" rather than a raw faction-vs-faction average.
- The sheet is structured around six views: a Totals roll-up, Group Averages (per faction), All Minions, and minion subdivisions by level band (1–20, etc.), plus rank-based breakdowns — so users can filter by content tier rather than treating every enemy group as equally common.
- Once weighted by encounter rate, the ranking from most-to-least resisted across the sample is: Toxic (most resisted overall, with no enemies weak to it in the 61-group sample), then the others, with Negative being the least resisted and having the highest count of enemies actively weak to it.
- Smashing damage is the most likely damage type to be resisted by an enemy you bump into, while Fire is the least likely to be resisted — a finding that runs counter to the common forum framing that "Smashing/Lethal is fine until endgame" and helps reframe attack-set selection for general-purpose play.
- Galaxy Brain explicitly flags two limitations and asks for community feedback: the encounter-rate weights treat every faction in the dataset roughly equally (e.g. Rularuu shows up despite arguably being uncommon in actual play), and Going Rogue and post-launch factions are missing — readers with that data are invited to extend the sheet.

## Verbatim excerpt

### Post 1 — Section: Common Resist Breakdown (overview, methodology, and findings)

Hello everyone!

I'm making a separate thread from the Scrapper Melee Testing to highlight the resistances that enemies carry throughout the game. Often we tote how X damage type is super resisted, or Y damage type is great until end game, but I don't think there is any easy to use listing of how those types perform in practice based on not only the resist amounts, but on the odds of encountering them.

This sheet covers 61 different enemy groups as collected by a user on Discord. However, it appears that this only covers enemy factions up until about Cimerora as it does not have data on Going Rogue and beyond. If anyone has access to the data on them, I can add them to the sheet to get more accurate representation!

The document is broken down as such:

- Totals — Shows the culmination of all the data
- Group Averages — Averaged resists per enemy faction
- All Minions — All minion rank enemies per faction, averaged
- Minions 1–20 [and additional minion subdivisions by level band, plus per-rank breakdowns]

[Reasoning behind weighted averaging:] An enemy group with 25% lethal resist on one type of unit, and 0% resist on another, would average out to 12.5% resist if you were to just run through a bunch at random — and probably even less than that if there are, say, 3 non-resistant enemies for every resistant one. To factor the spread of different units across factions, I sorted the data by raw average resistance, the odds of running into an enemy with that resistance (positive or negative for the enemy), and then factored those together for an "Adjusted Average."

Putting everything together, sorted by Highest to Lowest "ADJ Resist": Toxic is the most resisted overall throughout the game and has no enemies weak to it (in my sample of 61 groups), while Negative is the least resisted with the highest amount of enemies that are specifically weak to it. Smashing damage is the most likely to be resisted, and Fire is the least likely. Further breakdowns per enemy rank, and level range, can be seen in the doc.

It's my hope this can be used as a tool for players looking into different attack sets and their effectiveness across various areas of game play. I am also looking for feedback on how to best sort/categorize the factions / add factions to better show the true "encounter rate" for many enemy types. For example, Rularuu has a decent presence here, but are they _really_ commonly fought?

I look forward to everyone's feedback!

Link to Resistance Sheet.

Thank you, @Galaxy Brain.

## Notable replies

- As @Caulderone noted (7 Oct 2019), there's a prior community-compiled Excel resistance file (`CHres.xls`, 1.77 MB) that had been posted earlier in the year with attribution in the Scrapper Melee Testing thread; @Galaxy Brain confirmed in reply that the present sheet was based on that data source.
- As @Frostweaver noted (24 Apr 2020), an aggregate "Adjusted Average" hides important within-faction outliers — Toxic in particular has a few hugely-resistant units while most enemies aren't even slightly resistant — so a "cap resisters" list (which specific enemy in each group is near-immune to a given type) would help Dual Pistols and similar swap-ammo characters know when to change damage modes. Galaxy Brain acknowledged this and indicated he would extend the sheet, though that update did not land in subsequent years.
- As @KaizenSoze noted (3 Feb 2022) in a small data correction: Gold Brickers in Dr. Aeon's Strike Force have −20% Toxic resistance (i.e. are weak to Toxic), which the original sample did not capture and which slightly cuts against the OP's "no enemies weak to Toxic" finding for that group.

## Build attachments

- Common Resist Breakdown (Google Sheets, view link from OP): `https://docs.google.com/spreadsheets/d/1arWBGWuwGCWqSrkLgnWK26xNTrILUO_QNKn8034A3L0/edit`
- (Reply attachment from @Caulderone, prior community file the OP's data is based on) `CHres.xls`, 1.77 MB — hosted as a forum attachment in reply 4.

(No .mxd files or Mids' DataLink build URLs are posted in the OP or by named co-authors. The sheet above is the canonical artifact of this guide.)
