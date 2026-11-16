"""Generate a MOCK data/dataset.js in the exact final shape (see SPEC.md "Final dataset").

Only for developing the site before the real data exists. It is overwritten by
    python -I pipeline/build_dataset.py
Usage:
    python -I pipeline/mock_dataset.py
"""
import datetime
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "dataset.js")

FAMILIES = [
    {"id": "lac", "name": "ICPC Latin America Championship", "short": "LAC", "weight": 1.0, "group": "latam"},
    {"id": "latam_regional", "name": "ICPC Latin American Regional", "short": "Regional LATAM", "weight": 0.6, "group": "latam"},
    {"id": "nac", "name": "ICPC North America Championship", "short": "NAC", "weight": 0.8, "group": "world"},
    {"id": "nerc", "name": "ICPC Northern Eurasia Finals", "short": "NERC", "weight": 0.8, "group": "world"},
    {"id": "apac", "name": "ICPC Asia Pacific Championship", "short": "APAC", "weight": 0.8, "group": "world"},
]

AREAS = [
    ("graphs", "Grafos"), ("dp", "Programação dinâmica"), ("math", "Matemática e teoria dos números"),
    ("ds", "Estruturas de dados"), ("strings", "Strings"), ("geometry", "Geometria"),
    ("search", "Busca e técnicas"), ("greedy", "Guloso e ad hoc"), ("combinatorics", "Combinatória e probabilidade"),
    ("other", "Outros"),
]

