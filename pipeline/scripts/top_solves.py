"""Compute, for every problem, how many of the TOP-K official teams (official final rank) solved it.

Why: rel_solve = solved / max_solved is distorted for contests with hundreds of weak teams
(LATAM regionals, NERC). Counting solves among the top K=40 official teams (~ size of the Latin
America Championship) gives a difficulty measure comparable across families.

Reuses the per-family parsers and exactly the same official-team filtering used to build raw/*.json:
  lac / latam_regional 2024-25 : parse_boca_scoreboard (sitegroup 1 = PdA / Global)
  latam_regional 2019-2023     : parse_boca_regional_old (Global sitegroup, CCL/guest accounts excluded)
  nerc                         : nerc.itmo.ru PCMS2 standings, names starting with '*' excluded
  nac                          : nac_scoreboards (Kattis / DOMjudge / PC^2; unnamed placeholders excluded)
  apac                         : apac_parse_standings (all listed teams official)
Teams are taken in scoreboard row order (= official rank: solved desc, penalty asc); the script
checks that solved counts are non-increasing in that order.

Usage: python -I pipeline/scripts/top_solves.py
Writes pipeline/extra/top_solves.json: {"k": 40, "problems": {"<pid>": {"k_used": n, "solved_top": m}}}
"""
import glob
import html
import importlib.util
import json
import os
import re
import sys

K = 40
HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
DL = os.path.join(PIPE, "downloads")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


boca = load("parse_boca_scoreboard")
pbro = load("parse_boca_regional_old")
nacsb = load("nac_scoreboards")
apacps = load("apac_parse_standings")

# Each loader returns (letters, rows) with rows = [set of solved letters] in official rank order.


def boca_new(fname, group=1):
    labels, letters, rows = boca.parse(os.path.join(DL, "scorelatam", fname))
    n, st, sel = boca.stats(letters, rows, group)
    out = [{L for L, (t, m) in r["cells"].items() if m is not None} for r in sel]
    return letters, out


REG_OLD = {"latam2019": (2019, 1), "latam2021": (2020, 1), "latam2022": (2021, 32),
           "latam2023a": (2022, 1), "latam2023b": (2023, 1)}


def boca_old(cid):
    ed, group = REG_OLD[cid]
    path = os.path.join(DL, "latam_regional_2019_2023", f"latam-{ed}-index.html")
    out, teams = pbro.parse(path, group, pbro.DEFAULT_EXCLUDE)
    rows = [{L for L, v in t["probs"].items() if v and v[1] is not None} for t in teams.values()]
    return out["letters"], rows


NERC_FILES = {"nerc2019": "st_2019.html", "nerc2021": "st_2020.html", "nerc2022apr": "st_2021.html",
              "nerc2022dec": "st_2022.html", "nerc2023": "st_2023.html", "nerc2024": "st_2024.html",
              "nerc2025": "st_2025.html"}


