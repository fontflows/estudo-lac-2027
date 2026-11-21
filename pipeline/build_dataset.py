"""Merge pipeline/raw/*.json + pipeline/taxonomy.json into data/dataset.js.

Usage:  python -I pipeline/build_dataset.py
"""
import datetime
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "pipeline", "raw")
TAX = os.path.join(ROOT, "pipeline", "taxonomy.json")
TOP = os.path.join(ROOT, "pipeline", "extra", "top_solves.json")
CUR = os.path.join(ROOT, "pipeline", "curriculum", "curriculum.json")

# Difficulty = share of the top-K official teams of the contest that solved the problem
# (K = 40 ~ size of the Latin America Championship), so contests of 40 and 500 teams compare.
DIFF_BINS = [("easy", 0.7), ("medium", 0.3), ("hard", 0.1)]
OUT = os.path.join(ROOT, "data", "dataset.js")

FAMILIES = [
    {"id": "lac", "name": "ICPC Latin America Championship", "short": "LAC", "weight": 1.0, "group": "latam"},
    {"id": "latam_regional", "name": "ICPC Latin American Regional", "short": "Regional LATAM", "weight": 0.6, "group": "latam"},
    {"id": "nac", "name": "ICPC North America Championship", "short": "NAC", "weight": 0.8, "group": "world"},
    {"id": "nerc", "name": "ICPC Northern Eurasia Finals", "short": "NERC", "weight": 0.8, "group": "world"},
    {"id": "apac", "name": "ICPC Asia Pacific Championship", "short": "APAC", "weight": 0.8, "group": "world"},
]
FAMILY_IDS = {f["id"] for f in FAMILIES}


def difficulty(rate):
    if rate is None:
        return None
    for name, lo in DIFF_BINS:
        if rate >= lo:
            return name
    return "very_hard"


def main():
    contests, problems = [], []
    seen_c, seen_p = set(), set()
    for path in sorted(glob.glob(os.path.join(RAW, "*.json"))):
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
        for c in raw.get("contests", []):
            if c["id"] in seen_c:
                sys.exit(f"duplicate contest id {c['id']} in {path}")
            if c.get("family") not in FAMILY_IDS:
                sys.exit(f"unknown family {c.get('family')} in {path}")
            seen_c.add(c["id"])
            contests.append(c)
        for p in raw.get("problems", []):
            if p["id"] in seen_p:
                sys.exit(f"duplicate problem id {p['id']} in {path}")
            seen_p.add(p["id"])
            problems.append(p)

    tax = {"areas": [], "topics": [], "assignments": {}}
    if os.path.exists(TAX):
        with open(TAX, encoding="utf-8") as fh:
            tax = json.load(fh)
    top = {"k": None, "problems": {}}
    if os.path.exists(TOP):
        with open(TOP, encoding="utf-8") as fh:
            top = json.load(fh)
    topic_ids = {t["id"] for t in tax["topics"]}
    assign = tax.get("assignments", {})

    by_contest = {}
    for p in problems:
        by_contest.setdefault(p["contest"], []).append(p)

    out_contests = []
    for c in contests:
        ps = by_contest.get(c["id"], [])
        solved_vals = [p.get("solved_teams") for p in ps if p.get("solved_teams") is not None]
        c2 = dict(c)
        c2["problem_count"] = len(ps)
        c2["max_solved"] = max(solved_vals) if solved_vals else None
        out_contests.append(c2)
    cmap = {c["id"]: c for c in out_contests}

    out_problems, problems_missing_tax, warnings = [], [], []
    for p in problems:
        c = cmap.get(p["contest"])
        if c is None:
            sys.exit(f"problem {p['id']} references unknown contest {p['contest']}")
        solved, total = p.get("solved_teams"), c.get("total_teams")
        mx = c.get("max_solved")
        rel = (solved / mx) if (solved is not None and mx) else (0.0 if solved == 0 else None)
        ts = top["problems"].get(p["id"])
        top_rate = (ts["solved_top"] / ts["k_used"]) if (ts and ts.get("k_used")) else None
        if ts is None:
            warnings.append(f"{p['id']}: no top-K solve data")
        a = assign.get(p["id"])
        if a is None:
            problems_missing_tax.append(p["id"])
            a = {}
        for t in [a.get("primary")] + list(a.get("secondary", [])):
            if t and t not in topic_ids:
                warnings.append(f"{p['id']}: unknown topic {t}")
        out_problems.append({
            "id": p["id"], "contest": p["contest"], "family": c["family"], "year": c["year"],
            "letter": p["letter"], "title": p["title"],
            "solved": solved, "attempted": p.get("attempted_teams"), "total": total,
            "first_solve_min": p.get("first_solve_min"),
            "solve_rate": round(solved / total, 4) if (solved is not None and total) else None,
            "rel_solve": round(rel, 4) if rel is not None else None,
            "solved_top": ts["solved_top"] if ts else None, "k_used": ts["k_used"] if ts else None,
            "top_rate": round(top_rate, 4) if top_rate is not None else None,
            "difficulty": difficulty(top_rate if top_rate is not None else rel),
            "links": p.get("links", {}),
            "summary": p.get("statement_summary"), "solution": p.get("solution_idea"),
            "solution_source": p.get("solution_source"),
            "key_idea": a.get("key_idea"), "primary": a.get("primary"),
            "secondary": a.get("secondary", []), "confidence": a.get("confidence"),
            "cf_tags": p.get("cf_tags") or [], "cf_rating": p.get("cf_rating"),
        })

    out_contests.sort(key=lambda c: (c["year"], c.get("date") or "", c["id"]))
    out_problems.sort(key=lambda p: (p["contest"], p["letter"]))
    dataset = {
        "generated": datetime.date.today().isoformat(),
        "target": {"name": "ICPC Latin America Championship 2027", "date": "2027-07-13T09:00:00-03:00"},
        "families": FAMILIES,
        "difficulty_k": top.get("k"),
        "areas": tax["areas"], "topics": tax["topics"],
        "contests": out_contests, "problems": out_problems,
    }
    if os.path.exists(CUR):
        with open(CUR, encoding="utf-8") as fh:
            cur = json.load(fh)
        known = {p["id"] for p in out_problems}
        refs = [x["id"] for k in ("deepenings", "insights") for it in cur.get(k, []) for x in it.get("problems", [])]
        refs += [x for t in cur.get("techniques", []) for x in t.get("problems", [])]
        refs += list(cur.get("problem_steps", {}).keys())
        bad = sorted({r for r in refs if r not in known})
        if bad:
            sys.exit(f"curriculum references unknown problems: {bad[:10]}")
        dataset["curriculum"] = cur
        print(f"curriculum: {len(cur.get('techniques', []))} techniques, "
              f"{len(cur.get('deepenings', []))} deepenings, {len(cur.get('insights', []))} insights")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("window.DATASET = ")
        json.dump(dataset, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")

    print(f"contests={len(out_contests)} problems={len(out_problems)} topics={len(tax['topics'])}")
    if problems_missing_tax:
        print(f"WARNING {len(problems_missing_tax)} problems without taxonomy assignment")
    for w in warnings[:30]:
        print("WARNING", w)


if __name__ == "__main__":
    main()
