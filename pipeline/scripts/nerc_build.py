"""Build pipeline/raw/nerc.json from parsed standings, CF API dump and per-contest text modules.

Usage (from pipeline/): python -I scripts/nerc_build.py
Inputs:
  downloads/nerc/standings_parsed.json  (scripts/nerc_parse_standings.py)
  downloads/nerc/cf_problemset.json     (https://codeforces.com/api/problemset.problems)
  scripts/nerc_text_<suffix>.py          (summaries / ideas / tags, written from official tutorials)
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DL = ROOT / "downloads" / "nerc"
ARCH = "https://nerc.itmo.ru/archive"

CONTESTS = [
    # id, text module suffix, archive year, file prefix, CF id, date, season name, notes
    ("nerc2019", "2019", 2019, "nerc-2019", 1267, "2019-12-01", "2019-2020",
     "Held simultaneously in St. Petersburg, Barnaul, Tbilisi and Almaty; combined official standings used."),
    ("nerc2021", "2021", 2020, "nerc-2020-offline", 1510, "2021-04-04", "2020-2021",
     "2020-2021 season onsite final (St. Petersburg, Minsk, Tbilisi, Riga), held April 2021 after the "
     "Dec 2020 online NERC round (15 problems, ~300 teams) which is NOT included here. "
     "Only ~50 top teams from the online round took part."),
    ("nerc2022apr", "2022apr", 2021, "nerc-2021", 1666, "2022-04-13", "2021-2022",
     "2021-2022 season final, postponed to April 2022 (St. Petersburg, Almaty, Barnaul, Minsk, Yerevan). "
     "Second NERC held in calendar year 2022, hence the suffix."),
    ("nerc2022dec", "2022dec", 2022, "nef-2022", 1773, "2022-12-07", "2022-2023",
     "Sites: St. Petersburg, Barnaul, Kutaisi, Almaty. Two teams marked '*' in the standings "
     "(incomplete/out-of-competition) excluded from counts."),
    ("nerc2023", "2023", 2023, "nef-2023", 1912, "2023-12-13", "2023-2024",
     "Sites: St. Petersburg, Novosibirsk, Astana, Kutaisi; combined official standings used."),
    ("nerc2024", "2024", 2024, "nef-2024", 2052, "2024-12-15", "2024-2025",
     "Sites: St. Petersburg, Novosibirsk, Astana, Tbilisi; combined official standings used."),
    ("nerc2025", "2025", 2025, "nef-2025", 2181, "2025-12-17", "2025-2026",
     "Sites: St. Petersburg, Novosibirsk, Almaty, Tbilisi. One team marked '*' excluded. "
     "Problem B statement had a defect (jury accepted the 'attack opponent's maximum' variant)."),
]


def load_text(suffix):
    path = Path(__file__).resolve().parent / f"nerc_text_{suffix}.py"
    spec = importlib.util.spec_from_file_location(f"nerc_text_{suffix}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TEXT


def main():
    st = json.loads((DL / "standings_parsed.json").read_text(encoding="utf-8"))
    cf = json.loads((DL / "cf_problemset.json").read_text(encoding="utf-8"))["result"]["problems"]
    cfmap = {(p["contestId"], p["index"]): p for p in cf if "contestId" in p}
    contests, problems = [], []
    for cid, suf, ay, pref, cfid, date, season, notes in CONTESTS:
        s = st[cid]
        year = int(date[:4])
        contests.append({
            "id": cid,
            "family": "nerc",
            "name": f"ICPC {season} NERC - Northern Eurasia Finals",
            "short": f"NERC {season}" if cid != "nerc2021" else "NERC 2020-2021 Onsite",
            "year": year,
            "date": date,
            "total_teams": s["total_teams"],
            "links": {
                "scoreboard": f"{ARCH}/{ay}/standings.html",
                "statements": f"{ARCH}/{ay}/{pref}-statement.pdf",
                "editorial": f"{ARCH}/{ay}/{pref}-tutorial.pdf",
                "mirror": f"https://codeforces.com/contest/{cfid}",
                "kattis": None,
            },
            "notes": notes + " total_teams counts all ranked official teams in the final standings "
                             "(including teams with 0 solved).",
        })
        text = load_text(suf)
        for letter, ps in s["problems"].items():
            summ, idea, src, tags = text[letter]
            cfp = cfmap.get((cfid, letter))
            title = ps["title"]
            if cfp is None:
                raise SystemExit(f"missing CF problem {cfid}{letter}")
            problems.append({
                "id": f"{cid}-{letter}",
                "contest": cid,
                "letter": letter,
                "title": title,
                "solved_teams": ps["solved"],
                "attempted_teams": ps["attempted"],
                "first_solve_min": ps["first"],
                "links": {
                    "mirror": f"https://codeforces.com/contest/{cfid}/problem/{letter}",
                    "kattis": None,
                    "statement": f"{ARCH}/{ay}/{pref}-statement.pdf",
                },
                "statement_summary": summ,
                "solution_idea": idea,
                "solution_source": src,
                "candidate_tags": tags,
                "cf_tags": cfp.get("tags", []),
                "cf_rating": cfp.get("rating"),
            })
            if cfp["name"].lower().replace(" ", "")[:12] != title.lower().replace(" ", "")[:12]:
                print("title mismatch:", cid, letter, repr(title), repr(cfp["name"]))
        missing = set(text) - set(s["problems"])
        if missing:
            raise SystemExit(f"{cid}: text for unknown letters {missing}")
    out = {"source": "nerc", "contests": contests, "problems": problems}
    (ROOT / "raw" / "nerc.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(contests), "contests,", len(problems), "problems")


if __name__ == "__main__":
    main()
