# Rule: Markdown style and lint conformance

**Status:** MUST. Applies to every Markdown file authored or edited in this project — README, rule files, knowledge tree files, lessons docs, captures, plan files, frontmatter content.

This is the auto-loaded summary.
The full canonical guide, imported from `repo-template` as the SSOT, is at
[`docs/repository-standards/style-guides/markdown-style-guide.md`](../../docs/repository-standards/style-guides/markdown-style-guide.md).

## Lint conformance

The repo's `.markdownlint.yaml` is the single source of truth for lint rules. Authored markdown passes `markdownlint` cleanly except for the explicit exceptions defined in that config:

- `MD007/ul-indent` — disabled. EditorConfig governs indentation (`indent_size = 2` for `*.md`).
- `MD029/ol-prefix` — disabled. Numbered lists with sub-lists confuse the linter; prefix style isn't enforced.
- `MD013/line-length` — line length 200 in prose; disabled inside code blocks and tables.
- `MD033/no-inline-html` — `div`, `span`, `img`, `br`, `p`, `a` allowed; other inline HTML is rejected.

Run the lint check before committing markdown. Pre-commit hook will enforce this once Phase 3 wires it in.

**Exemption (user-directed, 2026-07-02):** generated engine-extraction docs under [`docs/engine/`](../../docs/engine/) carry a file-level `<!-- markdownlint-disable -->`.
The assembler normalizes their heading flow; the body is verbatim deep-math extraction (long cited lines, dense tables) and is not hand-lint-fixed.
Keep the disable comment when regenerating.

## Core requirements (summary — see canonical guide for full text)

### Structure

- Single top-level heading (`# Title`) per file.
- Headings form a stable outline; never skip levels (`##` directly to `####`).
- Use headings, not bold text, to mark structure.

### Prose

- Paragraph = one topic, multiple sentences as needed. Don't fragment a single thought into many one-liners.
- Active voice; positive form; specific concrete language.
- When a line exceeds 200 chars, **shorten the prose**, don't insert mid-sentence line breaks.
- Default short sentences. Vary length for rhythm.

### Lists

- `-` for unordered lists.
- Items short. Multi-step content becomes a subheading + sub-list, not a giant nested item.

### Code blocks

- Always tag the language: ` ```bash `, ` ```yaml `, ` ```python `, ` ```text `, etc.
- Show the minimal snippet; link to the file rather than pasting full files.

### Mermaid

- Fenced as ` ```mermaid `.
- Keep node labels plain — no curly-brace placeholders, no parens, no slashes inside labels (GitHub's renderer breaks).
- Put detailed REST endpoints / placeholders / URLs in surrounding prose.

### Links

- Relative paths for repository content.
- Link to SSOT docs rather than duplicating procedures.

### Verbatim Mids forum-export blocks

This project's specific exception to the "no abbreviations in prose" rule (see [`io-set-naming.md`](./io-set-naming.md)): inside ```text``` fences holding a verbatim Mids' Reborn forum-export block, IO set abbreviations stay as the export emits them. Outside the fence, prose uses full names.

## Tooling

- **markdownlint** (via the imported `.markdownlint.yaml`) — primary lint.
- **EditorConfig** (via the imported `.editorconfig`) — indentation, line endings, charset, final newline.
- **VS Code** picks up both automatically when the workspace is opened via `homecoming-build-companion.code-workspace`.

Future Phase 3 work: import the markdown-related Python checks from `repo-template/scripts/linting/` (heading numbering for runbook-style docs, mermaid label safety) and wire them as pre-commit hooks once the Python tooling is in place.

## Reference

- [`docs/repository-standards/style-guides/markdown-style-guide.md`](../../docs/repository-standards/style-guides/markdown-style-guide.md) — full canonical guide.
- [`.markdownlint.yaml`](../../.markdownlint.yaml) — lint config (single source of truth for rule selections).
- [`.editorconfig`](../../.editorconfig) — editor settings driving indentation and line endings.
- [`io-set-naming.md`](./io-set-naming.md) — full IO set names in prose; abbreviations only inside verbatim Mids forum-export blocks.
- [`error-output.md`](./error-output.md) — diagnostic messages also follow this style guide.
