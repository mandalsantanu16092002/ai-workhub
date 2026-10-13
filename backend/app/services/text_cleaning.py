
import re
import unicodedata


def clean_text(text: str) -> str:
    """Normalize extracted PDF text while preserving useful paragraph breaks."""
    if not text:
        return ""

    # Normalize Unicode characters.
    text = unicodedata.normalize("NFKC", text)

    # Join words split across lines by PDF extraction.
    text = re.sub(r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)", "", text)

    # Normalize Windows and old-style line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove control characters, but preserve line breaks and tabs for now.
    text = "".join(
        char for char in text
        if char in "\n\t" or unicodedata.category(char) != "Cc"
    )

    # Normalize horizontal whitespace.
    text = re.sub(r"[^\S\n]+", " ", text)

    # Remove whitespace around paragraph breaks.
    text = re.sub(r" *\n *", "\n", text)

    # Collapse excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
