#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc.
"""Which methods do NaNoGenMo's finished entries name, year by year (2013-2025)?

National Novel Generation Month runs every November on GitHub. Each participant opens an
issue in that year's repository, and the organisers label finished entries "completed".
This reads every issue and every issue comment of the 13 yearly repositories through
GitHub's public REST API (no token). For each completed entry it keeps the text its opener
wrote (title, issue body, and the opener's own comments up to the end of the following
January) and flags which method families that text names: pretrained language models
(GPT-2 onward), earlier neural networks, Markov chains, Tracery or context-free grammars,
Project Gutenberg, and whether it links to source code or pastes a block of code.

A mention is not a use. Every language-model mention is written to snippets.jsonl with
its context, so that the pre-registered primary coding can decide whether the novel's text
came from a language model.

Logins are never written: comments are matched to the issue opener by a salted hash, and
the cache keeps only the fields the census needs. Made by MV2 of Munim, Inc., with AI
agents working in his name.

Usage: python census.py --out-dir OUT --cache-dir CACHE [--years 2013-2025]
                        [--wait-prereg-minutes 60] [--budget-minutes 220]
"""
import argparse
import csv
import hashlib
import json
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

VERSION = "0.1.0"
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
UA = "mv2-nanogenmo-census/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % VERSION
CENSUS_REPO = "munimtechnologies/nanogenmo-census"
PREREG_PATH = "census/2026-11/PREREGISTRATION.md"
PER_PAGE = 100
MAX_PAGES = 300
REPOS = {2013: "dariusk/NaNoGenMo", 2014: "dariusk/NaNoGenMo-2014", 2015: "dariusk/NaNoGenMo-2015"}
REPOS.update({y: "NaNoGenMo/%d" % y for y in range(2016, 2026)})
# Completed projects per year in Nick Montfort, "A Glance at NaNoGenMo 2024" (2025-01-02).
MONTFORT = {2020: 56, 2021: 56, 2022: 33, 2023: 23, 2024: 22}

# Term families, matched case-insensitively. Keys are what entries.csv reports.
FAMILIES = {
    "llm": [
        ("gpt", r"\b(?:chat\s?)?gpt"),
        ("openai", r"\bopen\s?ai\b"),
        ("llm", r"\bllms?\b"),
        ("language model", r"\blanguage models?\b"),
        ("transformer", r"\btransformers?\b"),
        ("hugging face", r"\bhugging\s?face\b"),
        ("bert", r"\b(?:distil)?bert\b|\broberta\b"),
        ("llama", r"\b(?:o?llama|alpaca|vicuna)"),
        ("mistral", r"\bmi[sx]tral"),
        ("claude", r"\bclaude\b|\banthropic\b"),
        ("gemini", r"\bgemini\b"),
        ("other model", r"\b(?:qwen|gemma|deepseek|davinci|novelai|sudowrite|kobold|copilot|phi-[234])"),
    ],
    "neural": [
        ("rnn", r"rnn"),
        ("lstm", r"\blstm"),
        ("neural network", r"\bneural\s+net"),
        ("seq2seq", r"seq2seq"),
    ],
    "markov": [("markov", r"markov")],
    "grammar": [("tracery", r"\btracery\b"), ("context-free grammar", r"\bcontext[-\s]free\s+grammars?\b")],
    "gutenberg": [("gutenberg", r"gutenberg")],
}
COMPILED = {fam: [(k, re.compile(p, re.I)) for k, p in terms] for fam, terms in FAMILIES.items()}
LLM_ANY = re.compile("|".join("(?:%s)" % p for _, p in FAMILIES["llm"]), re.I)

URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`]+", re.I)
CODE_HOSTS = ("gitlab.com", "codeberg.org", "bitbucket.org", "sr.ht", "glitch.com", "replit.com", "repl.it",
              "observablehq.com", "codepen.io", "colab.research.google.com", "gist.github.com", "editor.p5js.org",
              "jsfiddle.net", "notabug.org", "sourceforge.net", "codesandbox.io")
CODE_EXT = (".py", ".js", ".mjs", ".ts", ".rb", ".pl", ".ipynb", ".bas", ".lisp", ".el", ".hs", ".go", ".rs",
            ".java", ".php", ".sh", ".c", ".cpp", ".lua", ".jl", ".scm", ".rkt", ".clj", ".ml", ".swift", ".kt",
            ".cs", ".r")
GITHUB_NOT_CODE = {"nanogenmo", "user-attachments", "orgs", "settings", "notifications", "sponsors", "topics",
                   "features", "marketplace", "about", "login", "search"}
GITHUB_NOT_CODE_SUB = {"issues", "pull", "pulls", "discussions", "wiki"}
FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.S)

FAMILY_NAMES = {"llm": "Language-model terms", "neural": "Earlier neural", "markov": "Markov",
                "grammar": "Tracery/CFG", "gutenberg": "Gutenberg"}
ENTRY_COLS = (["year", "issue", "url", "title", "created_at", "state", "own_comments"]
              + [c for fam in FAMILIES for c in (fam, fam + "_terms")] + ["code_link", "inline_code"])
YEAR_COLS = (["year", "issues", "completed", "completion_rate"]
             + [c for fam in FAMILIES for c in (fam, fam + "_share")]
             + ["code_link", "code_link_share", "inline_code", "inline_code_share"])
CODING_COLS = ["year", "issue", "url", "title", "llm_terms", "code", "quote", "note"]


def log(msg):
    print(msg, flush=True)


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- text checks

def term_hits(text):
    """{family: sorted term keys found in text}; families with no hit are left out."""
    out = {}
    for fam, terms in COMPILED.items():
        found = sorted(k for k, rx in terms if rx.search(text or ""))
        if found:
            out[fam] = found
    return out


def is_code_url(url):
    """True for a link to a code repository, gist, notebook, code sandbox or source file."""
    p = urllib.parse.urlparse(url.rstrip(".,;:!?*_"))
    host = p.netloc.lower().split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    path = p.path.lower()
    parts = [x for x in path.split("/") if x]
    if host == "github.com":
        if len(parts) < 2 or parts[0] in GITHUB_NOT_CODE:
            return False
        if parts[0] == "dariusk" and parts[1].startswith("nanogenmo"):
            return False
        return not (len(parts) >= 3 and parts[2] in GITHUB_NOT_CODE_SUB)
    if any(host == h or host.endswith("." + h) for h in CODE_HOSTS):
        return True
    return path.endswith(CODE_EXT)


def has_inline_code(text, min_lines=5):
    """True when the text holds a fenced block with at least min_lines non-empty lines."""
    for m in FENCE_RE.finditer(text or ""):
        if sum(1 for ln in m.group(1).splitlines() if ln.strip()) >= min_lines:
            return True
    return False


def llm_snippets(parts, width=200, limit=6):
    """Context around each language-model term, for the primary coding."""
    out = []
    for where, text in parts:
        for m in LLM_ANY.finditer(text or ""):
            a, b = max(0, m.start() - width), min(len(text), m.end() + width)
            out.append({"where": where, "term": m.group(0), "text": text[a:b]})
            if len(out) >= limit:
                return out
    return out


# ---------------------------------------------------------------- slim records

def author_key(login, salt):
    """Salted hash of a login, used only to match comments to the issue opener."""
    if not login:
        return ""
    return hashlib.sha256((salt + ":" + login.lower()).encode("utf-8")).hexdigest()[:16]


def slim_issue(x, salt):
    labels = []
    for lab in x.get("labels") or []:
        labels.append((lab.get("name") or "") if isinstance(lab, dict) else str(lab))
    return {"number": x.get("number"), "title": x.get("title") or "", "state": x.get("state") or "",
            "created_at": x.get("created_at") or "", "closed_at": x.get("closed_at"),
            "labels": sorted(labels), "comments": x.get("comments", 0), "is_pr": "pull_request" in x,
            "body": x.get("body") or "", "author": author_key((x.get("user") or {}).get("login"), salt)}


def slim_comment(x, salt):
    num = None
    try:
        num = int((x.get("issue_url") or "").rstrip("/").rsplit("/", 1)[1])
    except (IndexError, ValueError):
        pass
    return {"issue": num, "created_at": x.get("created_at") or "", "body": x.get("body") or "",
            "author": author_key((x.get("user") or {}).get("login"), salt)}


def load_salt(cache_dir):
    fn = os.path.join(cache_dir, "salt.txt")
    if os.path.exists(fn):
        with open(fn, encoding="utf-8") as f:
            s = f.read().strip()
        if s:
            return s
    s = secrets.token_hex(16)
    with open(fn, "w", encoding="utf-8") as f:
        f.write(s)
    return s


# ---------------------------------------------------------------- GitHub

class OutOfTime(Exception):
    pass


class HttpFailure(Exception):
    def __init__(self, status, path):
        super().__init__("HTTP %s for %s" % (status, path))
        self.status = status


def default_opener(req):
    """(status, lower-case headers, body bytes); HTTP errors are returned, not raised."""
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return e.code, {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}, body


def request(url, accept="application/vnd.github+json"):
    return urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})


class GitHub:
    """Unauthenticated REST client that waits out the rate limit and caches slim pages."""

    def __init__(self, cache_dir, salt, opener=default_opener, pause=1.0, deadline=None, sleep=time.sleep,
                 clock=time.time):
        self.cache_dir, self.salt, self.opener = cache_dir, salt, opener
        self.pause, self.deadline, self.sleep, self.clock = pause, deadline, sleep, clock
        self.requests = 0
        self.cache_hits = 0
        self.waits = []
        self.remaining = None
        self.reset = None

    def _note(self, headers):
        try:
            self.remaining = int(headers.get("x-ratelimit-remaining"))
        except (TypeError, ValueError):
            self.remaining = None
        try:
            self.reset = int(headers.get("x-ratelimit-reset"))
        except (TypeError, ValueError):
            self.reset = None

    def _wait_reset(self):
        now = self.clock()
        wait = max(5, (self.reset - now + 5) if self.reset else 600)
        if self.deadline is not None and now + wait > self.deadline:
            raise OutOfTime()
        self.waits.append(round(wait))
        log("rate limit: waiting %d s" % round(wait))
        self.sleep(wait)
        self.remaining = None

    def get(self, path):
        for attempt in range(8):
            if self.deadline is not None and self.clock() > self.deadline:
                raise OutOfTime()
            if self.remaining == 0:
                self._wait_reset()
            try:
                status, headers, body = self.opener(request(API + path))
            except (urllib.error.URLError, TimeoutError, OSError):
                self.sleep(10 * (attempt + 1))
                continue
            self.requests += 1
            self._note(headers)
            if status == 200:
                self.sleep(self.pause)
                return json.loads(body.decode("utf-8"))
            if status in (403, 429):
                if self.remaining == 0:
                    continue
                ra = str(headers.get("retry-after") or "")
                self.sleep(int(ra) if ra.isdigit() else 60 * (attempt + 1))
                continue
            if status >= 500:
                self.sleep(15 * (attempt + 1))
                continue
            raise HttpFailure(status, path)
        raise HttpFailure(0, path)

    def page(self, kind, repo, page):
        """One listing page of issues or comments, oldest first, from the cache when present."""
        fn = os.path.join(self.cache_dir, "%s__%s__%03d.json" % (repo.replace("/", "__"), kind, page))
        if os.path.exists(fn):
            self.cache_hits += 1
            with open(fn, encoding="utf-8") as f:
                return json.load(f)
        query = {"sort": "created", "direction": "asc", "per_page": PER_PAGE, "page": page}
        if kind == "issues":
            query["state"] = "all"
            endpoint = "issues"
        else:
            endpoint = "issues/comments"
        path = "/repos/%s/%s?%s" % (repo, endpoint, urllib.parse.urlencode(query))
        data = self.get(path)
        if not isinstance(data, list):
            raise HttpFailure("not a list", path)
        slim = [slim_issue(x, self.salt) if kind == "issues" else slim_comment(x, self.salt) for x in data]
        tmp = fn + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(slim, f)
        os.replace(tmp, fn)
        return slim


def fetch_all(gh, repo, kind):
    items = []
    for page in range(1, MAX_PAGES + 1):
        batch = gh.page(kind, repo, page)
        items.extend(batch)
        if len(batch) < PER_PAGE:
            break
    return items


def prereg_status(opener, sleep, minutes, every=120):
    """Poll the raw file until the pre-registration is on main, then read its first commit time."""
    raw = "%s/%s/main/%s" % (RAW, CENSUS_REPO, PREREG_PATH)
    waited = 0
    while True:
        try:
            status = opener(request(raw, "text/plain"))[0]
        except (urllib.error.URLError, TimeoutError, OSError):
            status = 0
        if status == 200 or waited >= minutes * 60:
            break
        sleep(every)
        waited += every
    out = {"live": status == 200, "waited_seconds": waited, "seen_live_at": now_iso() if status == 200 else None,
           "committed_at": None}
    if status == 200:
        url = "%s/repos/%s/commits?%s" % (API, CENSUS_REPO, urllib.parse.urlencode({"path": PREREG_PATH,
                                                                                   "per_page": 100}))
        try:
            st, _, body = opener(request(url))
            data = json.loads(body.decode("utf-8")) if st == 200 else []
            if isinstance(data, list) and data:
                out["committed_at"] = data[-1]["commit"]["committer"]["date"]
                out["sha"] = data[-1]["sha"]
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError, IndexError, TypeError):
            pass
    return out


# ---------------------------------------------------------------- census

def entry_url(repo, number):
    return "https://github.com/%s/issues/%d" % (repo, number)


def is_completed(issue):
    return any(str(lab).lower() == "completed" for lab in issue.get("labels") or [])


def is_admin(issue):
    return any(str(lab).lower() == "admin" for lab in issue.get("labels") or [])


def build_entries(year, repo, issues, comments):
    """One row per completed entry (pull requests left out), plus LLM snippets."""
    by_issue = defaultdict(list)
    for c in comments:
        by_issue[c.get("issue")].append(c)
    end = "%d-02-01T00:00:00Z" % (year + 1)
    rows, snips = [], []
    for i in sorted(issues, key=lambda x: x["number"]):
        if i.get("is_pr") or not is_completed(i):
            continue
        own = [c for c in sorted(by_issue.get(i["number"], []), key=lambda c: c.get("created_at") or "")
               if i.get("author") and c.get("author") == i["author"] and (c.get("created_at") or "") < end]
        parts = [("title", i.get("title") or ""), ("body", i.get("body") or "")]
        parts += [("comment %d" % n, c.get("body") or "") for n, c in enumerate(own, 1)]
        hits = {}
        for _, text in parts:
            for fam, keys in term_hits(text).items():
                hits.setdefault(fam, set()).update(keys)
        urls = [u for _, text in parts[1:] for u in URL_RE.findall(text)]
        row = {"year": year, "issue": i["number"], "url": entry_url(repo, i["number"]), "title": i.get("title") or "",
               "created_at": i.get("created_at") or "", "state": i.get("state") or "", "own_comments": len(own)}
        for fam in FAMILIES:
            row[fam] = int(fam in hits)
            row[fam + "_terms"] = ";".join(sorted(hits.get(fam, ())))
        row["code_link"] = int(any(is_code_url(u) for u in urls))
        row["inline_code"] = int(any(has_inline_code(text) for _, text in parts[1:]))
        rows.append(row)
        if row["llm"]:
            snips.append({"year": year, "issue": i["number"], "url": row["url"], "title": row["title"],
                          "terms": row["llm_terms"], "snippets": llm_snippets(parts)})
    return rows, snips


def year_row(year, issues, rows):
    n_issues = sum(1 for i in issues if not i.get("is_pr") and not is_admin(i))
    n = len(rows)
    out = {"year": year, "issues": n_issues, "completed": n,
           "completion_rate": round(n / n_issues, 3) if n_issues else None}
    for k in list(FAMILIES) + ["code_link", "inline_code"]:
        c = sum(r[k] for r in rows)
        out[k] = c
        out[k + "_share"] = round(c / n, 3) if n else 0.0
    return out


def grade(by_year):
    """The mechanically gradable predictions (P1, P2, P5, P6); P3 and P4 need the primary coding."""
    def have(ys):
        return all(y in by_year for y in ys)

    out = {}
    if have(MONTFORT):
        found = {y: by_year[y]["completed"] for y in MONTFORT}
        matches = sum(1 for y, n in MONTFORT.items() if found[y] == n)
        out["P1"] = {"held": matches >= 4, "detail": "%d of 5 years match exactly; found %s, Montfort %s" % (
            matches, ", ".join("%d: %d" % (y, found[y]) for y in sorted(found)),
            ", ".join("%d: %d" % (y, n) for y, n in sorted(MONTFORT.items())))}
    else:
        out["P1"] = {"held": None, "detail": "years missing"}
    ys = range(2013, 2019)
    if have(ys):
        worst = max(by_year[y]["llm_share"] for y in ys)
        out["P2"] = {"held": worst <= 0.10, "detail": "highest language-model-term share 2013-2018: %.3f" % worst}
    else:
        out["P2"] = {"held": None, "detail": "years missing"}
    for key in ("P3", "P4"):
        out[key] = {"held": None, "detail": "graded from the primary coding of snippets.jsonl"}
    ys = range(2013, 2026)
    if have(ys):
        mx = max(by_year[y]["neural_share"] for y in ys)
        top = [y for y in ys if by_year[y]["neural_share"] == mx]
        out["P5"] = {"held": mx > 0 and all(2016 <= y <= 2019 for y in top),
                     "detail": "highest earlier-neural share %.3f in %s" % (mx, ", ".join(str(y) for y in top))}
    else:
        out["P5"] = {"held": None, "detail": "years missing"}
    if have(range(2014, 2026)):
        late = max(by_year[y]["completed"] for y in range(2022, 2026))
        early = min(by_year[y]["completed"] for y in range(2014, 2022))
        out["P6"] = {"held": late < early,
                     "detail": "most completed in 2022-2025: %d; fewest in 2014-2021: %d" % (late, early)}
    else:
        out["P6"] = {"held": None, "detail": "years missing"}
    return out


def mention_view(rows):
    """Exploratory: code links among 2023-2025 entries that name a language-model term or not."""
    late = [r for r in rows if r["year"] >= 2023]
    llm = [r for r in late if r["llm"]]
    other = [r for r in late if not r["llm"]]

    def share(rs):
        return round(sum(r["code_link"] for r in rs) / len(rs), 3) if rs else None

    return {"entries_2023_2025": len(late), "with_language_model_term": len(llm),
            "code_link_share_with_term": share(llm), "code_link_share_without_term": share(other)}


def pc(x):
    return "" if x is None else "%.1f%%" % (100 * x)


def cnt(r, k):
    return "%d (%s)" % (r[k], pc(r[k + "_share"]))


def verdict(g):
    return {True: "held", False: "did not hold", None: "pending"}[g["held"]]


def report(by_year, grades, mv, meta):
    p = meta.get("prereg") or {}
    if p.get("live"):
        pre = "live on main, first committed %s" % (p.get("committed_at") or "(commit time unread)")
    else:
        pre = p.get("note") or "not live"
    lines = ["# NaNoGenMo census: which methods finished entries name, 2013-2025", "",
             "census.py %s. Read from GitHub's public API between %s and %s UTC. Pre-registration: %s." % (
                 VERSION, meta.get("started_at"), meta.get("finished_at"), pre), "",
             "Made by MV2 of Munim, Inc., with AI agents working in his name. Data CC BY 4.0, code Apache-2.0.", "",
             "Completed = issues carrying the organisers' `completed` label when read. Each entry's text is its "
             "title, its body and its opener's own comments up to the end of the following January. A term is a "
             "mention, not a use: whether a language model wrote the novel is decided by the primary coding.", "",
             "| Year | Issues | Completed | Completion rate | %s | %s | %s | %s | %s | Code link |" % tuple(
                 FAMILY_NAMES[f] for f in FAMILIES),
             "|---|---|---|---|---|---|---|---|---|---|"]
    for y in sorted(by_year):
        r = by_year[y]
        lines.append("| %d | %d | %d | %s | %s | %s | %s | %s | %s | %s |" % (
            y, r["issues"], r["completed"], pc(r["completion_rate"]), cnt(r, "llm"), cnt(r, "neural"),
            cnt(r, "markov"), cnt(r, "grammar"), cnt(r, "gutenberg"), cnt(r, "code_link")))
    lines += ["", "Issues = issues opened in the year's repository, without pull requests and admin issues.", "",
              "## Predictions this script can grade", ""]
    for k in sorted(grades):
        lines.append("- **%s**: %s. %s" % (k, verdict(grades[k]), grades[k]["detail"]))
    lines += ["", "## Exploratory (not a prediction)", "",
              "2023-2025: %d completed entries, %d name a language-model term. Share linking to code: %s with a "
              "term, %s without." % (mv["entries_2023_2025"], mv["with_language_model_term"],
                                     pc(mv["code_link_share_with_term"]), pc(mv["code_link_share_without_term"]))]
    bad = {y: s for y, s in (meta.get("status") or {}).items() if s != "ok"}
    if bad:
        lines += ["", "Years not read in full: " + "; ".join("%s: %s" % (y, s) for y, s in sorted(bad.items()))]
    lines += ["", "## Limits", "",
              "- The `completed` label is the organisers' own; an entry that finished without it is not counted, "
              "and labels can change after the event.",
              "- Terms are matched in the opener's own words only. Methods described only in a linked repository, "
              "a blog post or the novel itself are missed.",
              "- Term matching over-counts (a critique of LLMs, a character named Claude) and under-counts (a model "
              "named in a way the list does not cover). The language-model column is a mention count; the primary "
              "coding reads every mention.",
              "- A code link means a link to a code host, sandbox or source file. It does not check that the link "
              "still works or that the code is complete.", ""]
    return "\n".join(lines)


def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def parse_years(s):
    a, _, b = s.partition("-")
    lo, hi = int(a), int(b or a)
    return [y for y in range(lo, hi + 1) if y in REPOS]


def main(argv=None, opener=None, sleep=time.sleep, clock=time.time):
    ap = argparse.ArgumentParser(description="NaNoGenMo method census (MV2 of Munim, Inc.)")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--cache-dir", default="cache")
    ap.add_argument("--years", default="2013-2025")
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--budget-minutes", type=float, default=220)
    ap.add_argument("--wait-prereg-minutes", type=float, default=0)
    a = ap.parse_args(argv)
    opener = opener or default_opener
    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(a.cache_dir, exist_ok=True)
    started = now_iso()
    prereg = {"live": None, "note": "not checked (--wait-prereg-minutes 0)"}
    if a.wait_prereg_minutes > 0:
        prereg = prereg_status(opener, sleep, a.wait_prereg_minutes)
        log("pre-registration: %s" % json.dumps(prereg))
        if not prereg["live"]:
            write_json(os.path.join(a.out_dir, "meta.json"), {
                "version": VERSION, "started_at": started, "prereg": prereg,
                "error": "pre-registration not live; nothing fetched"})
            log("pre-registration not live after %s minutes; nothing fetched" % a.wait_prereg_minutes)
            return 3
    gh = GitHub(a.cache_dir, load_salt(a.cache_dir), opener=opener, pause=a.pause,
                deadline=clock() + a.budget_minutes * 60, sleep=sleep, clock=clock)
    years = parse_years(a.years)
    rows, snips, by_year, status = [], [], {}, {}
    for y in years:
        repo = REPOS[y]
        try:
            issues = fetch_all(gh, repo, "issues")
            comments = fetch_all(gh, repo, "comments")
        except OutOfTime:
            status[y] = "out of time"
            log("%d: out of time" % y)
            continue
        except HttpFailure as exc:
            status[y] = str(exc)
            log("%d: %s" % (y, exc))
            continue
        r, s = build_entries(y, repo, issues, comments)
        rows += r
        snips += s
        by_year[y] = year_row(y, issues, r)
        status[y] = "ok"
        log("%d %s: %d issues, %d comments, %d completed; requests %d, cache hits %d" % (
            y, repo, len(issues), len(comments), len(r), gh.requests, gh.cache_hits))
    complete = all(status.get(y) == "ok" for y in years)
    grades = grade(by_year)
    mv = mention_view(rows)
    meta = {"version": VERSION, "started_at": started, "finished_at": now_iso(), "prereg": prereg,
            "repos": {str(y): REPOS[y] for y in years}, "status": {str(y): s for y, s in status.items()},
            "complete": complete, "requests": gh.requests, "cache_hits": gh.cache_hits, "rate_limit_waits": gh.waits}
    write_csv(os.path.join(a.out_dir, "entries.csv"), ENTRY_COLS, rows)
    write_csv(os.path.join(a.out_dir, "years.csv"), YEAR_COLS, [by_year[y] for y in sorted(by_year)])
    write_csv(os.path.join(a.out_dir, "coding.csv"), CODING_COLS,
              [{"year": s["year"], "issue": s["issue"], "url": s["url"], "title": s["title"],
                "llm_terms": s["terms"]} for s in snips])
    with open(os.path.join(a.out_dir, "snippets.jsonl"), "w", encoding="utf-8") as f:
        for s in snips:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    write_json(os.path.join(a.out_dir, "meta.json"), meta)
    write_json(os.path.join(a.out_dir, "summary.json"), {
        "version": VERSION, "years": [by_year[y] for y in sorted(by_year)], "predictions": grades,
        "exploratory": mv, "complete": complete})
    with open(os.path.join(a.out_dir, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write(report(by_year, grades, mv, meta))
    log(json.dumps({"complete": complete, "predictions": grades, "exploratory": mv}))
    return 0 if complete else 2


if __name__ == "__main__":
    sys.exit(main())
