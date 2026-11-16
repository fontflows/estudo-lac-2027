"""Parse NAC official final scoreboards (Kattis 2021/22, DOMjudge 2023/24, PC^2 2025/26).

Usage: python -I nac_scoreboards.py <downloads/nac dir> <out.json>
Output: {contest_id: {"total_teams": n, "teams": [...], "problems": {letter: {...}}}}
"""
import html
import json
import re
import sys
from pathlib import Path


def text(s):
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def agg(letters, rows):
    """rows: list of (team, {letter: (tries, time_or_None)})"""
    out = {}
    for L in letters:
        solved = att = 0
        first = None
        for _, cells in rows:
            tries, t = cells.get(L, (0, None))
            if tries > 0 or t is not None:
                att += 1
            if t is not None:
                solved += 1
                first = t if first is None else min(first, t)
        out[L] = {"solved_teams": solved, "attempted_teams": att, "first_solve_min": first}
    return out


def parse_kattis(path):
    s = Path(path).read_text(encoding="utf8")
    head = s[s.find("<thead"): s.find("</thead>")]
    probs = re.findall(r'data-name="problem\d+">\s*<a href="[^"]*/problems/([^"]+)" title="([^"]*)"[^>]*>\s*([A-Z])\s*</a>', head)
    letters = [p[2] for p in probs]
    body = "".join(re.findall(r"<tbody.*?</tbody>", s, re.S))
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(tds) < 5 + len(letters):
            continue
        team = text(tds[1])
        if not team:  # unnamed host placeholder accounts (0 submissions) -> not official teams
            continue
        cells = {}
        for L, td in zip(letters, tds[5:5 + len(letters)]):
            m = re.search(r'<span class="(first|solved|attempted|pending)"', td)
            if not m:
                cells[L] = (0, None)
                continue
            tries = re.search(r'result-cell-primary">\s*(\d+)', td)
            tries = int(tries.group(1)) if tries else 1
            tm = re.search(r'result-cell-time">\s*(\d+) min', td)
            if m.group(1) in ("first", "solved"):
                cells[L] = (tries, int(tm.group(1)) if tm else None)
            else:
                cells[L] = (tries, None)
        rows.append((team, cells))
    titles = {p[2]: {"title": html.unescape(p[1]), "kattis_short": p[0]} for p in probs}
    return letters, titles, rows


def parse_domjudge(path):
    s = Path(path).read_text(encoding="utf8")
    head = s[s.find("<thead"): s.find("</thead>")]
    probs = re.findall(r'<th title="problem ([^"]*)" scope="col">.*?<span style="color: #[0-9a-fA-F]+;">([A-Z])</span>', head, re.S)
    letters = [p[1] for p in probs]
    titles = {p[1]: {"title": html.unescape(p[0])} for p in probs}
    body = s[s.find("<tbody"): s.find("</tbody>")]
    rows = []
    for tr in re.findall(r'<tr class="[^"]*" id="team:\d+">(.*?)</tr>', body, re.S):
        tn = re.search(r'<td class="scoretn[^"]*" title="([^"]*)"', tr)
        team = html.unescape(tn.group(1)) if tn else "?"
        tds = re.findall(r'<td class="score_cell">(.*?)</td>', tr, re.S)
        cells = {}
        for L, td in zip(letters, tds):
            m = re.search(r'<div class="(score_[a-z_ ]+)">\s*(\d*)(?:&nbsp;)?\s*<span>\s*(\d+) tr', td)
            if not m:
                cells[L] = (0, None)
                continue
            cls, t, tries = m.group(1), m.group(2), int(m.group(3))
            if "score_correct" in cls:
                cells[L] = (tries, int(t))
            else:
                cells[L] = (tries, None)
        rows.append((team, cells))
    return letters, titles, rows


def parse_pc2(path):
    s = Path(path).read_text(encoding="utf8", errors="replace")
    letters = re.findall(r"<th[^>]*>\s*([A-M])\s*</th>", s)
    if not letters:
        hdr = re.search(r"Rank.*?Total", text(s))
        letters = re.findall(r"\b([A-Z])\b", hdr.group(0))
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S | re.I):
        tds = [text(x) for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S | re.I)]
        if len(tds) < 4 + len(letters) or not tds[0].isdigit():
            continue
        team = re.sub(r"^\d+\s+", "", tds[1])
        cells = {}
        for L, c in zip(letters, tds[4:4 + len(letters)]):
            a, t = c.split("/")
            cells[L] = (int(a), None if t == "--" else int(t))
        rows.append((team, cells))
    return letters, {}, rows


def main():
    d = Path(sys.argv[1])
    spec = {
        "nac2021": (parse_kattis, "nac21_standings.html"),
        "nac2022": (parse_kattis, "nac22_standings.html"),
        "nac2023": (parse_domjudge, "nac23_scoreboard.html"),
        "nac2024": (parse_domjudge, "nac24_scoreboard.html"),
        "nac2025": (parse_pc2, "nac25_scoreboard_idx.html"),
        "nac2026": (parse_pc2, "nac26_scoreboard.html"),
    }
    out = {}
    for cid, (fn, f) in spec.items():
        letters, titles, rows = fn(d / f)
        probs = agg(letters, rows)
        for L in letters:
            probs[L].update(titles.get(L, {}))
        out[cid] = {"total_teams": len(rows), "teams": [r[0] for r in rows], "problems": probs}
        print(cid, len(rows), "teams", letters)
        for L in letters:
            print("  ", L, probs[L])
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf8")


if __name__ == "__main__":
    main()
