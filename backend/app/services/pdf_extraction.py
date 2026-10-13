import logging
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from app.services.text_cleaning import clean_text

logger = logging.getLogger(__name__)

MIN_TOTAL_CHARS = 50


class ExtractionError(Exception):
    """An extraction error safe to report to the user."""


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str


@dataclass(frozen=True)
class ExtractionResult:
    page_count: int
    pages: list[PageText]


def extract_pages(path: Path, *, max_pages: int) -> ExtractionResult:
    try:
        reader = PdfReader(str(path))

        if reader.is_encrypted and not reader.decrypt(""):
            raise ExtractionError(
                "This PDF is password-protected. Please upload an unlocked copy."
            )

        page_count = len(reader.pages)

        if page_count == 0:
            raise ExtractionError("The PDF has no pages.")

        if page_count > max_pages:
            raise ExtractionError(
                f"The PDF has {page_count} pages. "
                f"The maximum is {max_pages}."
            )

        pages: list[PageText] = []

        for index, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "")

            if text:
                pages.append(PageText(page_number=index, text=text))

    except ExtractionError:
        raise
    except Exception as exc:
        logger.warning("Could not read PDF %s: %s", path.name, exc)
        raise ExtractionError(
            "The PDF could not be read. "
            "It may be corrupted or in an unsupported format."
        ) from exc

    if sum(len(page.text) for page in pages) < MIN_TOTAL_CHARS:
        raise ExtractionError(
            "No readable text was found. This looks like a scanned "
            "or image-only PDF. OCR is not supported yet."
        )

    return ExtractionResult(page_count=page_count, pages=pages)