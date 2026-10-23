"""Data structures for PDF export."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PdfPageData:
    """One billboard page for the PDF."""

    billboard_id: int
    image_path: Optional[str] = None
    fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class PdfBuildInput:
    """Normalized input for WatchlistPdfGenerator."""

    pages: List[PdfPageData]
    show_image: bool = True
    show_brand: bool = False
    brand_header_path: Optional[str] = None
    brand_footer_path: Optional[str] = None


@dataclass
class PdfResult:
    """Result of PDF generation."""

    success: bool
    message: str
    pdf_bytes: Optional[bytes] = None
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'success': self.success,
            'message': self.message,
        }
        if self.pdf_bytes is not None:
            result['pdf_bytes'] = self.pdf_bytes
        if self.error_code:
            result['error_code'] = self.error_code
        if self.error_details:
            result['error_details'] = self.error_details
        return result
