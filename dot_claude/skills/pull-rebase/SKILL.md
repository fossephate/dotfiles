---
name: pull-rebase
description: Pull a branch with rebase, resolve all merge conflicts, and summarize how each conflict was resolved. Use when invoked as /pull-rebase <branch>, or when the user asks to pull and rebase onto a branch and fix the resulting conflicts.
---

# Pull–rebase with conflict resolution

The argument is the remote branch to pull (e.g. `/pull-rebase staging`). If no branch is given, ask the user which branch to pull — do not guess.

## Steps

1. **Preflight.** Run `git status` and `git log --oneline -5`.
   - If a rebase or merge is already in progress, tell the user and ask whether to continue it or abort it first. Do not start a new pull on top of it.
   - If the working tree is dirty, ask the user whether to stash the changes (and pop after) or abort. Never discard local changes silently.

2. **Pull with rebase.** Run:
   ```
   git pull --rebase origin <branch>
   ```
   If it completes cleanly, report that there were no conflicts, show the new HEAD, and stop (pop the stash first if one was made).

3. **Resolve conflicts, one commit at a time.** While the rebase is stopped:
   - List conflicted files with `git status`, then find markers with `grep -n '<<<<<<<' <file>`.
   - For each conflict, Read enough surrounding context to understand **both intents** — during `pull --rebase`, "ours/HEAD" is the incoming upstream branch and "theirs" is the local commit being replayed. Keep that orientation straight.
   - Resolution policy:
     - **Mechanical conflicts** (imports, adjacent additions, formatting, lockfiles, generated files like `*.pbxproj` or `uv.lock`): resolve autonomously, preferring the union of both sides when both are additive.
     - **Lockfiles/generated files** that can be regenerated: prefer taking one side wholesale and regenerating (e.g. `uv lock`, `pod install`) rather than hand-merging, when the regeneration command is cheap and obvious.
     - **Semantic conflicts** (both sides changed the same logic differently, a function was deleted on one side and modified on the other, conflicting config values): do NOT guess. Use AskUserQuestion with the concrete options (keep local version / keep upstream version / combine, with a short preview of each side).
   - After resolving each file, verify no markers remain (`grep -n '<<<<<<<\|=======\|>>>>>>>'`), then `git add` it.
   - Continue with `GIT_EDITOR=true git rebase --continue` and repeat until the rebase finishes.
   - Keep notes as you go: for every conflicted file, record which sides collided and how you resolved it. You need this for the summary — don't reconstruct it afterward.

4. **Verify.** After the rebase completes:
   - Run `git status` to confirm a clean tree and `git log --oneline -5` to show the result.
   - If a quick, cheap project check exists (build already known to the session, lint, typecheck of touched files), run it on the conflicted files only. Report failures; do not go on a fixing spree beyond the conflict resolution itself.
   - If changes were stashed in step 1, `git stash pop` now and report any conflicts from the pop.

5. **Summarize.** End with a per-file summary:
   - Each conflicted file, what the two sides were doing, and how it was resolved (union / kept local / kept upstream / combined / user-decided).
   - Any resolutions you're less confident about, flagged explicitly.
   - Do **not** push. Mention that the branch diverged from its remote (if it did) and that the user can ask for a `push --force-with-lease` if this rewrote published history.

## Notes

- Never use `git checkout --ours/--theirs` blindly on a source file — only on lockfiles/generated files, and say so in the summary.
- If the same file conflicts repeatedly across commits, consider suggesting `git rerere` to the user, but don't enable it yourself.
- If the rebase becomes a mess (cascading conflicts the user would rather avoid), offer `git rebase --abort` as a clean escape hatch before things are half-done.
