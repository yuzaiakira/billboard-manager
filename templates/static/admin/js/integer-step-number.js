(function () {
  'use strict';

  function parseValue(raw) {
    if (raw === '' || raw === null || raw === undefined) {
      return 0;
    }
    var num = Number(raw);
    return Number.isFinite(num) ? num : 0;
  }

  function formatStepped(value) {
    // Keep up to 3 decimal places, drop trailing zeros.
    var fixed = value.toFixed(3);
    return fixed.replace(/\.?0+$/, '') || '0';
  }

  function stepByOne(input, direction) {
    var next = parseValue(input.value) + direction;
    if (input.min !== '' && next < Number(input.min)) {
      next = Number(input.min);
    }
    if (input.max !== '' && next > Number(input.max)) {
      next = Number(input.max);
    }
    input.value = formatStepped(next);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function bindInput(input) {
    if (input.dataset.integerStepBound === '1') {
      return;
    }
    input.dataset.integerStepBound = '1';
    input.setAttribute('step', 'any');

    input.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowUp') {
        event.preventDefault();
        stepByOne(input, 1);
      } else if (event.key === 'ArrowDown') {
        event.preventDefault();
        stepByOne(input, -1);
      }
    });

    // Mouse spinner: briefly use step=1 so the browser adjusts by whole units.
    input.addEventListener('mousedown', function () {
      input.setAttribute('step', '1');
    });
    input.addEventListener('mouseup', function () {
      input.setAttribute('step', 'any');
    });
    input.addEventListener('blur', function () {
      input.setAttribute('step', 'any');
    });
  }

  function init(root) {
    var scope = root || document;
    scope.querySelectorAll('.integer-step-number').forEach(bindInput);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      init();
    });
  } else {
    init();
  }
})();
