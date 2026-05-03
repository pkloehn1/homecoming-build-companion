# Project rules — auto-loaded

Binding rules for every Claude session on this project. Read first. Rules are MUST-follow; deeper detail lives in [`.claude/rules/`](./.claude/rules/) and [`docs/`](./docs/).

When this file conflicts with prior assumptions, training-data shortcuts, or other docs, **this file wins.**

---

## What this project is

A Claude project for designing **City of Heroes (Homecoming)** character builds against MidsReborn data. Builds load into MidsReborn for verification and benchmark against community builds.

For orientation (folder layout, decision rules for which file to cite, etc.), read [`README.md`](./README.md).

---

## How we work (the rules)

These are stated as positive principles. Following them produces correct, playable, comparable builds.

### B1. Refer to the user generically

Second-person ("you") in conversation; generic placeholders (`local-capture`, `your_handle`) in code and prose. See [`.claude/rules/no-user-name.md`](./.claude/rules/no-user-name.md).

### B2. Optimize for level-50 endgame; ensure the build is exemplar-10 playable

Level 50 is the target. Verify exemplar-10 playability (attacks, defense, travel by L12) without trading level-50 quality. See [`.claude/rules/exemplar-10.md`](./.claude/rules/exemplar-10.md).

### B3. Treat builds as level-by-level allocations

Every build is a sequence of `(power picked at level X)` and `(slot placed at level Y in power Z)` records. Match MidsReborn's forum export format precisely:

- `(N)` is the **character level when the slot was placed in this power**.
- `(A)` is the inherent slot (free with the power).
- IO level (when shown) goes after the name as `: Level XX`.

See [`.claude/rules/build-creation.md`](./.claude/rules/build-creation.md) for the full mechanics + pre-flight checklist.

### B4. Respect the hard game limits as continuous constraints

Game-engine invariants — track these *during* draft, not after:

- 50 character levels max.
- 24 power picks (1+1 at level 1, then 1 every other level).
- 67 added enhancement slots per character.
- 6 enhancement slots per power max (1 inherent + 5 added).
- 4 power pools per build max.
- Pool tier prerequisites: T1/T2 before T3 before T4.
- Each power picked at or after its `Level` field.
- Each slot placed at or after its power's pick level, at a level that grants a slot per the schedule.
- Enhancement Diversification: same-aspect stacking past ~95% diminishes sharply.
- Rule of Five: at most 5 instances of any exact set-bonus value stack.
- AT caps per [`data/canonical/archetypes/<at>.json`](./data/canonical/archetypes/) and [`strategy/breakpoints.json`](./strategy/breakpoints.json).

A build that satisfies all of these is valid. When a draft hits a constraint, stop and re-budget. See [`.claude/rules/hard-limits.md`](./.claude/rules/hard-limits.md).

### B5. Cite canonical data; treat training memory as approximate

For specific numbers (recharge, end cost, damage, max targets, power pick level, ancillary pool composition, set bonus values), the order is:

1. `data/canonical/` — primary source.
2. `data/diff/current_overrides.json` — patch-history corrections.
3. Community captures in `community/`.
4. Training memory — labeled "approximate; verify in MidsReborn" when used.

For format details, read [`MidsReborn/clsOutput.cs`](../MidsReborn/MidsReborn/clsOutput.cs) (emitter) and [`build-format/schema.json`](./build-format/schema.json) (schema).

### B6. Emit JSON alongside markdown for every build

Every build proposal produces two artifacts:

- **JSON** — schema-valid per [`build-format/schema.json`](./build-format/schema.json). The loadable artifact.
- **Markdown** — MidsReborn forum-export format. For review and forum sharing.

The JSON is the source of truth; the markdown is a view. They agree on every power, slot, and enhancement.

### B7. Run a slot-count tracker during draft

Track added slots and per-power counts during composition. Hit the 67-slot cap exactly or under with intentional slack. Per-power max 5. Re-budget early on approach.

### B8. Run the pre-flight checklist before emitting

Walk the checklist in [`.claude/rules/build-creation.md`](./.claude/rules/build-creation.md). Every item passes or the build doesn't emit. Fix or escalate failures with details.

### B9. Use the trade-offs section for real design tensions

The "Trade-offs" section is for real design choices (defense vs damage, AoE vs ST, ATO 6-piece vs procs). Errors get fixed before emit. Unverified specifics go in "What I would verify".

### B10. Apply the canonical trust schema in captures