CPA = "https://cp-algorithms.com/"
# (id, area, name, popularity, hardness 0..1, ref path)
TOPICS = [
    ("shortest-paths-states", "graphs", "Caminho mínimo em grafo de estados", 6, .45, "graph/dijkstra.html"),
    ("dijkstra-basic", "graphs", "Dijkstra", 4, .3, "graph/dijkstra.html"),
    ("bfs-grid", "graphs", "BFS em grid", 4, .15, "graph/breadth-first-search.html"),
    ("dsu", "graphs", "Union-find (DSU)", 5, .35, "data_structures/disjoint_set_union.html"),
    ("mst", "graphs", "Árvore geradora mínima", 2, .35, "graph/mst_kruskal.html"),
    ("scc-2sat", "graphs", "Componentes fortemente conexas e 2-SAT", 2, .7, "graph/2SAT.html"),
    ("max-flow", "graphs", "Fluxo máximo e corte mínimo", 3, .8, "graph/dinic.html"),
    ("bipartite-matching", "graphs", "Emparelhamento bipartido", 2, .7, "graph/kuhn_maximum_bipartite_matching.html"),
    ("lca-binary-lifting", "graphs", "LCA com binary lifting", 3, .55, "graph/lca_binary_lifting.html"),
    ("tree-dp", "dp", "DP em árvore", 5, .55, "graph/depth-first-search.html"),
    ("dp-bitmask", "dp", "DP com bitmask", 4, .65, "dynamic_programming/profile-dynamics.html"),
    ("dp-intervals", "dp", "DP em intervalos", 3, .55, "dynamic_programming/intro-to-dp.html"),
    ("dp-knapsack", "dp", "Mochila e variações", 4, .35, "dynamic_programming/knapsack.html"),
    ("dp-digits", "dp", "DP de dígitos", 2, .6, "dynamic_programming/intro-to-dp.html"),
    ("dp-optimizations", "dp", "Otimizações de DP (CHT, D&C)", 2, .9, "geometry/convex_hull_trick.html"),
    ("dp-probability", "dp", "DP com probabilidade e esperança", 3, .65, "dynamic_programming/intro-to-dp.html"),
    ("modular-arith", "math", "Aritmética modular e inverso", 4, .4, "algebra/module-inverse.html"),
    ("sieve-factorization", "math", "Crivo e fatoração", 3, .35, "algebra/sieve-of-eratosthenes.html"),
    ("gcd-diophantine", "math", "MDC e equações diofantinas", 2, .45, "algebra/extended-euclid-algorithm.html"),
    ("matrix-expo", "math", "Exponenciação de matrizes", 2, .6, "algebra/binary-exp.html"),
    ("fft", "math", "FFT e convolução", 1, .9, "algebra/fft.html"),
    ("game-theory", "math", "Teoria dos jogos (Grundy)", 2, .6, "game_theory/sprague-grundy-nim.html"),
    ("segtree-lazy", "ds", "Segment tree com lazy", 5, .65, "data_structures/segment_tree.html"),
    ("segtree-basic", "ds", "Segment tree e BIT", 5, .45, "data_structures/fenwick.html"),
    ("sparse-table", "ds", "Sparse table e RMQ", 2, .4, "data_structures/sparse-table.html"),
    ("sweep-line", "ds", "Sweep line com estrutura", 3, .7, "geometry/intersecting_segments.html"),
    ("offline-queries", "ds", "Consultas offline (Mo, ordenação)", 2, .75, "data_structures/sqrt_decomposition.html"),
    ("sqrt-decomp", "ds", "Decomposição em raiz", 1, .7, "data_structures/sqrt_decomposition.html"),
    ("hld-centroid", "ds", "HLD e decomposição em centroides", 2, .85, "graph/hld.html"),
    ("hashing", "strings", "Hashing de strings", 3, .5, "string/string-hashing.html"),
    ("kmp-z", "strings", "KMP e função Z", 3, .5, "string/prefix-function.html"),
    ("suffix-array", "strings", "Suffix array e LCP", 2, .85, "string/suffix-array.html"),
    ("aho-corasick", "strings", "Aho-Corasick", 1, .8, "string/aho_corasick.html"),
    ("palindromes", "strings", "Palíndromos (Manacher)", 1, .6, "string/manacher.html"),
    ("convex-hull", "geometry", "Fecho convexo", 3, .6, "geometry/convex-hull.html"),
    ("geo-primitives", "geometry", "Primitivas geométricas (produto vetorial)", 4, .5, "geometry/basic-geometry.html"),
    ("polygon-area", "geometry", "Área e pontos em polígono", 2, .45, "geometry/area-of-simple-polygon.html"),
    ("circles", "geometry", "Círculos e interseções", 1, .75, "geometry/circle-circle-intersection.html"),
    ("binary-search-answer", "search", "Busca binária na resposta", 7, .45, "num_methods/binary_search.html"),
    ("two-pointers", "search", "Dois ponteiros", 4, .3, "num_methods/binary_search.html"),
    ("ternary-search", "search", "Busca ternária", 1, .5, "num_methods/ternary_search.html"),
    ("meet-in-middle", "search", "Meet in the middle", 1, .65, "num_methods/binary_search.html"),
    ("backtracking", "search", "Busca exaustiva com poda", 2, .5, "num_methods/binary_search.html"),
    ("greedy-exchange", "greedy", "Guloso com argumento de troca", 6, .4, "schedules/schedule_one_machine.html"),
    ("greedy-sorting", "greedy", "Ordenação e guloso por eventos", 5, .25, "schedules/schedule_with_completion_duration.html"),
    ("adhoc-observation", "greedy", "Ad hoc por observação", 7, .3, "index.html"),
    ("prefix-sums", "greedy", "Somas de prefixo e diferenças", 4, .15, "data_structures/fenwick.html"),
    ("counting-binomials", "combinatorics", "Contagem com binomiais", 4, .5, "combinatorics/binomial-coefficients.html"),
    ("inclusion-exclusion", "combinatorics", "Inclusão-exclusão", 2, .65, "combinatorics/inclusion-exclusion.html"),
    ("expected-value", "combinatorics", "Valor esperado e linearidade", 2, .6, "combinatorics/inclusion-exclusion.html"),
    ("constructive", "other", "Construtivo", 5, .5, "index.html"),
    ("interactive", "other", "Interativo", 2, .55, "index.html"),
    ("simulation", "other", "Simulação e implementação", 5, .2, "index.html"),
]

