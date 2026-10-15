from django.forms.widgets import ClearableFileInput, FileInput, NumberInput, TextInput
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe


class IntegerStepNumberWidget(NumberInput):
    """Number input whose spinner/arrows change the value by 1, not by decimals."""

    class Media:
        js = ('admin/js/integer-step-number.js',)

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'integer-step-number',
            # Allow any typed decimal; JS forces arrow/spinner step to 1.
            'step': 'any',
        }
        if attrs:
            classes = '{} {}'.format(
                default_attrs.get('class', ''),
                attrs.get('class', ''),
            ).strip()
            default_attrs.update(attrs)
            if classes:
                default_attrs['class'] = classes
            default_attrs['step'] = 'any'
        super().__init__(attrs=default_attrs)


class ThousandSeparatedNumberWidget(TextInput):
    """Text input that shows integers with thousand separators while typing."""

    class Media:
        js = ('admin/js/thousand-separator.js',)

    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'vBigIntegerField thousand-separator-input',
            'inputmode': 'numeric',
            'autocomplete': 'off',
        }
        if attrs:
            classes = '{} {}'.format(
                default_attrs.get('class', ''),
                attrs.get('class', ''),
            ).strip()
            default_attrs.update(attrs)
            if classes:
                default_attrs['class'] = classes
        super().__init__(attrs=default_attrs)

    def format_value(self, value):
        if value is None or value == '':
            return ''
        try:
            return '{:,}'.format(int(value))
        except (TypeError, ValueError):
            return value

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value is None:
            return None
        cleaned = (
            str(value)
            .replace(',', '')
            .replace('\u066c', '')  # Arabic thousands separator
            .replace('\u2009', '')  # thin space
            .replace(' ', '')
            .strip()
        )
        return cleaned or None


class MediaLibraryWidget(ClearableFileInput):
    """Clearable file input plus a WordPress-like media library picker."""

    input_text = ''
    initial_text = ''
    clear_checkbox_label = ''

    class Media:
        css = {'all': ('admin/css/media-library.css',)}
        js = ('admin/js/media-library.js',)

    def render(self, name, value, attrs=None, renderer=None):
        merged_attrs = {}
        merged_attrs.update(self.attrs or {})
        merged_attrs.update(attrs or {})
        media_url = merged_attrs.get('data-media-url', '')
        library_name = '{}_library_path'.format(name)
        widget_id = merged_attrs.get('id', 'id_{}'.format(name))
        library_id = '{}_library_path'.format(widget_id)

        render_attrs = dict(attrs or {})
        render_attrs['accept'] = merged_attrs.get('accept') or 'image/*'
        # Native file input only (no Django "Currently: path" chrome).
        file_html = FileInput.render(self, name, value, render_attrs, renderer)

        preview_url = ''
        preview_name = ''
        if self.is_initial(value):
            preview_url = value.url
            preview_name = conditional_escape(
                getattr(value, 'name', '') or ''
            ).rsplit('/', 1)[-1]

        clear_html = ''
        has_initial = self.is_initial(value)
        can_clear = has_initial and not self.is_required
        if can_clear:
            checkbox_name = self.clear_checkbox_name(name)
            checkbox_id = self.clear_checkbox_id(checkbox_name)
            clear_html = format_html(
                '<input type="checkbox" name="{}" id="{}"'
                ' class="media-library-clear-input" autocomplete="off">',
                checkbox_name,
                checkbox_id,
            )

        clear_disabled = '' if can_clear else ' disabled'
        preview_hidden = '' if preview_url else ' hidden'

        return format_html(
            '<div class="media-library-widget" data-field-name="{}">'
            '<div class="media-library-controls" data-media-url="{}">'
            '<input type="hidden" name="{}" id="{}" value=""'
            ' class="media-library-path-input" autocomplete="off">'
            '<button type="button" class="button media-library-open-btn">'
            'انتخاب از کتابخانه</button>'
            '<button type="button" class="button media-library-upload-btn">'
            'آپلود تصویر جدید</button>'
            '<button type="button" class="button media-library-clear-btn"{}>'
            'حذف تصویر</button>'
            '<span class="media-library-chosen" hidden></span>'
            '</div>'
            '<div class="media-library-preview"{}>'
            '<img src="{}" alt="{}" class="media-library-preview-img">'
            '</div>'
            '<div class="media-library-file-slot">{}{}</div>'
            '</div>',
            name,
            media_url,
            library_name,
            library_id,
            mark_safe(clear_disabled),
            mark_safe(preview_hidden),
            preview_url or '',
            preview_name,
            mark_safe(clear_html),
            mark_safe(file_html),
        )
