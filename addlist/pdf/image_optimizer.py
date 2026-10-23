"""Resize/compress images for PDF preview and server-side PDF export."""

import hashlib
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple, Union

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static
from PIL import Image

from .exceptions import ImageOptimizeException

logger = logging.getLogger(__name__)

DEFAULT_MAX_SIDE = 1400
DEFAULT_QUALITY = 75
BRAND_MAX_WIDTH = 1240


class PdfImageOptimizer:
    """Optimize images to JPEG and cache under MEDIA_ROOT/cache/pdf/."""

    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        max_side: int = DEFAULT_MAX_SIDE,
        quality: int = DEFAULT_QUALITY,
    ):
        self.cache_dir = Path(cache_dir or os.path.join(settings.MEDIA_ROOT, 'cache', 'pdf'))
        self.max_side = max_side
        self.quality = quality

    def ensure_cache_dir(self) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        return self.cache_dir

    def resolve_source_path(self, source: Optional[str]) -> Optional[str]:
        """Resolve a media relative path, absolute path, or static name to a filesystem path."""
        if not source:
            return None
        if os.path.isabs(source) and os.path.isfile(source):
            return source
        media_candidate = os.path.join(settings.MEDIA_ROOT, source)
        if os.path.isfile(media_candidate):
            return media_candidate
        static_path = find_static(source)
        if static_path and os.path.isfile(static_path):
            return static_path
        # Fallback: BASE_DIR/static/...
        fallback = os.path.join(settings.BASE_DIR, 'static', source)
        if os.path.isfile(fallback):
            return fallback
        return None

    def cache_key(self, source_path: str, max_side: int, quality: int) -> str:
        try:
            mtime = os.path.getmtime(source_path)
            size = os.path.getsize(source_path)
        except OSError:
            mtime = 0
            size = 0
        raw = f'{source_path}|{mtime}|{size}|{max_side}|{quality}'
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:40]

    def optimize_file(
        self,
        source_path: str,
        max_side: Optional[int] = None,
        quality: Optional[int] = None,
    ) -> str:
        """
        Return filesystem path to a cached optimized JPEG.
        Raises ImageOptimizeException on failure.
        """
        side = max_side if max_side is not None else self.max_side
        q = quality if quality is not None else self.quality
        if not source_path or not os.path.isfile(source_path):
            raise ImageOptimizeException(
                'Source image not found',
                response={'source_path': source_path},
            )

        self.ensure_cache_dir()
        key = self.cache_key(source_path, side, q)
        dest = self.cache_dir / f'{key}.jpg'
        if dest.is_file():
            return str(dest)

        try:
            jpeg_bytes = self._encode_jpeg(source_path, side, q)
            tmp = dest.with_suffix('.tmp.jpg')
            tmp.write_bytes(jpeg_bytes)
            tmp.replace(dest)
            return str(dest)
        except ImageOptimizeException:
            raise
        except Exception as exc:
            raise ImageOptimizeException(
                str(exc),
                response={'source_path': source_path, 'error': str(exc)},
            ) from exc

    def optimize_to_bytes(
        self,
        source_path: str,
        max_side: Optional[int] = None,
        quality: Optional[int] = None,
    ) -> bytes:
        path = self.optimize_file(source_path, max_side=max_side, quality=quality)
        return Path(path).read_bytes()

    def media_url_for_cached(self, cached_path: str) -> str:
        """Build MEDIA_URL path for a file under MEDIA_ROOT."""
        cached_path = os.path.abspath(cached_path)
        media_root = os.path.abspath(settings.MEDIA_ROOT)
        if not cached_path.startswith(media_root):
            return ''
        rel = os.path.relpath(cached_path, media_root).replace(os.sep, '/')
        base = settings.MEDIA_URL.rstrip('/')
        return f'{base}/{rel}'

    def optimize_billboard_image(self, billboard) -> Tuple[Optional[str], Optional[str]]:
        """
        Optimize billboard main image.
        Returns (filesystem_path, media_url) or (None, None).
        """
        field = getattr(billboard, 'billboard_pic', None)
        if not field or not getattr(field, 'name', None):
            return self._optimize_static_fallback()
        source = self.resolve_source_path(field.name)
        if not source:
            # Try absolute path via storage
            try:
                source = field.path
            except Exception:
                source = None
        if not source:
            return self._optimize_static_fallback()
        try:
            cached = self.optimize_file(source)
            return cached, self.media_url_for_cached(cached)
        except ImageOptimizeException as exc:
            logger.warning('PDF image optimize failed for billboard %s: %s', getattr(billboard, 'pk', None), exc)
            return self._optimize_static_fallback()

    def optimize_static_asset(
        self,
        static_name: str,
        max_side: Optional[int] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
        source = self.resolve_source_path(static_name)
        if not source:
            return None, None
        try:
            cached = self.optimize_file(source, max_side=max_side)
            return cached, self.media_url_for_cached(cached)
        except ImageOptimizeException as exc:
            logger.warning('PDF static optimize failed for %s: %s', static_name, exc)
            return None, None

    def optimize_brand_assets(self) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Return (header_path, header_url, footer_path, footer_url)."""
        header_path, header_url = self.optimize_static_asset(
            'template/images/print/header.png',
            max_side=BRAND_MAX_WIDTH,
        )
        footer_path, footer_url = self.optimize_static_asset(
            'template/images/print/footer.png',
            max_side=BRAND_MAX_WIDTH,
        )
        return header_path, header_url, footer_path, footer_url

    def _optimize_static_fallback(self) -> Tuple[Optional[str], Optional[str]]:
        return self.optimize_static_asset('template/images/no-image.png')

    def _encode_jpeg(self, source_path: str, max_side: int, quality: int) -> bytes:
        with Image.open(source_path) as im:
            im = im.convert('RGB')
            w, h = im.size
            longest = max(w, h)
            if longest > max_side:
                scale = max_side / float(longest)
                new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
                resample = getattr(Image, 'Resampling', Image).LANCZOS
                im = im.resize(new_size, resample)
            buf = BytesIO()
            im.save(buf, format='JPEG', quality=quality, optimize=True)
            return buf.getvalue()
