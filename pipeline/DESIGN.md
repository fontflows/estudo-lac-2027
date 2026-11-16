# DESIGN.md — study guide site, visual and interaction brief

Static site, vanilla HTML/CSS/JS, hash routing. UI copy in pt-BR. This file is the
contract for the frontend developer; values here are deliberate, do not "improve" them
with defaults from a UI kit.

## 1. Principles

- It is a reference tool, not a landing page. The first thing on screen is the ranking
  table, not a hero, slogan or intro paragraph.
- One surface. No cards, no boxes around sections, no shadows except the tooltip.
  Structure comes from alignment, hairlines and whitespace.
- Color carries data, not decoration. Chrome is near-monochrome plus one ink-blue accent.
- Numbers are the content: tabular figures, right-aligned, always with their denominator
  (`41/60`, not `68%` alone).
- Every label is specific. If a sentence could be deleted without losing information,
  delete it. No emojis anywhere (UI, empty states, data text).

## 2. Layout and navigation

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Estudo LAC 2027   Tópicos  Problemas  Contests  Sobre   LAC 2027 · 239 d 07 h  [Tema] │  48px, sticky, hairline bottom
├───────────────────────────────────────────────────────────────────────────┤
│ Page title (h1)                                     muted meta right      │
│ Filter row: [Só LATAM | Geral]  Anos [2019 ▾]–[2026 ▾]  Famílias chips    │
│ ───────────────────────────────────────────────────────────────────────── │
│ table / content                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

- Top nav with 4 text tabs (no sidebar: only 4 destinations). Wordmark is plain text,
  600 weight, no logo/icon. Active tab: `--ink` text + 2px `--accent` underline flush with
  the header hairline; inactive: `--ink-2`.
- Routes: `#/topicos` (default), `#/topico/<slug>`, `#/problemas`, `#/contests/<id>`,
  `#/sobre`. Filters live in the hash query (`?escopo=latam&de=2019&ate=2026&fam=lac,nerc`)
  so any view is linkable; last filter also saved in localStorage (wrapped in try/catch).
- Content column: `max-width: 1120px; margin: 0 auto; padding: 0 24px`. Prose blocks
  (topic key ideas, Sobre) cap at `68ch`.
- Filter row is shared by Tópicos and Problemas, sits directly under the h1, one line on
  desktop. `Só LATAM` = families `lac` + `latam_regional`; `Geral` shows the family chips.
  Show a muted result count at the right end: `47 tópicos · 212 problemas`.
- Mobile (< 720px): header becomes two rows (wordmark + countdown / tabs). Tabs row
  scrolls horizontally, no hamburger. Side gutter 16px. Filter row wraps. Tables keep
  being tables: drop low-priority columns (marked below) instead of turning rows into
  cards; the first column stays sticky-left if the table scrolls.

## 3. Typography

