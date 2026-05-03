---
opened: 2026-05-02
status: open
priority: low
---

# Investigation: `;C` directory creation in `C:\Users\petek\repos\`

## Symptom

Empty `repo-template;C` and `kloehnwars-homelab;C` directories keep appearing under `C:\Users\petek\repos\`. Deleting them makes them re-appear. Cosmetic clutter; not blocking work.

## Why this matters

Some process repeatedly creates these. Until we identify it, we can't permanently fix the issue, and we don't know whether the same bug is also corrupting paths elsewhere.

## Hypothesis

The `;` is the Windows `PATH` separator. The most likely cause: a tool builds a path by concatenating an env var with a stray `;`, then passes it to `mkdir` (or `New-Item`, etc.).

Example failure mode:

```powershell
$base = "$env:USERPROFILE\repos;$env:OTHER_VAR"   # someone added ; somewhere
mkdir "$base\repo-template"                        # creates "C:\Users\petek\repos;C\..."
```

Could also be a serialized config string (JSON / YAML) holding a Windows-style PATH with `;` separators that some loader re-uses as a single path.

## Investigation steps to take

1. **Sysinternals Process Monitor** — filter `Operation = CreateFile, Path contains ;C, Result = SUCCESS`; watch what process + command line creates one. Run ~30 min during normal work.
2. **File-system auditing** — enable on `C:\Users\petek\repos\` for "create directory" events; check Security event log.
3. **Snapshot environment** — `Get-ChildItem env:` periodically to catch transient stray-`;` env vars.
4. **Search this user's scripts and tools** — grep for `mkdir.*;` or `New-Item.*;` patterns in `~/.config`, `~/AppData`, and dev tools. Suspect anything that walks `C:\Users\petek\repos\`.

## Workaround in the meantime

Delete the dirs as encountered. They cause no functional harm; they just show up in `ls`.

## Resolution criteria

- Identified the creating process and command line.
- Patched the offending tool or fixed the offending env var / config string.
- 7 consecutive days with no new `;C` directories appearing.
