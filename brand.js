/* Booth branding overlay: Foundry logo + Contoso Expo 2027 watermark.
 *
 * A small, non-intrusive brand mark is pinned bottom-right on every page and
 * stays visible in kiosk mode (it lives outside the chrome that kiosk hides).
 * Mount with IdunBrand.mount(mountEl) where mountEl is any container; the
 * overlay is fixed-position so the container only provides config intent.
 *
 * Options (data-* or JS): none required — sensible defaults are used.
 */
(function () {
  'use strict';

  function mount(mountEl, opts) {
    opts = opts || {};
    var logo = opts.logo || 'assets/foundry_logo_white.svg';
    var title = opts.title || 'Contoso Expo 2027';
    var sub = opts.sub || 'NatureLM-Idun-5-MoE · Azure AI Foundry';

    var el = document.createElement('div');
    el.id = 'brand-overlay';
    el.className = 'brand-overlay';
    el.setAttribute('aria-hidden', 'true');
    el.innerHTML =
      '<img class="brand-logo" src="' + logo + '" alt="" onerror="this.style.display=\'none\'"/>' +
      '<div class="brand-text">' +
        '<div class="brand-title">' + title + '</div>' +
        '<div class="brand-sub">' + sub + '</div>' +
      '</div>';
    document.body.appendChild(el);
    return el;
  }

  window.IdunBrand = { mount: mount };
})();