def nerc(cid):
    # same logic as nerc_parse_standings.parse, but keeping per-team rows
    raw = open(os.path.join(DL, "nerc", NERC_FILES[cid]), "rb").read()
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        s = raw.decode("cp1251", errors="replace")
    txt = lambda x: html.unescape(re.sub(r"<[^>]+>", " ", x)).strip()
    head = re.search(r"<thead>(.*?)</thead>", s, re.S).group(1)
    letters = [l.strip() for t, l in re.findall(r'<th class="problem" title="([^"]*)">([^<]*)</th>', head)]
    rows = []
    for r in re.findall(r'<tr class="row\d\d">(.*?)</tr>', s, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        if txt(tds[1]).startswith("*"):
            continue
        solved = set()
        for L, c in zip(letters, tds[2:2 + len(letters)]):
            v = txt(re.sub(r"<s>.*?</s>", "", c, flags=re.S))
            if v.startswith("+"):
                solved.add(L)
        rows.append(solved)
    return letters, rows


NAC = {"nac2021": ("parse_kattis", "nac21_standings.html"), "nac2022": ("parse_kattis", "nac22_standings.html"),
       "nac2023": ("parse_domjudge", "nac23_scoreboard.html"), "nac2024": ("parse_domjudge", "nac24_scoreboard.html"),
       "nac2025": ("parse_pc2", "nac25_scoreboard_idx.html"), "nac2026": ("parse_pc2", "nac26_scoreboard.html")}


def nac(cid):
    fn, f = NAC[cid]
    letters, titles, rows = getattr(nacsb, fn)(os.path.join(DL, "nac", f))
    return letters, [{L for L, (t, m) in cells.items() if m is not None} for _, cells in rows]


def apac(cid):
    probs, teams = apacps.parse(os.path.join(DL, "apac", f"{cid[4:]}_standings.html"))
    letters = [l for _, l in probs]
    rows = [{L for L, c in zip(letters, t["cells"]) if c and c["cls"].startswith("score_correct")} for t in teams]
    return letters, rows


def loader(cid):
    if cid.startswith("lac"):
        return boca_new(f"pda{cid[5:7]}.html")
    if cid.startswith("latam_regional"):
        return boca_new(f"latam-{cid[-4:]}.html")
    if cid in REG_OLD:
        return boca_old(cid)
    if cid.startswith("nerc"):
        return nerc(cid)
    if cid.startswith("nac"):
        return nac(cid)
    if cid.startswith("apac"):
        return apac(cid)
    raise KeyError(cid)


def main():
    contests, problems = {}, {}
    for f in sorted(glob.glob(os.path.join(PIPE, "raw", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        for c in d["contests"]:
            contests[c["id"]] = c
        for p in d["problems"]:
            problems[p["id"]] = p

    result, errors, dist = {}, [], {}
    for cid, c in contests.items():
        try:
            letters, rows = loader(cid)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{cid}: cannot compute ({e!r})")
            continue
        if len(rows) != c["total_teams"]:
            errors.append(f"{cid}: parsed {len(rows)} official teams, raw total_teams={c['total_teams']}")
        counts = [len(r) for r in rows]
        if any(a < b for a, b in zip(counts, counts[1:])):
            errors.append(f"{cid}: solved counts not non-increasing in scoreboard order")
        k_used = min(K, len(rows))
        top = rows[:k_used]
        tie = (len(rows) > K and counts[K - 1] == counts[K])
        cps = [p for p in problems.values() if p["contest"] == cid]
        if sorted(p["letter"] for p in cps) != sorted(letters):
            errors.append(f"{cid}: letters mismatch raw={sorted(p['letter'] for p in cps)} sb={letters}")
        total_top = sum(len(r) for r in top)
        ssum = 0
        for p in cps:
            L = p["letter"]
            st = sum(1 for r in top if L in r)
            ssum += st
            result[p["id"]] = {"k_used": k_used, "solved_top": st}
            # check 2: solved_top <= solved_teams; check 3: small contests equal
            if st > p["solved_teams"]:
                errors.append(f"{p['id']}: solved_top {st} > solved_teams {p['solved_teams']}")
            if c["total_teams"] <= K and st != p["solved_teams"]:
                errors.append(f"{p['id']}: small contest but solved_top {st} != solved_teams {p['solved_teams']}")
            # also full-board recount must match raw
            full = sum(1 for r in rows if L in r)
            if full != p["solved_teams"]:
                errors.append(f"{p['id']}: full recount {full} != raw solved_teams {p['solved_teams']}")
            fam = dist.setdefault(c["family"], [0, 0, 0, 0])
            x = st / k_used
            fam[0 if x >= 0.6 else 1 if x >= 0.3 else 2 if x >= 0.1 else 3] += 1
        # check 1
        if ssum != total_top:
            errors.append(f"{cid}: sum solved_top {ssum} != total solves of top-{k_used} {total_top}")
        print(f"{cid:20s} teams={len(rows):4d} k_used={k_used:3d} top_solves={total_top:4d} sum={ssum:4d}"
              f" 40th/41st solved={counts[k_used-1]}/{counts[k_used] if len(rows) > k_used else '-'}"
              + ("  (tie on solved count at cut; rank order used)" if tie else ""))

    missing = sorted(set(problems) - set(result))
    os.makedirs(os.path.join(PIPE, "extra"), exist_ok=True)
    out = os.path.join(PIPE, "extra", "top_solves.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"k": K, "problems": dict(sorted(result.items()))}, fh, indent=1)
    print(f"\nwrote {out}: {len(result)} problems ({len(problems)} in raw, missing {missing})")
    print("\nsolved_top/k_used per family  [>=0.6, >=0.3, >=0.1, <0.1]")
    for fam, b in dist.items():
        print(f"  {fam:15s} {b}  (n={sum(b)})")
    print("\nchecks:", "ALL OK" if not errors else "")
    for e in errors:
        print("  !", e)


if __name__ == "__main__":
    main()
