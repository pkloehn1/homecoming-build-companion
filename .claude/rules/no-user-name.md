# Rule: Refer to the user generically

**Status:** MUST. Applies to every Claude session in this project — Claude Code, Claude.ai web project, Claude desktop app, and the Chrome browser extension.

## How we refer to the user

In conversation: use **"you"** and **"your"**. The user is the one we're talking with; second-person addresses them directly.

In code, comments, prose, frontmatter values, log output, and tooling strings: use **generic placeholders**:

| Context | Use |
|---|---|
| `captured_by:` frontmatter | `local-capture` |
| Prose attribution | "house rule," "standing rule," "the user" |
| Code template defaults | `<your_handle>`, `local-capture`, or omit |
| Log messages, error strings | "the user" or omit personal reference |
| Build attribution | "user-supplied," "from local capture" |

These placeholders are the canonical replacements. Apply them consistently.

## Why

The user has explicitly directed that their first name (or any other personally identifying name) stays out of project artifacts. They reinforced this is a MUST rule and instructed both this Claude session and the browser-extension Claude the same way. Following it is part of working with this project.

## How to apply

- **When generating templates**: embed the generic value, not a name. The template is shipped to the user verbatim, so a placeholder gets re-used cleanly.
- **When writing prose**: address with "you" / "your"; describe project preferences as "house rule" or "standing rule"; describe content origin as "user-supplied" or "captured locally."
- **When discovering an existing artifact with a name in it**: scrub on first touch. Replace with the canonical placeholder. Don't preserve the name "for context."
- **When a prior instruction conflicts**: this rule wins. Don't ask permission to apply it.

## What this looks like in practice

Building a frontmatter capture template:

```yaml
captured_by: local-capture
```

Writing prose about a project preference:

> Standing rule: every build must remain playable when exemplared as low as level 10.

Writing a tool's log output:

```powershell
Write-Host "Capture saved to $dest" -ForegroundColor Green
```

(rather than `"Pete's capture saved to $dest"`).

Writing build attribution:

```yaml
captured_by: local-capture
source: forums.homecomingservers.com
```

## Audit hook

Future maintenance: any tool that walks the project flags presence of a real name in `captured_by`, prose, or comments as a violation to fix. The frontmatter parser accepts `local-capture` (or any non-name value) as the canonical value. The capture-ingestion script ([`tools/ingest-forum-capture.ps1`](../../tools/ingest-forum-capture.ps1)) treats any non-canonical value as a soft warning.
