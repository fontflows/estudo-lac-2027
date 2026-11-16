/* core.js — constants, helpers and the topic statistics (SPEC.md "Final dataset").
   Classic script (no ES modules) so the site also works from file://. */
(function () {
  "use strict";

  // ---- All tunable constants live here -------------------------------------------------
  var CONFIG = {
    // Weight of a problem's topic role in per_contest.
    roleWeight: { primary: 1, secondary: 0.5 },
    // Tier by weighted presence (share of contests in scope with >= 1 problem of the topic).
    tiers: [
      { id: "essencial", name: "Essencial", min: 0.5 },
      { id: "importante", name: "Importante", min: 0.25 },
      { id: "diferencial", name: "Diferencial", min: 0.1 },
      { id: "raro", name: "Raro", min: 0 }
    ],
    // Difficulty bins, by top_rate = share of the contest's top-K official teams (K = DATASET.difficulty_k)
    // that solved the problem; rel_solve only as fallback when top_rate is null.
    // Same thresholds as pipeline/build_dataset.py; "unsolved" is display-only (0 teams).
    difficulty: [
      { id: "easy", name: "Fácil", min: 0.7 },
      { id: "medium", name: "Médio", min: 0.3 },
      { id: "hard", name: "Difícil", min: 0.1 },
      { id: "very_hard", name: "Muito difícil", min: 0 },
      { id: "unsolved", name: "Sem AC", min: null }
    ],
    defaultScope: "geral",          // "latam" | "geral"
    latamGroup: "latam",
    areaSlots: 12                   // categorical colors in style.css (--area-1..12), by DATASET.areas order;
                                    // areas beyond that get the grey fallback (.a-fb)
  };

  var D = window.DATASET || null;

  // ---- Helpers -------------------------------------------------------------------------
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function median(arr) {
    if (!arr.length) return null;
    var a = arr.slice().sort(function (x, y) { return x - y; });
    var m = a.length >> 1;
    return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
  }
  function fmtNum(x, digits) {
    if (x == null || isNaN(x)) return null;
    return x.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  }
  function fmtPct(x) {
    if (x == null || isNaN(x)) return null;
    return Math.round(x * 100) + "%";
  }
  function diffOfRel(rel) {
    if (rel == null) return null;
    for (var i = 0; i < CONFIG.difficulty.length; i++) {
      var b = CONFIG.difficulty[i];
      if (b.min != null && rel >= b.min) return b.id;
    }
    return "very_hard";
  }
  // Difficulty value of a problem: top_rate, else rel_solve (fallback).
  function diffValue(p) {
    if (p.top_rate != null) return p.top_rate;
    return p.rel_solve != null ? p.rel_solve : null;
  }
  // Display bin of a problem: dataset difficulty, but 0 solves -> "unsolved".
  function problemBin(p) {
    if (p.solved === 0) return "unsolved";
    return p.difficulty || diffOfRel(diffValue(p));
  }
  var DIFF_BY_ID = {};
  CONFIG.difficulty.forEach(function (b, i) { DIFF_BY_ID[b.id] = { id: b.id, name: b.name, rank: i }; });
  function tierOf(presence) {
    // small epsilon: weighted sums like 0.6+0.8+... may land a hair below an exact threshold
    for (var i = 0; i < CONFIG.tiers.length; i++) if (presence >= CONFIG.tiers[i].min - 1e-9) return CONFIG.tiers[i];
    return CONFIG.tiers[CONFIG.tiers.length - 1];
  }

  // ---- Indexes -------------------------------------------------------------------------
  var IX = null;
  function buildIndex() {
    if (!D) return null;
    var famById = {}, contestById = {}, topicById = {}, areaById = {}, problemById = {};
    D.families.forEach(function (f, i) { famById[f.id] = f; f._order = i; });
    var areas = (D.areas || []).slice().sort(function (a, b) { return (a.order || 0) - (b.order || 0); });
    areas.forEach(function (a, i) { areaById[a.id] = a; a._slot = i < CONFIG.areaSlots ? String(i + 1) : "-fb"; a._order = i; });
    (D.topics || []).forEach(function (t, i) { topicById[t.id] = t; t._order = i; });
    D.contests.forEach(function (c) { contestById[c.id] = c; });
    D.problems.forEach(function (p) {
      problemById[p.id] = p;
      p._dv = diffValue(p);
      p._bin = problemBin(p);
      var seen = {};
      p._topics = [];
      if (p.primary) { p._topics.push({ id: p.primary, role: "primary" }); seen[p.primary] = 1; }
      (p.secondary || []).forEach(function (s) {
        if (s && !seen[s]) { p._topics.push({ id: s, role: "secondary" }); seen[s] = 1; }
      });
    });
    var years = D.contests.map(function (c) { return c.year; });
    return {
      famById: famById, contestById: contestById, topicById: topicById, areaById: areaById,
      problemById: problemById, areas: areas,
      minYear: Math.min.apply(null, years), maxYear: Math.max.apply(null, years),
      latamFams: D.families.filter(function (f) { return f.group === CONFIG.latamGroup; }).map(function (f) { return f.id; }),
      allFams: D.families.map(function (f) { return f.id; })
    };
  }
  IX = buildIndex();

  // ---- Filter --------------------------------------------------------------------------
  // filter = { fams: {id:true}, from: year, to: year }
  function inScopeContest(c, f) {
    return !!f.fams[c.family] && c.year >= f.from && c.year <= f.to && (c.problem_count || 0) > 0;
  }
  function scopeOf(f) {
    var contests = D.contests.filter(function (c) { return inScopeContest(c, f); });
    var cset = {};
    var W = 0;
    contests.forEach(function (c) { cset[c.id] = 1; W += IX.famById[c.family].weight; });
    var problems = D.problems.filter(function (p) { return cset[p.contest]; });
    return { contests: contests, contestSet: cset, weightSum: W, problems: problems };
  }

  // ---- Topic statistics (SPEC) ---------------------------------------------------------
  // per_contest = sum_problems(role weight * family weight) / sum family weight of contests in scope
  // presence    = sum family weight of contests with >=1 problem of the topic / same denominator
  function topicStats(f, scope) {
    scope = scope || scopeOf(f);
    var W = scope.weightSum;
    var acc = {};
    function get(tid) {
      if (!acc[tid]) acc[tid] = { id: tid, wsum: 0, contests: {}, problems: [], nPrimary: 0, nSecondary: 0, years: {} };
      return acc[tid];
    }
    scope.problems.forEach(function (p) {
      var w = IX.famById[p.family].weight;
      p._topics.forEach(function (tr) {
        var a = get(tr.id);
        a.wsum += CONFIG.roleWeight[tr.role] * w;
        a.contests[p.contest] = 1;
        a.problems.push({ p: p, role: tr.role });
        if (tr.role === "primary") a.nPrimary++; else a.nSecondary++;
        a.years[p.year] = (a.years[p.year] || 0) + 1;
      });
    });
    var out = [];
    Object.keys(acc).forEach(function (tid) {
      var a = acc[tid];
      var cw = 0, nc = 0;
      Object.keys(a.contests).forEach(function (cid) { cw += IX.famById[IX.contestById[cid].family].weight; nc++; });
      var rels = [], fs = [], bins = {};
      a.problems.forEach(function (x) {
        if (x.p._dv != null) rels.push(x.p._dv);
        if (x.p.first_solve_min != null) fs.push(x.p.first_solve_min);
        var b = x.p._bin || "none";
        bins[b] = (bins[b] || 0) + 1;
      });
      var medRel = median(rels);
      a.per_contest = W ? a.wsum / W : 0;
      a.presence = W ? cw / W : 0;
      a.nContests = nc;
      a.nProblems = a.problems.length;
      a.medianDv = medRel;
      a.typicalDiff = diffOfRel(medRel);
      a.bins = bins;
      a.firstSolve = { n: fs.length, median: median(fs), min: fs.length ? Math.min.apply(null, fs) : null };
      a.tier = tierOf(a.presence);
      a.topic = IX.topicById[tid] || { id: tid, name: tid, area: null, _order: 9999 };
      out.push(a);
    });
    out.sort(function (x, y) {
      return (y.per_contest - x.per_contest) || (y.presence - x.presence) || (x.topic._order - y.topic._order);
    });
    out.forEach(function (a, i) { a.rankPerContest = i + 1; });
    return { list: out, byId: acc, scope: scope, nContests: scope.contests.length };
  }

  window.SG = {
    CONFIG: CONFIG, D: D, IX: IX,
    esc: esc, median: median, fmtNum: fmtNum, fmtPct: fmtPct,
    diffOfRel: diffOfRel, diffValue: diffValue, problemBin: problemBin, K: D ? D.difficulty_k || null : null, DIFF: DIFF_BY_ID, tierOf: tierOf,
    scopeOf: scopeOf, topicStats: topicStats, inScopeContest: inScopeContest
  };
})();
