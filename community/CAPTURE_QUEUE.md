# Forum Capture Queue

Forum threads to ingest into `community/`. Each row is one capture target with the destination path, primary topic tag, and trust level. Walk these in priority order via the [Chrome + Claude
extension workflow](CAPTURE.md).

After saving each markdown file, run:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\ingest-forum-capture.ps1" -Path <saved-md-file>
```

That validates frontmatter, drops it into the right folder, and re-runs `regen-index.ps1`.

**Trust legend:** `community-consensus` (multi-author or canonical), `single-author-opinion` (one author), `first-party` (dev / wiki).

---

## Priority 1 — high-leverage mechanics (do these first)

| Status  | #   | URL                                                                                                                                                     | Target file                                   | Topic                                   | Trust               |
| ------- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | --------------------------------------- | ------------------- |
| ✅ done | 1   | [PPM Information Guide](https://forums.homecomingservers.com/topic/5290-procs-per-minute-ppm-information-guide/)                                        | `mechanics/ppm-information-guide.md`          | mechanics, procs                        | community-consensus |
| ✅ done | 2   | [Comprehensive Incarnate Guide](https://forums.homecomingservers.com/topic/8727-a-comprehensive-guide-to-the-incarnate-system/)                         | `mechanics/incarnate-system-comprehensive.md` | mechanics, incarnates                   | community-consensus |
| ✅ done | 3   | [Wavicle's What Really Matters](https://forums.homecomingservers.com/topic/31511-wavicles-guide-to-what-really-matters/#comment-700039)                 | `mechanics/wavicle-what-really-matters.md`    | mechanics, min-maxing, build-philosophy | community-consensus |
| ✅ done | 4   | [Recharge Guide](https://forums.homecomingservers.com/topic/12685-recharge-guide/)                                                                      | `mechanics/recharge-guide.md`                 | mechanics, recharge                     | community-consensus |
| ✅ done | 5   | [Survivability Tool](https://forums.homecomingservers.com/topic/12212-the-survivability-tool/)                                                          | `tools/survivability-tool.md`                 | tools, survivability                    | community-consensus |
| ✅ done | 6   | [Common Resist Breakdown (Galaxy Brain)](https://forums.homecomingservers.com/topic/11157-galaxy-brains-common-resist-breakdown/#comment-395065)        | `mechanics/galaxy-brain-resist-breakdown.md`  | mechanics, resistance                   | community-consensus |
| ✅ done | 7   | [Health & Regeneration mechanics](https://forums.homecomingservers.com/topic/2065-a-guide-to-health-amp-regeneration-and-how-they-work/#comment-103380) | `mechanics/health-and-regen-explained.md`     | mechanics, regen, hp                    | community-consensus |

## Priority 2 — slotting / IO mechanics

| Status     | #   | URL                                                                                                                                                                             | Target file                                        | Topic                            | Trust                 |
| ---------- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------- | --------------------- |
| ✅ done    | 8   | [Nic's Guide to IOs with Impact](https://forums.homecomingservers.com/topic/4278-nics-guide-to-ios-with-impact/)                                                                | `mechanics/nics-ios-with-impact.md`                | mechanics, set-bonuses, slotting | community-consensus   |
| ✅ done    | 9   | [Pretty Damned Spectacular IO/SetIO Guide](https://forums.homecomingservers.com/topic/23164-a-pretty-damned-spectacular-guide-on-leveling-with-ios-and-io-sets/#comment-472634) | `mechanics/pretty-damned-spectacular-io-guide.md`  | mechanics, io-leveling           | single-author-opinion |
| ✅ done    | 10  | [Instant Improvements: IO Cheat Sheet](https://forums.homecomingservers.com/topic/12286-instant-improvements-a-cheat-sheet-for-io-enhancements/#comment-317143)                 | `mechanics/instant-improvements-io-cheat-sheet.md` | mechanics, io-cheatsheet         | community-consensus   |
| ✅ done    | 11  | [HP/Regen Proc Cheat Sheet](https://forums.homecomingservers.com/topic/19022-hpregen-proc-cheat-sheet/)                                                                         | `mechanics/hp-regen-proc-cheatsheet.md`            | mechanics, procs, hp, regen      | community-consensus   |
| ✅ done    | 12  | [Slotting for Endurance Recovery — Cheat Sheet](https://forums.homecomingservers.com/topic/8892-slotting-for-endurance-recovery-a-cheat-sheet/#comment-488125)                  | `mechanics/endurance-recovery-cheatsheet.md`       | mechanics, endurance, slotting   | community-consensus   |
| ⏳ pending | 13  | [Heatstroke's End Management & Stamina Tips](https://forums.homecomingservers.com/topic/40712-heatstrokes-helpful-hints-on-end-management-and-stamina/)                         | `mechanics/heatstroke-end-management.md`           | mechanics, endurance             | single-author-opinion |
| ⏳ pending | 14  | [Attuning / Catalyzing Enhancements](https://forums.homecomingservers.com/topic/2105-attuningcatalyzing-enhancements/)                                                          | `mechanics/attuning-and-catalyzing.md`             | mechanics, ios                   | community-consensus   |
| ⏳ pending | 15  | [Enhancement Converters Crash Course](https://forums.homecomingservers.com/topic/1682-a-quick-and-dirty-crash-course-in-enhancement-converters/#comment-21763)                  | `mechanics/enhancement-converters.md`              | mechanics, ios, market           | community-consensus   |
| ⏳ pending | 16  | [Don't Fear the Respec — Multiple Builds & Unslotters](https://forums.homecomingservers.com/topic/43047-dont-fear-the-respec-respecs-multiple-builds-and-unslotters/)           | `mechanics/respecs-multibuilds-unslotters.md`      | mechanics, respecs, multibuilds  | community-consensus   |
| ✅ done    | 25  | [For a new character leveling, how do you slot? (Sovera)](https://forums.homecomingservers.com/topic/63957-for-a-new-character-leveling-how-do-you-slot/)                       | `leveling/slotting-while-leveling-sovera.md`       | leveling, slotting, ios          | community-consensus   |
| ✅ done    | 26  | [Ultimate Guide to Enhancements and How to Make Them (Yomo)](https://forums.homecomingservers.com/topic/62648-the-ultimate-guide-to-enhancements-and-how-to-make-them/)         | `io-sets/enhancements-and-how-to-make-them.md`     | io-sets, converters, market      | community-consensus   |

## Priority 3 — accolades & reference

| Status     | #   | URL                                                                                                                     | Target file                                   | Topic                | Trust               |
| ---------- | --- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | -------------------- | ------------------- |
| ⏳ pending | 17  | [Accolade Guide — 4 Passive Bonuses](https://forums.homecomingservers.com/topic/4233-accolade-guide-4-passive-bonuses/) | `mechanics/accolade-guide-passive-bonuses.md` | mechanics, accolades | community-consensus |
| ⏳ pending | 18  | [Guide to Accolades and More](https://forums.homecomingservers.com/topic/43258-guide-to-accolades-and-more/)            | `mechanics/accolades-and-more.md`             | mechanics, accolades | community-consensus |

## Priority 4 — build types & farming

| Status     | #   | URL                                                                                                                                                                 | Target file                                           | Topic                                | Trust               |
| ---------- | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------ | ------------------- |
| ✅ done    | 19  | [I28P1 Farming Microguide — Maps & Builds](https://forums.homecomingservers.com/topic/37390-issue-28-page-1-farming-microguide-maps-builds/page/13/#comment-703643) | `meta-builds/farming-i28p1-microguide.md`             | meta-build, farming, brute, scrapper | community-consensus |
| ⏳ pending | 20  | [Invulnerability Tankers — Soft-cap Defense](https://forums.homecomingservers.com/topic/1642-invulnerability-tankers-soft-cap-defense/)                             | `archetypes/tanker-invulnerability-softcap.md`        | tanker, invulnerability, soft-cap    | community-consensus |
| ✅ done    | 27  | [Dominator Benchmarks](https://forums.homecomingservers.com/topic/63824-dominator-benchmarks/)                                                                      | `archetypes/dominator/dominator-benchmarks.md`        | dominator, benchmarks, perma-dom     | community-consensus |
| ✅ done    | 28  | [The Rich Alt's Guide to Perma-Dom](https://forums.homecomingservers.com/topic/47026-the-rich-alts-guide-to-perma-dom/)                                             | `archetypes/dominator/rich-alt-guide-to-perma-dom.md` | dominator, perma-dom, recharge       | community-consensus |

## Priority 5 — powerset deep-dives

| Status     | #   | URL                                                                                                               | Target file                      | Topic                         | Trust                 |
| ---------- | --- | ----------------------------------------------------------------------------------------------------------------- | -------------------------------- | ----------------------------- | --------------------- |
| ⏳ pending | 21  | [Time Manipulation Guide](https://forums.homecomingservers.com/topic/7238-time-manipulation-guide/)               | `powersets/time-manipulation.md` | powerset, support, time       | community-consensus   |
| ⏳ pending | 22  | [Poison Guide](https://forums.homecomingservers.com/topic/17683-poison-guide-a-guide-to-the-most-deadly-poisons/) | `powersets/poison.md`            | powerset, debuff, poison      | community-consensus   |
| ⏳ pending | 23  | [Energy Melee — Murder Bunny](https://forums.homecomingservers.com/topic/2915-enen-the-murder-bunny/)             | `powersets/energy-melee.md`      | powerset, melee, energy-melee | single-author-opinion |

## Priority 6 — guide aggregator (gives more URLs)

| Status     | #   | URL                                                                         | Target file            | Topic       | Trust       |
| ---------- | --- | --------------------------------------------------------------------------- | ---------------------- | ----------- | ----------- |
| ⏳ pending | 24  | [Guide Index](https://forums.homecomingservers.com/topic/5517-guide-index/) | `_meta/guide-index.md` | meta, index | first-party |

This one is special: it's an index of guides on the forum. Capture it, then walk the new URLs it surfaces back into this queue.

---

## How to capture (concise)

**Easiest path:** generate per-URL prompt blocks once, then copy/paste per capture. See [CAPTURE_WORKFLOW.md](../../homecoming-build-companion/scripts/CAPTURE_WORKFLOW.md) for full step-by-step.
Short version:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\generate-prompts.ps1"
# Open inbox/PROMPTS.md, copy the block for URL N, paste in Claude for Chrome,
# copy Claude's response, then:
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\capture.ps1" -Paste
```

