# `community/builds/` — captured forum builds

Each file here is a verbatim build extracted from a forum thread. Builds live in their own files (rather than nested inside the parent guide capture) because:

- A build is a loadable artifact — pasted directly into MidsReborn via Forum Import.
- A reader using one specific build doesn't need the parent guide open.
- Tooling can search by archetype, primary, secondary, or build goal across all captured builds.

## Layout

```text
community/builds/
├── tanker/
│   ├── invuln-ss-softcap-bopper.md
│   └── ...
├── brute/
├── scrapper/
├── stalker/
├── sentinel/
├── blaster/
│   └── energy-blast-energy-melee-procmonster.md
├── corruptor/
├── defender/
├── controller/
├── dominator/
├── mastermind/
├── peacebringer/
├── warshade/
├── arachnos-soldier/
└── arachnos-widow/
```

The folder is the lowercase archetype name (with hyphens for spaces).

## Frontmatter contract

Every build file carries:

| Field | Purpose |
| --- | --- |
| `title` | Build name from the post, or fallback `<AT>/<Primary>/<Secondary> — <theme>`. |
| `parent_guide` | Relative path to the parent capture (the forum thread guide). |
| `parent_url` | Forum thread URL. |
| `post_url` | URL of the specific post containing this build, with `#post-N` anchor when available. |
| `build_author` | Forum handle who posted this specific build. |
| `date_posted` | YYYY-MM-DD of the post containing the build. |
| `date_captured` | YYYY-MM-DD ingestion date. |
| `captured_by` | `local-capture`. |
| `archetype` | Tanker / Brute / Scrapper / etc. |
| `primary` | Powerset name as it appears in the build. |
| `secondary` | Powerset name. |
| `ancillary` | Ancillary / patron pool, or `none`. |
| `build_goal` | One phrase: `soft-cap defense`, `max damage`, `perma-Hasten farmer`, etc. |
| `build_format` | `forum-export` / `datalink` / `mxd` / `mixed`. |
| `verified` | `true` once the build has been loaded in MidsReborn and confirmed valid; `false` until verified. |
| `contradicts_data` | `none` or a flag. |
| `suggested_filename` | Self-reference, e.g. `builds/blaster/energy-blast-energy-melee-procmonster.md`. |

## Body shape

Each build file has these sections:

- **Context** — 2-4 sentences pulled from the parent guide explaining what the build is for.
- **Verbatim build** — the complete forum-export block (or BBCode), copied verbatim from the post.
- **DataLink** — when present, the verbatim DataLink URL importable via MidsReborn Ctrl+I.
- **Notes from the author** — author commentary that accompanied the build, when present.

## Ingestion

The capture pipeline ([`scripts/capture.ps1`](../../scripts/capture.ps1)) detects sub-capture frontmatter (presence of `archetype` + `primary` + `parent_url`) and routes the file to the path in
`suggested_filename`. The parent capture lands in its `community/<topic>/` folder; build files land here.

## Verification

A captured build is `verified: false` until loaded in MidsReborn and confirmed:

- Power picks at correct levels.
- Slot count within the 67 cap, ≤ 5 added per power.
- Enhancement set names match canonical.
- Stats panel matches author's claimed totals.

Once verified, set `verified: true`. Failures get logged in `community/builds/_verification-notes/<at>/<slug>.md` so future maintenance can act on them.
