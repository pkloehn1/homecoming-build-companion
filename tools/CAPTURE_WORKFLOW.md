# Capture Workflow — concrete steps

How to take one forum URL from [community/CAPTURE_QUEUE.md](../../homecoming-build-companion/community/CAPTURE_QUEUE.md) and end up with an ingested markdown file in `community/`. Every step is spelled out — no hand-waving on where to click or where to type.

Time per capture: 2-4 minutes once you've done one. First time: ~10 minutes including extension setup.

---

## One-time setup

### A. Install Claude for Chrome

1. Open Chrome.
2. Go to <https://www.anthropic.com/news/claude-for-chrome>.
3. Click **Install** (it'll redirect to the Chrome Web Store) → **Add to Chrome**.
4. After install, an icon appears at top-right of Chrome. If you don't see it, click the puzzle-piece icon next to your profile picture and **pin** "Claude" so it stays visible.
5. Click the icon. It opens a side panel on the right of Chrome. Sign in with your Anthropic account if prompted (same account as Claude.ai).

> Don't have / don't want the extension? **Fallback:** open <https://claude.ai/> in a separate tab, paste the forum thread's text into a new chat, then paste the prompt. Same outcome, more clicks.

### B. Generate the per-URL prompts (one command, one time)

Open **PowerShell** (not bash, not cmd):

- Press <kbd>Win</kbd>+<kbd>X</kbd> → click **Terminal** (Windows 11) or **Windows PowerShell**.
- Or press <kbd>Win</kbd>, type `powershell`, hit <kbd>Enter</kbd>.

Paste this and hit <kbd>Enter</kbd>:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\generate-prompts.ps1"
```

It writes [`homecoming-build-companion/inbox/PROMPTS.md`](../inbox/PROMPTS.md) — 24 ready-to-copy prompt blocks, one per URL in the queue, with the URL, today's date, topic tags, and trust level pre-filled.

Re-run this any time you change `CAPTURE_QUEUE.md` (add new URLs from the Guide Index, etc.). The `inbox/PROMPTS.md` file is the workbench.

### C. Open the prompts file in your editor

Open `homecoming-build-companion/inbox/PROMPTS.md` in VS Code, Notepad++, or whatever you have. You'll be scrolling to specific URL sections and copying prompt blocks from here.

> Tip: you can also `Ctrl+F` for the URL number ("## 5.") to jump to that capture's prompt.

---

## Per-capture flow (repeat for each URL in the queue)

Numbers below match what you'll see in `inbox/PROMPTS.md`. Pick any URL — they're independent. Recommended order is the queue's priority order (do Priority 1 first).

### Step 1 — Open the forum URL in Chrome

In `inbox/PROMPTS.md`, find the section for the URL you want (e.g. `## 1. PPM Information Guide`). Click the **URL** link in that section's bullet — it opens in Chrome.

Wait for the forum thread to fully load (let images and replies render).

### Step 2 — Open the Claude for Chrome side panel

Click the **Claude icon** at top-right of Chrome (the orange/red one). The side panel slides in from the right side of the window.

If this is the first time on a forum page: Claude may ask permission to read this site. Allow it (or "always for this site").

### Step 3 — Copy the prompt block from `PROMPTS.md`

Back in your editor, on the same `## N. <Title>` section, find the fenced block that starts with `You're reading a Homecoming City of Heroes forum thread...`. The block is wrapped in triple-backticks for display — **copy everything BETWEEN the backticks**, not the backticks themselves.

In VS Code: hover your cursor inside the block, press <kbd>Ctrl</kbd>+<kbd>A</kbd> on the block (or click the small "Copy" icon that appears at top-right of the code block on hover) to copy. In Notepad / Notepad++: select with the mouse from the line `You're reading a Homecoming...` to the closing `\`\`\`markdown` block (right before the closing backticks of the outer fence). Copy.

Now your clipboard holds the prompt with the URL pre-filled.

### Step 4 — Paste into the Claude for Chrome side panel

In the Claude side panel: click the message input box at the bottom. Press <kbd>Ctrl</kbd>+<kbd>V</kbd>. Press <kbd>Enter</kbd> (or click the send button).

Claude reads the page DOM (because that's what the extension does — it has access to the active tab's content) and produces a markdown block matching the format you sent.

Wait for the response to finish streaming. It'll be a single fenced markdown block starting with `\`\`\`markdown` and ending with `\`\`\``, containing `---` frontmatter at the top followed by `## Summary`, `## Verbatim excerpt`, and `## Build attachments` sections.

If Claude **refuses** or **summarizes instead of extracting**: re-send the prompt and add at the end "Output ONLY the markdown block, no preamble." If still wrong: try the claude.ai fallback — copy the forum thread's text into a Claude.ai chat with the same prompt.

### Step 5 — Copy Claude's response

In the side panel, hover over Claude's reply. A row of icons appears (usually at the bottom of the message). Click the **copy** icon (looks like two overlapping squares). The whole assistant message goes to your clipboard.

Alternative: select the response with the mouse (click at the start, shift-click at the end), Ctrl+C.

### Step 6 — Save and ingest in PowerShell

Switch to your **PowerShell** window (the one from one-time setup B; reopen if you closed it).

Paste this and hit <kbd>Enter</kbd>:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\capture.ps1" -Paste
```

What you'll see if it works:

```
Saved → C:\Users\petek\repos\homecoming-build-companion\inbox\<slug>.md
Target derived from topic_tags[0]='mechanics': mechanics/<slug>.md
Copied → C:\Users\petek\repos\homecoming-build-companion\community\mechanics\<slug>.md
Re-generating community/INDEX.md ...
Wrote ...\community\INDEX.md  (N captures indexed)
```

Done. The capture is now in the project, and `community/INDEX.md` lists it.

If you want to be paranoid and also pass the URL for a sanity check (the script verifies the frontmatter URL matches):

```powershell
$url = "https://forums.homecomingservers.com/topic/5290-procs-per-minute-ppm-information-guide/"
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\capture.ps1" -Paste -Url $url
```

Move on to the next URL.

---

## What if something goes wrong

### "Clipboard is empty" / "Clipboard content does not start with YAML frontmatter"

You either didn't copy Claude's response, or you copied something that wasn't markdown. Re-run Step 5, then Step 6.

### "Frontmatter missing required field(s): ..."

Claude's response didn't have all required fields. The fields are: `title`, `url`, `source`, `date_captured`, `captured_by`, `topic_tags`, `trust`. Open the file in `homecoming-build-companion/inbox/<slug>.md`, fix the frontmatter by hand, then run:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\capture.ps1" -Drain
```

This processes every file in `inbox/` — yours plus any others that previously failed.

### "Destination exists"

You already captured this URL. Either skip it, or pass `-Force` to overwrite:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\capture.ps1" -Paste -Force
```

### Claude in the extension produces a long preamble before the markdown

The script tries to peel a `\`\`\`markdown` fence if present. If there's text before/after the fence and it strips correctly, you're fine. If not, edit the saved `inbox/<slug>.md` to remove the preamble (everything before the first `---`), then `-Drain`.

### Forum is rate-limiting / asking for login

You may need to be logged into the forum for the extension to read full thread content. Sign in to forums.homecomingservers.com once in Chrome, then redo Step 4.

---

## Batch workflow (do several at once)

If you want to grind through 5-10 captures in a row without switching to PowerShell each time:

1. Capture URL 1 → copy response → paste into a new file in `inbox/<some-name>.md` (manually, in any editor).
2. Capture URL 2 → same.
3. ... repeat for as many as you want.
4. Once done, run:

```powershell
& "$env:USERPROFILE\repos\homecoming-build-companion\tools\capture.ps1" -Drain
```

It ingests every `inbox/*.md` in turn, moves successful ones to `inbox/.processed/`, and leaves any that fail validation in `inbox/` for fixing.

---

## When you're done with a session

Tell me (Claude Code in this terminal) "I've captured guides X, Y, Z, ready to read them." I'll glob `community/**/*.md` and pull them into context for the next task — typically synthesizing the Top 5 by AT, or whatever else we're working on.

You don't need to do anything special to "link" the sessions — the captures live on disk. I just need to know to read them.
