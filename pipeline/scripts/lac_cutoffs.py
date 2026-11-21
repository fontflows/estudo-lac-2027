"""Problems-solved thresholds for medals and World Finals qualification at the ICPC Latin America
Championship (LAC 2024, 2025, 2026).

Data: BOCA final scoreboards in pipeline/downloads/scorelatam/pda2X.html, 'PdA' sub-scoreboard
(sitegroup 1 = official teams; CCL guests are not in it), parsed with parse_boca_scoreboard.py.
Each team row carries annotations ("Gold Medalist", "<Region> Region Champion",
"Qualified for the World Finals in ...").

Rules (LAC rules of promotion, ICPC Latin America Regionals 2024/25 rules document):
  - medals by rank: gold 1-4, silver 5-8, bronze 9-12;
  - WF: the champion of each of the six regions gets a slot; the remaining N_WF - 6 slots go to the
    best overall performance; only one team per institution may advance.
Performance cutoff (owner's simple rule): walk the official ranking from rank 1; qualified teams
are "by performance" until the first non-qualified team that is NOT a rank-skip (a rank-skip is a
team whose institution already has a qualified team above it). Qualified teams below that point
got the slot by quota (region champion) and are excluded from the threshold.

Usage: python -I pipeline/scripts/lac_cutoffs.py
Writes pipeline/extra/lac_cutoffs.json.
"""
import html
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
DL = os.path.join(PIPE, "downloads", "scorelatam")
SL = "https://scorelatam.naquadah.com.br"
RULES_URL = "https://icpc.com.ar/wp-content/uploads/2024/11/icpc-latin-america-regionals-rules-2024-2025.pdf"

spec = importlib.util.spec_from_file_location("parse_boca_scoreboard",
                                              os.path.join(HERE, "parse_boca_scoreboard.py"))
boca = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boca)

EDITIONS = [("lac2024", "pda24"), ("lac2025", "pda25"), ("lac2026", "pda26")]
MEDALS = [("gold", "Ouro", "Gold Medalist"), ("silver", "Prata", "Silver Medalist"),
          ("bronze", "Bronze", "Bronze Medalist")]
REGION_PT = {"Brazil": "Brasil", "Mexico": "México", "Caribbean": "Caribe",
             "Central America": "América Central", "South America North": "América do Sul Norte",
             "South America South": "América do Sul Sul"}
