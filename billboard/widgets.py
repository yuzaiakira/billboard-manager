from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class MediaLibraryWidget(ClearableFileInput):
    """Clearable file input plus a WordPress-like media library picker."""

    class Media:
        css = {'all': ('admin/css/media-library.css',)}
        js = ('admin/js/media-library.js',)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        media_url = attrs.get('data-media-url', '')
        library_name = '{}_library_path'.format(name)
        widget_id = attrs.get('id', 'id_{}'.format(name))
        library_id = '{}_library_path'.format(widget_id)

        file_html = super().render(name, value, attrs, renderer)
        return format_html(
            '<div class="media-library-widget" data-field-name="{}">'
            '{}<div class="media-library-controls" data-media-url="{}">'
            '<input type="hidden" name="{}" id="{}" value=""'
            ' class="media-library-path-input" autocomplete="off">'
            '<button type="button" class="button media-library-open-btn">'
            'انتخاب از کتابخانه</button>'
            '<span class="media-library-chosen" hidden></span>'
            '</div></div>',
            name,
            mark_safe(file_html),
            media_url,
            library_name,
            library_id,
        )
