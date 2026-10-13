import re
import unicodedata

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_HYPHEN_AT_LINE_END = re.compile(r"(\w)-\n(\w)")
_SPACES_AND_TABS = re.compile(r"[ \t]+")
_MANY_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _CONTROL_CHARS.sub("", text)
    text = _HYPHEN_AT_LINE_END.sub(r"\1\2", text)
    text = _SPACES_AND_TABS.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = _MANY_BLANK_LINES.sub("\n\n", text)
    return text.strip()