/* charts.js — the two hand-rolled SVG charts (DESIGN.md §8) and the shared tooltip. */
(function () {
  "use strict";
  var SG = window.SG;
  var esc = SG.esc;

  // ---- Tooltip -------------------------------------------------------------------------
  var tip = null;
  function ensureTip() {
    if (tip) return tip;
    tip = document.createElement("div");
    tip.className = "tip";
    tip.setAttribute("role", "tooltip");
    tip.hidden = true;
    document.body.appendChild(tip);
    return tip;
  }
  // lines: [first (bold), second]
  function showTip(lines, x, y) {
    var t = ensureTip();
    t.textContent = "";
    lines.forEach(function (l, i) {
      var d = document.createElement("div");
      if (i === 0) d.className = "tip-h";
      d.textContent = l;
      t.appendChild(d);
    });
    t.hidden = false;
    var r = t.getBoundingClientRect();
    var left = Math.min(window.innerWidth - r.width - 8, Math.max(8, x - r.width / 2));
    var top = y - r.height - 10;
    if (top < 56) top = y + 16;
    t.style.left = left + "px";
    t.style.top = top + "px";
  }
  function hideTip() { if (tip) tip.hidden = true; }

  // ---- Presence strip: one 6x14 cell per year, 2px gap ---------------------------------
  function presenceStrip(yearsMap, from, to) {
    var n = to - from + 1, cw = 6, gap = 2, h = 14;
    var w = n * (cw + gap) - gap;
    var s = '<svg class="strip" width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + " " + h + '" aria-hidden="true">';
    for (var y = from; y <= to; y++) {
      var c = yearsMap[y] || 0;
      s += '<rect x="' + (y - from) * (cw + gap) + '" y="0" width="' + cw + '" height="' + h + '" class="' +
        (c ? "on" : "off") + '"><title>' + y + ": " + c + (c === 1 ? " problema" : " problemas") + "</title></rect>";
    }
    return s + "</svg>";
  }
  function presenceText(yearsMap, from, to) {
    var ys = [];
    for (var y = from; y <= to; y++) if (yearsMap[y]) ys.push(y + " (" + yearsMap[y] + ")");
    return ys.length ? "Anos: " + ys.join(", ") : "Nenhum ano";
  }

  // ---- Difficulty strip plot -----------------------------------------------------------
  // items: [{p, x (0..1), bin, label1, label2, href}]
  function hash01(str) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return ((h >>> 0) % 1000) / 1000;
  }
  function stripPlot(container, items, opts) {
    var width = Math.max(280, Math.floor(container.clientWidth || 600));
    var padL = 14, padR = 14, band = 40, top = 10, axisGap = 8, tickH = 18;
    var plotW = width - padL - padR;
    var baseY = top + band + axisGap;
    var height = baseY + tickH + 4;
    function X(v) { return padL + v * plotW; }
    var s = '<svg class="stripplot" width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + " " + height + '" role="group" aria-label="' + esc(opts.ariaLabel || "") + '">';
    [0, 0.25, 0.5, 0.75, 1].forEach(function (t) {
      var x = X(t);
      s += '<line class="grid" x1="' + x + '" x2="' + x + '" y1="' + top + '" y2="' + baseY + '"/>';
      var anchor = t === 0 ? "start" : t === 1 ? "end" : "middle";
      var tx = t === 0 ? x - 2 : t === 1 ? x + 2 : x;
      s += '<text class="tick" x="' + tx + '" y="' + (baseY + 15) + '" text-anchor="' + anchor + '">' + Math.round(t * 100) + "%</text>";
    });
    s += '<line class="base" x1="' + padL + '" x2="' + (width - padR) + '" y1="' + baseY + '" y2="' + baseY + '"/>';
    items.forEach(function (it, i) {
      var cx = X(Math.max(0, Math.min(1, it.x)));
      var cy = top + 6 + hash01(it.p.id) * (band - 12);
      s += '<a class="mark" href="' + esc(it.href) + '" data-i="' + i + '" aria-label="' + esc(it.label1 + ". " + it.label2) + '">' +
        '<circle class="hit" cx="' + cx + '" cy="' + cy + '" r="12"/>' +
        '<circle class="dot d-' + esc(it.bin || "none") + '" cx="' + cx + '" cy="' + cy + '" r="4.5"/></a>';
    });
    s += "</svg>";
    container.innerHTML = s;
    var marks = container.querySelectorAll("a.mark");
    Array.prototype.forEach.call(marks, function (a) {
      var it = items[+a.getAttribute("data-i")];
      function show() {
        var r = a.querySelector(".dot").getBoundingClientRect();
        showTip([it.label1, it.label2], r.left + r.width / 2, r.top);
      }
      a.addEventListener("mouseenter", show);
      a.addEventListener("focus", show);
      a.addEventListener("mouseleave", hideTip);
      a.addEventListener("blur", hideTip);
      a.addEventListener("click", function (e) {
        e.preventDefault();
        hideTip();
        if (opts.onClick) opts.onClick(it);
      });
    });
  }

  window.addEventListener("scroll", hideTip, { passive: true });

  SG.charts = { presenceStrip: presenceStrip, presenceText: presenceText, stripPlot: stripPlot, showTip: showTip, hideTip: hideTip };
})();
