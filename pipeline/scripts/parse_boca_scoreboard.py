"""Parse a BOCA "Report Page" final scoreboard (as published on scorelatam.naquadah.com.br).

The page contains one big table where each row belongs to a sub-scoreboard ("sitegroupN"),
e.g. group 1 = "PdA" (official LAC teams) or "Global" (official regional teams), and other
groups = sub-regions, CCL guests, etc. Each problem cell is "tries/minute" (accepted) or
"tries/-" (attempted, not accepted) or empty.

Usage:
  python -I parse_boca_scoreboard.py <score.html> [--group N] [--json out.json]

Prints the list of groups (index -> label, row count) and per-problem stats for the chosen
group (default 1): solved_teams, attempted_teams, first_solve_min.
"""
import html
import json
import re
import sys

ROW_RE = re.compile(r'<tr class="sitegroup(\d+)"[^>]*>(.*?)</tr>', re.S)
TD_RE = re.compile(r'<td[^>]*>(.*?)</td>', re.S)
TAG_RE = re.compile(r'<[^>]+>')
CELL_RE = re.compile(r'(\d+)/(\d+|-)')


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(TAG_RE.sub(' ', s))).strip()


def parse(path):
    raw = open(path, encoding='utf-8', errors='replace').read()
    # group labels from the "Available scores" links
    labels = {}
    for m in re.finditer(r'toggleGroup\((\d+)\)"\s*>(.*?)</a>', raw, re.S):
        labels[int(m.group(1))] = text(m.group(2)).replace('Available scores:', '').strip(' ()') or None
    # problem letters from header row
    hdr = re.search(r'<td><b>Name</b></td>(.*?)</tr>', raw, re.S)
    letters = [text(c).strip() for c in TD_RE.findall(hdr.group(1))]
    letters = [l for l in letters if l and l != 'Total']
    rows = []
    for m in ROW_RE.finditer(raw):
        g = int(m.group(1))
        tds = TD_RE.findall(m.group(2))
        if len(tds) < 3 + len(letters):
            continue
        user = text(tds[1])
        name = text(tds[2].split('<br>')[0])
        cells = {}
        for letter, c in zip(letters, tds[3:3 + len(letters)]):
            mm = CELL_RE.search(text(c))
            if mm:
                tries = int(mm.group(1))
                minute = None if mm.group(2) == '-' else int(mm.group(2))
                cells[letter] = (tries, minute)
        rows.append({'group': g, 'rank': text(tds[0]), 'user': user, 'name': name,
                     'cells': cells, 'total': text(tds[3 + len(letters)]) if len(tds) > 3 + len(letters) else None})
    return labels, letters, rows


def stats(letters, rows, group=1, exclude=None):
    seen = set()
    sel = []
    for r in rows:
        if r['group'] != group:
            continue
        key = r['user'].split('/')[0].strip()
        if exclude and exclude(r):
            continue
        if key in seen:  # defensive: same team twice in one group
            continue
        seen.add(key)
        sel.append(r)
    out = {}
    for L in letters:
        solved = [r['cells'][L][1] for r in sel if L in r['cells'] and r['cells'][L][1] is not None]
        att = [r for r in sel if L in r['cells'] and r['cells'][L][0] > 0]
        out[L] = {'solved_teams': len(solved), 'attempted_teams': len(att),
                  'first_solve_min': min(solved) if solved else None}
    return len(sel), out, sel


def main():
    args = sys.argv[1:]
    path = args[0]
    group = int(args[args.index('--group') + 1]) if '--group' in args else 1
    labels, letters, rows = parse(path)
    counts = {}
    for r in rows:
        counts[r['group']] = counts.get(r['group'], 0) + 1
    print('groups:', {g: (labels.get(g), c) for g, c in sorted(counts.items())})
    n, st, sel = stats(letters, rows, group)
    print('group', group, labels.get(group), 'teams:', n)
    for L, s in st.items():
        print(L, s)
    if '--json' in args:
        json.dump({'group': group, 'label': labels.get(group), 'total_teams': n, 'problems': st,
                   'teams': [{'user': r['user'], 'name': r['name']} for r in sel]},
                  open(args[args.index('--json') + 1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