TOTAL_RE = re.compile(r"(\d+)\s*\((\d+)\)")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def name_cells(path):
    """user -> (team name, [annotation strings]) for sitegroup-1 rows, from the raw name cell."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for m in boca.ROW_RE.finditer(raw):
        if m.group(1) != "1":
            continue
        tds = boca.TD_RE.findall(m.group(2))
        if len(tds) < 3:
            continue
        user = boca.text(tds[1])
        cell = tds[2]
        # name, then one annotation per line (<br>, <br/> or </br>; the <b> wrapper is not always closed)
        parts = re.split(r"</br>|<br\s*/?>", cell)
        head = parts[0]
        notes = [re.sub(r"^[^\w]+", "", clean(x)).strip() for x in parts[1:]]
        notes = [x for x in notes if x]
        out[user] = (clean(head), notes)
    return out


def institution(name):
    m = re.match(r"\s*\[([^\]]+)\]", name)
    return m.group(1).strip() if m else name


def load(fname):
    path = os.path.join(DL, fname + ".html")
    labels, letters, rows = boca.parse(path)
    assert labels.get(1) == "PdA", labels
    n, _, sel = boca.stats(letters, rows, 1)
    ann = name_cells(path)
    teams = []
    for i, r in enumerate(sel):
        solved = sum(1 for (_t, mnt) in r["cells"].values() if mnt is not None)
        tm = TOTAL_RE.search(r["total"] or "")
        assert tm and int(tm.group(1)) == solved, (fname, r["user"], r["total"], solved)
        name, notes = ann[r["user"]]
        champ = [x.replace(" Region Champion", "") for x in notes if x.endswith("Region Champion")]
        teams.append({"pos": i + 1, "rank": r["rank"], "user": r["user"], "team": name,
                      "inst": institution(name), "solved": solved, "penalty": int(tm.group(2)),
                      "notes": notes, "region_champion": champ[0] if champ else None,
                      "wf": any(x.startswith("Qualified for the World Finals") for x in notes)})
    for a, b in zip(teams, teams[1:]):  # official order: solved desc, penalty asc
        assert (a["solved"], -a["penalty"]) >= (b["solved"], -b["penalty"]), (fname, a, b)
    return letters, teams


def category(cid, name, members, teams, excluded=()):
    """members: teams in the category (rank order). tie_out: some team ranked below the last member,
    not in the category and not in `excluded` (rank-skips), solved exactly min_solved."""
    mins = min(t["solved"] for t in members)
    last = members[-1]
    ids = {t["user"] for t in members}
    out_same = [t for t in teams if t["pos"] > last["pos"] and t["user"] not in ids
                and t["user"] not in excluded and t["solved"] == mins]
    return {"id": cid, "name": name, "teams": len(members), "min_solved": mins,
            "max_solved": max(t["solved"] for t in members), "tie_out": bool(out_same),
            "last_penalty": last["penalty"],
            "first_out_penalty": out_same[0]["penalty"] if out_same else None}


def edition(cid, fname, year):
    letters, teams = load(fname)
    cats = []
    for mid, mname, label in MEDALS:
        members = [t for t in teams if label in t["notes"]]
        cats.append(category(mid, mname, members, teams))
    # medal ranks must be 1-4 / 5-8 / 9-12 (rules)
    for k, (mid, _n, label) in enumerate(MEDALS):
        assert [t["pos"] for t in teams if label in t["notes"]] == list(range(4 * k + 1, 4 * k + 5)), (cid, mid)

    qualified_inst = {}
    perf, quota, skipped = [], [], []
    stopped = False
    for t in teams:
        if t["wf"]:
            assert t["inst"] not in qualified_inst, (cid, t)
            qualified_inst[t["inst"]] = t
            (quota if stopped else perf).append(t)
        elif t["inst"] in qualified_inst:
            skipped.append(t)  # one team per institution
        else:
            stopped = True
    for t in quota:
        assert t["region_champion"], (cid, "qualified below cutoff without region title", t)
    n_champ_in_perf = sum(1 for t in perf if t["region_champion"])
    wf = category("wf", "World Finals (por desempenho)", perf, teams,
                  excluded={t["user"] for t in skipped})
    cats.append(wf)
    first_out = next(t for t in teams if not t["wf"] and t not in skipped and t["pos"] > perf[-1]["pos"])
    n_wf = len(perf) + len(quota)
    regions = sorted({t["region_champion"] for t in teams if t["region_champion"]})
    assert len(regions) == 6, (cid, regions)

    excl = [{"team": t["team"], "rank": t["pos"], "solved": t["solved"], "penalty": t["penalty"],
             "reason": f"vaga de campeão da região {REGION_PT.get(t['region_champion'], t['region_champion'])}"}
            for t in quota]
    skips = [{"team": t["team"], "rank": t["pos"], "solved": t["solved"], "penalty": t["penalty"],
              "reason": f"instituição {t['inst']} já classificada (rank {qualified_inst[t['inst']]['pos']})"}
             for t in skipped if t["pos"] < first_out["pos"]]
    notes = (f"{n_wf} vagas para o Mundial: 6 campeões de região + {n_wf - 6} por desempenho geral, "
             f"no máximo 1 time por instituição. Corte por desempenho = times classificados do 1º lugar "
             f"até o primeiro time não classificado (exceto pulos por instituição): {len(perf)} times, "
             f"dos quais {n_champ_in_perf} também foram campeões de região mas estavam dentro do corte. "
             f"Primeiro de fora: {first_out['team']} (rank {first_out['pos']}, {first_out['solved']} "
             f"problemas, {first_out['penalty']} min). "
             f"{len(skips)} time(s) acima do corte pulado(s) por já ter outro time da mesma instituição "
             f"classificado. Medalhas por posição: ouro 1–4, prata 5–8, bronze 9–12. "
             f"Times oficiais = placar 'PdA' (convidados CCL fora).")
    return {"contest": cid, "year": year, "teams": len(teams), "problems": len(letters),
            "wf_slots_total": n_wf, "categories": cats, "excluded_quota": excl,
            "rank_skipped": skips, "notes": notes}


def main():
    lac = json.load(open(os.path.join(PIPE, "raw", "lac.json"), encoding="utf-8"))
    years = {c["id"]: c["year"] for c in lac["contests"]}
    eds = [edition(cid, f, years[cid]) for cid, f in EDITIONS]
    out = {"generated_by": "pipeline/scripts/lac_cutoffs.py",
           "editions": eds,
           "sources": [f"{SL}/{f}/" for _c, f in EDITIONS] + [RULES_URL]}
    dst = os.path.join(PIPE, "extra", "lac_cutoffs.json")
    with open(dst, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    for e in eds:
        print(e["contest"], e["teams"], "teams", e["problems"], "problems, WF slots", e["wf_slots_total"])
        for c in e["categories"]:
            print("  ", c)
        for x in e["excluded_quota"]:
            print("   quota:", x)
        for x in e["rank_skipped"]:
            print("   skip:", x)
    print("wrote", dst)


if __name__ == "__main__":
    main()
