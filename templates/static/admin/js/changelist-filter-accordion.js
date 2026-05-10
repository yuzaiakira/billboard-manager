/**
 * Collapsible admin changelist sidebar filters (Django <5: h3 + ul siblings).
 */
(function () {
  'use strict';

  function rowHasNonDefaultChoice(ul) {
    var first = ul.querySelector('li:first-child');
    var selected = ul.querySelector('li.selected');
    if (!selected) {
      return false;
    }
    return first !== selected;
  }

  function toggleSection(h3, ul) {
    var open = h3.getAttribute('aria-expanded') === 'true';
    var nextOpen = !open;
    h3.setAttribute('aria-expanded', nextOpen ? 'true' : 'false');
    ul.hidden = !nextOpen;
  }

  function initChangelistFilterAccordion(root) {
    var h3s = root.querySelectorAll('h3');
    Array.prototype.forEach.call(h3s, function (h3) {
      var ul = h3.nextElementSibling;
      if (!ul || ul.tagName !== 'UL') {
        return;
      }

      h3.classList.add('bb-filter-accordion-header');
      h3.setAttribute('role', 'button');
      h3.setAttribute('tabindex', '0');

      var expanded = rowHasNonDefaultChoice(ul);
      h3.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      ul.hidden = !expanded;

      h3.addEventListener('click', function () {
        toggleSection(h3, ul);
      });

      h3.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleSection(h3, ul);
        }
      });
    });
  }

  function run() {
    var root = document.getElementById('changelist-filter');
    if (!root) {
      return;
    }
    initChangelistFilterAccordion(root);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
