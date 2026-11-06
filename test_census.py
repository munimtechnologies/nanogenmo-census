# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc.
"""Offline tests for census.py: GitHub is replaced by a stub, nothing goes on the network."""
import csv
import json
import os
import tempfile
import unittest
import urllib.parse

import census

A, B = "alice", "bob"


def issue(number, title, body, login=A, labels=("completed",), pr=False, created="2024-11-02T10:00:00Z"):
    x = {"number": number, "title": title, "body": body, "state": "open", "created_at": created,
         "closed_at": None, "comments": 0, "labels": [{"name": lab} for lab in labels], "user": {"login": login}}
    if pr:
        x["pull_request"] = {"url": "x"}
    return x


def comment(repo, number, body, login=A, created="2024-11-20T10:00:00Z"):
    return {"issue_url": "https://api.github.com/repos/%s/issues/%d" % (repo, number), "body": body,
            "created_at": created, "user": {"login": login}}


class TermTests(unittest.TestCase):
    def test_families(self):
        h = census.term_hits("We fine-tuned GPT-2 and then ran a Markov chain over Project Gutenberg texts.")
        self.assertEqual(h["llm"], ["gpt"])
        self.assertEqual(h["markov"], ["markov"])
        self.assertEqual(h["gutenberg"], ["gutenberg"])
        self.assertNotIn("neural", h)
        h = census.term_hits("A Tracery grammar and a char-rnn trained on an LSTM; no language models.")
        self.assertEqual(h["grammar"], ["tracery"])
        self.assertEqual(h["neural"], ["lstm", "rnn"])
        self.assertEqual(h["llm"], ["language model"])
        self.assertEqual(census.term_hits("Robert and Albert wrote 50,000 words by hand."), {})
        h = census.term_hits("Uses ChatGPT via the OpenAI API, then Claude and llama3 through Ollama.")
        self.assertEqual(h["llm"], ["claude", "gpt", "llama", "openai"])

    def test_code_urls(self):
        yes = ["https://github.com/someone/novel-gen", "https://github.com/someone/novel-gen/blob/main/gen.py",
               "https://gist.github.com/someone/abc123", "https://gitlab.com/someone/gen",
               "https://example.com/files/generate.py", "https://www.github.com/a/b."]
        no = ["https://github.com/NaNoGenMo/2024/issues/5", "https://github.com/user-attachments/files/1/novel.pdf",
              "https://github.com/someone", "https://github.com/dariusk/NaNoGenMo-2015/issues/3",
              "https://github.com/a/b/issues/3", "https://example.com/novel.pdf", "https://someone.github.io/novel/"]
        for u in yes:
            self.assertTrue(census.is_code_url(u), u)
        for u in no:
            self.assertFalse(census.is_code_url(u), u)

    def test_inline_code(self):
        self.assertTrue(census.has_inline_code("Intro\n```python\na\nb\nc\nd\ne\n```\n"))
        self.assertFalse(census.has_inline_code("```\na\nb\n\nc\nd\n```"))
        self.assertFalse(census.has_inline_code(""))

    def test_author_key(self):
        self.assertEqual(census.author_key("Alice", "s"), census.author_key("alice", "s"))
        self.assertNotEqual(census.author_key("alice", "s"), census.author_key("alice", "t"))
        self.assertEqual(census.author_key(None, "s"), "")
        self.assertNotIn("alice", census.author_key("alice", "s"))