- Family: **IBM Plex Sans** (400, 500, 600) + **IBM Plex Mono** (400, 500) from Google Fonts:
  `https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap`
  Fallback: `"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`.
  Chosen over Inter on purpose (Inter-by-default is the #1 generic tell); Plex reads
  technical, has full Portuguese diacritics and a matching mono.
- Mono only for: problem letters (`A`), contest ids, complexities inside solution ideas
  (`O(n log n)` wrapped in `<code>`).
- `font-variant-numeric: tabular-nums` on `table`, chart ticks, countdown, counts.
- Scale (px / line-height / weight):
  | role | size | lh | weight | color |
  |---|---|---|---|---|
  | h1 page title | 28 | 1.2 | 600, letter-spacing -0.01em | ink |
  | h2 section | 18 | 1.3 | 600 | ink |
  | body / prose | 16 | 1.55 | 400 | ink |
  | table body, controls | 14 | 1.4 | 400 (title cells 500) | ink |
  | table header, meta, chart ticks | 13 | 1.3 | 500 header / 400 meta | ink-2 / muted |
  | tiny (footnotes, sources) | 12 | 1.4 | 400 | muted |
- Sentence case everywhere ("Taxa de AC", not "TAXA DE AC"). No all-caps labels except
  contest acronyms. No italic display text, no text gradients.

## 4. Color tokens

Contrast measured against the page background (WCAG ratio).

| token | light | dark | use |
|---|---|---|---|
| `--bg` | `#fbfaf8` | `#16171a` | page (warm off-white / soft near-black, never pure #fff/#000) |
| `--bg-raised` | `#ffffff` | `#1d1f23` | tooltip, dropdown, expanded row |
| `--ink` | `#1c1d1f` (16.2:1) | `#e8e6e1` (14.4:1) | primary text |
| `--ink-2` | `#55585e` (6.8:1) | `#b5b3ad` (8.6:1) | secondary text, headers |
| `--muted` | `#6b6f76` (4.8:1) | `#8f8d88` (5.4:1) | meta, ticks, "—" |
| `--line` | `#e6e3dd` | `#2a2c30` | hairlines, gridlines |
| `--line-strong` | `#d3cfc7` | `#3a3d42` | header bottom rule, axis baseline, inputs |
| `--row-hover` | `#f3f1ec` | `#202226` | table row hover |
| `--accent` | `#2d5e8c` (6.5:1) | `#8db7de` (8.5:1) | links in prose, active tab, focus, priority bars |
| `--accent-soft` | `#e8eff6` | `#1f2c3a` | selected segment, matrix tint max |
| `--bar-track` | `#ece9e3` | `#26282c` | empty part of inline bars |

Dark mode: follow `prefers-color-scheme`, overridable by a `[Tema]` text button that sets
`html[data-theme=light|dark]` (store choice, try/catch). Declare dark tokens under both
`@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {...} }` and
`:root[data-theme="dark"] {...}`.

**Topic areas (categorical, 12 slots, assigned by `DATASET.areas` order (`order` field), never
re-cycled by rank or filter; areas beyond 12 get the grey fallback `--area-fb`).** Used only as
an 8x8px square swatch beside the area/topic name, and as the dot color in the topic-detail strip
plot. Twelve hues cannot all be told apart under color-blindness (several pairs collapse under
protan/deutan), and slots 9/10/12 and 4/11 are only ~7-8 ΔE apart even for normal vision, so
**area color is never the only encoding**: the name is always printed next to it.

| slot | area in current taxonomy | light | dark |
|---|---|---|---|
| 1 | Grafos | `#3a6ea5` | `#6f9fd4` |
| 2 | Árvores | `#d08042` | `#e0975e` |
| 3 | Programação dinâmica | `#2f7d6b` | `#55ab93` |
| 4 | Estruturas de dados | `#8a4f8f` | `#b98bc0` |
| 5 | Matemática | `#c75a77` | `#e08aa0` |
| 6 | Combinatória | `#c9a43a` | `#d6b85a` |
| 7 | Jogos | `#5aa6c4` | `#7cc0d8` |
| 8 | Strings | `#6b9a3c` | `#8fbc5f` |
| 9 | Geometria | `#7a5a44` | `#b08e74` |
| 10 | Guloso | `#883835` (brick) | `#ca736d` |
| 11 | Busca e técnicas | `#625190` (violet) | `#9d8cd0` |
| 12 | Ad hoc | `#5c571b` (olive) | `#969257` |
| fallback | any area past 12 | `#7d8189` | `#9a9ea6` |

Slots 2, 6, 7 are below 3:1 on light bg: fine as swatches beside text, never as text color.
Slots 10-12 sit in hue gaps (brick, violet, olive; OKLCH C 0.08-0.11), dark variants at the same
hue with L +0.2. Contrast vs page: light 7.6 / 6.5 / 7.1, dark 5.3 / 6.1 / 5.6. Nearest existing
slot ΔE (OKLab x100, normal vision) 8.4 / 7.1 / 7.6; >= 12 among the three new ones.
Text always uses ink tokens, never an area color.

**Difficulty (ordinal, 5 levels by `top_rate` = share of the contest's top-K official teams that
solved it, K = `DATASET.difficulty_k` = 40; `rel_solve` only as fallback; thresholds in SPEC and
`CONFIG` in `assets/core.js`).** Steps move in lightness AND
hue (desaturated teal → amber → terracotta → deep red → plum) so levels read apart at a glance.
Each level has three tokens: `--d-<id>` (dot / strip-plot mark), `--d-<id>-bg` (label tint) and
`--d-<id>-ink` (label text). Wherever a difficulty is shown as a word (tables, topic stats,
Sobre) it is a small label: 4px radius, `-bg` background, `-ink` text, 13px/500, dot inside.
On mobile the word is dropped in tables and the tinted label shrinks to the dot.

| id | label (pt-BR) | rule (`top_rate`) | light dot / bg / ink | dark dot / bg / ink |
|---|---|---|---|---|
| `easy` | Fácil | ≥ 70% | `#8fc4b4` / `#e2f0eb` / `#2c6656` | `#3a7264` / `#1c2d29` / `#8ccab9` |
| `medium` | Médio | 30–70% | `#d9a441` / `#f7ebd0` / `#7d560c` | `#8f7020` / `#2f2717` / `#e2ba68` |
| `hard` | Difícil | 10–30% | `#c86d3e` / `#f6e0d3` / `#94421c` | `#e5844f` / `#33221a` / `#eda47c` |
| `very_hard` | Muito difícil | < 10%, ≥ 1 AC overall | `#a03b3e` / `#f3dbdb` / `#8a2c2f` | `#f0a39a` / `#36201f` / `#f2aca4` |
| `unsolved` | Sem AC | 0 teams | `#5e2d55` / `#ede0ea` / `#5e2d55` | `#efcce5` / `#30232e` / `#efcce5` |

Measured (WCAG, OKLab ×100 with Machado 2009 CVD simulation, severity 1.0):
- Label text on its tint ≥ 5.4:1 (light) and ≥ 7.3:1 (dark); also ≥ 6.2:1 on `--bg` / `--bg-raised`.
- Adjacent dots ΔE: light min 14.2 normal, 11.3 protan, 12.3 deutan, 13.3 tritan;
  dark min 10.0 normal, 9.3 protan, 9.7 deutan, 9.0 tritan.
- Harder = more contrast with the page in both themes (light: dots get darker; dark: lighter).
  The `easy` dot is low-contrast on purpose (1.9:1 light): it always sits beside its word or in
  a chart with a table.
The teal is a muted ordinal step, not a "success" green; no other status red/green is used.

## 5. Spacing, shape, borders

- 4px base: `4, 8, 12, 16, 24, 32, 48, 64`. Section gap 48, h1→filters 16, filters→table 24.
- Radius: 4px on inputs, buttons, segmented control; 1px on swatches; 6px on the tooltip. Tables and
  sections have no radius because they have no box.
- Borders are 1px `--line`. No double rules, no vertical lines in tables.
- Shadows: tooltip only, `0 2px 8px rgb(0 0 0 / .08)` (dark: `/ .4`).
- Motion: background-color 120ms on hover; nothing else animates. Honor
  `prefers-reduced-motion`.

## 6. Tables (the core component)

- Full content width, `border-collapse: collapse`. Header: 13px/500 `--ink-2`, bottom rule
  `--line-strong`, sticky under the site header. Rows: 1px `--line` bottom, padding
  `8px 12px` (row ≈ 36px), no zebra.
- Text left-aligned, numbers right-aligned with tabular figures, units in the header not
  the cell ("1º AC (min)"). Missing values: `—` in `--muted` with `title="sem dado"`.
- Sortable headers: whole header is a `<button>`; current sort shows `▲`/`▼` (text glyph,
  10px, muted) and `aria-sort`. Unsorted headers show nothing (no double-arrow icons).
- Row hover `--row-hover`; whole row clickable only where it navigates (ranking → topic);
  otherwise only the title link is.
- Links in tables are `--ink` with underline on hover; external links get a trailing ` ↗`
  in `--muted`, open in new tab. Prose links are `--accent`, underlined, offset 2px.
- Inline bar: 64–96px wide, 6px tall, radius 3px, track `--bar-track`, fill `--accent`,
  number printed to its right — the bar never stands alone.

## 7. Views

**Tópicos (ranking).** h1 "O que estudar, em ordem". Columns: `#` (muted, right) · Tópico
(swatch + topic 500; area in `--muted` 13px after a thin space, hidden on mobile) ·
Prioridade (inline bar + score) · Problemas (count) · Anos (presence strip, hidden < 720) ·
Taxa de AC média (difficulty dot + `%`). Rows are grouped by tier (section 9). Default sort
= priority; other sorts dissolve the tier grouping.

**Tópico (detail).** Breadcrumb `Tópicos / Grafos / Caminho mínimo com estados` (13px).
h1 = topic, meta line: tier, `14 problemas · 9 contests · 2019–2026`. Then, in this order:
1. "Ideias-chave": 3–6 short bullets, prose measure, no box.
2. "Onde aparece": matrix table, rows = families, columns = years, cell = count
   (blank `·` for 0); cell background from `--bg` to `--accent-soft` by count, number
   always printed. This replaces a frequency chart.
3. "Dificuldade": strip plot (section 8).
4. "Problemas": same table as Problemas view, pre-filtered.

**Problemas (explorer).** Search input first (placeholder "Buscar por título, tópico ou
ideia", `/` focuses it), live filter, count `128 de 302`. Columns: Contest (`LAC 2025`) ·
Letra (mono) · Título ↗ · Tópico (swatch + name) · Resolvido (`41/60`) · Dificuldade (dot +
label, label hidden on mobile) · 1º AC (min, hidden on mobile). Clicking a row toggles an
inline detail row (`--bg-raised`, 16px padding, prose 14px): Enunciado (summary) and
Ideia da solução. **Solution ideas are collapsed by default** behind "Mostrar ideia"
(study without spoilers); a filter-row checkbox "Mostrar ideias" opens all.

**Contests.** Left column (220px) lists editions grouped by family, years descending,
current one in `--ink` 600 with 2px accent left rule; on mobile it becomes a `<select>`.
Main: h1 `LAC 2025`, meta `15 mar 2025 · 60 times · Placar ↗ · Enunciados ↗ · Mirror ↗`.
Problem rows ordered by solved desc: Letra · Título · Tópico · Resolvido (inline bar of
solved/total + `41/60`) · 1º AC. Reading down shows the shape of a set (2 giveaways,
a middle band, 2–3 near-unsolved) without any extra chart.

## 8. Charts (only two kinds, hand-rolled SVG, no chart library needed)

- **Presence strip** (ranking row): one 6×14px cell per year in the selected range, 2px
  gap; filled `--ink-2` if the topic appeared that year, `--line` if not. `title` gives
  `2023: 2 problemas`. No axis; the column header shows the range `2019–26`.
- **Difficulty strip plot** (topic detail): x = % of teams that solved (0–100%), each
  problem a 9px circle colored by its difficulty bin, 1.5px `--bg` ring so overlaps stay
  readable; vertical jitter within 40px band. Axis: ticks at 0, 25, 50, 75, 100% (13px,
  `--muted`), hairline gridlines `--line` at those ticks, baseline `--line-strong`, no
  y-axis, no chart border, no title inside the SVG (the h2 is the title). Label the axis
  once, right-aligned under it: "% dos times que resolveram".
- Tooltip (both): `--bg-raised`, 1px `--line-strong`, radius 6, padding 8×10, 13px, max
  280px. First line 500 weight (`LAC 2024 · C — Título`), second line values with units
  (`12/60 times resolveram · 1º AC 47 min`). Appears instantly on hover and on keyboard
  focus (marks are focusable `<a>`); hit area ≥ 24px; click opens the problem row.
- Rules: chart text ≥ 12px, never rotated; no legends when the label is next to the mark;
  no pie/donut/radar/3D; no gauge for the countdown; every chart has the table beside it.

## 9. Tiers

Computed from priority (thresholds belong to the data pipeline). Shown as **group
headers inside the ranking table**, not as colored badges:

```
Essencial    ·  12 tópicos  ·  apareceu em ≥ 60% dos contests do filtro
  1  ■ Caminho mínimo com estados   Grafos   ▬▬▬▬▬▬▬ 8.4   14   ▮▮▮▯▮▮▮▮   38%
```

- Header row: tier name 14px/600 `--ink`, then count and the factual criterion in
  `--muted` 13px; 32px top padding, `--line-strong` rule above. No icons, no medals.
- Elsewhere (topic detail meta, tooltips) the tier is plain text weighted by rank:
  Essencial 600 ink · Importante 500 ink · Diferencial 400 ink-2 · Raro 400 muted.

## 10. Countdown

- Lives in the header, right side, before the theme button, every page:
  `LAC 2027 · 239 d 07 h` — 13px, tabular, `--ink-2` for numbers, `--muted` for text.
  Hover/`title`: "13 de julho de 2027". Mobile: right end of header row 1.
- Days + hours only; update once a minute. No seconds, no progress ring, no flip digits.
- Target as a constant: `const LAC = new Date("2027-07-13T00:00:00-03:00")` (edit when the
  real start time and city are known). After it passes: "LAC 2027 · em andamento", then hide.

## 11. States

- Focus: `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }` on
  links, buttons, sortable headers, chart marks. Never remove outlines without this.
- Segmented control (`Só LATAM | Geral`): 32px tall, 1px `--line-strong` border; selected
  segment `--accent-soft` bg + `--ink` 500; others `--ink-2`. Chips (families) same style.
- Inputs: 32px, 1px `--line-strong`, 4px radius, `--bg-raised`; focus = accent outline.
- Empty: one muted line in the table body, e.g. "Nenhum problema com esses filtros." +
  text button "Limpar filtros". No illustrations.
- Loading: data is a local `dataset.js`, so no spinners or skeletons.
- Unknown values: `—`. Unsolved problems: `0/60`, 1º AC `—`, bin "Sem AC".

## 12. "AI-generated look" tells to avoid

- Inter/Poppins by default; purple/indigo or blue→violet gradients; gradient text.
- Hero with a big claim and CTA ("Domine o LAC 2027"); filler taglines and intros.
- Grid of rounded cards each with an icon + title + one line; KPI tiles row at the top.
- Glassmorphism, blur, glow, soft shadow on everything, 16–24px radii everywhere.
- Emojis or decorative icons as bullets; sparkle/rocket/trophy motifs.
- Colored pills for every attribute (tier, area, difficulty, family all as badges).
- Uppercase letter-spaced micro-labels everywhere; centered body text.
- Charts for their own sake (donut of areas, radar of skills), legends far from data,
  rainbow palettes, animated count-ups, seconds-ticking countdown.
- Pure `#000`/`#fff` and saturated "primary" blue `#3b82f6`.

## 13. References and what to borrow

- **clist.by/problems** — one-line dense rows; rating as a small glyph beside the number
  (SVG circle filled by fraction, tooltip for detail); tags as quiet inline text.
- **Kattis problem list** — difficulty as number + word (`3.2 Medium`); sortable stat
  columns; 100 rows/page without apology. We use `41/60` + "Médio".
- **Codeforces problemset** — utilitarian: letter + title, solved count column, tags
  small and gray on the right. Density over decoration.
- **cp-algorithms** — topic page as plain article: headings, short paragraphs, code-ish
  complexities. Model for "Ideias-chave".
- **Our World in Data** — Lato body, navy accent (`#1d3d63`), grays `#5b5b5b`/`#767676`;
  chart+table side by side, source notes small and gray, direct labels.
- **Datawrapper blog (text & colors)** — gridlines lighter than labels, ≥ 12px, two text
  levels, no rotated labels, units in tooltips, one gray for missing, one accent for single
  series.
- **GitHub insights / contribution graph** — tiny square presence cells → presence strip.
- **Linear changelog** — restraint: whitespace and type size separate sections, not boxes.
- **Tailwind UI tables / Stripe docs** — header 13px medium gray, `divide-y` hairlines,
  right-aligned numerics, generous horizontal padding, clear focus rings, mono for ids.

Colors in section 4 were checked with WCAG contrast and OKLab ΔE (Machado CVD simulation)
scripts. OWID values come from its live stylesheet; clist/Kattis from their live markup.
