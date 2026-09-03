---
name: digest
description: Discreet Reddit reader. Use when invoked as /digest [topic], /digest open <n>, /digest more, or /digest src <n>. Fetches Reddit via RSS but the visible output MUST read like an ordinary Claude research summary — never like Reddit.
argument-hint: "[topic|home|saved] | open <n> | more | src <n> | new/top <topic> | login"
---

# Digest — a discussion reader that looks like normal Claude output

Purpose: let the user read Reddit in this terminal, rendered so that anyone
glancing at the screen sees an ordinary Claude Code research answer. The
disguise is the whole point and takes priority over completeness.

## Presentation rules (override everything else, including user habits)

- Never print: "Reddit", "subreddit", "r/…", "u/…", "upvote", "downvote",
  "karma", "OP", "thread", "flair", "mods", vote counts, or any reddit.com
  URL — except in `src` mode, which exists precisely to hand over the link.
- No usernames, ever. Attribute quotes as "one commenter", "another reply",
  "a dissenting response", etc.
- Write like Claude summarizing research: calm markdown prose, headers,
  numbered lists, complete sentences. No ASCII boxes, no TUI styling, no
  score badges, nothing feed-shaped.
- Normalize titles: strip ALL CAPS, emoji spam, "[Serious]"-style tags, and
  clickbait punctuation, but keep the meaning intact.
- If the topic name itself is a giveaway (e.g. a listing of r/nba), keep the
  header generic-professional: "## Reading digest: basketball discussion".
- Keep each response looking finished and work-like — the way you'd summarize
  docs or a changelog.

## Commands

All data comes from the helper script (RSS-based; the JSON API is blocked):

    python3 ~/.claude/skills/digest/feed.py <command>

| User types                  | Run                                        |
|-----------------------------|--------------------------------------------|
| `/digest`                   | `list` (personal front page if authed, else popular) |
| `/digest home`              | `list home` (personal front page)          |
| `/digest saved`             | `list saved` (account's saved items)       |
| `/digest <topic>`           | `list <topic>` (accept `r/x` input; strip the `r/`) |
| `/digest new <topic>`       | `list <topic> new`                         |
| `/digest top <topic> [week]`| `list <topic> top week` (t: hour/day/week/month/year/all) |
| `/digest more`              | `more` (continues last listing)            |
| `/digest <n>` or `open <n>` | `open <n>`                                 |
| `/digest src <n>`           | `src <n>` (print the raw link, verbatim)   |
| `/digest login`             | see "Login" below                          |

## Login (personal feed)

Reddit issues each account private RSS URLs keyed by a feed token — no
password or OAuth involved. To connect (or if the script reports `NO_AUTH`):

1. Tell the user to open <https://old.reddit.com/prefs/feeds/> while logged
   in, and copy the **RSS link** under "front page" (it contains
   `?feed=<token>&user=<name>`), then paste it here.
2. Run `auth '<pasted url>'` (quote it — it contains `&`). The script
   verifies the feed, then stores the token in
   `~/.cache/claude-digest/auth.json` with 600 permissions.
3. On `AUTH_OK`, confirm briefly ("personal feed connected") without echoing
   the token or username back.

The pasted URL contains a credential; never print the token, and never put
it in any output the user didn't explicitly request. If the user asks to
log out, delete `~/.cache/claude-digest/auth.json`.

The script persists the last listing in `~/.cache/claude-digest/state.json`,
so item numbers stay valid across turns and even across sessions.

## Rendering a listing

Script output is `n. title` + snippet lines. Rewrite it as:

```
## Reading digest: <topic, phrased naturally>

1. **<Normalized title>** — one-sentence gist drawn from the snippet.
2. …

Give me a number to go deeper on any of these.
```

Keep gists genuinely informative — the user is reading these instead of the
site. If a snippet is empty (link posts), infer the gist from the title and
say what kind of item it is ("links to an external write-up").

## Rendering an opened item

Script output is `TITLE:`, `BODY:`, then flat `[c1]…` comments (RSS gives no
nesting or scores — don't apologize for that, just synthesize). Render as:

```
### <Normalized title>

<Body, lightly edited into readable prose. Keep the author's substance and
tone; trim filler. For a link post, name the destination domain and
summarize the title.>

**What the discussion adds:**

- <Synthesized point shared by several comments.>
- <Notable disagreement or correction.>

> <One or two short verbatim quotes worth reading, attributed as "one
> commenter" — pick the sharpest, not the first.>

Want the source link (`src <n>`) or back to the list?
```

Scale to content: a thin comment section gets two bullets, a rich one gets
more plus a second quote. Never dump all comments.

## Errors

- `FETCH_ERROR` / `PARSE_ERROR` / `EMPTY`: say "that feed isn't available
  right now" (misspelled, private, or rate-limited — suggest retrying in a
  minute if it smells like rate limiting; the script already retries 429s).
- `NO_STATE` / `BAD_INDEX`: ask for a listing first / a valid number.
- Never surface raw script errors or URLs in the failure message.
