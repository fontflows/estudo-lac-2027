# Estudo LAC 2027

Static study guide for the ICPC Latin America Championship: which topics appear most in
championship-level contests, how hard they are, and links to every problem.
Plain HTML/CSS/JS, no build step. Works on GitHub Pages and opened directly from disk (`file://`).

## Files

- `index.html`, `assets/` — the site (`core.js`: constants and topic statistics; `charts.js`: SVG charts; `app.js`: views and routing)
- `data/dataset.js` — the data, `window.DATASET = {...}` (generated, do not edit by hand)
- `pipeline/` — data collection and build (`SPEC.md`, `DESIGN.md`)

## Rebuild the data

```
python -I pipeline/build_dataset.py
```

Merges `pipeline/raw/*.json` and `pipeline/taxonomy.json` into `data/dataset.js`.
`python -I pipeline/mock_dataset.py` writes a fictitious dataset in the same shape, for working on the site without real data.

Tier thresholds, secondary-topic weight and difficulty bins are in `CONFIG` at the top of `assets/core.js`.
Family weights are in `pipeline/build_dataset.py`.

## View locally

Open `index.html` in a browser. Or serve the folder: `python -m http.server` and open http://localhost:8000.

## Publish on GitHub Pages

1. Push this folder to a GitHub repository (the repository root is the site root).
2. Settings → Pages → Build and deployment → Source: "Deploy from a branch"; branch `main`, folder `/ (root)`.
3. The site is served at `https://<user>.github.io/<repo>/`. `.nojekyll` disables Jekyll processing.

Links keep the filter in the URL (`#/topicos?escopo=latam&de=2019&ate=2026`), so any view can be shared.
