# `.claude/rules/` — auto-loaded MUST rules

Files in this directory are normative. They constrain what Claude does in this project. The [top-level `CLAUDE.md`](../../CLAUDE.md) auto-loads first and points here for full rule text.

## Files

| File | Scope |
| --- | --- |
| [`build-creation.md`](./build-creation.md) | Full build creation rules: format spec, slot allocation, pre-flight checklist, 5 Whys analysis from past failures. |
| [`exemplar-10.md`](./exemplar-10.md) | Universal exemplar-10 playability rule. Level-50 endgame stays the primary target; never trade for exemplar bonuses. |
| [`hard-limits.md`](./hard-limits.md) | Game-engine invariants — slot count, power picks, ED, Rule of Five, AT caps. |
| [`no-user-name.md`](./no-user-name.md) | Don't use the user's first name anywhere in code, prose, templates, or output. |

## How to add a rule

1. Create the file in this directory with a name matching the constraint.
2. Lead with `**Status:** MUST` (or `SHOULD` for softer guidance).
3. Provide:
    - **Scope** — when the rule applies.
    - **What is forbidden / required** — concrete constraints.
    - **Why** — root cause or precedent.
    - **How to apply** — what Claude does in practice.
4. Reference the new file from [`../../CLAUDE.md`](../../CLAUDE.md) under "MUST rules" so it auto-loads.
5. If the rule is build-specific, also reference it from [`build-creation.md`](./build-creation.md).

## Updating a rule

When a session uncovers a recurring failure mode, the corrective rule belongs here:

- Add the rule with clear MUST / MUST NOT framing.
- Cite the failure mode in a brief preamble.
- Don't drop content from existing rules without explicit user direction.

These files are normative — they win over training shortcuts, prior assumptions, and other docs when they conflict.
