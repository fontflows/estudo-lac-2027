"""Parse NERC (nerc.itmo.ru) PCMS2 final standings HTML into per-problem stats.

Usage: python -I nerc_parse_standings.py <downloads/nerc dir> <out.json>
Teams whose name starts with '*' are treated as out-of-competition and excluded.
"""
import html
import json
import re
import sys
from pathlib import Path

FILES = {
    "nerc2019": "st_2019.html",
    "nerc2021": "st_2020.html",      # 2020-2021 season onsite, held 2021-04-04
    "nerc2022apr": "st_2021.html",   # 2021-2022 season, held 2022-04-13
    "nerc2022dec": "st_2022.html",
    "nerc2023": "st_2023.html",
    "nerc2024": "st_2024.html",
    "nerc2025": "st_2025.html",
}


def text(x):
    return html.unescape(re.sub(r"<[^>]+>", " ", x)).strip()


def parse(path):
    raw = path.read_bytes()
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        s = raw.decode("cp1251", errors="replace")
    head = re.search(r"<thead>(.*?)</thead>", s, re.S).group(1)
    probs = re.findall(r'<th class="problem" title="([^"]*)">([^<]*)</th>', head)
    probs = [(html.unescape(t), l.strip()) for t, l in probs]
    rows = re.findall(r'<tr class="row\d\d">(.*?)</tr>', s, re.S)
    stats = {l: {"title": t, "solved": 0, "attempted": 0, "first": None} for t, l in probs}
    total = excluded = 0
    excl_names = []
    for r in rows:
        tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        name = text(tds[1])
        if name.startswith("*"):
            excluded += 1
            excl_names.append(name)
            continue
        total += 1
        cells = tds[2:2 + len(probs)]
        for (t, l), c in zip(probs, cells):
            m = re.search(r"<s>\s*(?:<br>)?\s*(\d+):(\d+)", c)
            v = text(re.sub(r"<s>.*?</s>", "", c, flags=re.S))
            if v.startswith("+"):
                st = stats[l]
                st["solved"] += 1
                st["attempted"] += 1
                if m:
                    mins = int(m.group(1))
                    if st["first"] is None or mins < st["first"]:
                        st["first"] = mins
            elif v.startswith("-") or v.startswith("?"):
                stats[l]["attempted"] += 1
    return {"total_teams": total, "excluded": excluded, "excluded_names": excl_names,
            "problems": stats}


def main():
    d = Path(sys.argv[1])
    out = {cid: parse(d / f) for cid, f in FILES.items()}
    Path(sys.argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for cid, v in out.items():
        print(cid, v["total_teams"], "excl", v["excluded_names"])
        for l, st in v["problems"].items():
            print("  ", l, st["title"], st["solved"], st["attempted"], st["first"])


if __name__ == "__main__":
    main()