class EntryTests(unittest.TestCase):
    def test_build_entries(self):
        repo = "NaNoGenMo/2024"
        salt = "s"
        issues = [census.slim_issue(x, salt) for x in [
            issue(1, "Robot novel", "Uses GPT-2. Code: https://github.com/alice/gen"),
            issue(2, "Not finished", "markov", labels=()),
            issue(3, "A pull request", "gpt", pr=True),
            issue(4, "Admin", "rules", login=B, labels=("admin",)),
            issue(5, "Grammar book", "Pure Tracery.", login=B, labels=("Completed", "preview")),
        ]]
        self.assertNotIn("login", json.dumps(issues))
        comments = [census.slim_comment(x, salt) for x in [
            comment(repo, 1, "Added a Markov pass."),
            comment(repo, 1, "Have you tried an LSTM?", login=B),
            comment(repo, 1, "Later I added Claude.", created="2025-02-01T00:00:00Z"),
            comment(repo, 5, "Done. ```\n1\n2\n3\n4\n5\n```", login=B),
        ]]
        self.assertEqual([c["issue"] for c in comments], [1, 1, 1, 5])
        rows, snips = census.build_entries(2024, repo, issues, comments)
        self.assertEqual([r["issue"] for r in rows], [1, 5])
        r1, r5 = rows
        self.assertEqual((r1["llm"], r1["markov"], r1["neural"], r1["code_link"]), (1, 1, 0, 1))
        self.assertEqual(r1["llm_terms"], "gpt")
        self.assertEqual(r1["own_comments"], 1)
        self.assertEqual(r1["url"], "https://github.com/NaNoGenMo/2024/issues/1")
        self.assertEqual((r5["llm"], r5["grammar"], r5["code_link"], r5["inline_code"]), (0, 1, 0, 1))
        self.assertEqual(len(snips), 1)
        self.assertEqual(snips[0]["issue"], 1)
        self.assertIn("GPT-2", snips[0]["snippets"][0]["text"])
        row = census.year_row(2024, issues, rows)
        self.assertEqual((row["issues"], row["completed"], row["llm"], row["llm_share"]), (3, 2, 1, 0.5))


class GradeTests(unittest.TestCase):
    def test_grades(self):
        by_year = {}
        for y in range(2013, 2026):
            completed = {2020: 56, 2021: 56, 2022: 33, 2023: 23, 2024: 20}.get(y, 80 if y < 2020 else 25)
            by_year[y] = {"completed": completed, "llm_share": 0.02 if y < 2019 else 0.3,
                          "neural_share": 0.2 if y == 2017 else 0.05}
        g = census.grade(by_year)
        self.assertTrue(g["P1"]["held"])
        self.assertTrue(g["P2"]["held"])
        self.assertTrue(g["P5"]["held"])
        self.assertTrue(g["P6"]["held"])
        self.assertIsNone(g["P3"]["held"])
        by_year[2016]["llm_share"] = 0.2
        by_year[2021]["completed"] = 20
        g = census.grade(by_year)
        self.assertFalse(g["P2"]["held"])
        self.assertFalse(g["P6"]["held"])
        self.assertIsNone(census.grade({2024: by_year[2024]})["P1"]["held"])


