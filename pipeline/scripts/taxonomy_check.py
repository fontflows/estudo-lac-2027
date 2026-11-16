"""Sanity checks for pipeline/taxonomy.json against pipeline/raw/*.json.

Usage (from Dados_Latam/):  python -I pipeline/scripts/taxonomy_check.py [--urls]
  --urls  also curl every ref URL and require HTTP 200 (network).
Exit code 1 if any hard error (missing/unknown ids, bad fields).
"""
import collections
import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
LO, HI = 4, 30          # hard bounds (warn outside); target is ~5-25
TARGET_LO, TARGET_HI = 5, 25
MAX_SMALL_EXCEPTIONS = 6


def main():
    with open(os.path.join(PIPE, "taxonomy.json"), encoding="utf-8") as fh:
        tax = json.load(fh)
    problems = {}
    for path in sorted(glob.glob(os.path.join(PIPE, "raw", "*.json"))):
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
        fam = {c["id"]: c["family"] for c in raw["contests"]}
        for p in raw["problems"]:
            problems[p["id"]] = {"family": fam[p["contest"]], "source": p.get("solution_source")}

    errors = []
    area_ids = {a["id"] for a in tax["areas"]}
    topics = {t["id"]: t for t in tax["topics"]}
    if len(topics) != len(tax["topics"]):
        errors.append("duplicate topic ids")
    for t in tax["topics"]:
        if t["area"] not in area_ids:
            errors.append(f"topic {t['id']}: unknown area {t['area']}")
        for f in ("name", "description", "includes", "refs"):
            if not t.get(f):
                errors.append(f"topic {t['id']}: empty {f}")

    asg = tax["assignments"]
    missing = sorted(set(problems) - set(asg))
    extra = sorted(set(asg) - set(problems))
    if missing:
        errors.append(f"{len(missing)} problems without assignment: {missing}")
    if extra:
        errors.append(f"{len(extra)} assignments for unknown problems: {extra}")

    prim = collections.Counter()
    sec = collections.Counter()
    fam_cnt = collections.defaultdict(collections.Counter)
    conf = collections.Counter()
    for pid, a in asg.items():
        refs = [a.get("primary")] + list(a.get("secondary", []))
        for t in refs:
            if t not in topics:
                errors.append(f"{pid}: unknown topic {t}")
        if len(a.get("secondary", [])) > 2:
            errors.append(f"{pid}: more than 2 secondary topics")
        if a.get("primary") in a.get("secondary", []) or len(set(a.get("secondary", []))) != len(a.get("secondary", [])):
            errors.append(f"{pid}: repeated topic in primary/secondary")
        if a.get("confidence") not in ("high", "medium"):
            errors.append(f"{pid}: bad confidence {a.get('confidence')}")
        if not a.get("key_idea"):
            errors.append(f"{pid}: empty key_idea")
        conf[a.get("confidence")] += 1
        fam = problems.get(pid, {}).get("family", "?")
        prim[a["primary"]] += 1
        fam_cnt[a["primary"]][fam] += 1
        for t in a.get("secondary", []):
            sec[t] += 1
            fam_cnt[t][fam] += 1

    fams = ["lac", "latam_regional", "nac", "nerc", "apac"]
    area_name = {a["id"]: a["name"] for a in tax["areas"]}
    print(f"{len(tax['areas'])} areas, {len(topics)} topics, {len(asg)}/{len(problems)} problems assigned")
    print(f"confidence: {dict(conf)}")
    hdr = f"{'topic':28s} {'prim':>4s} {'sec':>4s} {'tot':>4s}  " + " ".join(f"{f[:6]:>6s}" for f in fams)
    small, big = [], []
    for aid in [a["id"] for a in sorted(tax["areas"], key=lambda a: a["order"])]:
        print(f"\n== {area_name[aid]}")
        print(hdr)
        for t in tax["topics"]:
            if t["area"] != aid:
                continue
            tid = t["id"]
            tot = prim[tid] + sec[tid]
            flag = ""
            if tot < TARGET_LO or tot > TARGET_HI:
                flag = "  <-- outside target"
            if tot < LO:
                small.append((tid, tot))
            if tot > HI:
                big.append((tid, tot))
            print(f"{tid:28s} {prim[tid]:4d} {sec[tid]:4d} {tot:4d}  " +
                  " ".join(f"{fam_cnt[tid][f]:6d}" for f in fams) + flag)
    unused = [t for t in topics if prim[t] + sec[t] == 0]
    if unused:
        errors.append(f"unused topics: {unused}")
    print(f"\ntopics with total < {LO}: {small}")
    print(f"topics with total > {HI}: {big}")
    if big:
        errors.append(f"catch-all topics above {HI}: {big}")
    if len(small) > MAX_SMALL_EXCEPTIONS:
        errors.append(f"too many small topics ({len(small)} > {MAX_SMALL_EXCEPTIONS})")

    if "--urls" in sys.argv:
        urls = sorted({r["url"] for t in tax["topics"] for r in t["refs"]})
        print(f"\nchecking {len(urls)} URLs ...")
        for u in urls:
            out = subprocess.run(["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", "--max-time", "20", u],
                                 capture_output=True, text=True).stdout.strip()
            if out != "200":
                errors.append(f"URL {u} -> {out}")
        print("URL check done")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    print("\nOK")


if __name__ == "__main__":
    main()
