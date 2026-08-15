/* Kiosk / fullscreen booth mode for the Idun playground.
 *
 * Enter kiosk via:
 *   - the "Kiosk" button in the topbar (mounted by IdunKiosk.mountButton)
 *   - the URL query param ?kiosk=1 (auto-enters on load)
 *
 * In kiosk mode the page chrome (top bar, footers, secondary controls) is
 * hidden and only the core stage remains, scaled to fill the screen. A small
 * floating toolbar (top-right) keeps the Live/Demo toggle and an Exit button
 * reachable. Pressing Escape or the Exit button leaves kiosk mode.
 */
(function () {
  'use strict';

  var KIOSK_CLASS = 'kiosk-mode';
  var KEY = 'idun-kiosk';

  function isOn() {
    return document.documentElement.classList.contains(KIOSK_CLASS);
  }
  function enter() {
    document.documentElement.classList.add(KIOSK_CLASS);
    try { localStorage.setItem(KEY, '1'); } catch (e) {}
    // request real fullscreen if available (user-gesture only)
    var el = document.documentElement;
    if (el.requestFullscreen) { try { el.requestFullscreen(); } catch (e) {} }
    else if (el.webkitRequestFullscreen) { try { el.webkitRequestFullscreen(); } catch (e) {} }
  }
  function exit() {
    document.documentElement.classList.remove(KIOSK_CLASS);
    try { localStorage.setItem(KEY, '0'); } catch (e) {}
    if (document.fullscreenElement && document.exitFullscreen) {
      try { document.exitFullscreen(); } catch (e) {}
    } else if (document.webkitFullscreenElement && document.webkitExitFullscreen) {
      try { document.webkitExitFullscreen(); } catch (e) {}
    }
  }
  function toggle() { isOn() ? exit() : enter(); }

  // Build the floating kiosk toolbar (toggle + exit). `modeMount` is the
  // element that already hosts the Live/Demo toggle; we keep it visible.
  function mountButton(mountEl, opts) {
    opts = opts || {};
    if (!mountEl) return;
    var btn = document.createElement('button');
    btn.id = 'kiosk-btn';
    btn.type = 'button';
    btn.className = 'material-symbols-outlined kiosk-enter-btn';
    btn.textContent = 'fullscreen';
    btn.title = 'Kiosk/Vollbild-Modus';
    btn.setAttribute('aria-label', 'Kiosk/Vollbild-Modus');
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      enter();
    });
    mountEl.appendChild(btn);

    // floating toolbar shown only in kiosk mode
    var bar = document.createElement('div');
    bar.id = 'kiosk-bar';
    bar.className = 'kiosk-bar';
    bar.innerHTML =
      '<span class="kiosk-bar-label">KIOSK</span>' +
      '<button type="button" id="kiosk-exit" class="kiosk-exit-btn" title="Kiosk verlassen (Esc)">' +
      '<span class="material-symbols-outlined">fullscreen_exit</span></button>';
    document.body.appendChild(bar);
    bar.querySelector('#kiosk-exit').addEventListener('click', function (e) {
      e.preventDefault();
      exit();
    });

    // Escape leaves kiosk
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOn()) { exit(); }
    });

    // auto-enter if ?kiosk=1 or previously left it on
    try {
      var params = new URLSearchParams(location.search);
      if (params.get('kiosk') === '1' || localStorage.getItem(KEY) === '1') {
        // defer so layout is ready and a user-gesture isn't required for styling
        setTimeout(enter, 50);
      }
    } catch (e) {}
  }

  window.IdunKiosk = { enter: enter, exit: exit, toggle: toggle, isOn: isOn, mountButton: mountButton };
})();
