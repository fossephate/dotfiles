---
name: cont
description: Continue the work that was in progress, and re-request any tool call that was auto-denied so the user can approve it manually. Use when invoked as /cont, or when the user says "continue" after a permission denial interrupted the work.
argument-hint: (optional) extra instruction or correction for the continuation
---

# Continue

Pick the work back up where it stopped. Two things happen, in this order.

## 1. Re-request anything that was auto-denied

Scan back through this session's tool results for calls that never ran because permission was refused — the auto-approval classifier rejecting them, a hook blocking them, or a `permission mode` denial. They read as a rejection in the tool result rather than as real output. Typical shapes:

- "The user doesn't want to proceed with this tool use"
- "Claude requested permissions to ... but hasn't granted it yet"
- a hook returning a deny/block decision
- any tool result reporting the call was rejected, blocked, or not permitted

For each one still relevant to the task:

- **Re-issue the identical call.** Same tool, same arguments. Reissuing is the whole point — it surfaces a fresh prompt the user can approve by hand. Do not reword the command to slip past the classifier, do not swap it for a different tool that happens to be allowed, and do not silently substitute a weaker version of the action.
- Before the retry, say in one line what you are re-requesting and why it's needed.
- If it's denied a second time, stop retrying that call. Treat the second denial as a real "no": say what stays blocked, and continue with everything else.

Skip re-requesting a call that is no longer needed — the task moved on, or another approach already covered it. Say that you skipped it rather than silently dropping it.

A user turn that only says "no" or "don't" to a specific action is a real refusal, not an auto-denial. Never re-request those.

## 2. Continue the work

Resume the task in progress, without re-explaining what was already done or re-deriving decisions the user already made. Finish it — don't hand back a partial result and ask whether to keep going.

If an argument was passed to `/cont`, treat it as a course correction on top of the resumed work.

If nothing was actually in progress, say so plainly and ask what to pick up, instead of inventing work.