CONTESTS = [
    ("lac", 2024, "03-16", 60), ("lac", 2025, "03-15", 62), ("lac", 2026, "03-14", 60),
    ("latam_regional", 2019, "11-09", 412), ("latam_regional", 2020, "11-21", 380),
    ("latam_regional", 2021, "11-13", 401), ("latam_regional", 2022, "11-12", 455),
    ("latam_regional", 2023, "11-11", 471), ("latam_regional", 2024, "11-09", 489),
    ("latam_regional", 2025, "11-08", 503),
    ("nac", 2021, "08-05", 48), ("nac", 2022, "05-28", 52), ("nac", 2023, "05-27", 50), ("nac", 2024, "05-25", 50),
    ("nerc", 2019, "12-01", 300), ("nerc", 2021, "04-21", 260), ("nerc", 2022, "12-07", 290), ("nerc", 2024, "12-04", 310),
    ("apac", 2024, "03-03", 64), ("apac", 2025, "03-01", 66),
]

W1 = ["Lazy", "Broken", "Hidden", "Twin", "Circular", "Magic", "Secret", "Balanced", "Fast", "Long",
      "Lost", "Silent", "Golden", "Crazy", "Royal", "Final", "Mirror", "Prime", "Little", "Endless"]
W2 = ["Robots", "Bridges", "Tokens", "Gardens", "Towers", "Trains", "Queries", "Fences", "Coins", "Cards",
      "Lamps", "Rivers", "Islands", "Palindromes", "Permutations", "Paths", "Shelves", "Dice", "Buses", "Grid"]
COMPLEX = ["O(n log n)", "O(n)", "O(n log^2 n)", "O(n sqrt n)", "O(n · 2^k)", "O(n^2)", "O((n + m) log n)"]


def difficulty(rel):
    if rel is None:
        return None
    if rel >= 0.6:
        return "easy"
    if rel >= 0.25:
        return "medium"
    if rel >= 0.05:
        return "hard"
    return "very_hard"


