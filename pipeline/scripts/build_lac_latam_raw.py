"""Build pipeline/raw/lac.json and pipeline/raw/latam_regional_2024_2025.json.

Solve counts come from the BOCA final scoreboards saved in pipeline/downloads/scorelatam/*.html
(parsed by parse_boca_scoreboard.py, official sub-scoreboard = sitegroup 1: "PdA" for the
championship, "Global" for the regional). Text annotations live in annotations_lac_latam.py.

Run from anywhere:  python -I pipeline/scripts/build_lac_latam_raw.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse_boca_scoreboard as boca  # noqa: E402
from annotations_lac_latam import CONTESTS, PROBLEMS  # noqa: E402

PIPE = os.path.dirname(HERE)
DL = os.path.join(PIPE, 'downloads', 'scorelatam')


def build(contest_ids, source):
    contests, problems = [], []
    for cid in contest_ids:
        c = dict(CONTESTS[cid])
        html_file = c.pop('_html')
        group = c.pop('_group', 1)
        gym = c.pop('_gym')
        labels, letters, rows = boca.parse(os.path.join(DL, html_file))
        n, st, _ = boca.stats(letters, rows, group)
        c['total_teams'] = n
        contests.append(c)
        ann = PROBLEMS[cid]
        assert sorted(ann) == letters, (cid, sorted(ann), letters)
        for L in letters:
            a = ann[L]
            problems.append({
                'id': f'{cid}-{L}',
                'contest': cid,
                'letter': L,
                'title': a['title'],
                'solved_teams': st[L]['solved_teams'],
                'attempted_teams': st[L]['attempted_teams'],
                'first_solve_min': st[L]['first_solve_min'],
                'links': {
                    'mirror': f'https://codeforces.com/gym/{gym}/problem/{L}' if gym else None,
                    'kattis': None,
                    'statement': c['links']['statements'],
                },
                'statement_summary': a['summary'],
                'solution_idea': a['idea'],
                'solution_source': a['source'],
                'candidate_tags': a['tags'],
                'cf_tags': [],
                'cf_rating': None,
            })
    out = os.path.join(PIPE, 'raw', source + '.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'source': source, 'contests': contests, 'problems': problems}, f,
                  ensure_ascii=False, indent=2)
    print('wrote', out, len(contests), 'contests', len(problems), 'problems')


if __name__ == '__main__':
    build(['lac2024', 'lac2025', 'lac2026'], 'lac')
    build(['latam_regional2024', 'latam_regional2025'], 'latam_regional_2024_2025')
