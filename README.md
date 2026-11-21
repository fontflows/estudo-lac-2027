# Estudo LAC 2027

**Site: https://fontflows.github.io/estudo-lac-2027/**

Static study guide for the ICPC Latin America Championship: a curriculum of reusable insights,
technique deepenings and named techniques taken from the solutions of championship-level problems,
plus topic statistics, difficulty and links to every problem.
Plain HTML/CSS/JS, no build step. Works on GitHub Pages and opened directly from disk (`file://`).

## Files

- `index.html`, `assets/` — the site (`core.js`: constants, topic and curriculum statistics; `charts.js`: SVG charts; `app.js`: views and routing)
- `data/dataset.js` — the data, `window.DATASET = {...}` (generated, do not edit by hand)
- `pipeline/` — data collection and build (`SPEC.md`, `DESIGN.md`)

## Rebuild the data

```
python -I pipeline/build_dataset.py
```

Merges `pipeline/raw/*.json`, `pipeline/taxonomy.json` and, when present, `pipeline/curriculum/curriculum.json` into `data/dataset.js`.
Without the curriculum the Currículo tab shows a short note and the home page is Tópicos.

For working on the site without real data, write a fictitious dataset in the same shape to a separate file
(gitignored) and point a copy of `index.html` at it:

```
python -I pipeline/mock_dataset.py --curriculum --out data/dataset.mock.js
```

Without `--out` the mock overwrites `data/dataset.js`.

Tier thresholds, secondary-topic weight, difficulty bins and curriculum generality labels are in `CONFIG` at the top of `assets/core.js`.
Family weights are in `pipeline/build_dataset.py`.

## View locally

Open `index.html` in a browser. Or serve the folder: `python -m http.server` and open http://localhost:8000.

## Publish on GitHub Pages

1. Push this folder to a GitHub repository (the repository root is the site root).
2. Settings → Pages → Build and deployment → Source: "Deploy from a branch"; branch `main`, folder `/ (root)`.
3. The site is served at https://fontflows.github.io/estudo-lac-2027/ and updates a minute or two after each push to `main`. `.nojekyll` disables Jekyll processing.

Links keep the filter in the URL (`#/topicos?escopo=latam&de=2019&ate=2026`), so any view can be shared.
