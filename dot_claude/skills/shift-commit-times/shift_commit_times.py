#!/usr/bin/env python3
"""Rewrite commit times so weekday daytime commits become evening commits.

Any commit whose author/committer time falls on a weekday (Mon-Fri) between
07:00 and 19:00 America/Los_Angeles time is remapped proportionally into the
19:30 -> 01:00 (next day) window of the same evening:

    07:00 -> 19:30
    13:00 -> 22:15
    18:59 -> ~00:59 (next calendar day)

Ordering and relative spacing within a day are preserved. Commits outside the
window, on weekends, or outside the given --since/--until timeframe are left
untouched.

Requires git-filter-repo (pip install git-filter-repo). Rewrites ALL branches
and tags; commit hashes change, so remotes need a force-push afterwards.

Usage:
    shift-commit-times.py [repo] --since 2026-01-01 --until 2026-06-30 --dry-run
    shift-commit-times.py [repo] --since 2026-01-01 --until 2026-06-30 --force
"""

import argparse
import datetime as dt
import os
import subprocess
import sys
from zoneinfo import ZoneInfo

PACIFIC = ZoneInfo("America/Los_Angeles")

WINDOW_START = 7 * 3600           # 07:00 wall clock
WINDOW_END = 19 * 3600            # 19:00 wall clock (exclusive)
TARGET_START = 19 * 3600 + 1800   # 19:30 wall clock
TARGET_LEN = 5.5 * 3600           # 19:30 -> 01:00 next day


def shift_epoch(epoch, since, until):
    """Return a new (epoch, tz_offset_str) if the commit time needs shifting, else None."""
    local = dt.datetime.fromtimestamp(epoch, tz=PACIFIC)
    if since and local.date() < since:
        return None
    if until and local.date() > until:
        return None
    if local.weekday() >= 5:  # Sat/Sun
        return None
    wall = local.hour * 3600 + local.minute * 60 + local.second
    if not (WINDOW_START <= wall < WINDOW_END):
        return None

    frac = (wall - WINDOW_START) / (WINDOW_END - WINDOW_START)
    new_wall = TARGET_START + frac * TARGET_LEN
    naive = dt.datetime.combine(local.date(), dt.time()) + dt.timedelta(seconds=new_wall)
    shifted = naive.replace(tzinfo=PACIFIC)
    offset = shifted.utcoffset()
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    return int(shifted.timestamp()), f"{sign}{total // 3600:02d}{(total % 3600) // 60:02d}"


def shift_date_bytes(raw, since, until):
    """raw is git-filter-repo's b'<epoch> <tzoffset>' form; returns new bytes or None."""
    epoch_str, _, _ = raw.decode().partition(" ")
    result = shift_epoch(int(epoch_str), since, until)
    if result is None:
        return None
    new_epoch, tz = result
    return f"{new_epoch} {tz}".encode()


def fmt(epoch):
    return dt.datetime.fromtimestamp(epoch, tz=PACIFIC).strftime("%a %Y-%m-%d %H:%M:%S %Z")


def list_shifts(since, until):
    """Return [(sha, subject, field, old_epoch, new_epoch)] for every date that would change."""
    out = subprocess.run(
        ["git", "log", "--all", "--format=%H%x09%at%x09%ct%x09%s"],
        check=True, capture_output=True, text=True,
    ).stdout
    shifts = []
    for line in out.splitlines():
        sha, a_epoch, c_epoch, subject = line.split("\t", 3)
        for field, epoch in (("author", int(a_epoch)), ("committer", int(c_epoch))):
            new = shift_epoch(epoch, since, until)
            if new:
                shifts.append((sha, subject, field, epoch, new[0]))
    return shifts


def future_violations(shifts):
    """Shifts whose new timestamp lands after the current moment.

    The evening target window for a daytime commit is later the same day (or
    just past midnight), so running before that window has fully passed would
    stamp commits with times that haven't happened yet — an obvious tell.
    """
    now = dt.datetime.now(tz=PACIFIC).timestamp()
    return [s for s in shifts if s[4] > now]


def report_future_violations(bad):
    print("ABORT: the following shifted timestamps would land in the future:\n", file=sys.stderr)
    seen = set()
    for sha, subject, field, old, new in bad:
        if sha not in seen:
            seen.add(sha)
            print(f"  {sha[:10]}  {subject}", file=sys.stderr)
        print(f"      {field}: {fmt(old)}  ->  {fmt(new)}  (not yet reached)", file=sys.stderr)
    print(
        "\nA commit can only be shifted once its evening target window has passed.\n"
        "Re-run after the latest target time above (typically tomorrow), or exclude\n"
        "today's commits with --until.",
        file=sys.stderr,
    )


def dry_run(since, until):
    shifts = list_shifts(since, until)
    seen = set()
    for sha, subject, field, old, new in shifts:
        if sha not in seen:
            seen.add(sha)
            print(f"{sha[:10]}  {subject}")
        print(f"    {field + ':':<10} {fmt(old)}  ->  {fmt(new)}")
    print(f"\n{len(seen)} commit(s) would be rewritten. Re-run without --dry-run to apply.")
    bad = future_violations(shifts)
    if bad:
        print(file=sys.stderr)
        report_future_violations(bad)
        sys.exit(1)


def apply_rewrite(since, until, force):
    bad = future_violations(list_shifts(since, until))
    if bad:
        report_future_violations(bad)
        sys.exit(1)

    try:
        import git_filter_repo as fr
    except ImportError:
        sys.exit("git-filter-repo is required: pip install git-filter-repo")

    stats = {"changed": 0}

    def commit_callback(commit, _metadata):
        touched = False
        for attr in ("author_date", "committer_date"):
            new = shift_date_bytes(getattr(commit, attr), since, until)
            if new is not None:
                setattr(commit, attr, new)
                touched = True
        if touched:
            stats["changed"] += 1

    fr_args = ["--force"] if force else []
    options = fr.FilteringOptions.parse_args(fr_args, error_on_empty=False)
    fr.RepoFilter(options, commit_callback=commit_callback).run()
    print(f"\nRewrote dates on {stats['changed']} commit(s) across all branches and tags.")
    print("Hashes have changed; use `git push --force-with-lease` to update remotes.")


def parse_date(s):
    return dt.date.fromisoformat(s)


def main():
    parser = argparse.ArgumentParser(
        description="Shift weekday 7am-7pm Pacific commit times into the 7:30pm-1am window."
    )
    parser.add_argument("repo", nargs="?", default=".", help="path to the git repo (default: .)")
    parser.add_argument("--since", type=parse_date, metavar="YYYY-MM-DD",
                        help="only shift commits on/after this Pacific date")
    parser.add_argument("--until", type=parse_date, metavar="YYYY-MM-DD",
                        help="only shift commits on/before this Pacific date")
    parser.add_argument("--dry-run", action="store_true",
                        help="preview which commits would change without rewriting")
    parser.add_argument("--force", action="store_true",
                        help="pass --force to git-filter-repo (needed on non-fresh clones)")
    args = parser.parse_args()

    os.chdir(args.repo)
    if args.dry_run:
        dry_run(args.since, args.until)
    else:
        apply_rewrite(args.since, args.until, args.force)


if __name__ == "__main__":
    main()
