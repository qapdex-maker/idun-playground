/*
 * trace-viz.js — reusable Tool-Agent trajectory visualizer (Phase 4.2)
 *
 * Standalone, dependency-free (plain ES, no framework). Renders an Idun-style
 * agent trace (reasoning steps + tool calls) into any container element, using
 * the host page's CSS variables so it adapts to the Foundry dark/light theme.
 *
 * Usage:
 *   <link rel="stylesheet" href="trace-viz.css">
 *   <script src="trace-viz.js"></script>
 *   <div id="trace"></div>
 *   <script>
 *     TraceViz.render(document.getElementById('trace'), stepsArray);
 *   </script>
 *
 * `steps` shape (matches IdunClient.complete() / /api/idun/chat response):
 *   [{ kind: "reasoning"|"tool"|"message", text, tool, query, status, id }, ...]
 *
 * The same module is used by playground.html (chat trace) and diff.html
 * (side-by-side), so there is exactly ONE rendering implementation to maintain.
 */
(function (global) {
  "use strict";

  // Material Symbols glyph per step kind / status. Falls back gracefully if the
  // icon font is absent (text label still shows).
  var ICONS = {
    reasoning: "psychology",
    message: "chat",
    tool: "public",
    plan: "checklist",
  };

  var STATUS_BADGE = {
    searching:
      '<span class="tv-chip tv-blue flex items-center gap-1"><span class="tv-spinner"></span>SUCHT…</span>',
    running:
      '<span class="tv-chip tv-blue flex items-center gap-1"><span class="tv-spinner"></span>LÄUFT…</span>',
    completed: '<span class="tv-chip tv-green">✓ DONE</span>',
    error: '<span class="tv-chip tv-red">✕ ERROR</span>',
  };

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function icon(name) {
    return '<span class="tv-icon material-symbols-outlined">' + (ICONS[name] || "circle") + "</span>";
  }

  function rowForStep(s, n) {
    var kind = s.kind || "message";
    var row = document.createElement("div");
    row.className = "tv-row tv-cap-card rounded p-3 flex gap-3 items-start";

    if (kind === "tool") {
      var badge =
        STATUS_BADGE[s.status] ||
        '<span class="tv-chip tv-muted">' + esc((s.status || "tool").toUpperCase()) + "</span>";
      row.innerHTML =
        '<div class="tv-ic-bg tv-blue-bg">' +
        icon("tool") +
        "</div>" +
        '<div class="flex-grow min-w-0">' +
        '<div class="flex items-center justify-between gap-2">' +
        '<span class="tv-label">' +
        n +
        ". Tool · " +
        esc(s.tool || "web_search") +
        "</span>" +
        badge +
        "</div>" +
        '<div class="tv-query">' +
        esc(s.query || "(query)") +
        "</div>" +
        "</div>";
    } else {
      var preview = esc((s.text || "").replace(/\n/g, " ")).slice(0, 140);
      var label = kind === "reasoning" ? "Reasoning / Plan" : "Message";
      row.innerHTML =
        '<div class="tv-ic-bg tv-purple-bg">' +
        icon(kind) +
        "</div>" +
        '<div class="flex-grow min-w-0">' +
        '<div class="tv-label">' +
        n +
        ". " +
        label +
        "</div>" +
        '<div class="tv-text">' +
        preview +
        (preview.length >= 140 ? "…" : "") +
        "</div>" +
        "</div>";
    }
    return row;
  }

  function render(container, steps) {
    if (!container) return;
    container.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      container.innerHTML =
        '<div class="tv-empty">Keine Schritte — Agent hat direkt geantwortet.</div>';
      return;
    }
    var n = 0;
    steps.forEach(function (s) {
      n++;
      container.appendChild(rowForStep(s, n));
    });
    container.scrollTop = container.scrollHeight;
  }

  // Incremental update: mark the Nth step (1-based) as completed, or append a
  // new "running" step. Used by the live streaming UI so steps appear
  // progressively instead of re-rendering the whole list on every event.
  function markRunning(container, step) {
    if (!container) return;
    var rows = container.querySelectorAll(".tv-row");
    var n = rows.length + 1;
    var row = rowForStep(
      Object.assign({ status: "running" }, step),
      n
    );
    container.appendChild(row);
    container.scrollTop = container.scrollHeight;
  }

  function markDone(container, idx, step) {
    if (!container) return;
    var rows = container.querySelectorAll(".tv-row");
    var row = rows[idx]; // 0-based
    if (!row) return;
    var fresh = rowForStep(
      Object.assign({ status: "completed" }, step),
      idx + 1
    );
    container.replaceChild(fresh, row);
    container.scrollTop = container.scrollHeight;
  }

  // Convenience: render into a selector (returns false if not found).
  function renderSelector(sel, steps) {
    var el = typeof sel === "string" ? document.querySelector(sel) : sel;
    if (!el) return false;
    render(el, steps);
    return true;
  }

  global.TraceViz = {
    render: render,
    renderSelector: renderSelector,
    markRunning: markRunning,
    markDone: markDone,
    ICONS: ICONS,
  };

  // Phase 4.2 extension: side-by-side diff render. `steps` is one trace column,
  // `opts.sharedQueries` / `opts.uniqueQueries` are Sets of tool queries that the
  // column marks with a left border (shared = blue, unique = purple). This is the
  // single shared renderer used by diff.html so the card styling stays identical
  // to the single-trace view.
  function rowForStepDiff(s, n, opts) {
    var shared = false, uniqueSide = false;
    if (s.kind === "tool" && s.query) {
      if (opts.sharedQueries && opts.sharedQueries.has(s.query)) shared = true;
      if (opts.uniqueQueries && opts.uniqueQueries.has(s.query)) uniqueSide = true;
    }
    var row = rowForStep(s, n);
    if (shared) row.classList.add("tv-shared");
    else if (uniqueSide) row.classList.add("tv-unique");
    return row;
  }

  function renderDiff(container, steps, opts) {
    opts = opts || {};
    if (!container) return;
    container.innerHTML = "";
    if (!Array.isArray(steps) || steps.length === 0) {
      container.innerHTML = '<div class="tv-empty">Keine Schritte.</div>';
      return;
    }
    var n = 0;
    steps.forEach(function (s) {
      n++;
      container.appendChild(rowForStepDiff(s, n, opts));
    });
    container.scrollTop = container.scrollHeight;
  }

  global.TraceViz.renderDiff = renderDiff;
})(typeof window !== "undefined" ? window : this);
