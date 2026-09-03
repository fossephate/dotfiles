#!/usr/bin/env python3
"""Fetch Reddit RSS feeds and emit compact plain text for the digest skill.

Commands:
  list [sub] [hot|new|top] [hour|day|week|month|year|all]
      (no sub, or sub "home": personal front page if authed, else r/popular;
       sub "saved": the account's saved items)
  auth <pasted-feed-url | token> [username]
  more
  open <n>
  src <n>

State (last listing) lives in ~/.cache/claude-digest/state.json so `open`,
`src`, and `more` can resolve item numbers without refetching.
Output is raw material only — the skill reformats it before showing the user.
"""
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
NS = {"a": "http://www.w3.org/2005/Atom"}
STATE = Path.home() / ".cache" / "claude-digest" / "state.json"
AUTH = Path.home() / ".cache" / "claude-digest" / "auth.json"
LIMIT = 12


def fetch(url):
    last = None
    for attempt in range(4):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429 and attempt < 3:
                time.sleep(6 * (attempt + 1))
                continue
            break
        except urllib.error.URLError as e:
            last = e
            break
    sys.exit(f"FETCH_ERROR: {last}")


def clean(raw, keep_breaks=False):
    """Strip HTML to plain text; drop the 'submitted by /u/x' footer."""
    s = raw or ""
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"</p>|<br\s*/?>|</blockquote>", "\n", s)
    s = re.sub(r"<blockquote>", "\n> ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"submitted by\s+/u/\S+.*", "", s, flags=re.S)
    s = re.sub(r"\[link\]\s*\[comments\]", "", s)
    s = re.sub(r"/?u/[A-Za-z0-9_-]+", "someone", s)
    if keep_breaks:
        s = "\n".join(re.sub(r"[ \t]+", " ", ln).strip() for ln in s.splitlines())
        return re.sub(r"\n{3,}", "\n\n", s).strip()
    return re.sub(r"\s+", " ", s).strip()


def entries(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        sys.exit("PARSE_ERROR: response was not a feed (blocked or not found)")
    out = []
    for e in root.findall("a:entry", NS):
        link = e.find("a:link", NS)
        content = e.find("a:content", NS)
        author = e.find("a:author/a:name", NS)
        out.append({
            "id": (e.findtext("a:id", "", NS) or "").strip(),
            "title": (e.findtext("a:title", "", NS) or "").strip(),
            "link": link.get("href") if link is not None else "",
            "content": content.text if content is not None else "",
            "author": author.text if author is not None else "",
        })
    return out


def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        sys.exit("NO_STATE: run a listing first (e.g. `list programming`)")


def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st))


def print_listing(items, start):
    for i, e in enumerate(items, start):
        snippet = clean(e["content"])[:220]
        print(f"{i}. {e['title']}")
        if snippet:
            print(f"   {snippet}")


def load_auth():
    try:
        return json.loads(AUTH.read_text())
    except (OSError, ValueError):
        return None


def cmd_auth(arg, user=None):
    m = re.search(r"[?&]feed=([A-Za-z0-9]+)", arg)
    token = m.group(1) if m else (arg if re.fullmatch(r"[A-Za-z0-9]{16,}", arg) else None)
    um = re.search(r"[?&]user=([A-Za-z0-9_-]+)", arg)
    user = user or (um.group(1) if um else None)
    if not token or not user:
        sys.exit("AUTH_ERROR: paste the full personal RSS URL "
                 "(contains feed=<token>&user=<name>), or pass `auth <token> <username>`")
    items = entries(fetch(f"https://www.reddit.com/.rss?feed={token}&user={user}&limit=3"))
    if not items:
        sys.exit("AUTH_ERROR: token was accepted but the feed came back empty — check it")
    AUTH.parent.mkdir(parents=True, exist_ok=True)
    AUTH.write_text(json.dumps({"token": token, "user": user}))
    AUTH.chmod(0o600)
    print(f"AUTH_OK: personal feed verified ({len(items)} sample items)")


def cmd_list(sub=None, sort="hot", t="day"):
    auth = load_auth()
    if sub is None:
        sub = "home" if auth else "popular"
    sub = re.sub(r"^/?r/", "", sub.strip("/"))
    if sub in ("home", "front", "me", "saved"):
        if not auth:
            sys.exit("NO_AUTH: personal feed not configured — run the auth command first")
        creds = f"feed={auth['token']}&user={auth['user']}"
        if sub == "saved":
            url = f"https://www.reddit.com/user/{auth['user']}/saved.rss?{creds}&limit={LIMIT}"
        else:
            url = f"https://www.reddit.com/.rss?{creds}&limit={LIMIT}"
    else:
        url = f"https://www.reddit.com/r/{sub}/{sort}/.rss?limit={LIMIT}"
        if sort == "top":
            url += f"&t={t}"
    items = entries(fetch(url))
    if not items:
        sys.exit("EMPTY: no items (feed may be private, banned, or misspelled)")
    print_listing(items, 1)
    save_state({"sub": sub, "sort": sort, "t": t, "url": url,
                "items": [{"title": e["title"], "link": e["link"], "id": e["id"]}
                          for e in items]})


def cmd_more():
    st = load_state()
    after = st["items"][-1]["id"]
    items = entries(fetch(st["url"] + f"&after={after}"))
    known = {e["id"] for e in st["items"]}
    items = [e for e in items if e["id"] not in known]
    if not items:
        sys.exit("EMPTY: no further items")
    print_listing(items, len(st["items"]) + 1)
    st["items"] += [{"title": e["title"], "link": e["link"], "id": e["id"]}
                    for e in items]
    save_state(st)


def resolve(n):
    st = load_state()
    try:
        return st["items"][int(n) - 1]
    except (IndexError, ValueError):
        sys.exit(f"BAD_INDEX: no item {n} in the last listing")


def cmd_open(n):
    item = resolve(n)
    url = item["link"].rstrip("/") + "/.rss?limit=30"
    auth = load_auth()
    if auth:  # lets threads in private communities load; harmless for public ones
        url += f"&feed={auth['token']}&user={auth['user']}"
    items = entries(fetch(url))
    if not items:
        sys.exit("EMPTY: thread unavailable")
    post, comments = items[0], items[1:]
    print(f"TITLE: {post['title']}")
    print(f"BODY:\n{clean(post['content'], keep_breaks=True)[:3000]}\n")
    print(f"COMMENTS ({len(comments)} fetched, flat order, no scores):")
    for i, c in enumerate(comments, 1):
        print(f"[c{i}] {clean(c['content'], keep_breaks=True)[:600]}\n")


def cmd_src(n):
    print(resolve(n)["link"])


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit("usage: list <sub> [sort] [t] | more | open <n> | src <n>")
    cmd, rest = args[0], args[1:]
    if cmd == "list":
        cmd_list(*rest)
    elif cmd == "auth":
        cmd_auth(*rest)
    elif cmd == "more":
        cmd_more()
    elif cmd == "open":
        cmd_open(rest[0])
    elif cmd == "src":
        cmd_src(rest[0])
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
