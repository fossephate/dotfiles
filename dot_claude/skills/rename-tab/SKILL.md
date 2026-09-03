---
name: rename-tab
description: Rename the current Zed terminal tab. Use when invoked as /rename-tab <name>, or when the user asks to rename, retitle, or clear the terminal tab title.
argument-hint: <new tab name, or empty to clear>
---

# Rename tab

Set the Zed terminal tab title to the argument.

Run exactly this, passing the argument through unquoted-but-safe:

```bash
~/.claude/hooks/zed-set-tab-title.sh <argument>
```

Then report the resulting title in one short sentence. Do not explain the escape sequence unless asked.

## Rules

- **No argument** — run the script with no arguments. That clears the custom title and restores the process-derived one (`zed — zsh`). Do not ask the user to confirm; clearing is the documented behavior of the bare command.
- **Argument given** — pass it verbatim as a single argument. Do not paraphrase, shorten, title-case, or "improve" it; the user chose that name. The script handles truncation (40 chars) and strips control characters itself.
- If the user describes a name in prose rather than giving one directly (e.g. "call it something about the auth refactor"), pick a short label yourself, use it, and say which one you chose.

## Caveats to surface only when relevant

- The title is sticky: it persists across restarts (stored in Zed's workspace DB) and overrides the automatic process-derived title until cleared with a bare `/rename-tab`.
- This only visibly renames tabs in a Zed build carrying the `zed;tab-title=` OSC patch. In other terminals, and in unpatched Zed, the sequence is silently discarded — the command still reports success because the bytes were written. If the user says nothing happened, that mismatch is the first thing to check.
- Task terminals ignore the rename; their tab shows the task label instead.