def main():
    rnd = random.Random(2027)
    fam = {f["id"]: f for f in FAMILIES}
    areas = [{"id": a, "name": n, "order": i + 1} for i, (a, n) in enumerate(AREAS)]
    topics = []
    for tid, area, name, pop, hard, ref in TOPICS:
        topics.append({
            "id": tid, "area": area, "name": name,
            "description": f"{name}: reconhecer quando aplicar, variações comuns e armadilhas de implementação.",
            "includes": [tid.replace("-", " ")],
            "refs": [{"label": f"cp-algorithms — {name}", "url": CPA + ref}],
        })
    pops = [t[3] for t in TOPICS]
    tinfo = {t[0]: t for t in TOPICS}

    contests, problems = [], []
    gym = 104000
    for fid, year, md, teams in CONTESTS:
        gym += rnd.randint(30, 260)
        cid = f"{fid}{year}"
        n = rnd.choice([11, 12, 12, 12, 13])
        mirror = f"https://codeforces.com/gym/{gym}"
        contests.append({
            "id": cid, "family": fid, "name": f"{fam[fid]['name']} {year}",
            "short": f"{fam[fid]['short']} {year}", "year": year, "date": f"{year}-{md}",
            "total_teams": teams,
            "links": {
                "scoreboard": f"https://example.org/{cid}/scoreboard",
                "statements": f"https://example.org/{cid}/problems.pdf",
                "editorial": f"https://example.org/{cid}/editorial.pdf" if rnd.random() < .6 else None,
                "mirror": mirror,
                "kattis": f"https://open.kattis.com/contests/{cid}" if fid == "nac" else None,
            },
            "notes": "dados fictícios (mock)",
        })
        # pick topics, order by hardness -> solve curve
        chosen = []
        while len(chosen) < n:
            t = rnd.choices(TOPICS, weights=pops)[0][0]
            if t not in chosen or rnd.random() < .1:
                chosen.append(t)
        chosen.sort(key=lambda t: tinfo[t][4] + rnd.uniform(-.25, .25))
        curve = sorted([rnd.uniform(.0, 1.0) ** 2.2 for _ in range(n)], reverse=True)
        curve[0] = max(curve[0], rnd.uniform(.8, .97))
        letters = [chr(65 + i) for i in range(n)]
        rnd.shuffle(letters)
        ps = []
        for i, t in enumerate(chosen):
            letter = letters[i]
            solved = int(round(curve[i] * teams))
            if i == n - 1 and rnd.random() < .5:
                solved = 0
            att = min(teams, solved + int(rnd.uniform(.05, .4) * teams)) if rnd.random() < .85 else None
            fs = None
            if solved:
                fs = int(4 + (1 - curve[i]) ** 1.5 * 260 * rnd.uniform(.6, 1.1))
                if rnd.random() < .08:
                    fs = None
            sec = []
            for _ in range(rnd.choice([0, 0, 0, 1, 1, 2])):
                s = rnd.choices(TOPICS, weights=pops)[0][0]
                if s != t and s not in sec:
                    sec.append(s)
            title = f"{rnd.choice(W1)} {rnd.choice(W2)}"
            cx = rnd.choice(COMPLEX)
            ps.append({
                "id": f"{cid}-{letter}", "contest": cid, "family": fid, "year": year, "letter": letter,
                "title": title, "solved": solved, "attempted": att, "total": teams,
                "first_solve_min": fs,
                "links": {
                    "mirror": f"{mirror}/problem/{letter}",
                    "kattis": f"https://open.kattis.com/problems/{title.lower().replace(' ', '')}" if fid == "nac" else None,
                    "statement": f"https://example.org/{cid}/problems.pdf",
                },
                "summary": f"Dado um conjunto de até 2·10^5 elementos, responder ao que o enunciado de \"{title}\" pede. Texto fictício.",
                "solution": f"Aplicar {tinfo[t][2].lower()} depois de reduzir o problema à forma certa; a observação central limita os estados. Complexidade {cx}.",
                "solution_source": rnd.choice(["editorial", "editorial", "community", "own"]),
                "key_idea": f"Reduzir a {tinfo[t][2].lower()} observando a monotonicidade da resposta.",
                "primary": t, "secondary": sec,
                "confidence": rnd.choice(["high", "high", "medium"]),
                "cf_tags": [], "cf_rating": None,
            })
        mx = max(p["solved"] for p in ps)
        for p in ps:
            if rnd.random() < .03:
                p["solved"] = None
            s = p["solved"]
            rel = (s / mx) if (s is not None and mx) else (0.0 if s == 0 else None)
            p["solve_rate"] = round(s / teams, 4) if s is not None else None
            p["rel_solve"] = round(rel, 4) if rel is not None else None
            p["difficulty"] = difficulty(rel)
        contests[-1]["problem_count"] = len(ps)
        contests[-1]["max_solved"] = mx
        problems.extend(ps)

    # key order like build_dataset.py
    order = ["id", "contest", "family", "year", "letter", "title", "solved", "attempted", "total",
             "first_solve_min", "solve_rate", "rel_solve", "difficulty", "links", "summary", "solution",
             "solution_source", "key_idea", "primary", "secondary", "confidence", "cf_tags", "cf_rating"]
    problems = [{k: p[k] for k in order} for p in problems]
    contests.sort(key=lambda c: (c["year"], c.get("date") or "", c["id"]))
    problems.sort(key=lambda p: (p["contest"], p["letter"]))
    dataset = {
        "generated": datetime.date.today().isoformat(),
        "mock": True,
        "target": {"name": "ICPC Latin America Championship 2027", "date": "2027-07-13T09:00:00-03:00"},
        "families": FAMILIES, "areas": areas, "topics": topics,
        "contests": contests, "problems": problems,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("window.DATASET = ")
        json.dump(dataset, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")
    print(f"MOCK contests={len(contests)} problems={len(problems)} topics={len(topics)} -> {OUT}")


if __name__ == "__main__":
    main()
