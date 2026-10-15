(function () {
  'use strict';

  function digitsOnly(value) {
    return String(value || '').replace(/[^\d]/g, '');
  }

  function formatThousands(value) {
    var digits = digitsOnly(value);
    if (!digits) {
      return '';
    }
    return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  function caretAfterDigits(formatted, digitCount) {
    if (digitCount <= 0) {
      return 0;
    }
    var seen = 0;
    for (var i = 0; i < formatted.length; i += 1) {
      if (/\d/.test(formatted.charAt(i))) {
        seen += 1;
        if (seen >= digitCount) {
          return i + 1;
        }
      }
    }
    return formatted.length;
  }

  function bindInput(input) {
    if (input.dataset.thousandBound === '1') {
      return;
    }
    input.dataset.thousandBound = '1';

    if (input.value) {
      input.value = formatThousands(input.value);
    }

    input.addEventListener('input', function () {
      var previous = input.value;
      var cursor = input.selectionStart || 0;
      var digitsBefore = digitsOnly(previous.slice(0, cursor)).length;
      var formatted = formatThousands(previous);
      input.value = formatted;
      var nextPos = caretAfterDigits(formatted, digitsBefore);
      input.setSelectionRange(nextPos, nextPos);
    });

    if (input.form) {
      input.form.addEventListener('submit', function () {
        input.value = digitsOnly(input.value);
      });
    }
  }

  function init(root) {
    var scope = root || document;
    scope.querySelectorAll('.thousand-separator-input').forEach(bindInput);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      init();
    });
  } else {
    init();
  }
})();