Captures set `trust:` to `first-party`, `community-consensus`, or `single-author-opinion`. Forum user-rank labels map to the canonical value at save. Ingestion fixes drift on contact.

---

## Reading order for a new session

1. This file (CLAUDE.md) — binding rules.
2. [`README.md`](./README.md) — orientation, folder layout, decision rules for which data to cite.
3. [`.claude/rules/build-creation.md`](./.claude/rules/build-creation.md) — full build creation rules + pre-flight checklist.
4. [`.claude/rules/exemplar-10.md`](./.claude/rules/exemplar-10.md) — exemplar mechanics + the universal playability rule.
5. [`.claude/rules/hard-limits.md`](./.claude/rules/hard-limits.md) — game-engine invariants.
6. [`.claude/rules/attack-slotting.md`](./.claude/rules/attack-slotting.md) — accuracy in slot (A) and first added slot of every attack.
7. [`.claude/rules/io-set-naming.md`](./.claude/rules/io-set-naming.md) — full IO set names in prose; abbreviations only inside verbatim Mids forum-export blocks.
8. [`.claude/rules/no-user-name.md`](./.claude/rules/no-user-name.md) — generic placeholders only; never the user's first name.
9. [`.claude/rules/coh-knowledge-navigation.md`](./.claude/rules/coh-knowledge-navigation.md) — for build requests, navigate `knowledge/coh/INDEX.md` to load only relevant files.
10. [`.claude/rules/python.md`](./.claude/rules/python.md) — Python 3.14 conventions for tooling and validators.
11. [`.claude/rules/gitops.md`](./.claude/rules/gitops.md) — GitOps conventions: branches, Conventional Commits, signed commits, PR structure with issue grouping.
12. [`.claude/rules/devsecops.md`](./.claude/rules/devsecops.md) — DevSecOps non-negotiables: no secrets in code, signed commits, least-privilege CI, no hook bypass.
13. [`.claude/rules/error-output.md`](./.claude/rules/error-output.md) — diagnostic and error message standard.
14. [`.claude/rules/markdown.md`](./.claude/rules/markdown.md) — Markdown style and lint conformance for all prose authoring.
15. [`docs/repository-standards/style-guides/`](./docs/repository-standards/style-guides/) — canonical Markdown / Python / error-output guides (imported SSOTs).
16. [`docs/repository-standards/`](./docs/repository-standards/) — git-standards, git-branching, devsecops-workflow (one-time imports from kloehnwars-homelab; standalone-consumer model, not auto-synced).
17. [`docs/automation/runbooks/`](./docs/automation/runbooks/) — git-workflow-checklist, fix-unsigned-commits-in-pr (operational runbooks).
18. [`docs/`](./docs/) — game mechanics reference (powers, enhancements, procs, incarnates, attack chains, min-maxing).
19. [`community/INDEX.md`](./community/INDEX.md) — captured forum guides, grouped by topic.

---

## Workflow for emitting a build

1. Identify the AT, primary, secondary, build goal from the user.
2. Read [`.claude/rules/build-creation.md`](./.claude/rules/build-creation.md) and confirm the pre-flight checklist applies.
3. Pull the relevant powerset data from [`data/canonical/powers/`](./data/canonical/powers/).
4. Pull the AT caps from [`data/canonical/archetypes/<at>.json`](./data/canonical/archetypes/) or [`strategy/breakpoints.json`](./strategy/breakpoints.json).
5. Cross-check [`data/diff/current_overrides.json`](./data/diff/current_overrides.json) for any patched values affecting the chosen powers.
6. If a community capture exists for the AT or powerset, read it ([`community/archetypes/<at>/`](./community/archetypes/), [`community/powersets/<set>/`](./community/powersets/)).
7. Draft the build with running slot count and per-power tally.
8. Walk the pre-flight checklist.
9. Emit JSON + markdown.
10. Surface real trade-offs and verification gaps.

---

## Updating these rules

When a session uncovers a recurring failure mode, the corrective rule belongs in [`.claude/rules/`](./.claude/rules/):

- Frame the rule as a positive principle ("Apply X" rather than "Don't do Y") so it engages reward-seeking behavior.
- Cite the failure mode in a brief preamble so future-you understands the precedent.
- Reference the new file from this CLAUDE.md so it auto-loads.
- If the rule is build-specific, link it from [`.claude/rules/build-creation.md`](./.claude/rules/build-creation.md) too.

This file and the files under [`.claude/rules/`](./.claude/rules/) are normative. Preserve their content unless the user explicitly directs otherwise.
