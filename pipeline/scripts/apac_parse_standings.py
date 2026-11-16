"""Parse DOMjudge static standings HTML (ICPC APAC Championship archive) into JSON.

Usage: python -I apac_parse_standings.py <standings.html> [<standings.html> ...]
Prints, per file: list of problems, per-team rows, and per-problem stats.
"""
import json
import re
import sys
from html import unescape


def strip(s):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def parse(path):
    s = open(path, encoding="utf-8").read()
    probs = re.findall(r'<th title="problem ([^"]*)" scope="col">.*?<span style="color: #[0-9a-fA-F]+;">([A-Z]+)</span>', s, re.S)
    tb = s[s.find("<tbody"):]
    tb = tb[: tb.find("scoresummary")]
    rows = re.split(r'<tr class="[^"]*" id="team:', tb)[1:]
    teams = []
    for r in rows:
        tid = r[: r.find('"')]
        rank = strip(re.search(r'<td class="scorepl[^"]*">(.*?)</td>', r, re.S).group(1))
        tn = re.search(r'<td class="scoretn ([^"]*)" title="([^"]*)"', r)
        univ = re.search(r'<span class="univ forceWidth">(.*?)</span>', r, re.S)
        cells = re.findall(r'<td class="score_cell">(.*?)</td>', r, re.S)
        res = []
        for c in cells:
            m = re.search(r'<div class="(score_[^"]*)">\s*(.*?)<span>(.*?)</span>', c, re.S)
            if not m:
                res.append(None)
                continue
            cls, t, tries = m.group(1), strip(m.group(2)), strip(m.group(3))
            n = int(re.match(r"(\d+)", tries).group(1)) if re.match(r"(\d+)", tries) else 0
            res.append({"cls": cls, "time": int(t) if t.isdigit() else None, "tries": n})
        teams.append({
            "id": tid, "rank": rank, "cat": tn.group(1) if tn else None,
            "name": unescape(tn.group(2)) if tn else None,
            "univ": strip(univ.group(1)) if univ else None,
            "solved": int(strip(re.search(r'<td class="scorenc">(.*?)</td>', r, re.S).group(1))),
            "cells": res,
        })
    return probs, teams


def stats(probs, teams, official=lambda t: True):
    out = []
    off = [t for t in teams if official(t)]
    for i, (title, letter) in enumerate(probs):
        solved = att = 0
        first = None
        for t in off:
            c = t["cells"][i]
            if c is None:
                continue
            if c["tries"] > 0 or "correct" in c["cls"]:
                att += 1
            if c["cls"].startswith("score_correct"):
                solved += 1
                if c["time"] is not None and (first is None or c["time"] < first):
                    first = c["time"]
        out.append({"letter": letter, "title": title, "solved": solved, "attempted": att, "first": first})
    return len(off), out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        probs, teams = parse(p)
        cats = {}
        for t in teams:
            cats[t["cat"]] = cats.get(t["cat"], 0) + 1
        pend = sum(1 for t in teams for c in t["cells"] if c and "pending" in c["cls"])
        n, st = stats(probs, teams)
        print(json.dumps({"file": p, "nteams": n, "cats": cats, "pending_cells": pend,
                          "unranked": [t["name"] for t in teams if not t["rank"]][:50],
                          "problems": st}, ensure_ascii=False, indent=1))
