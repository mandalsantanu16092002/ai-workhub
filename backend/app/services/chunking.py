import re
from dataclasses import dataclass

from app.services.pdf_extraction import PageText

SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+")


@dataclass(frozen=True)
class Chunk:
    page_number: int
    text: str


def split_units(text: str, size: int) -> list[str]:
    units: list[str] = []

    for piece in SENTENCE_BOUNDARY.split(text):
        piece = piece.strip()
        if not piece:
            continue

        if len(piece) <= size:
            units.append(piece)
        else:
            units.extend(
                piece[index : index + size]
                for index in range(0, len(piece), size)
            )

    return units


def overlap_tail(units: list[str], overlap: int) -> tuple[list[str], int]:
    tail: list[str] = []
    total = 0

    for unit in reversed(units):
        if total + len(unit) + 1 > overlap:
            break
        tail.insert(0, unit)
        total += len(unit) + 1

    return tail, total


def chunk_text(text: str, *, size: int, overlap: int) -> list[str]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > overlap >= 0")

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for unit in split_units(text, size):
        needed = len(unit) + 1

        if current and current_len + needed > size:
            chunks.append(" ".join(current))
            current, current_len = overlap_tail(current, overlap)

            while current and current_len + needed > size:
                dropped = current.pop(0)
                current_len -= len(dropped) + 1

        current.append(unit)
        current_len += needed

    if current:
        chunks.append(" ".join(current))

    return chunks


def chunk_pages(
    pages: list[PageText],
    *,
    size: int,
    overlap: int,
) -> list[Chunk]:
    return [
        Chunk(page_number=page.page_number, text=text)
        for page in pages
        for text in chunk_text(page.text, size=size, overlap=overlap)
    ]