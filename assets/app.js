/* app.js — router, filter state and the four views. Everything is derived from window.DATASET. */
(function () {
  "use strict";
  var SG = window.SG, D = SG.D, IX = SG.IX, CONFIG = SG.CONFIG, esc = SG.esc;
  var app = document.getElementById("app");
  var EXT = '<span class="ext" aria-hidden="true"> ↗</span>';
  var DASH = '<span class="na" title="sem dado">—</span>';
  var MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"];

  if (!D || !IX) {
    app.innerHTML = '<h1>Sem dados</h1><p class="prose">Arquivo <code>data/dataset.js</code> não encontrado. Gere com <code>python -I pipeline/build_dataset.py</code>.</p>';
    return;
  }

  // ---- Storage (always guarded) --------------------------------------------------------
  function store(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* ignore */ } }
  function load(k) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : null; } catch (e) { return null; } }

  // ---- Small formatters ----------------------------------------------------------------
  function fmtDate(iso) {
    if (!iso) return null;
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
    if (!m) return iso;
    return (+m[3]) + " " + MONTHS[+m[2] - 1] + " " + m[1];
  }
  function num(x, d) { var s = SG.fmtNum(x, d); return s == null ? DASH : s; }
  function extLink(url, label, cls) {
    if (!url) return "";
    return '<a class="' + (cls || "") + '" href="' + esc(url) + '" target="_blank" rel="noopener">' + label + EXT + "</a>";
  }
  function codeify(text) {
    return esc(text).replace(/O\((?:[^()]|\([^()]*\))*\)/g, function (m) { return "<code>" + m + "</code>"; });
  }
  function norm(s) {
    return String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  function topicName(id) { var t = IX.topicById[id]; return t ? t.name : id; }
  function areaOfTopic(id) { var t = IX.topicById[id]; return t ? IX.areaById[t.area] : null; }
  function swatch(areaId) {
    var a = IX.areaById[areaId];
    return '<span class="sw a' + (a ? a._slot : "-fb") + '" aria-hidden="true"></span>';
  }
  function diffCell(bin, showLabel, title) {
    if (!bin) return DASH;
    var d = SG.DIFF[bin];
    return '<span class="diff lv lv-' + bin + '"' + (title ? ' title="' + esc(title) + '"' : "") + '><span class="dot d-' + bin + '" aria-hidden="true"></span>' +
      '<span class="' + (showLabel === "desktop" ? "hide-m" : "") + '">' + esc(d.name) + "</span></span>";
  }
  function tierText(tier) { return '<span class="tier t-' + tier.id + '">' + esc(tier.name) + "</span>"; }
  function yearSpan(a, b) { return a === b ? String(a) : a + "–" + b; }
  function bestLink(p) { var l = p.links || {}; return l.mirror || l.kattis || l.statement || null; }
  // "12 de 40 melhores" (top_rate) or "34% do mais resolvido" (fallback)
  function topText(p) {
    if (p.top_rate != null) {
      var k = p.k_used || SG.K;
      if (p.solved_top != null && k) return p.solved_top + " de " + k + " melhores times";
      return Math.round(p.top_rate * 100) + "% dos melhores times";
    }
    if (p.rel_solve != null) return Math.round(p.rel_solve * 100) + "% do problema mais resolvido";
    return null;
  }
  var TOPK = SG.K ? SG.K + " melhores times" : "melhores times";
  function contestShort(cid) { var c = IX.contestById[cid]; return c ? (c.short || c.id) : cid; }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }

  // ---- Curriculum references (DATASET.curriculum may be absent) -----------------------
  var CUR = IX.cur;
  var HOME = CUR ? "curriculo" : "topicos";
  var SEC_OF_KIND = { insight: "insights", deepening: "aprofundamentos", technique: "tecnicas" };
  var CAT_KIND = { A: "technique", B: "deepening", C: "insight" };
  var CAT_LABEL = { A: "técnica", B: "aprofundamento", C: "insight" };
  function curItem(kind, id) {
    if (!CUR || id == null) return null;
    if (kind === "insight") return CUR.insightById[id] || null;
    if (kind === "deepening") return CUR.deepeningById[id] || null;
    if (kind === "technique") return CUR.techniqueByName[id] || null;
    return null;
  }
  function curHref(kind, id) { return link("curriculo/" + SEC_OF_KIND[kind] + "/" + encodeURIComponent(id)); }
  function curDomId(kind, id) {
    return "c-" + kind + "-" + String(id).replace(/[^A-Za-z0-9_-]/g, function (c) { return "_" + c.charCodeAt(0).toString(16); });
  }
  function stepsOf(p) { return CUR ? CUR.steps[p.id] || null : null; }
  // "Etapas da solução" block inside the (spoiler) idea area of a problem row.
  function stepsHTML(p) {
    var ps = stepsOf(p);
    if (!ps) return "";
    if (ps.keep === false) {
      return '<p class="small muted">Fora do currículo' + (ps.discard_reason ? ": " + codeify(ps.discard_reason) : "") + "</p>";
    }
    var steps = ps.steps || [];
    if (!steps.length) return "";
    return '<p class="pd-sub"><strong>Etapas da solução.</strong>' +
      (ps.unverified === true ? ' <span class="small muted">Solução não verificada contra o júri.</span>' : "") +
      '</p><ol class="steps">' + steps.map(function (x) {
      var tag = "";
      var kind = CAT_KIND[x.cat];
      if (kind) {
        var it = curItem(kind, x.ref);
        var label = CAT_LABEL[x.cat] + ": " + (it ? it.name : (x.ref || "?"));
        tag = it ? ' <a class="ctag" href="' + esc(curHref(kind, it.id)) + '">' + esc(label) + "</a>" : ' <span class="ctag">' + esc(label) + "</span>";
      }
      return "<li>" + (x.kind ? '<span class="skind">' + esc(x.kind) + "</span> " : "") + codeify(x.text) + tag + "</li>";
    }).join("") + "</ol>";
  }
  var UNVERIFIED = "Solução não verificada contra o júri (análise própria)";
  function unverifiedMark(p) {
    var ps = stepsOf(p);
    if (!ps || ps.unverified !== true) return "";
    return '<span class="unv" title="' + UNVERIFIED + '" aria-label="' + UNVERIFIED + '">†</span>';
  }
  function stepsSearchText(p) {
    var ps = stepsOf(p);
    if (!ps || !ps.steps) return "";
    return ps.steps.map(function (x) {
      var it = curItem(CAT_KIND[x.cat], x.ref);
      return (x.text || "") + " " + (it ? it.name : "");
    }).join(" | ");
  }

  // ---- Target / countdown --------------------------------------------------------------
  var target = D.target || {};
  var targetDate = target.date ? new Date(target.date) : null;
  function targetLabel() {
    if (target.short) return target.short;
    var name = target.name || "";
    var year = (name.match(/\b(\d{4})\b/) || [])[1] || (targetDate ? targetDate.getFullYear() : "");
    var acr = name.replace(/\b\d{4}\b/g, "").split(/\s+/).filter(function (w) {
      return /^[A-Z]/.test(w) && w !== "ICPC";
    }).map(function (w) { return w[0]; }).join("");
    return (acr + " " + year).trim();
  }
  var TLABEL = targetLabel();
  function tickCountdown() {
    var el = document.getElementById("countdown");
    if (!el || !targetDate || isNaN(targetDate)) { if (el) el.hidden = true; return; }
    var ms = targetDate - Date.now();
    el.title = targetDate.toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric", timeZone: "America/Sao_Paulo" });
    if (ms <= -5 * 864e5) { el.hidden = true; return; }
    if (ms <= 0) { el.innerHTML = '<span class="cd-t">' + esc(TLABEL) + " · em andamento</span>"; return; }
    var h = Math.floor(ms / 36e5), d = Math.floor(h / 24);
    h = h % 24;
    el.innerHTML = '<span class="cd-t">' + esc(TLABEL) + ' · </span><span class="cd-n">' + d + '</span><span class="cd-t"> d </span><span class="cd-n">' +
      (h < 10 ? "0" : "") + h + '</span><span class="cd-t"> h</span>';
    el.setAttribute("aria-label", "Faltam " + d + " dias e " + h + " horas para " + (target.name || TLABEL));
  }

  // ---- Theme ---------------------------------------------------------------------------
  function effectiveTheme() {
    var t = document.documentElement.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function syncThemeBtn() {
    var b = document.getElementById("themebtn");
    var next = effectiveTheme() === "dark" ? "light" : "dark";
    b.textContent = next === "dark" ? "Escuro" : "Claro";
    b.setAttribute("aria-label", "Usar tema " + (next === "dark" ? "escuro" : "claro"));
  }
  document.getElementById("themebtn").addEventListener("click", function () {
    var next = effectiveTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("sg-theme", next); } catch (e) { /* ignore */ }
    syncThemeBtn();
  });
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", syncThemeBtn);
  }

  // ---- Filter state + hash -------------------------------------------------------------
  function famSet(list) { var o = {}; list.forEach(function (f) { if (IX.famById[f]) o[f] = true; }); return o; }
  function famList(set) { return IX.allFams.filter(function (f) { return set[f]; }); }
  function sameList(a, b) { return a.length === b.length && a.every(function (x, i) { return x === b[i]; }); }
  function defaultFilter() {
    return { fams: famSet(CONFIG.defaultScope === "latam" ? IX.latamFams : IX.allFams), from: IX.minYear, to: IX.maxYear };
  }
  function scopeName(f) {
    var l = famList(f.fams);
    if (sameList(l, IX.latamFams)) return "latam";
    if (sameList(l, IX.allFams)) return "geral";
    return null;
  }
  function clampFilter(f) {
    f.from = Math.max(IX.minYear, Math.min(IX.maxYear, f.from | 0 || IX.minYear));
    f.to = Math.max(IX.minYear, Math.min(IX.maxYear, f.to | 0 || IX.maxYear));
    if (f.from > f.to) { var t = f.from; f.from = f.to; f.to = t; }
    if (!famList(f.fams).length) f.fams = famSet(IX.allFams);
    return f;
  }
  function filterFromParams(p) {
    var has = p.escopo || p.fam || p.de || p.ate;
    var base = has ? defaultFilter() : (function () {
      var s = load("sg-filter");
      return s ? clampFilter({ fams: famSet(s.fams || []), from: s.from, to: s.to }) : defaultFilter();
    })();
    if (p.escopo === "latam") base.fams = famSet(IX.latamFams);
    else if (p.escopo === "geral") base.fams = famSet(IX.allFams);
    else if (p.fam) base.fams = famSet(p.fam.split(","));
    if (p.de) base.from = +p.de;
    if (p.ate) base.to = +p.ate;
    return clampFilter(base);
  }
  function filterQuery(f) {
    var q = {};
    var s = scopeName(f);
    if (s) q.escopo = s; else q.fam = famList(f.fams).join(",");
    q.de = f.from; q.ate = f.to;
    return q;
  }
  function qs(obj) {
    return Object.keys(obj).filter(function (k) { return obj[k] !== "" && obj[k] != null && obj[k] !== false; })
      .map(function (k) { return k + "=" + encodeURIComponent(obj[k]); }).join("&");
  }
  function link(path, extra) {
    var q = filterQuery(filter);
    if (extra) Object.keys(extra).forEach(function (k) { q[k] = extra[k]; });
    var s = qs(q);
    return "#/" + path + (s ? "?" + s : "");
  }
  function parseHash() {
    var h = location.hash.replace(/^#\/?/, "");
    var i = h.indexOf("?");
    var path = i < 0 ? h : h.slice(0, i);
    var params = {};
    (i < 0 ? "" : h.slice(i + 1)).split("&").forEach(function (kv) {
      if (!kv) return;
      var j = kv.indexOf("=");
      var k = j < 0 ? kv : kv.slice(0, j);
      try { params[k] = decodeURIComponent(j < 0 ? "" : kv.slice(j + 1)); } catch (e) { params[k] = ""; }
    });
    var parts = path.split("/").filter(Boolean).map(function (x) { try { return decodeURIComponent(x); } catch (e) { return x; } });
    return { parts: parts, params: params, path: path };
  }

  var filter = defaultFilter();
  var lastWritten = null;
  var cur = null; // current view {update(), local()}
  function writeHash(path, extra) {
    var h = link(path, extra);
    if (location.hash !== h) { lastWritten = h; location.replace(h); }
    store("sg-filter", { fams: famList(filter.fams), from: filter.from, to: filter.to });
    updateTabLinks();
  }
  function setFilter(f) {
    filter = clampFilter(f);
    if (cur && cur.update) {
      cur.update();
      writeHash(cur.path, cur.local ? cur.local() : null);
    }
  }

  // ---- Filter row component ------------------------------------------------------------
  function filterRowHTML() {
    var years = "";
    for (var y = IX.minYear; y <= IX.maxYear; y++) years += "<option>" + y + "</option>";
    var chips = D.families.map(function (f) {
      return '<button type="button" class="chip" data-fam="' + esc(f.id) + '" title="' + esc(f.name + " · peso " + f.weight) + '">' + esc(f.short) + "</button>";
    }).join("");
    return '<div class="filters" role="group" aria-label="Filtro de contests">' +
      '<div class="seg" role="group" aria-label="Escopo">' +
      '<button type="button" data-scope="latam">Só LATAM</button><button type="button" data-scope="geral">Geral</button></div>' +
      '<span class="yrs"><label for="f-de">Anos</label> <select id="f-de" data-y="from" aria-label="Ano inicial">' + years +
      '</select><span aria-hidden="true">–</span><select id="f-ate" data-y="to" aria-label="Ano final">' + years + "</select></span>" +
      '<div class="chips" role="group" aria-label="Famílias">' + chips + "</div>" +
      '<span class="fcount" aria-live="polite"></span></div>';
  }
  function bindFilterRow(root) {
    var row = root.querySelector(".filters");
    row.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      var f = { fams: Object.assign({}, filter.fams), from: filter.from, to: filter.to };
      if (b.dataset.scope) f.fams = famSet(b.dataset.scope === "latam" ? IX.latamFams : IX.allFams);
      else if (b.dataset.fam) {
        if (f.fams[b.dataset.fam]) {
          if (famList(f.fams).length === 1) return;
          delete f.fams[b.dataset.fam];
        } else f.fams[b.dataset.fam] = true;
      } else return;
      setFilter(f);
      syncFilterRow(root);
    });
    row.addEventListener("change", function (e) {
      var s = e.target;
      if (!s.dataset.y) return;
      var f = { fams: filter.fams, from: filter.from, to: filter.to };
      f[s.dataset.y] = +s.value;
      if (s.dataset.y === "from" && f.from > f.to) f.to = f.from;
      if (s.dataset.y === "to" && f.to < f.from) f.from = f.to;
      setFilter(f);
      syncFilterRow(root);
    });
    syncFilterRow(root);
  }
  function syncFilterRow(root) {
    var row = root.querySelector(".filters");
    if (!row) return;
    var s = scopeName(filter);
    Array.prototype.forEach.call(row.querySelectorAll("[data-scope]"), function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.scope === s));
    });
    Array.prototype.forEach.call(row.querySelectorAll("[data-fam]"), function (b) {
      b.setAttribute("aria-pressed", String(!!filter.fams[b.dataset.fam]));
    });
    row.querySelector("[data-y=from]").value = String(filter.from);
    row.querySelector("[data-y=to]").value = String(filter.to);
  }
  function setCount(root, html) { var c = root.querySelector(".fcount"); if (c) c.innerHTML = html; }
  function emptyRow(colspan, text) {
    return '<tr class="empty"><td colspan="' + colspan + '">' + esc(text) + ' <button type="button" class="textbtn" data-clear>Limpar filtros</button></td></tr>';
  }
  // One delegated listener for every "Limpar filtros" button (app element persists across views).
  app.addEventListener("click", function (e) {
    if (!e.target.closest("[data-clear]")) return;
    if (cur && cur.clearLocal) cur.clearLocal();
    setFilter(defaultFilter());
    syncFilterRow(app);
  });

  // ---- Sortable header -----------------------------------------------------------------
  function th(col, sort) {
    var cls = (col.num ? "num " : "") + (col.cls || "");
    if (!col.sort) return '<th scope="col" class="' + cls + '">' + col.label + "</th>";
    var active = sort.key === col.key;
    return '<th scope="col" class="' + cls + '"' + (active ? ' aria-sort="' + (sort.dir > 0 ? "ascending" : "descending") + '"' : "") +
      '><button type="button" class="sortbtn" data-sort="' + col.key + '">' + col.label +
      (active ? '<span class="arr" aria-hidden="true">' + (sort.dir > 0 ? "▲" : "▼") + "</span>" : "") + "</button></th>";
  }
  function sortBy(list, valFn, dir) {
    return list.slice().sort(function (a, b) {
      var x = valFn(a), y = valFn(b);
      var xn = x == null, yn = y == null;
      if (xn || yn) return xn === yn ? 0 : xn ? 1 : -1; // missing values always last
      if (typeof x === "string") return dir * x.localeCompare(y, "pt-BR");
      return dir * (x - y);
    });
  }
  function nextSort(sort, key, cols) {
    if (sort.key === key) return { key: key, dir: -sort.dir };
    var c = cols.filter(function (c) { return c.key === key; })[0];
    return { key: key, dir: c && c.dir ? c.dir : 1 };
  }

  // ---- Problem table component ---------------------------------------------------------
  var SOLVED_LABEL = SG.K ? "Resolvido (top " + SG.K + ")" : "Resolvido";
  var PCOLS = {
    contest: { key: "contest", label: "Contest", sort: true, dir: -1 },
    letter: { key: "letter", label: "Letra", sort: true, dir: 1, cls: "c-letter" },
    title: { key: "title", label: "Título", sort: true, dir: 1 },
    topic: { key: "topic", label: "Tópico", sort: true, dir: 1 },
    solved: { key: "solved", label: SOLVED_LABEL, sort: true, num: true, dir: -1 },
    solvedbar: { key: "solved", label: SOLVED_LABEL, sort: true, num: true, dir: -1 },
    diff: { key: "diff", label: "Dificuldade", sort: true, dir: 1 },
    fs: { key: "fs", label: "1º AC (min)", sort: true, num: true, dir: 1, cls: "hide-m" }
  };
  var PSORT = {
    contest: function (p) { return p.year * 100 + (50 - IX.famById[p.family]._order); },
    letter: function (p) { return p.letter; },
    title: function (p) { return p.title; },
    topic: function (p) { return p.primary ? topicName(p.primary) : null; },
    solved: function (p) { return solvedShare(p); },
    diff: function (p) { return p._dv == null ? null : 1 - p._dv; },
    fs: function (p) { return p.first_solve_min; }
  };
  function sortProblems(list, sort) {
    var out = sortBy(list, PSORT[sort.key] || PSORT.contest, sort.dir);
    if (sort.key === "contest") {
      // within a contest keep letter order
      out = list.slice().sort(function (a, b) {
        var d = PSORT.contest(b) - PSORT.contest(a);
        if (sort.dir > 0) d = -d;
        return d || a.contest.localeCompare(b.contest) || a.letter.localeCompare(b.letter);
      });
    }
    return out;
  }
  // Solve count shown for a problem: solved among the contest's top-K official teams ("5/40"),
  // so it agrees with the difficulty label; whole-field numbers go in the tooltip.
  // Falls back to solved/total when there is no top-K data.
  function solvedText(p) {
    var k = p.k_used || SG.K;
    var hasTop = p.solved_top != null && k;
    var tt = [];
    if (hasTop) tt.push(p.solved_top + " dos " + k + " melhores times");
    if (p.solved != null) tt.push(p.total ? p.solved + " de " + p.total + " times" : p.solved + " times");
    if (p.attempted != null) tt.push(p.attempted + " tentaram");
    var t = hasTop ? p.solved_top + "/" + k : p.solved == null ? null : (p.total ? p.solved + "/" + p.total : String(p.solved));
    if (t == null) return DASH;
    return '<span title="' + esc(tt.join(" · ")) + '">' + t + "</span>";
  }
  function solvedShare(p) { return p.top_rate != null ? p.top_rate : p.solve_rate; }
  function problemRow(p, cols, st) {
    var href = bestLink(p);
    var cells = cols.map(function (k) {
      switch (k) {
        case "contest":
          return '<td class="c-contest"><a href="' + link("contests/" + encodeURIComponent(p.contest)) + '">' + esc(contestShort(p.contest)) + "</a></td>";
        case "letter":
          return '<td class="c-letter"><button type="button" class="rowtog mono" aria-expanded="' + (st.expanded[p.id] ? "true" : "false") +
            '" aria-controls="d-' + esc(p.id) + '" aria-label="Detalhes: ' + esc(contestShort(p.contest) + " " + p.letter + " — " + p.title) + '">' +
            '<span class="tri" aria-hidden="true">' + (st.expanded[p.id] ? "▼" : "▶") + "</span>" + esc(p.letter) + "</button></td>";
        case "title":
          return '<td class="c-title">' + (href ? extLink(href, esc(p.title), "plain") : esc(p.title)) + "</td>";
        case "topic":
          if (!p.primary) return "<td>" + DASH + "</td>";
          var a = areaOfTopic(p.primary);
          var extra = st.topicCtx && st.topicCtx !== p.primary ? ' <span class="muted small">(secundário aqui)</span>' : "";
          return '<td class="c-topic">' + swatch(a && a.id) + '<a href="' + link("topico/" + encodeURIComponent(p.primary)) + '">' + esc(topicName(p.primary)) + "</a>" + extra + "</td>";
        case "solved":
          return '<td class="num">' + solvedText(p) + "</td>";
        case "solvedbar":
          var w = solvedShare(p) != null ? Math.round(solvedShare(p) * 100) : 0;
          return '<td class="num"><span class="barwrap"><span class="bar hide-m" aria-hidden="true"><span style="width:' + w + '%"></span></span>' + solvedText(p) + "</span></td>";
        case "diff":
          return "<td>" + diffCell(p._bin, "desktop", topText(p) ? "Resolvido por " + topText(p) : null) + "</td>";
        case "fs":
          return '<td class="num hide-m">' + (p.first_solve_min != null ? p.first_solve_min : DASH) + "</td>";
      }
      return "<td></td>";
    }).join("");
    var row = '<tr class="prow' + (st.expanded[p.id] ? " open" : "") + '" data-id="' + esc(p.id) + '">' + cells + "</tr>";
    if (st.expanded[p.id]) row += detailRow(p, cols.length, st);
    return row;
  }
  function detailRow(p, n, st) {
    var l = p.links || {};
    var c = IX.contestById[p.contest] || {};
    var links = [
      extLink(l.mirror, "Mirror"), extLink(l.kattis, "Kattis"), extLink(l.statement, "Enunciado"),
      extLink(c.links && c.links.editorial, "Editorial do contest"),
      '<a href="' + link("contests/" + encodeURIComponent(p.contest)) + '">' + esc(contestShort(p.contest)) + "</a>"
    ].filter(Boolean).join('<span class="sep" aria-hidden="true"> · </span>');
    var topics = p._topics.map(function (t) {
      return '<a href="' + link("topico/" + encodeURIComponent(t.id)) + '">' + esc(topicName(t.id)) + "</a>" +
        (t.role === "secondary" ? ' <span class="muted">(secundário)</span>' : "");
    }).join(", ");
    var open = st.showIdeas || st.ideaOpen[p.id];
    var srcName = { editorial: "editorial oficial", community: "comunidade", own: "análise própria" }[p.solution_source] || null;
    var confName = { high: "alta", medium: "média", low: "baixa" }[p.confidence] || null;
    var steps = stepsHTML(p);
    var idea = (p.key_idea ? "<p><strong>Ideia-chave.</strong> " + codeify(p.key_idea) + "</p>" : "") +
      (p.solution ? "<p><strong>Solução.</strong> " + codeify(p.solution) + "</p>" : "") + steps +
      ((srcName || confName) ? '<p class="small muted">' + [srcName ? "Fonte: " + srcName : null, confName ? "confiança da classificação: " + confName : null].filter(Boolean).join(" · ") + "</p>" : "");
    if (!p.key_idea && !p.solution && !steps) idea = '<p class="muted">Sem ideia registrada.</p>';
    return '<tr class="pdetail" id="d-' + esc(p.id) + '"><td colspan="' + n + '"><div class="pd">' +
      '<p class="pd-h">' + esc(contestShort(p.contest)) + " · " + esc(p.letter) + " — " + esc(p.title) + "</p>" +
      "<p><strong>Enunciado.</strong> " + (p.summary ? codeify(p.summary) : '<span class="muted">Sem resumo.</span>') + "</p>" +
      (topics ? "<p><strong>Tópicos.</strong> " + topics + "</p>" : "") +
      '<p class="pd-links">' + links + "</p>" +
      '<button type="button" class="textbtn ideabtn" aria-expanded="' + (open ? "true" : "false") + '" aria-controls="i-' + esc(p.id) + '"' + (st.showIdeas ? " hidden" : "") + ">" +
      (open ? "Ocultar ideia" : "Mostrar ideia") + "</button>" +
      '<div class="idea" id="i-' + esc(p.id) + '"' + (open ? "" : " hidden") + ">" + idea + "</div>" +
      "</div></td></tr>";
  }
  // Renders a sortable problem table into `el`. st: {cols, sort, expanded, ideaOpen, showIdeas, topicCtx, emptyText}
  function renderProblemTable(el, list, st) {
    var cols = st.cols;
    var head = "<tr>" + cols.map(function (k) { return th(PCOLS[k], st.sort); }).join("") + "</tr>";
    var rows = sortProblems(list, st.sort);
    var body = rows.length ? rows.map(function (p) { return problemRow(p, cols, st); }).join("") : emptyRow(cols.length, st.emptyText || "Nenhum problema com esses filtros.");
    el.innerHTML = '<table class="t ptable"><thead>' + head + "</thead><tbody>" + body + "</tbody></table>";
    if (el._bound) return;
    el._bound = true;
    el.addEventListener("click", function (e) {
      var sb = e.target.closest(".sortbtn");
      if (sb) {
        st.sort = nextSort(st.sort, sb.dataset.sort, cols.map(function (k) { return PCOLS[k]; }));
        renderProblemTable(el, el._list, st);
        var nb = el.querySelector('.sortbtn[data-sort="' + sb.dataset.sort + '"]');
        if (nb) nb.focus();
        return;
      }
      var ib = e.target.closest(".ideabtn");
      if (ib) {
        var pid = ib.getAttribute("aria-controls").slice(2);
        st.ideaOpen[pid] = !st.ideaOpen[pid];
        var box = document.getElementById("i-" + pid);
        box.hidden = !st.ideaOpen[pid];
        ib.setAttribute("aria-expanded", String(st.ideaOpen[pid]));
        ib.textContent = st.ideaOpen[pid] ? "Ocultar ideia" : "Mostrar ideia";
        return;
      }
      var tr = e.target.closest("tr.prow");
      if (!tr) return;
      if (e.target.closest("a") || (e.target.closest("button") && !e.target.closest(".rowtog"))) return;
      if (window.getSelection && String(window.getSelection()).length && !e.target.closest(".rowtog")) return;
      toggleRow(el, st, tr.dataset.id, !!e.target.closest(".rowtog"));
    });
  }
  function toggleRow(el, st, pid, keepFocus) {
    st.expanded[pid] = !st.expanded[pid];
    var tr = el.querySelector('tr.prow[data-id="' + cssEsc(pid) + '"]');
    if (!tr) return;
    var p = IX.problemById[pid];
    var tmp = document.createElement("tbody");
    tmp.innerHTML = problemRow(p, st.cols, st);
    var newRow = tmp.firstChild;
    var next = tr.nextElementSibling;
    if (next && next.classList.contains("pdetail")) next.remove();
    tr.replaceWith(newRow);
    if (tmp.firstChild) newRow.after(tmp.firstChild);
    if (keepFocus) { var b = newRow.querySelector(".rowtog"); if (b) b.focus(); }
  }
  function openRow(el, st, pid) {
    if (!st.expanded[pid]) toggleRow(el, st, pid, false);
    var tr = el.querySelector('tr.prow[data-id="' + cssEsc(pid) + '"]');
    if (tr) {
      tr.scrollIntoView({ block: "center" });
      var b = tr.querySelector(".rowtog"); if (b) b.focus({ preventScroll: true });
    }
  }
  function cssEsc(s) { return window.CSS && CSS.escape ? CSS.escape(s) : String(s).replace(/["\\]/g, "\\$&"); }

  // ---- View: Currículo -----------------------------------------------------------------
  var CSECS = [
    { id: "insights", name: "Insights", kind: "insight", one: "insight", many: "insights",
      lede: "Observações sem nome de livro que destravam uma família de problemas, da mais útil para a menos útil no filtro." },
    { id: "aprofundamentos", name: "Aprofundamentos", kind: "deepening", one: "aprofundamento", many: "aprofundamentos",
      lede: "Propriedades e usos de técnicas conhecidas que costumam passar despercebidos, agrupados pela técnica." },
    { id: "tecnicas", name: "Técnicas", kind: "technique", one: "técnica", many: "técnicas",
      lede: "Técnicas com nome, usadas do jeito padrão; o número é quantos problemas do filtro usam cada uma." }
  ];
  function viewCurriculum(r) {
    if (!CUR) {
      app.innerHTML = '<div class="pagehead"><h1>Currículo</h1></div><p class="prose">O currículo ainda não foi gerado para estes dados. ' +
        'Enquanto isso, a ordem de estudo por tema está em <a href="' + link("topicos") + '">Tópicos</a>.</p>';
      return { path: "curriculo" };
    }
    var sec = CSECS.filter(function (s) { return s.id === r.parts[1]; })[0] || CSECS[0];
    var target = r.parts[2] != null ? String(r.parts[2]) : null;
    var p0 = r.params;
    var st = { mode: p0.ordem === "ranking" ? "ranking" : "grupo", showIdeas: p0.ideias === "1", ideaOpen: {}, showHidden: false, techOpen: {}, moreOpen: {}, ctxOpen: {} };
    if (target && sec.kind === "technique") st.techOpen[target] = true;
    var known = load("sg-known") || {};
    var path = "curriculo/" + sec.id + (target != null ? "/" + encodeURIComponent(target) : "");

    function local() { return { ordem: st.mode === "ranking" ? "ranking" : "", ideias: st.showIdeas ? "1" : "" }; }
    var controls = "";
    if (sec.kind !== "technique") {
      controls = '<div class="seg" role="group" aria-label="Ordem"><button type="button" data-mode="grupo">Por grupo</button><button type="button" data-mode="ranking">Ranking</button></div>' +
        '<label class="check"><input type="checkbox" id="c-ideas"> Mostrar ideias</label>';
    }
    app.innerHTML = '<div class="pagehead"><h1>Currículo</h1></div>' + filterRowHTML() +
      '<div class="cbar"><nav class="seg segnav" id="csecs" aria-label="Partes do currículo"></nav>' + controls + "</div>" +
      '<p class="lede">' + esc(sec.lede) + "</p>" +
      '<div id="clist" class="clist-' + sec.id + '"></div>';
    bindFilterRow(app);
    var listEl = document.getElementById("clist");
    var ideasEl = document.getElementById("c-ideas");
    if (ideasEl) ideasEl.checked = st.showIdeas;
    function syncMode() {
      Array.prototype.forEach.call(app.querySelectorAll("[data-mode]"), function (b) {
        b.setAttribute("aria-pressed", String(b.dataset.mode === st.mode));
      });
    }
    syncMode();

    function sortCurProbs(list) {
      // easiest first (study order), then most recent
      return list.slice().sort(function (a, b) {
        var x = a.p._dv, y = b.p._dv;
        if ((x == null) !== (y == null)) return x == null ? 1 : -1;
        return (x != null && y - x) || (b.p.year - a.p.year) || a.p.id.localeCompare(b.p.id);
      });
    }
    function probRows(a) {
      var it = a.item;
      if (!a.problems.length) return '<p class="small muted">Sem problemas neste filtro.</p>';
      var all = sortCurProbs(a.problems);
      var mkey = it.kind + "|" + it.id;
      var cap = CONFIG.curriculumRows;
      var more = all.length > cap + 2 && !st.moreOpen[mkey];
      var rows = more ? all.slice(0, cap) : all;
      var moreBtn = all.length > cap + 2 ? '<button type="button" class="textbtn morebtn" data-more="' + esc(mkey) + '" aria-expanded="' + !more + '">' +
        (more ? "Mais " + plural(all.length - cap, "problema", "problemas") : "Mostrar menos") + "</button>" : "";
      return '<ul class="plist">' + rows.map(function (x) {
        var p = x.p, key = it.kind + "|" + it.id + "|" + p.id;
        var open = st.showIdeas || !!st.ideaOpen[key];
        var href = bestLink(p);
        var tt = topText(p);
        return '<li class="pli">' +
          '<span class="pl-c"><a href="' + link("contests/" + encodeURIComponent(p.contest)) + '">' + esc(contestShort(p.contest)) + '</a> <span class="mono">' + esc(p.letter) + "</span></span>" +
          '<span class="pl-t">' + (href ? extLink(href, esc(p.title), "plain") : esc(p.title)) + unverifiedMark(p) + "</span>" +
          '<span class="pl-m">' + diffCell(p._bin, true, tt ? "Resolvido por " + tt : null) + '<span class="pl-s">' + solvedText(p) + "</span>" +
          (x.how ? '<button type="button" class="textbtn howbtn" data-key="' + esc(key) + '" aria-expanded="' + open + '"' + (st.showIdeas ? " hidden" : "") +
            ' aria-label="' + (open ? "Ocultar" : "Mostrar") + " ideia: " + esc(p.title) + '">' + (open ? "Ocultar ideia" : "Mostrar ideia") + "</button>" : "") + "</span>" +
          (x.how ? '<p class="pl-how"' + (open ? "" : " hidden") + ">" + codeify(x.how) + "</p>" : "") +
          "</li>";
      }).join("") + "</ul>" + moreBtn;
    }
    function metaLine(a, extra) {
      var g = CONFIG.generality[a.generality];
      var util = "Utilidade " + SG.fmtNum(a.utility, 2) + " = generalidade " + a.generality + " × " + SG.fmtNum(a.freq, 2) +
        " problemas por contest do filtro (ponderado por família)";
      var bits = [plural(a.nProblems, "problema", "problemas"), plural(a.nContests, "contest", "contests"),
        '<span title="' + esc("Generalidade: " + g.help) + '">' + esc(g.name) + "</span>"];
      if (extra) bits.push(esc(extra));
      return '<p class="cmeta" title="' + esc(util) + '">' + bits.join('<span class="sep"> · </span>') + "</p>";
    }
    function para(label, text) {
      if (!text) return "";
      return '<p><span class="lbl">' + label + ":</span> " + codeify(text) + "</p>";
    }
    function itemHTML(a, rank, groupName) {
      var it = a.item;
      var ctx = (it.contexts || []).filter(Boolean);
      var kp = (it.known_problems || []).filter(Boolean);
      var ckey = it.kind + "|" + it.id;
      var copen = !!st.ctxOpen[ckey] || target === String(it.id);
      var ctxHtml = ctx.length || kp.length ?
        '<button type="button" class="textbtn ctxbtn" data-ctx="' + esc(ckey) + '" aria-expanded="' + copen + '">' +
        '<span class="tri" aria-hidden="true">' + (copen ? "▼" : "▶") + "</span>Onde mais serve</button>" +
        '<div class="cctx"' + (copen ? "" : " hidden") + ">" +
        (ctx.length ? '<ul class="ctxl">' + ctx.map(function (c) { return "<li>" + codeify(c) + "</li>"; }).join("") + "</ul>" : "") +
        (kp.length ? '<p class="muted small">Problemas conhecidos: ' + esc(kp.join("; ")) + ".</p>" : "") + "</div>" : "";
      var body = it.kind === "insight" ?
        '<p class="cstmt">' + codeify(it.statement) + "</p>" :
        '<p class="cstmt">' + codeify(it.property) + "</p>" + para("Por que vale", it.why);
      return '<article class="citem' + (target === String(it.id) ? " hl" : "") + (a.nProblems ? "" : " nop") + '" id="' + curDomId(it.kind, it.id) + '">' +
        '<div class="ctext"><h3 class="cname">' + (rank ? '<span class="crank">' + rank + "</span>" : "") + esc(it.name) + "</h3>" +
        metaLine(a, groupName) + body + para("Sinal no enunciado", it.signal) + ctxHtml + "</div>" +
        '<div class="cprobs">' + probRows(a) + "</div></article>";
    }
    // groups: [{key, name}] in order of their best item (list is already sorted by utility)
    function grouped(list, keyOf, nameOf) {
      var out = [], by = {};
      list.forEach(function (a) {
        var k = keyOf(a.item);
        if (!by[k]) { by[k] = { key: k, name: nameOf(k), items: [] }; out.push(by[k]); }
        by[k].items.push(a);
      });
      return out;
    }
    function hiddenLine(n) {
      if (!n) return "";
      return '<p class="note chid">' + plural(n, "item", "itens") + " sem problemas no filtro. " +
        '<button type="button" class="textbtn" data-hidden aria-expanded="' + st.showHidden + '">' + (st.showHidden ? "Ocultar" : "Mostrar") + "</button></p>";
    }
    function renderItems(shown, hidden) {
      var html = "";
      var rankOrder = st.mode === "ranking";
      if (!shown.length) html += '<p class="muted cempty">Nenhum ' + esc(sec.one) + ' com problemas neste filtro. <button type="button" class="textbtn" data-clear>Limpar filtros</button></p>';
      else if (rankOrder) {
        html += '<div class="cgroup">' + shown.map(function (a, i) {
          var gname = sec.kind === "insight" ? groupNameOf(a.item.group) : a.item.base;
          return itemHTML(a, i + 1, gname);
        }).join("") + "</div>";
      } else {
        var gs = sec.kind === "insight" ?
          grouped(shown, function (it) { return CUR.groupById[it.group] ? it.group : ""; }, groupNameOf) :
          grouped(shown, function (it) { return it.base || ""; }, function (k) { return k || "Outras técnicas"; });
        html += gs.map(function (g) {
          return '<section class="cgroup"><h2 class="cgrp">' + esc(g.name) + '<span class="gmeta"> · ' + plural(g.items.length, sec.one, sec.many) + "</span></h2>" +
            g.items.map(function (a) { return itemHTML(a, null, null); }).join("") + "</section>";
        }).join("");
      }
      html += hiddenLine(hidden.length);
      if (st.showHidden && hidden.length) {
        html += '<section class="cgroup chidden"><h2 class="cgrp">Sem problemas no filtro</h2>' +
          hidden.map(function (a) { return itemHTML(a, null, sec.kind === "insight" ? groupNameOf(a.item.group) : a.item.base); }).join("") + "</section>";
      }
      return html;
    }
    function groupNameOf(gid) { var g = CUR.groupById[gid]; return g ? g.name : "Outros"; }
    function techRows(a) {
      if (!a.problems.length) return '<p class="small muted">Sem problemas neste filtro.</p>';
      return '<ul class="tprobs">' + sortCurProbs(a.problems).map(function (x) {
        var p = x.p, href = bestLink(p), tt = topText(p);
        return '<li><a class="tp-c" href="' + link("contests/" + encodeURIComponent(p.contest)) + '">' + esc(contestShort(p.contest)) + '</a> <span class="mono">' + esc(p.letter) + "</span> " +
          (href ? extLink(href, esc(p.title), "plain") : esc(p.title)) + unverifiedMark(p) +
          ' <span class="tp-s">' + solvedText(p) + "</span>" +
          (p._bin ? ' <span class="dot d-' + p._bin + '" role="img" aria-label="' + esc(SG.DIFF[p._bin].name) + '" title="' + esc(SG.DIFF[p._bin].name + (tt ? " · resolvido por " + tt : "")) + '"></span>' : "") + "</li>";
      }).join("") + "</ul>";
    }
    function techHTML(list) {
      return '<ol class="techlist">' + list.map(function (a) {
        var it = a.item, open = !!st.techOpen[it.name];
        return '<li class="tech' + (target === it.name ? " hl" : "") + (a.nProblems ? "" : " nop") + '" id="' + curDomId("technique", it.name) + '">' +
          '<div class="trow"><input type="checkbox" class="tknown" data-name="' + esc(it.name) + '" aria-label="' + esc("Já domino " + it.name) + '"' + (known[it.name] ? " checked" : "") + ">" +
          '<button type="button" class="techbtn" data-name="' + esc(it.name) + '" aria-expanded="' + open + '"><span class="tri" aria-hidden="true">' + (open ? "▼" : "▶") + "</span>" +
          '<span class="tname2">' + esc(it.name) + "</span></button>" +
          '<span class="tn" title="' + esc(plural(a.nProblems, "problema", "problemas") + " no filtro · " + plural(a.nContests, "contest", "contests")) + '">' + a.nProblems + "</span></div>" +
          (open ? techRows(a) : "") + "</li>";
      }).join("") + "</ol>";
    }
    function knownCount(list) { return list.filter(function (a) { return known[a.item.name]; }).length; }

    var S = null;
    function update() {
      S = SG.curriculumStats(filter);
      var lists = { insights: S.insights, aprofundamentos: S.deepenings, tecnicas: S.techniques };
      setCount(app, plural(S.scope.problems.length, "problema", "problemas") + " · " + plural(S.scope.contests.length, "contest", "contests"));
      document.getElementById("csecs").innerHTML = CSECS.map(function (s) {
        var n = lists[s.id].filter(function (a) { return a.nProblems; }).length;
        return '<a href="' + esc(link("curriculo/" + s.id, local())) + '"' + (s === sec ? ' aria-current="page"' : "") + ">" + esc(s.name) +
          '<span class="segn"> ' + n + "</span></a>";
      }).join("");
      var list = lists[sec.id];
      var shown = list.filter(function (a) { return a.nProblems; });
      var hidden = list.filter(function (a) { return !a.nProblems; });
      if (target != null && hidden.some(function (a) { return String(a.item.id) === target; })) st.showHidden = true;
      if (sec.kind === "technique") {
        var kc = knownCount(list);
        listEl.innerHTML = (shown.length ? techHTML(shown) : '<p class="muted cempty">Nenhuma técnica com problemas neste filtro. <button type="button" class="textbtn" data-clear>Limpar filtros</button></p>') +
          '<p class="note">' + (kc ? kc + " de " + list.length + " marcadas como dominadas neste navegador. " : "A caixa ao lado de cada técnica marca o que o time já domina; fica salvo neste navegador. ") + "</p>" +
          hiddenLine(hidden.length) + (st.showHidden && hidden.length ? '<div class="chidden">' + techHTML(hidden) + "</div>" : "");
      } else {
        listEl.innerHTML = renderItems(shown, hidden);
      }
    }
    function rerender() { update(); writeHash(path, local()); }

    app.querySelector(".cbar").addEventListener("click", function (e) {
      var b = e.target.closest("[data-mode]");
      if (!b || b.dataset.mode === st.mode) return;
      st.mode = b.dataset.mode;
      syncMode();
      rerender();
    });
    if (ideasEl) ideasEl.addEventListener("change", function () { st.showIdeas = ideasEl.checked; rerender(); });
    listEl.addEventListener("click", function (e) {
      var hb = e.target.closest(".howbtn");
      if (hb) {
        var k = hb.dataset.key;
        st.ideaOpen[k] = !st.ideaOpen[k];
        var box = hb.closest("li").querySelector(".pl-how");
        if (box) box.hidden = !st.ideaOpen[k];
        hb.setAttribute("aria-expanded", String(st.ideaOpen[k]));
        hb.textContent = st.ideaOpen[k] ? "Ocultar ideia" : "Mostrar ideia";
        hb.setAttribute("aria-label", (st.ideaOpen[k] ? "Ocultar" : "Mostrar") + " ideia: " + hb.closest("li").querySelector(".pl-t").textContent.replace(/\s*↗$/, ""));
        return;
      }
      var cb = e.target.closest(".ctxbtn");
      if (cb) {
        var ck = cb.dataset.ctx;
        var now = cb.getAttribute("aria-expanded") !== "true";
        st.ctxOpen[ck] = now;
        cb.setAttribute("aria-expanded", String(now));
        cb.querySelector(".tri").textContent = now ? "▼" : "▶";
        cb.nextElementSibling.hidden = !now;
        return;
      }
      var mb = e.target.closest(".morebtn");
      if (mb) {
        var mk = mb.dataset.more;
        st.moreOpen[mk] = !st.moreOpen[mk];
        update();
        var nm = listEl.querySelector('.morebtn[data-more="' + cssEsc(mk) + '"]');
        if (nm) nm.focus();
        return;
      }
      var tb = e.target.closest(".techbtn");
      if (tb) {
        var name = tb.dataset.name;
        st.techOpen[name] = !st.techOpen[name];
        update();
        var nb = listEl.querySelector('.techbtn[data-name="' + cssEsc(name) + '"]');
        if (nb) nb.focus();
        return;
      }
      if (e.target.closest("[data-hidden]")) {
        st.showHidden = !st.showHidden;
        update();
        var hb2 = listEl.querySelector("[data-hidden]");
        if (hb2) hb2.focus();
      }
    });
    listEl.addEventListener("change", function (e) {
      var cb = e.target.closest(".tknown");
      if (!cb) return;
      if (cb.checked) known[cb.dataset.name] = 1; else delete known[cb.dataset.name];
      store("sg-known", known);
      update();
      var nb = listEl.querySelector('.tknown[data-name="' + cssEsc(cb.dataset.name) + '"]');
      if (nb) nb.focus();
    });
    update();
    return {
      path: path, update: update, local: local,
      after: function () {
        if (target == null) return;
        var el = document.getElementById(curDomId(sec.kind, target));
        if (el) el.scrollIntoView({ block: "start" });
      }
    };
  }

  // ---- View: Tópicos (ranking) ---------------------------------------------------------
  var RCOLS = [
    { key: "rank", label: "#", sort: true, num: true, dir: 1, cls: "c-rank" },
    { key: "name", label: "Tópico", sort: true, dir: 1 },
    { key: "tier", label: "Nível", sort: true, dir: 1, cls: "hide-m c-tier" },
    { key: "per", label: "Por contest", sort: true, num: true, dir: -1 },
    { key: "pres", label: "Presença", sort: true, num: true, dir: -1 },
    { key: "n", label: "Problemas", sort: true, num: true, dir: -1, cls: "hide-m" },
    { key: "diff", label: '<span class="hide-m">Dificuldade típica</span><span class="show-m">Dif.</span>', sort: true, dir: 1 },
    { key: "years", label: "Anos", sort: false, cls: "hide-m c-years" }
  ];
  var RSORT = {
    rank: function (a) { return a.rankStudy; },
    name: function (a) { return a.topic.name; },
    tier: function (a) { return CONFIG.tiers.indexOf(a.tier) * 1000 - a.per_contest; },
    per: function (a) { return a.per_contest; },
    pres: function (a) { return a.presence; },
    n: function (a) { return a.nProblems; },
    diff: function (a) { return a.medianDv == null ? null : 1 - a.medianDv; }
  };
  function tierCriterion(i) {
    var t = CONFIG.tiers[i];
    if (i === CONFIG.tiers.length - 1) return "presença abaixo de " + Math.round(CONFIG.tiers[i - 1].min * 100) + "%";
    return "presença ≥ " + Math.round(t.min * 100) + "% dos contests do filtro";
  }

  function viewTopics(r) {
    var st = { sort: { key: "rank", dir: 1 } };
    app.innerHTML = '<div class="pagehead"><h1>O que estudar, em ordem</h1></div>' + filterRowHTML() +
      '<div class="tw" id="rank"></div><p class="note" id="rank-note"></p>';
    bindFilterRow(app);
    var el = document.getElementById("rank");

    function update() {
      var S = SG.topicStats(filter);
      var list = S.list;
      // study order: tier, then per_contest desc
      var grouped = CONFIG.tiers.map(function (t) { return list.filter(function (a) { return a.tier === t; }); });
      var k = 0;
      grouped.forEach(function (g) { g.forEach(function (a) { a.rankStudy = ++k; }); });
      setCount(app, list.length + " tópicos · " + S.scope.problems.length + " problemas · " + S.nContests + " contests");
      var isGrouped = st.sort.key === "rank" && st.sort.dir === 1;
      var cols = RCOLS.filter(function (c) { return !(isGrouped && c.key === "tier"); });
      var yl = String(filter.from) + (filter.to !== filter.from ? "–" + String(filter.to).slice(2) : "");
      var head = "<tr>" + cols.map(function (c) {
        if (c.key === "years") return '<th scope="col" class="' + c.cls + '">' + yl + "</th>";
        return th(c, st.sort);
      }).join("") + "</tr>";
      var maxPer = list.reduce(function (m, a) { return Math.max(m, a.per_contest); }, 0) || 1;
      var nC = S.nContests;
      function row(a) {
        var t = a.topic, area = IX.areaById[t.area];
        var href = link("topico/" + encodeURIComponent(t.id));
        return '<tr class="clickrow" data-href="' + esc(href) + '">' + cols.map(function (c) {
          switch (c.key) {
            case "rank": return '<td class="num muted c-rank">' + a.rankStudy + "</td>";
            case "name": return '<td class="c-name">' + swatch(t.area) + '<a href="' + esc(href) + '" class="tname">' + esc(t.name) + "</a>" +
              (area ? '<span class="tarea hide-m">' + esc(area.name) + "</span>" : "") + "</td>";
            case "tier": return '<td class="hide-m">' + tierText(a.tier) + "</td>";
            case "per": return '<td class="num"><span class="barwrap"><span class="bar hide-m" aria-hidden="true"><span style="width:' +
              (a.per_contest / maxPer * 100).toFixed(1) + '%"></span></span><span title="problemas esperados por contest">' + SG.fmtNum(a.per_contest, 2) + "</span></span></td>";
            case "pres": return '<td class="num" title="' + esc(a.nContests + " de " + nC + " contests; percentual ponderado pelo peso da família") + '">' +
              SG.fmtPct(a.presence) + '<span class="den hide-m"> ' + a.nContests + "/" + nC + "</span></td>";
            case "n": return '<td class="num hide-m" title="' + esc(a.nPrimary + " como principal, " + a.nSecondary + " como secundário") + '">' + a.nProblems + "</td>";
            case "diff": return "<td>" + diffCell(a.typicalDiff, "desktop", a.medianDv != null ? "Mediana: resolvido por " + Math.round(a.medianDv * 100) + "% dos " + TOPK : null) + "</td>";
            case "years": return '<td class="hide-m c-years" title="' + esc(SG.charts.presenceText(a.years, filter.from, filter.to)) + '">' + SG.charts.presenceStrip(a.years, filter.from, filter.to) + "</td>";
          }
          return "<td></td>";
        }).join("") + "</tr>";
      }
      var body = "";
      if (!list.length) body = emptyRow(cols.length, "Nenhum tópico com esses filtros.");
      else if (isGrouped) {
        grouped.forEach(function (g, i) {
          if (!g.length) return;
          body += '<tr class="grp"><th scope="colgroup" colspan="' + cols.length + '"><span class="gname">' + esc(CONFIG.tiers[i].name) +
            '</span><span class="gmeta"> · ' + g.length + (g.length === 1 ? " tópico" : " tópicos") + " · " + esc(tierCriterion(i)) + "</span></th></tr>";
          body += g.map(row).join("");
        });
      } else {
        body = sortBy(list, RSORT[st.sort.key], st.sort.dir).map(row).join("");
      }
      el.innerHTML = '<table class="t rank"><thead>' + head + "</thead><tbody>" + body + "</tbody></table>";
      var missing = (D.topics || []).filter(function (t) { return !S.byId[t.id]; });
      document.getElementById("rank-note").innerHTML = missing.length ?
        missing.length + (missing.length === 1 ? " tópico" : " tópicos") + " sem problemas neste filtro: " +
        missing.map(function (t) { return '<a href="' + link("topico/" + encodeURIComponent(t.id)) + '">' + esc(t.name) + "</a>"; }).join(", ") + "." : "";
    }
    el.addEventListener("click", function (e) {
      var sb = e.target.closest(".sortbtn");
      if (sb) {
        st.sort = nextSort(st.sort, sb.dataset.sort, RCOLS);
        update();
        var nb = el.querySelector('.sortbtn[data-sort="' + sb.dataset.sort + '"]');
        if (nb) nb.focus();
        return;
      }
      if (e.target.closest("a, button")) return;
      var tr = e.target.closest("tr.clickrow");
      if (tr) location.hash = tr.dataset.href;
    });
    update();
    return { path: "topicos", update: update };
  }

  // ---- View: Tópico (detail) -----------------------------------------------------------
  function viewTopic(r) {
    var tid = r.parts[1];
    var t = IX.topicById[tid];
    if (!t) {
      app.innerHTML = '<div class="pagehead"><h1>Tópico não encontrado</h1></div><p class="prose"><a href="' + link("topicos") + '">Voltar ao ranking</a></p>';
      return { path: r.path };
    }
    var area = IX.areaById[t.area];
    var pst = { cols: ["contest", "letter", "title", "topic", "solved", "diff", "fs"], sort: { key: "contest", dir: -1 },
      expanded: {}, ideaOpen: {}, showIdeas: false, topicCtx: tid, emptyText: "Nenhum problema deste tópico com esses filtros." };
    var refs = (t.refs || []).map(function (x) {
      return '<li><a class="prose-link" href="' + esc(x.url) + '" target="_blank" rel="noopener">' + esc(x.label || x.url) + "</a></li>";
    }).join("");
    app.innerHTML =
      '<nav class="crumb" aria-label="Trilha"><a href="' + link("topicos") + '">Tópicos</a><span aria-hidden="true"> / </span>' +
      (area ? '<a href="' + link("problemas", { area: area.id }) + '">' + esc(area.name) + '</a><span aria-hidden="true"> / </span>' : "") +
      '<span aria-current="page">' + esc(t.name) + "</span></nav>" +
      '<div class="pagehead"><h1>' + esc(t.name) + '</h1></div><p class="meta" id="tmeta"></p>' +
      filterRowHTML() +
      '<div class="prose">' + (t.description ? "<p>" + codeify(t.description) + "</p>" : "") +
      (t.includes && t.includes.length ? '<p class="muted small">Inclui: ' + esc(t.includes.join(", ")) + "</p>" : "") + "</div>" +
      (refs ? '<section><h2>Para estudar</h2><ul class="refs">' + refs + "</ul></section>" : "") +
      '<section><h2>Números</h2><div id="tnums"></div></section>' +
      '<section><h2>Onde aparece</h2><div class="tw" id="tmatrix"></div></section>' +
      '<section><h2>Dificuldade</h2><div id="tstrip" class="stripwrap"></div><p class="axislabel">Resolvido por % dos ' + esc(TOPK) + ' do contest</p></section>' +
      '<section><h2>Problemas</h2><div class="tw" id="tprobs"></div></section>';
    bindFilterRow(app);
    var probsEl = document.getElementById("tprobs");
    var stripItems = [];

    function update() {
      var S = SG.topicStats(filter);
      var a = S.byId[tid];
      var nC = S.nContests;
      setCount(app, nC + " contests no filtro");
      var meta = document.getElementById("tmeta");
      var probs = a ? a.problems.map(function (x) { return x.p; }) : [];
      if (a) {
        var ys = probs.map(function (p) { return p.year; });
        meta.innerHTML = tierText(a.tier) + '<span class="sep"> · </span>' + a.nProblems + (a.nProblems === 1 ? " problema" : " problemas") + " · " +
          a.nContests + (a.nContests === 1 ? " contest" : " contests") + " · " + yearSpan(Math.min.apply(null, ys), Math.max.apply(null, ys));
      } else meta.innerHTML = '<span class="muted">Sem problemas neste filtro.</span>';

      // Numbers
      var nums = document.getElementById("tnums");
      if (!a) nums.innerHTML = '<p class="muted">Nenhum problema deste tópico com esses filtros. <button type="button" class="textbtn" data-clear>Limpar filtros</button></p>';
      else {
        var binsHtml = CONFIG.difficulty.map(function (b) {
          var n = a.bins[b.id] || 0;
          return n ? '<span class="diff lv lv-' + b.id + '"><span class="dot d-' + b.id + '" aria-hidden="true"></span>' + esc(b.name) + " " + n + "</span>" : "";
        }).filter(Boolean).join('<span class="sep"> · </span>') + (a.bins.none ? '<span class="sep"> · </span>sem dado ' + a.bins.none : "");
        var fsTxt = a.firstSolve.n ? "mediana " + SG.fmtNum(a.firstSolve.median, 0) + " min · mais rápido " + a.firstSolve.min + " min" +
          ' <span class="muted">(' + a.firstSolve.n + " de " + a.nProblems + " com dado)</span>" : DASH;
        nums.innerHTML = '<table class="t kv"><tbody>' +
          '<tr><th scope="row">Problemas por contest</th><td class="num">' + SG.fmtNum(a.per_contest, 2) + '</td><td class="muted small">esperado num contest do filtro (secundário conta 0,5; ponderado por família)</td></tr>' +
          '<tr><th scope="row">Presença</th><td class="num">' + SG.fmtPct(a.presence) + '</td><td class="muted small">' + a.nContests + " de " + nC + " contests têm ao menos um problema (ponderado por família)</td></tr>" +
          '<tr><th scope="row">Problemas</th><td class="num">' + a.nProblems + '</td><td class="muted small">' + a.nPrimary + " como tópico principal, " + a.nSecondary + " como secundário</td></tr>" +
          '<tr><th scope="row">Posição</th><td class="num">' + a.rankPerContest + "º</td><td class=\"muted small\">de " + S.list.length + " tópicos, por problemas por contest</td></tr>" +
          '<tr><th scope="row">Dificuldade típica</th><td class="num"></td><td>' + diffCell(a.typicalDiff, true) +
          (a.medianDv != null ? ' <span class="muted small">no problema mediano do tópico, ' +
            (SG.K ? Math.round(a.medianDv * SG.K) + " dos " + SG.K : Math.round(a.medianDv * 100) + "% dos") +
            " melhores times do contest resolveram</span>" : "") + "</td></tr>" +
          '<tr><th scope="row">Distribuição</th><td class="num">' + a.nProblems + "</td><td>" + binsHtml + "</td></tr>" +
          '<tr><th scope="row">1º AC</th><td class="num">' + (a.firstSolve.n ? SG.fmtNum(a.firstSolve.median, 0) : DASH) + "</td><td>" + fsTxt + "</td></tr>" +
          "</tbody></table>";
      }

      // Matrix families x years
      var fams = D.families.filter(function (f) { return filter.fams[f.id]; });
      var years = [];
      for (var y = filter.from; y <= filter.to; y++) years.push(y);
      var held = {}, cnt = {}, mx = 0;
      S.scope.contests.forEach(function (c) { held[c.family + "|" + c.year] = (held[c.family + "|" + c.year] || 0) + 1; });
      probs.forEach(function (p) { var k = p.family + "|" + p.year; cnt[k] = (cnt[k] || 0) + 1; mx = Math.max(mx, cnt[k]); });
      var mh = '<table class="t matrix"><thead><tr><th scope="col">Família</th>' + years.map(function (y) { return '<th scope="col" class="num">' + y + "</th>"; }).join("") +
        '<th scope="col" class="num">Total</th></tr></thead><tbody>' +
        fams.map(function (f) {
          var tot = 0;
          return '<tr><th scope="row">' + esc(f.short) + "</th>" + years.map(function (y) {
            var k = f.id + "|" + y;
            if (!held[k]) return '<td class="num nocontest" title="' + y + ': sem contest no filtro"></td>';
            var n = cnt[k] || 0; tot += n;
            var pct = n && mx ? Math.round(25 + 75 * n / mx) : 0;
            return '<td class="num' + (n ? "" : " zero") + '"' + (n ? ' style="background:color-mix(in srgb, var(--accent-soft) ' + pct + '%, transparent)"' : "") +
              ' title="' + esc(f.short + " " + y + ": " + n + (n === 1 ? " problema" : " problemas")) + '">' + (n || "·") + "</td>";
          }).join("") + '<td class="num total">' + tot + "</td></tr>";
        }).join("") + "</tbody></table>";
      document.getElementById("tmatrix").innerHTML = mh + '<p class="note">Vazio: a família não teve contest naquele ano dentro do filtro. “·”: teve contest, sem problema do tópico.</p>';

      // Strip plot
      stripItems = probs.filter(function (p) { return p._dv != null; }).map(function (p) {
        var bits = [];
        if (p.solved != null) bits.push((p.total ? p.solved + "/" + p.total : p.solved) + " times resolveram");
        bits.push(topText(p));
        if (p.first_solve_min != null) bits.push("1º AC " + p.first_solve_min + " min");
        return { p: p, x: p._dv, bin: p._bin, href: "#d-" + p.id,
          label1: contestShort(p.contest) + " · " + p.letter + " — " + p.title, label2: bits.join(" · ") };
      });
      drawStrip();

      pst.list = probs;
      probsEl._list = probs;
      renderProblemTable(probsEl, probs, pst);
    }
    function drawStrip() {
      var box = document.getElementById("tstrip");
      if (!box) return;
      if (!stripItems.length) { box.innerHTML = '<p class="muted">Sem dados de solução neste filtro.</p>'; return; }
      SG.charts.stripPlot(box, stripItems, {
        ariaLabel: "Problemas do tópico por fração de times que resolveram",
        onClick: function (it) { openRow(probsEl, pst, it.p.id); }
      });
    }
    update();
    return { path: r.path, update: update, resize: drawStrip };
  }

  // ---- View: Problemas (explorer) ------------------------------------------------------
  function viewProblems(r) {
    var p0 = r.params;
    var loc = { q: p0.q || "", area: p0.area || "", topico: p0.topico || "", dif: p0.dif || "" };
    var pst = { cols: ["contest", "letter", "title", "topic", "solved", "diff", "fs"], sort: { key: "contest", dir: -1 },
      expanded: {}, ideaOpen: {}, showIdeas: p0.ideias === "1" };
    var areaOpts = IX.areas.map(function (a) { return '<option value="' + esc(a.id) + '">' + esc(a.name) + "</option>"; }).join("");
    var topicOpts = IX.areas.map(function (a) {
      var ts = (D.topics || []).filter(function (t) { return t.area === a.id; });
      if (!ts.length) return "";
      return '<optgroup label="' + esc(a.name) + '">' + ts.map(function (t) { return '<option value="' + esc(t.id) + '">' + esc(t.name) + "</option>"; }).join("") + "</optgroup>";
    }).join("");
    var difOpts = CONFIG.difficulty.map(function (b) { return '<option value="' + b.id + '">' + esc(b.name) + "</option>"; }).join("");
    app.innerHTML = '<div class="pagehead"><h1>Problemas</h1></div>' + filterRowHTML() +
      '<div class="filters sub" role="group" aria-label="Filtros de problemas">' +
      '<input type="search" id="q" placeholder="Buscar por título, tópico ou ideia" aria-label="Buscar problemas (atalho: /)" autocomplete="off">' +
      '<select id="f-area" aria-label="Área"><option value="">Todas as áreas</option>' + areaOpts + "</select>" +
      '<select id="f-topic" aria-label="Tópico"><option value="">Todos os tópicos</option>' + topicOpts + "</select>" +
      '<select id="f-dif" aria-label="Dificuldade"><option value="">Todas as dificuldades</option>' + difOpts + "</select>" +
      '<label class="check"><input type="checkbox" id="f-ideas"> Mostrar ideias</label>' +
      '<span class="fcount2" aria-live="polite"></span></div>' +
      '<div class="tw" id="plist"></div>';
    bindFilterRow(app);
    var qEl = document.getElementById("q"), aEl = document.getElementById("f-area"), tEl = document.getElementById("f-topic"),
      dEl = document.getElementById("f-dif"), iEl = document.getElementById("f-ideas"), listEl = document.getElementById("plist");
    qEl.value = loc.q; aEl.value = loc.area; tEl.value = loc.topico; dEl.value = loc.dif; iEl.checked = pst.showIdeas;
    if (aEl.value !== loc.area) loc.area = "";
    if (tEl.value !== loc.topico) loc.topico = "";

    var searchText = {};
    D.problems.forEach(function (p) {
      searchText[p.id] = norm([p.title, contestShort(p.contest), p.letter, p.summary, p.key_idea, p.solution, stepsSearchText(p)]
        .concat(p._topics.map(function (t) { return topicName(t.id); })).join(" | "));
    });
    function update() {
      var scope = SG.scopeOf(filter);
      var terms = norm(loc.q).split(/\s+/).filter(Boolean);
      var list = scope.problems.filter(function (p) {
        if (loc.topico && !p._topics.some(function (t) { return t.id === loc.topico; })) return false;
        if (loc.area && !p._topics.some(function (t) { var a = areaOfTopic(t.id); return a && a.id === loc.area; })) return false;
        if (loc.dif && p._bin !== loc.dif) return false;
        if (terms.length) { var s = searchText[p.id]; for (var i = 0; i < terms.length; i++) if (s.indexOf(terms[i]) < 0) return false; }
        return true;
      });
      setCount(app, scope.problems.length + " problemas · " + scope.contests.length + " contests");
      app.querySelector(".fcount2").textContent = list.length + " de " + scope.problems.length;
      listEl._list = list;
      renderProblemTable(listEl, list, pst);
    }
    function local() { return { q: loc.q, area: loc.area, topico: loc.topico, dif: loc.dif, ideias: pst.showIdeas ? "1" : "" }; }
    function commit() { update(); writeHash("problemas", local()); }
    var tmr = null;
    qEl.addEventListener("input", function () {
      loc.q = qEl.value;
      clearTimeout(tmr);
      tmr = setTimeout(commit, 120);
    });
    aEl.addEventListener("change", function () { loc.area = aEl.value; commit(); });
    tEl.addEventListener("change", function () { loc.topico = tEl.value; commit(); });
    dEl.addEventListener("change", function () { loc.dif = dEl.value; commit(); });
    iEl.addEventListener("change", function () { pst.showIdeas = iEl.checked; commit(); });
    update();
    return {
      path: "problemas", update: update, local: local,
      clearLocal: function () { loc.q = loc.area = loc.topico = loc.dif = ""; qEl.value = aEl.value = tEl.value = dEl.value = ""; },
      search: qEl
    };
  }

  // ---- View: Contests ------------------------------------------------------------------
  function viewContests(r) {
    var byDate = D.contests.slice().sort(function (a, b) {
      return (b.year - a.year) || String(b.date || "").localeCompare(String(a.date || "")) || a.id.localeCompare(b.id);
    });
    var cid = r.parts[1] || (byDate[0] && byDate[0].id);
    var c = IX.contestById[cid];
    var groups = D.families.map(function (f) {
      return { f: f, list: byDate.filter(function (x) { return x.family === f.id; }) };
    }).filter(function (g) { return g.list.length; });
    var aside = '<nav class="clist" aria-label="Edições">' + groups.map(function (g) {
      return '<div class="cgroup"><p class="cfam">' + esc(g.f.short) + "</p><ul>" + g.list.map(function (x) {
        return '<li><a href="' + link("contests/" + encodeURIComponent(x.id)) + '"' + (x.id === cid ? ' aria-current="page"' : "") + ">" + esc(x.short || x.id) + "</a></li>";
      }).join("") + "</ul></div>";
    }).join("") + "</nav>";
    var select = '<label class="csel"><span class="vh">Edição</span><select id="csel">' + groups.map(function (g) {
      return '<optgroup label="' + esc(g.f.short) + '">' + g.list.map(function (x) {
        return '<option value="' + esc(x.id) + '"' + (x.id === cid ? " selected" : "") + ">" + esc(x.short || x.id) + "</option>";
      }).join("") + "</optgroup>";
    }).join("") + "</select></label>";
    if (!c) {
      app.innerHTML = '<div class="contests">' + aside + '<div class="cmain">' + select + '<div class="pagehead"><h1>Contest não encontrado</h1></div></div></div>';
    } else {
      var L = c.links || {};
      var metaBits = [fmtDate(c.date), c.total_teams != null ? c.total_teams + " times" : null,
        extLink(L.scoreboard, "Placar"), extLink(L.statements, "Enunciados"), extLink(L.editorial, "Editorial"),
        extLink(L.mirror, "Mirror"), extLink(L.kattis, "Kattis")].filter(Boolean);
      app.innerHTML = '<div class="contests">' + aside + '<div class="cmain">' + select +
        '<div class="pagehead"><h1>' + esc(c.short || c.id) + '</h1></div><p class="meta">' + metaBits.join('<span class="sep"> · </span>') + "</p>" +
        '<p class="note">' + esc(c.name || "") + (c.max_solved != null ? " · problema mais resolvido: " + c.max_solved + " times" : "") +
        (c.notes ? " · " + esc(c.notes) : "") + "</p>" +
        '<div class="tw" id="cprobs"></div></div></div>';
      var probs = D.problems.filter(function (p) { return p.contest === c.id; });
      var pst = { cols: ["letter", "title", "topic", "solvedbar", "diff", "fs"], sort: { key: "solved", dir: -1 },
        expanded: {}, ideaOpen: {}, showIdeas: false, emptyText: "Sem problemas registrados para este contest." };
      var el = document.getElementById("cprobs");
      el._list = probs;
      renderProblemTable(el, probs, pst);
    }
    document.getElementById("csel").addEventListener("change", function (e) {
      location.hash = link("contests/" + encodeURIComponent(e.target.value));
    });
    return { path: "contests/" + (cid || "") };
  }

  // ---- View: Cortes LAC ---------------------------------------------------------------
  // DATASET.lac_cutoffs: problems needed at each Latin America Championship edition for the
  // World Finals slot by performance and for each medal. Not affected by the global filter.
  var CUTS = D.lac_cutoffs && (D.lac_cutoffs.editions || []).length ? D.lac_cutoffs : null;
  var CUT_COLS = [
    { id: "wf", name: "World Finals" }, { id: "gold", name: "Ouro" }, { id: "silver", name: "Prata" }, { id: "bronze", name: "Bronze" }
  ];
  var TIE = "decidido no tempo: times com o mesmo número de problemas ficaram de fora pela penalidade";
  function viewCutoffs() {
    if (!CUTS) {
      app.innerHTML = '<div class="pagehead"><h1>Cortes do LAC</h1></div><p class="prose">Os cortes ainda não foram calculados para estes dados.</p>';
      return { path: "cortes" };
    }
    var eds = CUTS.editions.slice().sort(function (a, b) { return (b.year || 0) - (a.year || 0); });
    function cat(e, id) { return (e.categories || []).filter(function (c) { return c.id === id; })[0] || null; }
    function cell(e, c) {
      if (!c || c.min_solved == null) return '<td class="num">' + DASH + "</td>";
      var tip = [c.name || "", c.teams != null ? plural(c.teams, "time", "times") : null,
        c.max_solved != null && c.max_solved !== c.min_solved ? "resolveram de " + c.min_solved + " a " + c.max_solved : "resolveram " + c.min_solved,
        c.last_penalty != null ? "último dentro: " + c.last_penalty + " min de penalidade" : null,
        c.first_out_penalty != null ? "primeiro fora, com o mesmo número de problemas: " + c.first_out_penalty + " min" : null,
        c.tie_out ? TIE : null].filter(Boolean).join(" · ");
      return '<td class="num cut" title="' + esc(tip) + '"><span class="cutn">' + c.min_solved + "</span>" +
        (e.problems != null ? '<span class="cutd"> de ' + e.problems + "</span>" : "") +
        '<span class="tiem"' + (c.tie_out ? ' aria-label="' + esc(TIE) + '">*' : ">") + "</span></td>";
    }
    var anyTie = false;
    var rows = eds.map(function (e) {
      var c = IX.contestById[e.contest];
      return '<tr><th scope="row">' + (c ? '<a href="' + link("contests/" + encodeURIComponent(e.contest)) + '">' + esc(e.year) + "</a>" : esc(e.year)) + "</th>" +
        '<td class="num hide-m">' + (e.teams != null ? e.teams : DASH) + '</td><td class="num hide-m">' + (e.problems != null ? e.problems : DASH) + "</td>" +
        CUT_COLS.map(function (k) { var x = cat(e, k.id); if (x && x.tie_out) anyTie = true; return cell(e, x); }).join("") + "</tr>";
    }).join("");
    var typ = CUT_COLS.map(function (k) {
      var v = eds.map(function (e) { var x = cat(e, k.id); return x ? x.min_solved : null; }).filter(function (x) { return x != null; });
      if (!v.length) return '<td class="num">' + DASH + "</td>";
      var med = SG.median(v), lo = Math.min.apply(null, v), hi = Math.max.apply(null, v);
      return '<td class="num cut" title="' + esc("mediana de " + plural(v.length, "edição", "edições")) + '"><span class="cutn">' + SG.fmtNum(med, med % 1 ? 1 : 0) + "</span>" +
        (lo !== hi ? '<span class="cutd"> ' + lo + "–" + hi + "</span>" : "") + '<span class="tiem"></span></td>';
    }).join("");
    var head = '<tr><th scope="col">Edição</th><th scope="col" class="num hide-m">Times</th><th scope="col" class="num hide-m">Problemas</th>' +
      CUT_COLS.map(function (k) { return '<th scope="col" class="num">' + esc(k.name) + "</th>"; }).join("") + "</tr>";
    // "[UFMG] team name" -> "UFMG"
    function inst(team) { var m = /^\s*\[([^\]]+)\]/.exec(team || ""); return m ? m[1].trim() : team; }
    function teamBits(t, withReason) {
      return [t.rank != null ? t.rank + "º" : null, t.solved != null ? plural(t.solved, "problema", "problemas") : null,
        withReason && t.reason ? t.reason : null].filter(Boolean).join(", ");
    }
    var anySkip = false, notes = [], rawNotes = [];
    eds.forEach(function (e) {
      var bits = [];
      var sk = e.rank_skipped || [];
      if (sk.length) {
        anySkip = true;
        bits.push("Ficaram fora do World Finals por já haver time melhor da mesma instituição: " +
          sk.map(function (t) { return '<span title="' + esc(t.team) + '">' + esc(inst(t.team)) + "</span> (" + esc(teamBits(t, false)) + ")"; }).join(", "));
      }
      var q = e.excluded_quota || [];
      if (q.length) {
        bits.push("Classificados como campeões de sub-região, fora da conta do corte por desempenho: " +
          q.map(function (t) { return esc(t.team) + " (" + esc(teamBits(t, true)) + ")"; }).join("; "));
      }
      if (bits.length) notes.push("<li><strong>" + esc(e.year) + ".</strong> " + bits.join(". ") + ".</li>");
      if (e.notes) rawNotes.push("<li><strong>" + esc(e.year) + ".</strong> " + esc(e.notes) + "</li>");
    });
    var slots = eds.map(function (e) { return e.wf_slots_total; }).filter(function (x) { return x != null; })[0] || 18;
    var src = (CUTS.sources || []).filter(Boolean).map(function (u) {
      return /^https?:\/\//.test(u) ? '<a href="' + esc(u) + '" target="_blank" rel="noopener">' + esc(u.replace(/^https?:\/\//, "")) + "</a>" : esc(u);
    });
    app.innerHTML = '<div class="pagehead"><h1>Cortes do LAC</h1></div>' +
      '<p class="lede">Quantos problemas foram precisos em cada edição do Latin America Championship para a vaga no World Finals por desempenho e para cada medalha. Esta aba não usa o filtro das outras.</p>' +
      '<div class="tw"><table class="t cuts"><thead>' + head + "</thead><tbody>" + rows + '</tbody><tfoot><tr><th scope="row">Típico</th><td class="hide-m"></td><td class="hide-m"></td>' + typ + "</tr></tfoot></table></div>" +
      '<div class="cutrule"><p>Vagas no World Finals: ' + slots + " = 6 campeões de sub-região + " + (slots - 6) + " por desempenho, no máximo 1 time por instituição.</p>" +
      (anySkip ? "<p>Por isso o corte do World Finals pode ficar abaixo do bronze: times bem colocados de instituições que já têm vaga são pulados, e a vaga desce na classificação.</p>" : "") +
      "</div>" +
      '<div class="cutnotes">' +
      "<p>Cada célula é o menor número de problemas resolvidos entre os times da categoria" + (anyTie ? "; * = " + esc(TIE) : "") + ". Típico: mediana das edições, com a faixa quando variam.</p>" +
      (notes.length ? "<ul>" + notes.join("") + "</ul>" : "") +
      (rawNotes.length ? '<details class="cutdet"><summary>Notas do cálculo por edição</summary><ul>' + rawNotes.join("") + "</ul></details>" : "") +
      (src.length ? "<p>Fontes: " + src.join(" · ") + "</p>" : "") + "</div>";
    return { path: "cortes" };
  }

  // ---- View: Sobre ---------------------------------------------------------------------
  function curriculumMethod() {
    var counts = "";
    if (CUR) {
      var ids = Object.keys(CUR.steps);
      var kept = ids.filter(function (id) { return CUR.steps[id].keep !== false; }).length;
      counts = " Hoje são " + plural(CUR.insights.length, "insight", "insights") + ", " + plural(CUR.deepenings.length, "aprofundamento", "aprofundamentos") + " e " +
        plural(CUR.techniques.length, "técnica", "técnicas") + "; " + kept + " de " + ids.length + " problemas analisados ficaram no currículo.";
    }
    var gens = [3, 2, 1].map(function (g) { return CONFIG.generality[g].name + " (" + CONFIG.generality[g].help + ")"; }).join(", ");
    return "<h2>Currículo</h2><p>Primeiro saem os problemas que não ensinam nada reutilizável: implementação direta, simulação, guloso óbvio e, por padrão, os que " +
      "70% ou mais dos " + esc(TOPK) + " resolveram. A solução de cada problema restante foi escrita em etapas, e cada etapa relevante foi classificada como " +
      "técnica nomeada (usada do jeito padrão), aprofundamento (propriedade pouco conhecida de uma técnica) ou insight (observação reutilizável sem nome). " +
      "Aprofundamentos e insights só entram se servem em pelo menos dois contextos diferentes do problema de origem, e recebem uma generalidade: " + esc(gens) + ". " +
      "A ordem é por utilidade: generalidade (3, 2 ou 1) vezes a frequência dos seus problemas no filtro, ponderada por família como em Problemas por contest." + counts + "</p>";
  }
  function viewAbout() {
    var famRows = D.families.map(function (f) {
      var cs = D.contests.filter(function (c) { return c.family === f.id; });
      var ys = cs.map(function (c) { return c.year; }).sort();
      var np = D.problems.filter(function (p) { return p.family === f.id; }).length;
      return '<tr><th scope="row">' + esc(f.short) + '</th><td>' + esc(f.name) + '</td><td class="num">' + SG.fmtNum(f.weight, 1) +
        "</td><td>" + (f.group === CONFIG.latamGroup ? "LATAM" : "Mundo") + '</td><td class="num">' + cs.length + "</td><td>" +
        (ys.length ? esc(ys.join(", ")) : DASH) + '</td><td class="num">' + np + "</td></tr>";
    }).join("");
    var tiers = CONFIG.tiers.map(function (t, i) {
      return "<li>" + tierText(t) + ": " + esc(tierCriterion(i)) + ".</li>";
    }).join("");
    var difs = CONFIG.difficulty.map(function (b, i) {
      var next = CONFIG.difficulty[i - 1];
      var rule = b.min == null ? "nenhum time resolveu" :
        (next && next.min != null ? "de " + Math.round(b.min * 100) + "% a menos de " + Math.round(next.min * 100) + "%" : Math.round(b.min * 100) + "% ou mais");
      if (b.id === "very_hard") rule = "menos de " + Math.round(next.min * 100) + "% (com ao menos um AC)";
      return '<li><span class="diff lv lv-' + b.id + '"><span class="dot d-' + b.id + '" aria-hidden="true"></span>' + esc(b.name) + "</span>: " + esc(rule) + ".</li>";
    }).join("");
    var nSec = D.problems.filter(function (p) { return (p.secondary || []).length; }).length;
    var tName = target.name ? esc(target.name) : "";
    var tDate = targetDate && !isNaN(targetDate) ? targetDate.toLocaleString("pt-BR", { dateStyle: "long", timeStyle: "short", timeZone: "America/Sao_Paulo" }) : "";
    app.innerHTML = '<div class="pagehead"><h1>Sobre e método</h1></div><div class="prose">' +
      (D.mock ? '<p class="warn">Os dados atuais são fictícios (mock de desenvolvimento). Rode o pipeline real para substituí-los.</p>' : "") +
      '<h2 class="first">Como usar</h2><ul class="howto">' +
      '<li><a href="' + link("curriculo") + '">Currículo</a> é por onde começar' + (CUR ? "" : " (ainda não gerado para estes dados)") +
      ": <strong>insights</strong> (observações reutilizáveis sem nome de livro), <strong>aprofundamentos</strong> de técnicas conhecidas e a lista de <strong>técnicas</strong>, cada item com os problemas em que aparece, do mais útil para o menos útil.</li>" +
      '<li><a href="' + link("topicos") + '">Tópicos</a> é o ranking por tema amplo: de cima para baixo, agrupado em níveis (' + esc(CONFIG.tiers.map(function (t) { return t.name; }).join(", ")) + ").</li>" +
      "<li><strong>Por contest</strong>: quantos problemas do tópico se espera num contest. <strong>Presença</strong>: em quantos contests do filtro ele apareceu.</li>" +
      "<li>O filtro <strong>Só LATAM</strong> / <strong>Geral</strong>, as famílias e os anos mudam todos os números, em todas as abas.</li>" +
      "<li>Clique num tópico para ver seus números, onde apareceu (família × ano) e seus problemas.</li>" +
      "<li>Clique numa linha de problema (ou na letra) para ver o resumo do enunciado e os links (mirror no Codeforces ou Kattis, enunciado). A solução, e as etapas da solução quando o problema está no currículo, ficam escondidas em <strong>Mostrar ideia</strong>, para não dar spoiler.</li>" +
      '<li><a href="' + link("problemas") + '">Problemas</a>: busca e filtros (área, tópico, dificuldade) sobre todos os problemas; a tecla <kbd>/</kbd> vai para a busca.</li>' +
      '<li><a href="' + link("contests") + '">Contests</a>: cada prova com seus problemas ordenados por quantos times resolveram.</li>' +
      (CUTS ? '<li><a href="' + link("cortes") + '">Cortes LAC</a>: quantos problemas foram precisos em cada edição do LAC para a vaga no World Finals e para cada medalha.</li>' : "") +
      "<li>Os filtros ficam no endereço da página: copie o link para compartilhar exatamente a mesma visão.</li></ul>" +
      "<h2>Fontes</h2><p>" + D.contests.length + " contests, " + D.problems.length + " problemas, " + (D.topics || []).length +
      " tópicos. Solves vêm do placar final oficial (só times oficiais, sem convidados nem mirrors). Ideias de solução vêm do editorial oficial quando existe; senão de discussões da comunidade ou de análise própria, indicado em cada problema.</p></div>" +
      '<div class="tw"><table class="t"><thead><tr><th scope="col">Família</th><th scope="col">Nome</th><th scope="col" class="num">Peso</th><th scope="col">Grupo</th><th scope="col" class="num">Edições</th><th scope="col">Anos</th><th scope="col" class="num">Problemas</th></tr></thead><tbody>' +
      famRows + "</tbody></table></div>" +
      '<div class="prose"><p class="small muted">“Só LATAM” usa as famílias do grupo LATAM; “Geral” usa todas. O peso de cada família multiplica a contribuição dos seus contests.</p>' +
      curriculumMethod() +
      "<h2>Tópicos</h2><p>Cada problema tem um tópico principal e, às vezes, secundários (" + nSec + " problemas têm algum). A classificação parte da ideia de solução, não do enunciado.</p>" +
      "<h2>Problemas por contest</h2><p>Soma, sobre os problemas do filtro, de " + SG.fmtNum(CONFIG.roleWeight.primary, 0) + " (tópico principal) ou " +
      SG.fmtNum(CONFIG.roleWeight.secondary, 1) + " (secundário) vezes o peso da família, dividida pela soma dos pesos dos contests do filtro. Lê-se como o número esperado de problemas do tópico num contest. É a ordem do ranking dentro de cada nível.</p>" +
      "<h2>Presença e níveis</h2><p>Presença é a fração dos contests do filtro (ponderada pelo peso da família) com ao menos um problema do tópico, principal ou secundário. O nível vem da presença:</p><ul>" + tiers + "</ul>" +
      "<h2>Dificuldade</h2><p>Dificuldade é a fração dos " + esc(TOPK) + " oficiais do contest (pela classificação final) que resolveram o problema. " +
      (SG.K ? SG.K + " é perto do tamanho do LAC, então" : "Assim,") + " um regional com 500 times e um campeonato com 40 ficam na mesma escala. Quando falta esse dado, usa-se a fração em relação ao problema mais resolvido do contest.</p><ul>" + difs +
      "</ul><p>A dificuldade típica de um tópico é a mediana desse valor entre seus problemas. A coluna " + esc(SOLVED_LABEL) + " mostra quantos desses melhores times resolveram (por exemplo 5/" + (SG.K || 40) + "), na mesma escala da dificuldade; os números de todos os times oficiais ficam na dica ao passar o mouse. Sem esse dado, mostra times que resolveram / todos os times oficiais.</p>" +
      "<h2>Contagem regressiva</h2><p>" + tName + (tDate ? ", " + esc(tDate) + " (horário de Brasília)" : "") + ".</p>" +
      "<h2>Atualização</h2><p>Dados gerados em " + esc(D.generated || "—") + ". Para regenerar: <code>python -I pipeline/build_dataset.py</code>.</p></div>";
    return { path: "sobre" };
  }

  // ---- Router --------------------------------------------------------------------------
  var VIEWS = { cortes: viewCutoffs, curriculo: viewCurriculum, topicos: viewTopics, topico: viewTopic, problemas: viewProblems, contests: viewContests, sobre: viewAbout };
  var TAB_OF = { cortes: "cortes", curriculo: "curriculo", topicos: "topicos", topico: "topicos", problemas: "problemas", contests: "contests", sobre: "sobre" };
  var lastPath = null;
  function updateTabLinks() {
    Array.prototype.forEach.call(document.querySelectorAll(".tabs a"), function (a) {
      var t = a.dataset.tab;
      a.setAttribute("href", link(t === "contests" && cur && /^contests\//.test(cur.path) ? cur.path : t));
    });
    var wm = document.querySelector(".wordmark");
    if (wm) wm.setAttribute("href", link(HOME));
  }
  function route() {
    var r = parseHash();
    var key = r.parts[0] || HOME;
    if (!VIEWS[key]) key = HOME;
    if (!r.parts.length) { r.parts = [HOME]; r.path = HOME; }
    filter = filterFromParams(r.params);
    store("sg-filter", { fams: famList(filter.fams), from: filter.from, to: filter.to });
    SG.charts.hideTip();
    cur = VIEWS[key](r) || { path: r.path };
    var tab = TAB_OF[key];
    Array.prototype.forEach.call(document.querySelectorAll(".tabs a"), function (a) {
      if (a.dataset.tab === tab) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    updateTabLinks();
    var titles = { cortes: "Cortes LAC", curriculo: "Currículo", topicos: "Tópicos", topico: (IX.topicById[r.parts[1]] || {}).name || "Tópico", problemas: "Problemas",
      contests: (IX.contestById[r.parts[1]] || {}).short || "Contests", sobre: "Sobre" };
    document.title = titles[key] + " · Estudo " + TLABEL;
    if (lastPath !== r.path) { window.scrollTo(0, 0); lastPath = r.path; }
    if (cur.after) cur.after();
    // make the address bar reflect the effective filter (for sharing)
    if (key === "curriculo" || key === "topicos" || key === "topico" || key === "problemas") {
      var extra = cur.local ? cur.local() : null;
      writeHash(cur.path || r.path || HOME, extra);
    }
  }
  window.addEventListener("hashchange", function () {
    if (lastWritten && location.hash === lastWritten) { lastWritten = null; return; }
    lastWritten = null;
    route();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
    var tag = (document.activeElement && document.activeElement.tagName) || "";
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(tag)) return;
    var q = document.getElementById("q");
    if (q) { e.preventDefault(); q.focus(); q.select(); }
    else { e.preventDefault(); location.hash = link("problemas"); setTimeout(function () { var q2 = document.getElementById("q"); if (q2) q2.focus(); }, 0); }
  });
  var rt = null;
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () { if (cur && cur.resize) cur.resize(); }, 150);
  });

  // ---- Boot ----------------------------------------------------------------------------
  document.querySelector(".wordmark").textContent = "Estudo " + TLABEL;
  var cutTab = document.querySelector('.tabs a[data-tab="cortes"]');
  if (cutTab) cutTab.hidden = !CUTS;
  var mockNote = document.getElementById("mocknote");
  if (mockNote && D.mock) { mockNote.innerHTML = '<span aria-hidden="true"> · </span><strong>dados fictícios (mock)</strong>'; mockNote.hidden = false; }
  var skip = document.querySelector(".skip");
  if (skip) skip.addEventListener("click", function (e) { e.preventDefault(); app.focus(); });
  syncThemeBtn();
  tickCountdown();
  setInterval(tickCountdown, 60000);
  route();
})();
