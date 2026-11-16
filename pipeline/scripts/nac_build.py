"""Build pipeline/raw/nac.json from parsed scoreboards + hand annotations.

Usage (from pipeline/):
  python -I scripts/nac_scoreboards.py downloads/nac downloads/nac/parsed_scoreboards.json
  python -I scripts/nac_build.py downloads/nac/parsed_scoreboards.json raw/nac.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nac_annotations import P  # noqa: E402

KATTIS = "https://open.kattis.com/problems/"

CONTESTS = [
    dict(id="nac2021", year=2021, date="2021-08-14",
         name="ICPC North America Championship 2021",
         links=dict(scoreboard="https://nac21.kattis.com/contests/nac21/standings",
                    statements="http://seusa.vanb.org/nac2021.pdf",
                    editorial="https://icpcarchive.github.io/North-America/ICPC-North-America-Championship/ICPC-North-America-Championship-2021/tutorials_en.pdf",
                    mirror="https://open.kattis.com/contests/gvj893",
                    kattis="https://nac21.kattis.com/contests/nac21"),
         notes="Held online (virtual) because of COVID; official contest on nac21.kattis.com. 48 official teams "
               "(6 unnamed placeholder accounts with no submissions excluded). Solution ideas from the NAC/Petrozavodsk 2021 "
               "editorial by Ildar Gainullin; judges' video explanations at serjudging.vanb.org/?p=1687. "
               "Problem H unsolved. No Codeforces gym mirror found; mirror = open Kattis mirror contest."),
    dict(id="nac2022", year=2022, date="2022-05-30",
         name="ICPC North America Championship 2022",
         links=dict(scoreboard="https://nac22.kattis.com/contests/nac22/standings",
                    statements="http://serjudging.vanb.org/wp-content/uploads/nac2022.pdf",
                    editorial="http://serjudging.vanb.org/?p=1795",
                    mirror=None,
                    kattis="https://nac22.kattis.com/contests/nac22"),
         notes="Onsite at UCF, Orlando. 50 official teams (Kattis final standings). No solution slides were published; "
               "solution_idea fields were derived from the judges' accepted reference solutions (code) published on "
               "serjudging.vanb.org (marked 'editorial'). No Codeforces gym mirror found."),
    dict(id="nac2023", year=2023, date="2023-05-29",
         name="ICPC North America Championship 2023",
         links=dict(scoreboard="https://nac.icpc.global/scoreboard/2023/",
                    statements="https://nac.icpc.global/wp-content/uploads/2023/06/nac2023_problems.pdf",
                    editorial="http://serjudging.vanb.org/wp-content/uploads/nac.pdf",
                    mirror="https://open.kattis.com/contests/p524yj",
                    kattis="https://open.kattis.com/contests/p524yj"),
         notes="Onsite at UCF, Orlando; DOMjudge final scoreboard (51 teams). Official solution slides (PDF title page "
               "mistakenly says 2022) hosted on serjudging.vanb.org. D and H unsolved. vanb's per-problem stats list 11 "
               "solves for J; the official scoreboard shows 10 (scoreboard used)."),
    dict(id="nac2024", year=2024, date="2024-05-27",
         name="ICPC North America Championship 2024",
         links=dict(scoreboard="https://nac.icpc.global/scoreboard/2024/",
                    statements="http://serjudging.vanb.org/wp-content/uploads/nac2024.pdf",
                    editorial="https://assets.ucup.ac/tutorials/tutorials-3-00-en.pdf",
                    mirror="https://open.kattis.com/contests/dmh7ro",
                    kattis="https://open.kattis.com/contests/dmh7ro"),
         notes="Onsite at UCF, Orlando; DOMjudge final scoreboard (50 teams). Official judges' slides (also used as "
               "Universal Cup Season 3 Stage 0; same slides at serjudging.vanb.org/wp-content/uploads/nac-1.pdf). "
               "E, K, L unsolved. Problem F is 'Magic Bean' on Kattis, 'Magic Bean Cube' on the scoreboard; vanb lists 2 "
               "solves for F, the official scoreboard shows 3 (scoreboard used)."),
    dict(id="nac2025", year=2025, date="2025-05-26",
         name="ICPC North America Championship 2025",
         links=dict(scoreboard="https://nac.icpc.global/scoreboard/2025/",
                    statements="https://nac.icpc.global/problems/2025/nac2025_problemset.pdf",
                    editorial="https://nac.icpc.global/problems/2025/nac2025_solutions.pdf",
                    mirror=None,
                    kattis=None),
         notes="Onsite at UCF, Orlando; PC^2 final unfrozen scoreboard (52 teams). Official solution slides. G unsolved. "
               "Also used as Universal Cup Season 4 Stage 0. Problems are on open.kattis.com (per-problem links)."),
    dict(id="nac2026", year=2026, date="2026-03-22",
         name="ICPC North America Championship 2026",
         links=dict(scoreboard="https://nac.icpc.global/scoreboard/2026/nac/index.html",
                    statements="https://nac.icpc.global/problems/2026/nac/ProblemSet.pdf",
                    editorial="https://nac.icpc.global/problems/2026/nac2026_solutions.pdf",
                    mirror=None,
                    kattis=None),
         notes="Onsite at UCF, Orlando, held in March (earlier than usual); PC^2 final scoreboard (52 teams). Official "
               "solution slides. B and G unsolved. Problems are on open.kattis.com (per-problem links)."),
]

STATEMENT_2026 = {
    "A": "A-Acornquarrels", "B": "B-Bossrush", "C": "C-Cablepruning", "D": "D-Drawyourdeck",
    "E": "E-Eviljudges", "F": "F-Friendmeetup", "G": "G-Gemstonedowsing", "H": "H-Heistofthecentury",
    "I": "I-Idontmisspennies", "J": "J-Jellyfusion", "K": "K-Kindergartenrevisited",
    "L": "L-Leakingsantassecrets", "M": "M-Makiconveyorbelt",
}


def main():
    sb = json.loads(Path(sys.argv[1]).read_text(encoding="utf8"))
    out = {"source": "nac", "contests": [], "problems": []}
    for c in CONTESTS:
        cid = c["id"]
        s = sb[cid]
        out["contests"].append({
            "id": cid, "family": "nac", "name": c["name"], "short": f"NAC {c['year']}",
            "year": c["year"], "date": c["date"], "total_teams": s["total_teams"],
            "links": c["links"], "notes": c["notes"],
        })
        for L in sorted(P[cid]):
            title, short, summ, idea, src, tags = P[cid][L]
            st = s["problems"][L]
            sb_title = st.get("title")
            if sb_title and sb_title != title and not (cid == "nac2024" and L == "F"):
                print("WARN title mismatch", cid, L, title, "| scoreboard:", sb_title)
            if cid == "nac2026":
                stmt = f"https://nac.icpc.global/problems/2026/nac/{STATEMENT_2026[L]}/{STATEMENT_2026[L]}.pdf"
            else:
                stmt = c["links"]["statements"]
            kat = KATTIS + short
            out["problems"].append({
                "id": f"{cid}-{L}", "contest": cid, "letter": L, "title": title,
                "solved_teams": st["solved_teams"], "attempted_teams": st["attempted_teams"],
                "first_solve_min": st["first_solve_min"],
                "links": {"mirror": kat, "kattis": kat, "statement": stmt},
                "statement_summary": summ, "solution_idea": idea, "solution_source": src,
                "candidate_tags": tags, "cf_tags": [], "cf_rating": None,
            })
        assert len(P[cid]) == len(s["problems"]), cid
    Path(sys.argv[2]).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf8")
    print(len(out["contests"]), "contests,", len(out["problems"]), "problems")


if __name__ == "__main__":
    main()
