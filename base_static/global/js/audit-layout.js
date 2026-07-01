/**
 * Auditoria contínua de layout responsivo — Arancia.
 * Uso no console do navegador ou como bookmarklet após carregar a página.
 *
 * Exemplo:
 *   auditLayout('.app-page--fluid')
 *   auditLayoutAll()
 */
(function (global) {
  'use strict';

  function readToken(name) {
    var root = getComputedStyle(document.documentElement);
    return parseFloat(root.getPropertyValue(name)) || 0;
  }

  function usableWidth() {
    var offset = readToken('--content-offset');
    var gutter = readToken('--content-gutter');
    return window.innerWidth - offset - gutter * 2;
  }

  function hasHorizontalOverflow() {
    return document.documentElement.scrollWidth > window.innerWidth + 1;
  }

  function auditLayout(selector) {
    var el = document.querySelector(selector);
    var usable = usableWidth();
    var width = el ? el.offsetWidth : null;
    var fillsSpace = el ? width >= usable - 60 : null;
    return {
      selector: selector,
      found: !!el,
      width: width,
      usableApprox: usable,
      fillsSpace: fillsSpace,
      horizontalOverflow: hasHorizontalOverflow(),
      ok: el ? fillsSpace && !hasHorizontalOverflow() : null,
    };
  }

  function auditLayoutAll(selectors) {
    var list = selectors || [
      '.app-page--fluid',
      '.app-page--form',
      '.mural-feed-page',
      '.mural-mgmt-page',
      '.form-card-2col',
      '.form-card',
      '.form-1col',
      '.os-container',
      '.user-list-container',
      '.setcontainer',
      '.crm-tasks-page',
    ];
    var results = list.map(auditLayout);
    var overflow = hasHorizontalOverflow();
    return {
      viewport: { width: window.innerWidth, height: window.innerHeight },
      usableApprox: usableWidth(),
      horizontalOverflow: overflow,
      results: results,
      ok: !overflow && results.some(function (r) { return r.found && r.ok; }),
    };
  }

  global.auditLayout = auditLayout;
  global.auditLayoutAll = auditLayoutAll;
})(typeof window !== 'undefined' ? window : globalThis);
