"""Server-side watchlist PDF generator (ReportLab + RTL)."""

import logging
import os
from io import BytesIO
from typing import Any, Dict, List, Optional

import arabic_reshaper
try:
    from bidi.algorithm import get_display
except ImportError:  # python-bidi >= 0.6
    from bidi import get_display
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from billboard.utils import billboard_bool_value

from .dataclasses import PdfBuildInput, PdfPageData, PdfResult
from .exceptions import PdfGenerationException, ResponseException
from .image_optimizer import PdfImageOptimizer

logger = logging.getLogger(__name__)

PAGE_WIDTH, PAGE_HEIGHT = A4

FIELD_ORDER = (
    ('id_code', 'کد بیلبورد'),
    ('name', 'نام'),
    ('description', 'توضیحات'),
    ('address_location', 'محل بیلبورد'),
    ('address', 'آدرس'),
    ('has_power', 'وضعیت روشنایی'),
    ('size_length', 'طول'),
    ('size_width', 'عرض'),
    ('reservation_date', 'تاریخ قابل اجاره'),
    ('price', 'قیمت'),
)


def _normalize_decimal(value) -> str:
    if value is None:
        return ''
    try:
        num = float(value)
        if num == int(num):
            return str(int(num))
        return str(num).rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return str(value) if value is not None else ''


def reshape_rtl(text: str) -> str:
    """Prepare Persian/Arabic text for ReportLab LTR canvas."""
    if text is None:
        return ''
    s = str(text)
    if not s:
        return ''
    try:
        return get_display(arabic_reshaper.reshape(s))
    except Exception:
        return s


