"""Exceptions for PDF export pipeline."""

from typing import Any, Optional


class ResponseException(Exception):
    """Base exception for PDF pipeline errors."""

    def __init__(self, message: str, response: Any = None):
        self.message = message
        self.response = response
        super().__init__(self.message)


class PdfGenerationException(ResponseException):
    """Raised when PDF generation fails."""

    pass


class ImageOptimizeException(ResponseException):
    """Raised when an image cannot be optimized for PDF."""

    pass
