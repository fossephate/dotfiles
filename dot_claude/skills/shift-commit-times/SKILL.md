---
name: shift-commit-times
description: Rewrite git commit timestamps so weekday commits made between 7am and 7pm Pacific are shifted into the 7:30pm-1am evening window, for a given date range. Use when invoked as /shift-commit-times [repo] [--since YYYY-MM-DD] [--until YYYY-MM-DD], or when the user asks to shift, rewrite, or move commit times out of work hours.
---

# Shift Commit Times

Rewrites author and committer dates across ALL branches and tags of a repo:
any commit falling on a weekday (Mon-Fri) between 07:00 and 19:00
America/Los_Angeles time is proportionally remapped into the 19:30 -> 01:00
window of the same evening (7:00am -> 7:30pm, 10:00am -> 8:52pm,
6:59pm -> 12:59am next day). Ordering and relative spacing are preserved.
Timezone handling is DST-aware (PST in winter, PDT in summer). Weekend
commits, evening commits, and commits outside the date range are untouched.

**Future-timestamp guard:** the script refuses to run (both dry-run and
apply exit 1 with an ABORT listing) if any shifted timestamp would land after
the current moment — e.g. a 10am commit from today maps to ~8:52pm tonight,
which hasn't happened yet. Same-day commits can only be shifted once their
evening target time has passed; until then, either wait (typically until
tomorrow) or exclude them with `--until <yesterday>`. Relay this to the user
verbatim when the guard fires — do not work around it by faking dates or
moving commits to a different day.

The implementation is the bundled `shift_commit_times.py` in this skill's
base directory. It depends on the `git-filter-repo` Python package.

## Arguments

`/shift-commit-times [repo] [--since YYYY-MM-DD] [--until YYYY-MM-DD]`

- `repo`: path to the git repository. If omitted, use the current working
  directory (verify it is actually a git repo first).
- `--since` / `--until`: inclusive Pacific-date bounds on which commits get
  shifted. If the user gave a timeframe in prose ("last month", "June"),
  convert it to explicit dates and confirm them in the preview step. If no
  timeframe was given at all, all history is eligible — call that out
  explicitly before applying.

## Workflow

1. **Ensure the dependency.** The script needs `git_filter_repo` importable.
   Use a venv inside this skill's base directory so nothing global is touched:
   - If `<base>/.venv/bin/python -c "import git_filter_repo"` fails (or the
     venv doesn't exist), run `python3 -m venv <base>/.venv` and
     `<base>/.venv/bin/pip install git-filter-repo`.
   - Use `<base>/.venv/bin/python` for all script invocations.

2. **Always dry-run first.** Run:
   `<base>/.venv/bin/python <base>/shift_commit_times.py <repo> [--since ...] [--until ...] --dry-run`
   Show the user the preview (which commits change, old -> new times, total
   count). Dry-run is read-only and safe.

3. **Confirm before applying.** History rewriting is destructive and changes
   every affected hash plus all descendant hashes. Do NOT apply without the
   user confirming after seeing the dry-run — unless they already explicitly
   said to apply/rewrite without preview in this conversation.

4. **Apply.** Same command without `--dry-run`, adding `--force` (required on
   anything but a fresh clone; git-filter-repo refuses otherwise). Note:
   git-filter-repo removes the `origin` remote's old refs and the rewrite
   cannot be undone except from a backup clone or the pre-rewrite reflog.

5. **Report.** Relay how many commits were rewritten and remind the user that
   remotes need `git push --force-with-lease`, and that other clones of the
   repo must be re-cloned or hard-reset.

## Forks that merge from an upstream remote (IMPORTANT)

The rewrite shifts ANY commit in the date window **regardless of author**, and git-filter-repo
rewrites ALL refs — including remote-tracking refs like `refs/remotes/upstream/dev`. On a fork
that periodically merges an upstream (e.g. `~/dev/glassly`), this means merged upstream-authored
commits get new timestamps and hashes, and the stored upstream ref no longer matches what the
real upstream serves. Consequences (hit on 2026-08-13 in glassly):

- The next `git fetch upstream dev` reports a spurious `(forced update)` that looks exactly like
  an upstream force-push.
- `git merge-base` with upstream collapses to an ancient commit, so a naive upstream merge
  fabricates thousands of bogus conflicts.

Mitigations:

- **Warn the user before applying** when the repo has a non-`origin` remote or the dry-run shows
  commits authored by people other than the user: those are likely merged upstream commits, and
  shifting them will break the upstream merge base (and misstate other people's timestamps).
  Suggest tightening `--since` to after the last upstream merge, or accepting the repair below.
- **Repair after the fact**: the fork's `/merge-upstream` skill has a "Preflight: detect history
  rewrites" section — the fix is a `git merge -s ours upstream/<branch>` once trees are verified
  identical, which re-anchors the merge base with zero content change.

## Failure notes

- "Refusing to destructively overwrite repo history" from git-filter-repo
  means `--force` wasn't passed — rerun with it (after user confirmation).
- If the repo has uncommitted changes, git-filter-repo may refuse; ask the
  user whether to stash/commit first rather than doing it silently.