class WatchlistPdfGenerator:
    """
    Pipeline-based watchlist PDF builder.

    Pipeline:
    1. Normalize input (flags, items, overrides)
    2. Register fonts
    3. Optimize brand assets when needed
    4. Build pages
    5. Return PDF bytes
    """

    FONT_REGULAR = 'VazirmatnFD'
    FONT_BOLD = 'VazirmatnFD-Bold'

    def __init__(self, optimizer: Optional[PdfImageOptimizer] = None):
        self.optimizer = optimizer or PdfImageOptimizer()
        self._fonts_ready = False

    def execute(
        self,
        items,
        field_flags: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        normalized_flags = field_flags or {}
        normalized_overrides = overrides or {}

        try:
            build_input = self._normalize_input(items, normalized_flags, normalized_overrides)
            self._ensure_fonts()
            pdf_bytes = self._render_pdf(build_input)
            return self._build_success(pdf_bytes).to_dict()
        except ResponseException as exc:
            return self._build_error(exc).to_dict()
        except Exception as exc:
            logger.exception('Unexpected PDF generation error')
            return self._build_unexpected(exc).to_dict()

    def _normalize_input(self, items, field_flags: Dict[str, Any], overrides: Dict[str, Dict[str, str]]) -> PdfBuildInput:
        show_image = bool(field_flags.get('billboard_pic', True))
        show_brand = bool(field_flags.get('brand', False))

        header_path = footer_path = None
        if show_brand:
            header_path, _, footer_path, _ = self.optimizer.optimize_brand_assets()

        pages: List[PdfPageData] = []
        for item in items:
            billboard = item.billboard
            bb_id = billboard.pk
            override = overrides.get(str(bb_id)) or overrides.get(bb_id) or {}

            image_path = None
            if show_image:
                image_path, _ = self.optimizer.optimize_billboard_image(billboard)

            fields = self._build_field_values(billboard, field_flags, override)
            pages.append(PdfPageData(billboard_id=bb_id, image_path=image_path, fields=fields))

        if not pages:
            raise PdfGenerationException(
                'لیست بیلبورد خالی است',
                response={'error_code': 'EMPTY_LIST'},
            )

        return PdfBuildInput(
            pages=pages,
            show_image=show_image,
            show_brand=show_brand,
            brand_header_path=header_path,
            brand_footer_path=footer_path,
        )

    def _build_field_values(self, billboard, field_flags: Dict[str, Any], override: Dict[str, str]) -> Dict[str, str]:
        values: Dict[str, str] = {}

        def pick(key: str, default: str) -> str:
            if key in override and override[key] is not None:
                return str(override[key])
            return default

        if field_flags.get('id_code', True):
            values['id_code'] = pick('id_code', str(billboard.id))
        if field_flags.get('name'):
            values['name'] = pick('name', billboard.name or '')
        if field_flags.get('description'):
            values['description'] = pick('description', billboard.description or '')
        if field_flags.get('address', True):
            city = getattr(billboard, 'city', None)
            state_name = ''
            city_name = ''
            if city is not None:
                city_name = getattr(city, 'name', '') or ''
                state = getattr(city, 'state', None)
                if state is not None:
                    state_name = getattr(state, 'name', '') or ''
            location = f'{state_name} - {city_name}'.strip(' -')
            values['address_location'] = pick('address_location', location)
            values['address'] = pick('address', billboard.address or '')
        if field_flags.get('has_power', True):
            values['has_power'] = pick('has_power', billboard_bool_value(billboard.has_power))
        if field_flags.get('size', True):
            values['size_length'] = pick('size_length', _normalize_decimal(billboard.billboard_length))
            values['size_width'] = pick('size_width', _normalize_decimal(billboard.billboard_width))
        if field_flags.get('reservation_date'):
            d = billboard.reservation_date
            if d and hasattr(d, 'year'):
                default_date = f'{d.year}/{d.month:02d}/{d.day:02d}'
            else:
                default_date = str(d) if d else ''
            values['reservation_date'] = pick('reservation_date', default_date)
        if field_flags.get('price'):
            price_val = None
            final = getattr(billboard, 'BillboardFinalPriceModel', None)
            if final is not None and getattr(final, 'final_price', None):
                price_val = final.final_price
            else:
                price_val = billboard.price
            try:
                formatted = f'{int(price_val):,}' if price_val is not None else ''
            except (TypeError, ValueError):
                formatted = str(price_val or '')
            default_price = f'{formatted} تومان' if formatted else ''
            values['price'] = pick('price', default_price)

        return values

    def _ensure_fonts(self) -> None:
        if self._fonts_ready:
            return
        regular = os.path.join(
            settings.BASE_DIR,
            'static/template/fonts/vazir-Farsi-Digits/ttf/Vazirmatn-FD-Regular.ttf',
        )
        bold = os.path.join(
            settings.BASE_DIR,
            'static/template/fonts/vazir-Farsi-Digits/ttf/Vazirmatn-FD-Bold.ttf',
        )
        if not os.path.isfile(regular):
            raise PdfGenerationException(
                'فونت فارسی یافت نشد',
                response={'path': regular, 'error_code': 'FONT_MISSING'},
            )
        if self.FONT_REGULAR not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(self.FONT_REGULAR, regular))
        if os.path.isfile(bold) and self.FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(self.FONT_BOLD, bold))
        else:
            # Fall back to regular if bold missing
            if self.FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(self.FONT_BOLD, regular))
        self._fonts_ready = True

    def _render_pdf(self, build_input: PdfBuildInput) -> bytes:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        for index, page in enumerate(build_input.pages):
            if index > 0:
                c.showPage()
            self._draw_page(c, page, build_input)

        c.save()
        return buffer.getvalue()

    def _draw_page(self, c: canvas.Canvas, page: PdfPageData, build_input: PdfBuildInput) -> None:
        margin_x = 15 * mm
        content_top = PAGE_HEIGHT - 12 * mm
        content_bottom = 12 * mm

        if build_input.show_brand:
            brand_h = 28 * mm
            if build_input.brand_header_path and os.path.isfile(build_input.brand_header_path):
                self._draw_image_fit(
                    c,
                    build_input.brand_header_path,
                    0,
                    PAGE_HEIGHT - brand_h,
                    PAGE_WIDTH,
                    brand_h,
                )
                content_top = PAGE_HEIGHT - brand_h - 6 * mm
            if build_input.brand_footer_path and os.path.isfile(build_input.brand_footer_path):
                self._draw_image_fit(
                    c,
                    build_input.brand_footer_path,
                    0,
                    0,
                    PAGE_WIDTH,
                    brand_h,
                )
                content_bottom = brand_h + 6 * mm

        y = content_top
        max_img_h = 120 * mm
        max_img_w = PAGE_WIDTH - 2 * margin_x

        if build_input.show_image and page.image_path and os.path.isfile(page.image_path):
            drawn_h = self._draw_image_fit(
                c,
                page.image_path,
                margin_x,
                y - max_img_h,
                max_img_w,
                max_img_h,
                anchor_top=True,
            )
            y = y - drawn_h - 8 * mm
        else:
            y = y - 4 * mm

        right_x = PAGE_WIDTH - margin_x
        line_h = 8 * mm
        c.setFont(self.FONT_REGULAR, 12)

        for key, label in FIELD_ORDER:
            if key not in page.fields:
                continue
            if y < content_bottom + line_h:
                break
            value = page.fields[key]
            label_rtl = reshape_rtl(f'{label}: ')
            value_rtl = reshape_rtl(value)
            c.setFont(self.FONT_BOLD, 12)
            c.drawRightString(right_x, y, label_rtl)
            label_width = c.stringWidth(label_rtl, self.FONT_BOLD, 12)
            c.setFont(self.FONT_REGULAR, 12)
            c.drawRightString(right_x - label_width - 2 * mm, y, value_rtl)
            y -= line_h

    def _draw_image_fit(
        self,
        c: canvas.Canvas,
        path: str,
        x: float,
        y: float,
        max_w: float,
        max_h: float,
        anchor_top: bool = False,
    ) -> float:
        """Draw image contained in box; return drawn height."""
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(path)
            iw, ih = img.getSize()
            if iw <= 0 or ih <= 0:
                return 0
            scale = min(max_w / iw, max_h / ih)
            dw, dh = iw * scale, ih * scale
            draw_x = x + (max_w - dw) / 2
            if anchor_top:
                draw_y = y + max_h - dh
            else:
                draw_y = y + (max_h - dh) / 2
            c.drawImage(img, draw_x, draw_y, width=dw, height=dh, preserveAspectRatio=True, mask='auto')
            return dh
        except Exception as exc:
            logger.warning('Failed to draw image %s: %s', path, exc)
            return 0

    def _build_success(self, pdf_bytes: bytes) -> PdfResult:
        return PdfResult(success=True, message='PDF generated', pdf_bytes=pdf_bytes)

    def _build_error(self, exc: ResponseException) -> PdfResult:
        error_code = None
        if isinstance(exc.response, dict):
            error_code = exc.response.get('error_code')
        return PdfResult(
            success=False,
            message=str(exc),
            error_code=error_code,
            error_details=exc.response if isinstance(exc.response, dict) else None,
        )

    def _build_unexpected(self, exc: Exception) -> PdfResult:
        return PdfResult(
            success=False,
            message='خطا در ساخت PDF',
            error_code='UNEXPECTED_ERROR',
            error_details={'exception': str(exc)},
        )
