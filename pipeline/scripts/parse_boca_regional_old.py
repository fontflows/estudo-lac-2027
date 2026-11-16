"""Parse BOCA "Final Scoreboard" HTML reports (scorelatam.naquadah.com.br, LATAM 2019-2023 style).

Usage:
    python -I parse_boca_regional_old.py <score.html> [--group N] [--exclude REGEX] [--list-teams]

BOCA reports repeat every team once per "sitegroup" (global, per-country, CCL, ...).
We keep the rows of one group (the "Global" group, --group, default 1), dedupe by username,
and drop non-official accounts (CCL parallel contest, guests, judges, test/warmup accounts)
by username / team-name regex.

Each problem cell is "tries/minute" (solved, balloon image present) or "tries/-" (not solved).

Output (stdout): JSON with per-problem stats:
  {letters, total_teams, teams_with_submissions, excluded:[...], problems:{L:{solved, attempted, first_solve_min}}}
"""
import argparse
import html
import json
import re
import sys

# applied to the BOCA username only (official accounts are "team<site><n>"; CCL = parallel club contest)
DEFAULT_EXCLUDE = r"(^(?!team)|ccl|guest|judge|juiz|staff|admin|warmup|mirror)"
# applied to the team display name
NAME_EXCLUDE = r"^\s*\[CCL"


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\xa0", " ").strip()


def parse(path, group, exclude_re):
    s = open(path, encoding="utf-8", errors="replace").read()
    i = s.find('id="myscoretable"')
    if i < 0:
        raise SystemExit("no score table found")
    tbl = s[i : s.find("</table>", i)]
    rows = re.findall(r"<tr([^>]*)>(.*?)</tr>", tbl, flags=re.S)
    header = rows[0][1]
    hcells = [strip_tags(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", header, flags=re.S)]
    letters = [h.strip() for h in hcells[3:-1]]
    teams = {}
    excluded = []
    for attrs, body in rows[1:]:
        m = re.search(r'class="sitegroup(\d+)"', attrs)
        if not m or int(m.group(1)) != group:
            continue
        cells = re.findall(r"<td[^>]*>(.*?)</td>", body, flags=re.S)
        if len(cells) < 3 + len(letters):
            continue
        user = strip_tags(cells[1])
        name = strip_tags(cells[2])
        if user in teams:
            continue
        if (exclude_re and re.search(exclude_re, user, re.I)) or re.search(NAME_EXCLUDE, name, re.I):
            excluded.append(f"{user} | {name}")
            continue
        probs = {}
        for L, c in zip(letters, cells[3 : 3 + len(letters)]):
            txt = strip_tags(c)
            mm = re.search(r"(\d+)\s*/\s*(\d+|-)", txt)
            if not mm:
                probs[L] = None
                continue
            tries = int(mm.group(1))
            solved = mm.group(2) != "-"
            # balloon image is the definitive "solved" marker in BOCA
            if solved and "<img" not in c:
                solved = False
            probs[L] = (tries, int(mm.group(2)) if solved else None)
        teams[user] = {"name": name, "probs": probs, "total": strip_tags(cells[-1])}
    active = sum(1 for t in teams.values() if any(v and v[0] > 0 for v in t["probs"].values()))
    out = {"letters": letters, "total_teams": len(teams), "teams_with_submissions": active,
           "excluded": excluded, "problems": {}}
    for L in letters:
        solved = [t["probs"][L][1] for t in teams.values() if t["probs"].get(L) and t["probs"][L][1] is not None]
        attempted = [1 for t in teams.values() if t["probs"].get(L) and t["probs"][L][0] > 0]
        out["problems"][L] = {
            "solved": len(solved),
            "attempted": len(attempted),
            "first_solve_min": min(solved) if solved else None,
        }
    return out, teams


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--group", type=int, default=1, help="sitegroup id of the Global scoreboard")
    ap.add_argument("--exclude", default=DEFAULT_EXCLUDE)
    ap.add_argument("--list-teams", action="store_true")
    a = ap.parse_args()
    out, teams = parse(a.html, a.group, a.exclude)
    if a.list_teams:
        for u, t in teams.items():
            print(u, "|", t["name"], "|", t["total"])
        return
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