**Manual path** (if you'd rather hand-craft the prompt): in Chrome with the Claude extension, on the forum thread, give Claude this prompt:

> Extract this forum thread into markdown blocks matching the format in community/CAPTURE.md.
>
> **Multi-post guides.** Many threads spread the guide across several sequential posts by the same author (post 1: intro / table of contents, post 2: section A, post 3: section B, ...). Walk the
> entire thread and treat ALL posts by the original poster (and any users the OP explicitly names as co-authors) as one continuous guide. Concatenate them in chronological order, preserving the OP's
> section structure and headings. If the OP edits a post over time, capture the latest version.
>
> Replies from other users are community discussion. Include them only if they materially correct, extend, or codify the guide content (with attribution: "as @user noted in reply 17, ..."). Skip
> flames, signatures, brief praise, off-topic chatter.
>
> **Embedded builds.** When a forum post contains a complete build dump (a Hero Plan / Villain Plan forum-export block, a `[b]Hero Plan...[/b]` BBCode block, or a DataLink URL), extract it as a
> SEPARATE markdown block in your response, immediately after the parent capture. Each build is a loadable artifact and gets its own file when ingested, so it carries enough context to stand alone.
> When the thread has zero embedded builds, emit only the parent capture.
>
> **Output**: Emit one PARENT capture block followed by zero or more BUILD sub-capture blocks. All output is fenced markdown blocks; no other commentary.
>
> **PARENT frontmatter**: title, url (full), source (forums.homecomingservers.com), authors (every author whose content you included), date_posted (OP's first-post date), date_captured (today),
> captured_by (local-capture), topic_tags (3-5 tags, first one = topic folder), trust (the level shown on this row), multi_post (true/false), post_count, contradicts_data (none unless something
> stands out vs game data).
>
> **PARENT body**: Summary (3-5 bullets covering the WHOLE guide); Verbatim excerpt (substantive paragraphs chronologically, multi-post sections marked `### Post N — Section: <name>`); Notable
> replies (optional); Build attachments (lists every embedded build emitted in per-build blocks, plus any DataLink-only references and .mxd attachments).
>
> **BUILD sub-capture frontmatter** (one per embedded build): title, parent_guide (relative path), parent_url, post_url (with `#post-N` anchor when available), build_author, date_posted,
> date_captured (today), captured_by (local-capture), archetype, primary, secondary, ancillary (or "none"), build_goal (one phrase), build_format (forum-export | datalink | mxd | mixed), verified
> (false), contradicts_data (none unless flag), suggested_filename (`builds/<archetype-lowercase>/<slug>.md`).
>
> **BUILD body**: Context (2-4 sentences pulled from the parent guide so the build reads cleanly on its own); Verbatim build (the complete forum-export block, copied verbatim, source formatting
> preserved); DataLink (when posted); Notes from the author (when present in the same post).

Save the markdown locally. Then in PowerShell:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\ingest-forum-capture.ps1" -Path <local-md> -Target <one-of-target-paths-from-the-table>
```

The script validates the frontmatter, copies the file to `community/<target>/<slug>.md`, and re-runs the index regenerator.

---

## Progress tracking

Mark rows here when captured: change the row to `~~strikethrough~~` or add a ✓ at the end. Or just check `community/INDEX.md` after each capture — it auto-regenerates from frontmatter and shows
what's in the project now.
