"""Split pdftotext output of NERC statements/tutorials into per-problem chunks.

Usage: python -I nerc_split.py <file.txt> [maxchars]
Prints each problem as: header, then condensed text (whitespace collapsed),
dropping page headers and the solution-stats tables.
"""
import re
import sys

path = sys.argv[1]
maxc = int(sys.argv[2]) if len(sys.argv) > 2 else 2500
s = open(path, encoding="utf-8", errors="replace").read()
lines = []
for ln in s.splitlines():
    t = ln.strip()
    if not t:
        continue
    if re.match(r"^(ICPC 20\d\d|St\. Petersburg|Page \d+ of \d+)", t):
        continue
    if re.match(r"^(Fastest|Shortest|Max atts\.|solution team|Total time|0h 1h|Accepted|Rejected|Time limit|Memory limit)", t):
        continue
    lines.append(re.sub(r"\s+", " ", t))
txt = "\n".join(lines)
parts = re.split(r"\n(?=Problem [A-Z]\. )", txt)
for p in parts:
    if not p.startswith("Problem "):
        continue
    body = p
    if "statement" in path:
        # keep legend + Input section, skip examples
        body = re.split(r"\n(Example|Examples)\n", body)[0]
    print("=" * 8)
    print(body[:maxc])