class RateLimitTests(unittest.TestCase):
    def test_waits_for_reset(self):
        now = [1000.0]
        answers = [(403, {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1300"}, b"{}"),
                   (200, {"x-ratelimit-remaining": "59", "x-ratelimit-reset": "4600"}, b"[1, 2]")]
        slept = []

        def sleep(s):
            slept.append(s)
            now[0] += s

        with tempfile.TemporaryDirectory() as tmp:
            gh = census.GitHub(tmp, "s", opener=lambda req: answers.pop(0), pause=0, deadline=None, sleep=sleep,
                               clock=lambda: now[0])
            self.assertEqual(gh.get("/x"), [1, 2])
        self.assertEqual(slept[0], 305)
        self.assertEqual(gh.requests, 2)
        self.assertEqual(gh.waits, [305])

    def test_out_of_time_when_reset_is_past_deadline(self):
        answer = (403, {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "5000"}, b"{}")
        with tempfile.TemporaryDirectory() as tmp:
            gh = census.GitHub(tmp, "s", opener=lambda req: answer, pause=0, deadline=2000,
                               sleep=lambda s: None, clock=lambda: 1000.0)
            with self.assertRaises(census.OutOfTime):
                gh.get("/x")


class Stub:
    """Answers like GitHub and raw.githubusercontent.com; records every URL asked for."""

    def __init__(self, live=True, issues=None, comments=None):
        self.live = live
        self.calls = []
        self.issues = issues or {}
        self.comments = comments or {}

    def __call__(self, req):
        url = req.full_url
        self.calls.append(url)
        hdr = {"x-ratelimit-remaining": "50", "x-ratelimit-reset": "0"}
        if url.startswith(census.RAW):
            return (200 if self.live else 404), {}, b"prereg"
        p = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(p.query)
        if p.path.endswith("/commits"):
            body = [{"sha": "abc", "commit": {"committer": {"date": "2026-11-06T04:00:00Z"}}}]
            return 200, hdr, json.dumps(body).encode("utf-8")
        page = int(q.get("page", ["1"])[0])
        repo = p.path.split("/repos/", 1)[1].split("/issues", 1)[0]
        store = self.comments if p.path.endswith("/issues/comments") else self.issues
        chunk = store.get(repo, [])[(page - 1) * census.PER_PAGE: page * census.PER_PAGE]
        return 200, hdr, json.dumps(chunk).encode("utf-8")


class PipelineTests(unittest.TestCase):
    def data(self):
        r24, r25 = "NaNoGenMo/2024", "NaNoGenMo/2025"
        issues = {r24: [issue(1, "One", "GPT-4 wrote it. https://github.com/alice/one"),
                        issue(2, "Two", "Markov.", login=B),
                        issue(3, "Three", "Intent only", labels=())],
                  r25: [issue(1, "Uno", "Tracery.", created="2025-11-01T00:00:00Z")]}
        comments = {r24: [comment(r24, 2, "Code: https://gitlab.com/bob/two", login=B)]}
        return issues, comments

    def test_run_then_resume_from_cache(self):
        issues, comments = self.data()
        with tempfile.TemporaryDirectory() as tmp:
            out, cache = os.path.join(tmp, "out"), os.path.join(tmp, "cache")
            stub = Stub(issues=issues, comments=comments)
            slept = []
            rc = census.main(["--out-dir", out, "--cache-dir", cache, "--years", "2024-2025", "--pause", "0",
                              "--wait-prereg-minutes", "5"], opener=stub, sleep=slept.append)
            self.assertEqual(rc, 0)
            with open(os.path.join(out, "years.csv"), newline="", encoding="utf-8") as f:
                years = {int(r["year"]): r for r in csv.DictReader(f)}
            self.assertEqual(sorted(years), [2024, 2025])
            self.assertEqual((years[2024]["issues"], years[2024]["completed"], years[2024]["llm"]), ("3", "2", "1"))
            self.assertEqual(years[2024]["code_link"], "2")
            self.assertEqual(years[2025]["grammar"], "1")
            with open(os.path.join(out, "meta.json"), encoding="utf-8") as f:
                meta = json.load(f)
            self.assertTrue(meta["complete"])
            self.assertEqual(meta["prereg"]["committed_at"], "2026-11-06T04:00:00Z")
            with open(os.path.join(out, "entries.csv"), encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn(A, text)
            self.assertNotIn(B, text)
            for name in os.listdir(cache):
                with open(os.path.join(cache, name), encoding="utf-8") as f:
                    self.assertNotIn('"login"', f.read())
            with open(os.path.join(out, "REPORT.md"), encoding="utf-8") as f:
                rep = f.read()
            self.assertIn("| 2024 | 3 | 2 |", rep)
            self.assertIn("first committed 2026-11-06T04:00:00Z", rep)
            with open(os.path.join(out, "snippets.jsonl"), encoding="utf-8") as f:
                self.assertEqual(len(f.readlines()), 1)

            stub2 = Stub()
            out2 = os.path.join(tmp, "out2")
            rc = census.main(["--out-dir", out2, "--cache-dir", cache, "--years", "2024-2025", "--pause", "0"],
                             opener=stub2, sleep=slept.append)
            self.assertEqual(rc, 0)
            self.assertEqual(stub2.calls, [])
            with open(os.path.join(out2, "years.csv"), newline="", encoding="utf-8") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 2)

    def test_waits_for_prereg_then_gives_up(self):
        issues, comments = self.data()
        with tempfile.TemporaryDirectory() as tmp:
            stub = Stub(live=False, issues=issues, comments=comments)
            slept = []
            rc = census.main(["--out-dir", tmp, "--cache-dir", os.path.join(tmp, "c"), "--years", "2024",
                              "--wait-prereg-minutes", "4"], opener=stub, sleep=slept.append)
            self.assertEqual(rc, 3)
            self.assertTrue(all(u.startswith(census.RAW) for u in stub.calls))
            self.assertEqual(len(stub.calls), 3)
            self.assertEqual(sum(slept), 240)


if __name__ == "__main__":
    unittest.main()
