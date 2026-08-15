// Shared Live/Demo mode toggle for the Idun playground pages.
// Mode is persisted in localStorage so it carries across Expo / Playground / Diff.
//   'live' -> ask the router for a real Foundry run (falls back to demo if no token)
//   'demo' -> force a recorded replay (deterministic, no network)
// The router honours a `force_demo: true` flag on /api/chat/stream and treats
// the absence of a live token as a demo fallback either way, so the toggle's
// main effect is: in 'demo' we never even attempt a live call.

(function () {
  'use strict';

  var KEY = 'idun-mode';
  // default to demo so a booth with no token always shows a replay
  function current() {
    try {
      var v = localStorage.getItem(KEY);
      return v === 'live' ? 'live' : 'demo';
    } catch (e) {
      return 'demo';
    }
  }
  function set(m) {
    try { localStorage.setItem(KEY, m); } catch (e) {}
  }

  // Build the toggle control and insert it into `mountEl`.
  // `onChange(mode)` is called whenever the user flips the switch.
  function mount(mountEl, onChange) {
    if (!mountEl) return;
    var mode = current();

    var wrap = document.createElement('div');
    wrap.className = 'mode-toggle';
    wrap.innerHTML =
      '<span class="mode-label" data-mode="demo">DEMO</span>' +
      '<button type="button" class="mode-switch" role="switch" aria-checked="' +
        (mode === 'live') + '" aria-label="Live/Demo umschalten">' +
        '<span class="mode-knob"></span>' +
      '</button>' +
      '<span class="mode-label" data-mode="live">LIVE</span>';

    mountEl.appendChild(wrap);

    var sw = wrap.querySelector('.mode-switch');
    function paint() {
      var m = current();
      sw.setAttribute('aria-checked', String(m === 'live'));
      wrap.classList.toggle('is-live', m === 'live');
      wrap.classList.toggle('is-demo', m === 'demo');
    }
    sw.addEventListener('click', function () {
      var next = current() === 'live' ? 'demo' : 'live';
      set(next);
      paint();
      if (typeof onChange === 'function') onChange(next);
    });
    paint();
    return {
      get: current,
      set: function (m) { set(m); paint(); if (typeof onChange === 'function') onChange(m); }
    };
  }

  window.IdunMode = { current: current, set: set, mount: mount };
})();
