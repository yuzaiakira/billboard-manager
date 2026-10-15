(function () {
  'use strict';

  var PAGE_SIZE = 24;
  var modal = null;
  var activeWidget = null;
  var currentPage = 1;
  var currentQuery = '';
  var hasNext = false;

  function ensureModal() {
    if (modal) {
      return modal;
    }

    modal = document.createElement('div');
    modal.className = 'media-library-modal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.innerHTML =
      '<div class="media-library-dialog">' +
      '  <div class="media-library-header">' +
      '    <h2>کتابخانه رسانه</h2>' +
      '    <button type="button" class="media-library-close-btn" aria-label="بستن">&times;</button>' +
      '  </div>' +
      '  <div class="media-library-toolbar">' +
      '    <input type="search" class="media-library-search" placeholder="جستجوی نام فایل..." />' +
      '    <button type="button" class="button media-library-search-btn">جستجو</button>' +
      '  </div>' +
      '  <div class="media-library-body">' +
      '    <div class="media-library-loading">در حال بارگذاری...</div>' +
      '    <div class="media-library-grid" hidden></div>' +
      '    <div class="media-library-empty" hidden>تصویری یافت نشد.</div>' +
      '    <div class="media-library-error" hidden></div>' +
      '  </div>' +
      '  <div class="media-library-footer">' +
      '    <button type="button" class="button media-library-prev-btn" disabled>قبلی</button>' +
      '    <span class="media-library-page-label"></span>' +
      '    <button type="button" class="button media-library-next-btn" disabled>بعدی</button>' +
      '  </div>' +
      '</div>';

    document.body.appendChild(modal);

    modal.querySelector('.media-library-close-btn').addEventListener('click', closeModal);
    modal.addEventListener('click', function (event) {
      if (event.target === modal) {
        closeModal();
      }
    });
    modal.querySelector('.media-library-search-btn').addEventListener('click', function () {
      currentQuery = modal.querySelector('.media-library-search').value.trim();
      currentPage = 1;
      loadItems();
    });
    modal.querySelector('.media-library-search').addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        currentQuery = event.target.value.trim();
        currentPage = 1;
        loadItems();
      }
    });
    modal.querySelector('.media-library-prev-btn').addEventListener('click', function () {
      if (currentPage > 1) {
        currentPage -= 1;
        loadItems();
      }
    });
    modal.querySelector('.media-library-next-btn').addEventListener('click', function () {
      if (hasNext) {
        currentPage += 1;
        loadItems();
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && modal.classList.contains('is-open')) {
        closeModal();
      }
    });

    return modal;
  }

  function openModal(widget) {
    activeWidget = widget;
    currentPage = 1;
    currentQuery = '';
    ensureModal();
    modal.querySelector('.media-library-search').value = '';
    modal.classList.add('is-open');
    loadItems();
  }

  function closeModal() {
    if (!modal) {
      return;
    }
    modal.classList.remove('is-open');
    activeWidget = null;
  }

  function setLoading(isLoading) {
    modal.querySelector('.media-library-loading').hidden = !isLoading;
    if (isLoading) {
      modal.querySelector('.media-library-grid').hidden = true;
      modal.querySelector('.media-library-empty').hidden = true;
      modal.querySelector('.media-library-error').hidden = true;
    }
  }

  function showError(message) {
    setLoading(false);
    var err = modal.querySelector('.media-library-error');
    err.hidden = false;
    err.textContent = message || 'خطای ناشناخته';
  }

  function loadItems() {
    if (!activeWidget) {
      return;
    }
    var controls = activeWidget.querySelector('.media-library-controls');
    var mediaUrl = (controls && controls.getAttribute('data-media-url')) || '';
    if (!mediaUrl) {
      var fileInput = activeWidget.querySelector('input[type="file"]');
      mediaUrl = (fileInput && fileInput.getAttribute('data-media-url')) || '';
    }
    if (!mediaUrl) {
      showError('آدرس کتابخانه رسانه تنظیم نشده است.');
      return;
    }

    setLoading(true);
    var url = mediaUrl + (mediaUrl.indexOf('?') >= 0 ? '&' : '?') +
      'page=' + encodeURIComponent(currentPage) +
      '&page_size=' + encodeURIComponent(PAGE_SIZE) +
      '&q=' + encodeURIComponent(currentQuery);

    fetch(url, {
      credentials: 'same-origin',
      headers: { 'Accept': 'application/json' }
    })
      .then(function (response) {
        if (!response.ok) {
          throw new Error('خطا در دریافت تصاویر');
        }
        return response.json();
      })
      .then(function (data) {
        renderItems(data.results || []);
        hasNext = !!data.has_next;
        modal.querySelector('.media-library-prev-btn').disabled = currentPage <= 1;
        modal.querySelector('.media-library-next-btn').disabled = !hasNext;
        modal.querySelector('.media-library-page-label').textContent =
          'صفحه ' + currentPage + (data.total != null ? ' از ' + Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : '');
      })
      .catch(function (error) {
        showError(error.message || 'خطای ناشناخته');
      });
  }

  function renderItems(items) {
    setLoading(false);
    var grid = modal.querySelector('.media-library-grid');
    var empty = modal.querySelector('.media-library-empty');
    grid.innerHTML = '';

    if (!items.length) {
      grid.hidden = true;
      empty.hidden = false;
      return;
    }

    empty.hidden = true;
    grid.hidden = false;

    items.forEach(function (item) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'media-library-item';
      button.setAttribute('data-path', item.path);
      button.title = item.name || item.path;

      var img = document.createElement('img');
      img.src = item.url;
      img.alt = item.name || '';
      img.loading = 'lazy';

      var label = document.createElement('span');
      label.className = 'media-library-item-name';
      label.textContent = item.name || item.path;

      button.appendChild(img);
      button.appendChild(label);
      button.addEventListener('click', function () {
        selectItem(item);
      });
      grid.appendChild(button);
    });
  }

  function getPreview(widget) {
    return widget.querySelector('.media-library-preview');
  }

  function getPreviewImg(widget) {
    return widget.querySelector('.media-library-preview-img');
  }

  function setClearChecked(widget, checked) {
    var clearInput = widget.querySelector('.media-library-clear-input');
    if (clearInput) {
      clearInput.checked = !!checked;
    }
  }

  function setClearEnabled(widget, enabled) {
    var clearBtn = widget.querySelector('.media-library-clear-btn');
    if (clearBtn) {
      clearBtn.disabled = !enabled;
    }
  }

  function showPreview(widget, url, note) {
    var preview = getPreview(widget);
    var img = getPreviewImg(widget);
    var chosen = widget.querySelector('.media-library-chosen');
    if (preview && img && url) {
      img.src = url;
      img.alt = note || '';
      preview.hidden = false;
    }
    if (chosen) {
      if (note) {
        chosen.hidden = false;
        chosen.textContent = note;
      } else {
        chosen.hidden = true;
        chosen.textContent = '';
      }
    }
    setClearEnabled(widget, true);
    setClearChecked(widget, false);
  }

  function hidePreview(widget, note) {
    var preview = getPreview(widget);
    var img = getPreviewImg(widget);
    var chosen = widget.querySelector('.media-library-chosen');
    if (preview) {
      preview.hidden = true;
    }
    if (img) {
      img.removeAttribute('src');
      img.alt = '';
    }
    if (chosen) {
      if (note) {
        chosen.hidden = false;
        chosen.textContent = note;
      } else {
        chosen.hidden = true;
        chosen.textContent = '';
      }
    }
  }

  function selectItem(item) {
    if (!activeWidget) {
      return;
    }
    var pathInput = activeWidget.querySelector('.media-library-path-input');
    var fileInput = activeWidget.querySelector('input[type="file"]');

    if (pathInput) {
      pathInput.value = item.path;
    }
    if (fileInput) {
      try {
        fileInput.value = '';
      } catch (e) {
        /* ignore */
      }
    }
    showPreview(activeWidget, item.url, 'انتخاب شده: ' + (item.name || item.path));
    closeModal();
  }

  function clearImage(widget) {
    var pathInput = widget.querySelector('.media-library-path-input');
    var fileInput = widget.querySelector('input[type="file"]');
    if (pathInput) {
      pathInput.value = '';
    }
    if (fileInput) {
      try {
        fileInput.value = '';
      } catch (e) {
        /* ignore */
      }
    }
    setClearChecked(widget, true);
    setClearEnabled(widget, false);
    hidePreview(widget, 'تصویر پس از ذخیره حذف می‌شود');
  }

  function updateUploadChosen(widget, fileInput) {
    var pathInput = widget.querySelector('.media-library-path-input');
    if (pathInput) {
      pathInput.value = '';
    }
    if (fileInput.files && fileInput.files.length) {
      var file = fileInput.files[0];
      var objectUrl = URL.createObjectURL(file);
      showPreview(widget, objectUrl, 'آماده آپلود: ' + file.name);
    }
  }

  function bindWidgets(root) {
    (root || document).querySelectorAll('.media-library-widget').forEach(function (widget) {
      if (widget.getAttribute('data-media-bound') === '1') {
        return;
      }
      widget.setAttribute('data-media-bound', '1');

      var openBtn = widget.querySelector('.media-library-open-btn');
      if (openBtn) {
        openBtn.addEventListener('click', function () {
          openModal(widget);
        });
      }

      var fileInput = widget.querySelector('input[type="file"]');
      var uploadBtn = widget.querySelector('.media-library-upload-btn');
      if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', function () {
          fileInput.click();
        });
      }
      if (fileInput) {
        fileInput.addEventListener('change', function () {
          updateUploadChosen(widget, fileInput);
        });
      }

      var clearBtn = widget.querySelector('.media-library-clear-btn');
      if (clearBtn) {
        clearBtn.addEventListener('click', function () {
          clearImage(widget);
        });
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindWidgets(document);
  });

  if (typeof django !== 'undefined' && django.jQuery) {
    django.jQuery(document).on('formset:added', function (event, $row) {
      bindWidgets(($row && $row[0]) || event.target);
    });
  }
})();
